#  The MIT License (MIT)
#
#  Copyright (c) 2019 László Hegedűs
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy of
#  this software and associated documentation files (the "Software"), to deal in
#  the Software without restriction, including without limitation the rights to
#  use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
#  the Software, and to permit persons to whom the Software is furnished to do so,
#  subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
#  FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
#  COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
#  IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
#  CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


import six
from six import StringIO
from six.moves import configparser


def test_file(host, path, owner="root", group="root"):
    """Test an expected file.
    Validate that the file exists and has the correct ownership.
    """
    f = host.file(path)

    assert f.exists
    assert f.is_file
    assert owner == f.user
    assert group == f.group


def test_ini_file(host, path, owner="root", group="root", expected=None):
    """Test an expected INI file.
    Validate that the file exists, has the correct ownership, format and
    expected contents.
    :param expected: a dict of dicts providing config that should be present.
    """

    test_file(host, path, owner, group)

    sio = StringIO(host.file(path).content_string)
    parser = configparser.RawConfigParser()

    if six.PY3:
        parser.read_file(sio)
    else:
        parser.readfp(sio)

    if expected is None:
        return

    for exp_section_name, exp_section in expected.items():
        assert parser.has_section(exp_section_name)
        for exp_key, exp_value in exp_section.items():
            assert parser.has_option(exp_section_name, exp_key)
            assert parser.get(exp_section_name, exp_key) == exp_value


def test_directory(host, path, owner="root", group="root"):
    """Test an expected directory.
    Validate that the directory exists and has the correct ownership.
    """

    d = host.file(path)

    assert d.exists
    assert d.is_directory
    assert owner == d.user
    assert group == d.group


def test_path_absent(host, path):
    """Test a path expected to not exist."""

    p = host.file(path)

    assert not p.exists
