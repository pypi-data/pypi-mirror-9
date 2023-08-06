from nose.tools import assert_equals
from sinor import posts
from sinor.config import config
from mock import Mock
from data_builder import MarkdownPostBuilder


def test_draft():
    a = MarkdownPostBuilder().with_status('draft').build()
    b = MarkdownPostBuilder().with_status('published').build()
    assert_equals(posts.no_drafts([a, b]), [b])


def test_limit_count():
    a = b = c = d = MarkdownPostBuilder().build()
    plist = [a, b, c, d]
    assert_equals([a, b], posts.limit(plist, 2))


def test_limit_negative_count():
    a = b = c = d = MarkdownPostBuilder().build()
    post_list = [a, b, c, d]
    assert_equals(post_list, posts.limit(post_list, -1))


def test_default_partial_dir():
    config.build_partials_dir = Mock(return_value='')
    assert_equals(posts.partials_dir("/foo/bar.mustache"), "/foo")


def test_selects_config_partial_dir():
    config.build_partials_dir = Mock(return_value="/bar")
    assert_equals(posts.partials_dir("/foo/bar.mustache"), "/bar")
