# utils.py
#
# Copyright 2020 Martin Abente Lahaye
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import re

from gi.repository import Gio, GLib

from .cache import cached


def find_new_name(directory, name):
    counter = 1

    while os.path.exists(os.path.join(directory, name)):
        components = re.split("(\(\d+\)$)", name)
        if len(components) > 1:
            name = "".join(components[:-2])

        name = f"{name}({counter})"
        counter += 1

    return name


def count(path):
    _count = 1

    if os.path.isdir(path):
        for directory, _, files in os.walk(path):
            _count += len(files)

    return _count


def flatten_walk(path):
    _paths = []

    def _callback(error):
        raise error

    if os.path.isdir(path):
        for directory, _, files in os.walk(path, topdown=False, onerror=_callback):
            for file in files:
                _paths += [os.path.join(directory, file)]
            _paths += [directory]
    else:
        _paths += [path]

    return _paths


def is_uri(uri):
    try:
        GLib.uri_parse(uri, GLib.UriFlags.NONE)
        return True
    except:
        return False


def join_uri(uri, name):
    parsed_uri = GLib.uri_parse(uri, GLib.UriFlags.NONE)
    return GLib.uri_join(
        GLib.UriFlags.NONE,
        parsed_uri.get_scheme(),
        None,
        None,
        -1,
        os.path.join(parsed_uri.get_path(), name),
        None,
        None,
    )


def get_uri_info(uri, attributes):
    file = Gio.File.new_for_uri(uri)
    info = file.query_info(
        attributes,
        Gio.FileQueryInfoFlags.NONE,
        None,
    )

    return info


def is_trash(uri):
    try:
        uri = GLib.uri_parse(uri, GLib.UriFlags.NONE)
        return uri.get_scheme() == "trash"
    except:
        return False


def list_trash(uri):
    uris = []

    file = Gio.File.new_for_uri(uri)
    enumerator = file.enumerate_children(
        f"{Gio.FILE_ATTRIBUTE_STANDARD_NAME}",
        Gio.FileQueryInfoFlags.NOFOLLOW_SYMLINKS,
        None,
    )

    while True:
        info = enumerator.next_file(None)
        if info is None:
            break
        uris.append(info.get_name())

    return uris


def get_trash_uri_file_name(uri):
    uri = GLib.uri_parse(uri, GLib.UriFlags.NONE)
    return os.path.basename(uri.get_path())


def get_trash_uri_orig_path(uri):
    info = get_uri_info(uri, Gio.FILE_ATTRIBUTE_TRASH_ORIG_PATH)
    return info.get_attribute_as_string(Gio.FILE_ATTRIBUTE_TRASH_ORIG_PATH)


def get_trash_uri_modified_time(uri):
    info = get_uri_info(uri, Gio.FILE_ATTRIBUTE_TIME_MODIFIED)
    time = info.get_modification_date_time()
    return time.to_unix()


def is_trash_uri_dir(uri):
    info = get_uri_info(uri, Gio.FILE_ATTRIBUTE_STANDARD_CONTENT_TYPE)
    return info.get_content_type() == "inode/directory"


@cached
def get_file_name(string):
    try:
        return get_trash_uri_file_name(string)
    except:
        return os.path.basename(string)


@cached
def get_file_mtime(string):
    try:
        return get_trash_uri_modified_time(string)
    except:
        return os.path.getmtime(string)


@cached
def is_file_dir(string):
    try:
        return is_trash_uri_dir(string)
    except:
        return os.path.isdir(string)


def list_directory(string):
    try:
        return list_trash(string)
    except:
        return os.listdir(string)


def join_directory(directory, name):
    try:
        return join_uri(directory, name)
    except:
        return os.path.join(directory, name)
