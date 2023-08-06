from nose.tools import assert_equals
from sinor.config import config
from mock import Mock


def test_empty_feed_title():
    config.load_toml_file = Mock(return_value={'build': {}})
    config.blog_title = Mock(return_value="foo")
    assert_equals(config.feed_title(), 'foo')


def test_empty_partials_dir():
    config.load_toml_file = Mock(return_value={'build': {}})
    assert_equals(config.build_partials_dir(), '')
