# -*- coding: utf-8 -*-
# pylint: disable=bad-continuation
""" WWW access helpers.
"""
# Copyright ©  2015 Jürgen Hermann <jh@web.de>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from __future__ import absolute_import, unicode_literals, print_function

import os
import tempfile
from contextlib import contextmanager

import requests

from ._compat import urlparse, encode_filename  # pylint: disable=unused-import


__all__ = ['url_as_file']


@contextmanager
def url_as_file(url, ext=None):
    """
        Context manager that GETs a given ``url`` and provides it as a local file.

        The file is in a closed state upon entering the context,
        and removed when leaving it, if still there.

        To give the file name a specific extension, use ``ext``;
        the extension can optionally include a separating dot,
        otherwise it will be added.

        >>> import io, re, json
        >>> with url_as_file('https://api.github.com/meta', ext='json') as meta:
        ...     encode_filename('*'.join(re.match(r'.+/(.+)-[^.]+?([.][^.]+?)$', meta).groups()))
        ...     bool(re.match(r"[0-9]+([.][0-9]+){3}/[0-9]{2}", json.load(io.open(meta, encoding='ascii'))['hooks'][0]))
        'www-api.github.com*.json'
        True
    """
    if ext:
        ext = '.' + ext.strip('.')  # normalize extension
    url_hint = 'www-{}-'.format(urlparse(url).hostname or 'any')

    content = requests.get(url).content
    with tempfile.NamedTemporaryFile(suffix=ext, prefix=url_hint, delete=False) as handle:
        handle.write(content)

    try:
        yield handle.name
    finally:
        if os.path.exists(handle.name):
            os.remove(handle.name)
