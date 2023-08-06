from sinor import html_content
from nose.tools import assert_equals
from data_builder import HTMLContentBuilder


def test_parse_empty_string():
    html = HTMLContentBuilder().build()
    assert_equals(html_content.from_string(html), {'title': '',
                                                   'date': '',
                                                   'content': '',
                                                   'status': ''})


def test_finds_a_post_title_class():
    html = HTMLContentBuilder().with_title('Title').build()
    assert_equals(html_content.from_string(html)['title'],  'Title')


def test_finds_a_post_date():
    html = HTMLContentBuilder().with_post_date('2010-01-01').build()
    assert_equals(html_content.from_string(html)['date'], '2010-01-01')


def test_finds_post_content():
    html = HTMLContentBuilder().with_content('<p>Ulysseus!</p>').build()
    assert_equals(html_content.from_string(html)['content'],
                  '<div id="post-content"><p>Ulysseus!</p></div>')


def test_multihtml():
    html = HTMLContentBuilder().with_title('Foo').with_post_date('2010-01-01').with_content('<p>Hej</p>').with_draft_status().build()
    assert_equals(html_content.from_string(html),
                  {'content':
                   '<div id="post-content"><p>Hej</p></div>',
                   'title': 'Foo',
                   'date': '2010-01-01',
                   'status': 'draft'})


def test_draft():
    html = HTMLContentBuilder().with_draft_status().build()
    assert_equals(html_content.from_string(html)['status'], 'draft')
