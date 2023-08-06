"""
    Emonoda -- The set of tools to organize and manage your torrents
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


import urllib.parse
import re
import time

from . import BaseFetcher
from . import WithLogin


# =====
def _encode(arg):
    return arg.encode("cp1251")


def _decode(arg):
    return arg.decode("cp1251")


class Plugin(BaseFetcher, WithLogin):
    def __init__(self, **kwargs):  # pylint: disable=super-init-not-called
        self._init_bases(**kwargs)
        self._init_opener(with_cookies=(self._user is not None))
        self._comment_regexp = re.compile(r"http://tfile\.(me|ru)/forum/viewtopic\.php\?p=(\d+)")

    @classmethod
    def get_name(cls):
        return "tfile.me"

    @classmethod
    def get_version(cls):
        return 0

    @classmethod
    def get_fingerprint(cls):
        return {
            "url":      "http://tfile.me",
            "encoding": "cp1251",
            "text":     "href=\"http://tfile.me/opensearch.xml\"",
        }

    @classmethod
    def get_options(cls):
        return cls._get_merged_options()

    # ===

    def is_torrent_changed(self, torrent):
        self._assert_match(torrent)
        page = _decode(self._read_url(torrent.get_comment(), opener=self._build_opener()))

        hash_match = re.search(r"<a href=\"magnet:\?xt=urn:btih:([a-fA-F0-9]{40})", page)
        if hash_match is not None:
            torrent_hash = hash_match.group(1).lower()
            return (torrent.get_hash() != torrent_hash)
        else:
            reg_match = re.search(r"class=\"regDate\">(\d\d\d\d-\d\d-\d\d \d\d:\d\d)</span><br/>", page)
            if reg_match is None:
                page = _decode(self._read_url(torrent.get_comment()))
                reg_match = re.search(r"Зарегистрирован: (\d\d\d\d-\d\d-\d\d \d\d:\d\d),", page)
                self._assert_logic(reg_match is not None, "Unknown hash and date")
            reg_time = int(time.mktime(time.strptime(reg_match.group(1), "%Y-%m-%d %H:%M")))
            return (torrent.get_mtime() <= reg_time)

    def fetch_new_data(self, torrent):
        self._assert_match(torrent)
        page = _decode(self._read_url(torrent.get_comment()))

        dl_id_match = re.search(r"<a href=\"download.php\?id=(\d+)\" class=\"dlLink\"", page)
        self._assert_logic(dl_id_match is not None, "Unknown dl_id")
        dl_id = dl_id_match.group(1)

        data = self._read_url("http://tfile.me/forum/download.php?id={}".format(dl_id))
        self._assert_valid_data(data)
        return data

    # ===

    def login(self):
        if self._user is not None:
            self._assert_auth(self._passwd is not None, "Required passwd nnmclub")
            post = {
                "username":  _encode(self._user),
                "password":  _encode(self._passwd),
                "autologin": b"",
                "login":     b"",
            }
            post_data = _encode(urllib.parse.urlencode(post))
            page = _decode(self._read_url("http://tfile.me/login/", data=post_data))
            self._assert_auth("class=\"nick u\">{}</a>".format(self._user) in page, "Invalid login or password")
