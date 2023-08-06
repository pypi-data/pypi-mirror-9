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
import errno
import argparse

from .. import fmt
from .. import helpers

from . import init
from . import get_configured_log
from . import get_configured_client


# =====
def make_path(path, tail_mode):
    try:
        os.makedirs(path)
        if tail_mode is not None:
            os.chmod(path, tail_mode)
    except OSError as err:
        if err.errno != errno.EEXIST:
            raise


def link_data(torrent, data_dir_path, link_to_path, mkdir_mode):
    mkdir_path = link_to_path = os.path.abspath(link_to_path)
    if torrent.is_single_file():
        link_to_path = os.path.join(link_to_path, torrent.get_name())
    else:
        mkdir_path = os.path.dirname(link_to_path)

    if os.path.exists(link_to_path):
        raise RuntimeError("{}: link target already exists".format(link_to_path))

    make_path(mkdir_path, mkdir_mode)
    os.symlink(os.path.join(data_dir_path, torrent.get_name()), link_to_path)


def load_torrents(torrents, client, data_root_path, link_to_path, torrent_mode, mkdir_mode, customs):
    for torrent in torrents:
        if client.has_torrent(torrent):
            raise RuntimeError("{}: already loaded".format(torrent.get_path()))
        elif torrent_mode is not None:
            os.chmod(torrent.get_path(), torrent_mode)

    if data_root_path is None:
        data_root_path = client.get_data_prefix_default()

    for torrent in torrents:
        dir_name = os.path.basename(torrent.get_path()) + ".data"
        data_dir_path = os.path.join(data_root_path, dir_name[0], dir_name)
        make_path(data_dir_path, mkdir_mode)

        if link_to_path is not None:
            link_data(torrent, data_dir_path, link_to_path, mkdir_mode)

        client.load_torrent(torrent, data_dir_path)
        if len(customs) != 0:
            client.set_customs(torrent, {
                key: fmt.format_now(value)
                for (key, value) in customs.items()
            })


def parse_customs(items):
    customs = {}
    for item in filter(None, map(str.strip, items)):
        (key, value) = map(str.strip, (item.split("=", 1) + [""])[:2])
        customs[key] = value
    return customs


# ===== Main =====
def main():
    (parent_parser, argv, config) = init()
    args_parser = argparse.ArgumentParser(
        prog="emload",
        description="Load torrent to client",
        parents=[parent_parser],
    )
    args_parser.add_argument("-l", "--link-to", default=None, metavar="<path>")
    args_parser.add_argument("--set-customs", default=[], nargs="+", metavar="<key=value>")
    args_parser.add_argument("-v", "--verbose", action="store_true")
    args_parser.add_argument("torrents", nargs="+", metavar="<path>")
    options = args_parser.parse_args(argv[1:])

    if len(options.torrents) > 1 and options.link_to is not None:
        raise RuntimeError("Option -l/--link-to be used with only one torrent")

    customs = parse_customs(options.set_customs)
    torrents = helpers.find_torrents(config.core.torrents_dir, options.torrents, False)

    with get_configured_log(config, (not options.verbose), sys.stderr) as log_stderr:
        client = get_configured_client(
            config=config,
            required=True,
            with_customs=bool(customs),
            log=log_stderr,
        )

        load_torrents(
            torrents=torrents,
            client=client,
            data_root_path=config.core.data_root_dir,
            link_to_path=options.link_to,
            torrent_mode=config.emload.torrent_mode,
            mkdir_mode=config.emload.mkdir_mode,
            customs=customs,
        )


if __name__ == "__main__":
    main()  # Do the thing!
