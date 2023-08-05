import io
import glob
import os.path

import pytest

from readme.rst import render


@pytest.mark.parametrize(
    ("rst_filename", "html_filename"),
    [
        (fn, os.path.splitext(fn)[0] + ".html")
        for fn in glob.glob(
            os.path.join(os.path.dirname(__file__), "fixtures", "test_*.rst")
        )
    ],
)
def test_rst_fixtures(rst_filename, html_filename):
    # Get our Markup
    with io.open(rst_filename, encoding='utf-8') as f:
        rst_markup = f.read()

    # Get our expected
    with io.open(html_filename, encoding="utf-8") as f:
        expected = f.read()

    out, rendered = render(rst_markup)

    assert out == expected
    assert rendered == ("<" in expected)


def test_rst_001():
    assert render('Hello') == ('<p>Hello</p>\n', True)


def test_rst_002():
    assert render('http://mymalicioussite.com/') == (
        ('<p><a href="http://mymalicioussite.com/" rel="nofollow">' +
         'http://mymalicioussite.com/</a></p>\n'),
        True)
