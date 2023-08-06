"""
    Emonoda -- A set of tools to organize and manage your torrents
    Copyright (C) 2015  Devaev Maxim <mdevaev@gmail.com>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""


import sys
import os
import contextlib
import argparse

from ..optconf import make_config
from ..optconf import Section
from ..optconf import Option

from ..optconf import build_raw_from_options
from ..optconf.dumper import make_config_dump
from ..optconf.loaders.yaml import load_file as load_yaml_file
from ..optconf.converters import (
    as_string_or_none,
    as_string_list,
    as_path,
    as_path_or_none,
    as_8int_or_none,
)

from ..plugins import get_conveyor_class
from ..plugins import get_client_class
from ..plugins import get_fetcher_class

from ..plugins.conveyors import WithLogs as O_WithLogs
from ..plugins.fetchers import WithLogin as F_WithLogin
from ..plugins.fetchers import WithCaptcha as F_WithCaptcha
from ..plugins.clients import WithCustoms as C_WithCustoms

from .. import cli


# =====
def init():
    args_parser = argparse.ArgumentParser(add_help=False)
    args_parser.add_argument("-c", "--config", dest="config_file_path", default="~/.config/emonoda.yaml", metavar="<file>")
    args_parser.add_argument("-o", "--set-options", dest="set_options", default=[], nargs="+")
    args_parser.add_argument("-m", "--dump-config", dest="dump_config", action="store_true")
    (options, remaining) = args_parser.parse_known_args(sys.argv)

    options.config_file_path = os.path.expanduser(options.config_file_path)
    if os.path.exists(options.config_file_path):
        raw_config = load_yaml_file(options.config_file_path)
    else:
        raw_config = {}
    _merge_dicts(raw_config, build_raw_from_options(options.set_options))
    scheme = _get_config_scheme()
    config = make_config(raw_config, scheme)

    if config.core.client is not None:
        client_scheme = get_client_class(config.core.client).get_options()
        scheme["client"] = client_scheme
        config = make_config(raw_config, scheme)

    for fetcher_name in raw_config.get("fetchers", []):
        fetcher_scheme = get_fetcher_class(fetcher_name).get_options()
        scheme.setdefault("fetchers", {})
        scheme["fetchers"][fetcher_name] = fetcher_scheme
    config = make_config(raw_config, scheme)

    conveyor_scheme = get_conveyor_class(config.emfetch.conveyor).get_options()
    scheme["conveyor"] = conveyor_scheme
    config = make_config(raw_config, scheme)

    if options.dump_config:
        print(make_config_dump(config, split_by=((), ("fetchers",))))
        sys.exit(0)

    config.setdefault("client", Section())
    config.setdefault("fetchers", Section())

    return (args_parser, remaining, config)


def _merge_dicts(dest, src, path=None):
    if path is None:
        path = []
    for key in src:
        if key in dest:
            if isinstance(dest[key], dict) and isinstance(src[key], dict):
                _merge_dicts(dest[key], src[key], list(path) + [str(key)])
                continue
        dest[key] = src[key]


# =====
@contextlib.contextmanager
def get_configured_log(config, quiet, output):
    log = cli.Log(config.core.use_colors, config.core.force_colors, quiet, output)
    try:
        yield log
    finally:
        log.finish()


def get_configured_conveyor(config, log_stdout, log_stderr):
    name = config.emfetch.conveyor
    log_stderr.info("Enabling the conveyor {blue}%s{reset} ...", (name,), one_line=True)
    try:
        kwargs = dict(config.conveyor)
        conveyor_class = get_conveyor_class(name)
        if O_WithLogs in conveyor_class.get_bases():
            kwargs.update({
                "log_stdout": log_stdout,
                "log_stderr": log_stderr,
            })
        conveyor = conveyor_class(**kwargs)
    except Exception as err:
        log_stderr.error("Init error: {red}%s{reset}: {red}%s{reset}(%s)", (name, type(err).__name__, err))
        raise
    log_stderr.info("Conveyor {blue}%s{reset} is {green}ready{reset}", (name,))
    return conveyor


def get_configured_client(config, required, with_customs, log):
    name = config.core.client
    if name is not None:
        log.info("Enabling the client {blue}%s{reset} ...", (name,), one_line=True)
        try:
            client = get_client_class(name)(**config.client)
            if with_customs and C_WithCustoms not in client.get_bases():
                raise RuntimeError("Your client does not support customs")
        except Exception as err:
            log.error("Init error: {red}%s{reset}: {red}%s{reset}(%s)", (name, type(err).__name__, err))
            raise
        log.info("Client {blue}%s{reset} is {green}ready{reset}", (name,))
        return client
    elif required:
        raise RuntimeError("No configured client found")
    else:
        return None


def get_configured_fetchers(config, captcha_decoder, only, exclude, log):
    to_init = set(config.fetchers).difference(exclude)
    if len(only) != 0:
        to_init = to_init.intersection(only)

    if len(to_init) == 0:
        raise RuntimeError("No fetchers to init")

    fetchers = []
    for fetcher_name in sorted(to_init):
        log.info("Enabling the fetcher {blue}%s{reset} ...", (fetcher_name,), one_line=True)

        fetcher_class = get_fetcher_class(fetcher_name)
        fetcher_kwargs = dict(config.fetchers[fetcher_name])
        if F_WithCaptcha in fetcher_class.get_bases():
            fetcher_kwargs["captcha_decoder"] = captcha_decoder
        fetcher = fetcher_class(**fetcher_kwargs)

        try:
            log.info("Enabling the fetcher {blue}%s{reset}: {yellow}testing{reset} ...", (fetcher_name,), one_line=True)
            fetcher.test()
            if F_WithLogin in fetcher_class.get_bases():
                log.info("Enabling the fetcher {blue}%s{reset}: {yellow}logging in{reset} ...", (fetcher_name,), one_line=True)
                fetcher.login()
            log.info("Fetcher {blue}%s{reset} is {green}ready{reset}", (fetcher_name,))
        except Exception as err:
            log.error("Init error: {red}%s{reset}: {red}%s{reset}(%s)", (fetcher_name, type(err).__name__, err))
            raise

        fetchers.append(fetcher)

    return fetchers


# =====
def _get_config_scheme():
    return {
        "core": {
            "client":        Option(default=None, type=as_string_or_none, help="The name of plugin for torrent client"),
            "torrents_dir":  Option(default=".", type=as_path, help="Path to directory with torrent files"),
            "data_root_dir": Option(default=None, type=as_path_or_none, help="Path to root directory with data of torrents"),
            "use_colors":    Option(default=True, help="Enable colored output"),
            "force_colors":  Option(default=False, help="Always use the coloring"),
        },

        "emfetch": {
            "conveyor":      Option(default="term", help="Logger and captcha decoder"),
            "backup_dir":    Option(default=None, type=as_path_or_none, help="Backup old torrent files after update here"),
            "backup_suffix": Option(default=".%Y.%m.%d-%H:%M:%S.bak", help="Append this suffix to backuped file"),
            "save_customs":  Option(default=[], type=as_string_list, help="Save client custom fields after update if supports"),
            "set_customs":   Option(default=[], type=as_string_list, help="Set client custom fileds after update if supports")
        },

        "emload": {
            "torrent_mode": Option(default=None, type=as_8int_or_none, help="Change permissions of torrent file before load"),
            "mkdir_mode": Option(default=None, type=as_8int_or_none, help="Permission for new directories"),
        },

        "emfind": {
            "cache_file": Option(default=as_path("~/.cache/emfind.json"), type=as_path, help="Torrents cache"),
            "name_filter": Option(default="*.torrent", type=str, help="Cache only filtered torrent files"),
        }
    }
