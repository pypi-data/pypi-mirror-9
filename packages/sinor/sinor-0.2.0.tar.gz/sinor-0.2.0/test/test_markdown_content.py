from sinor import markdown_content
from nose.tools import assert_equals


def test_gets_title():
    assert_equals(markdown_content.from_string(
        "title: hej \n date: 2014-10-01 \n\n Hej")['title'],
                  "hej")


def test_gets_date():
    assert_equals(markdown_content.from_string(
        "title: hej \n date: 2014-10-01 \n\n Hej")['date'],
                  "2014-10-01")


def test_gets_content():
    assert_equals(markdown_content.from_string(
        "title: hej \n date: 2014-10-01 \n\n Hej")['content'],
                  "<p>Hej</p>")


def test_gets_draft():
    assert_equals(markdown_content.from_string(
        "title: hej \n date: 2014-10-01 \ndraft: true\n\n Hej")['status'],
                  "draft")
