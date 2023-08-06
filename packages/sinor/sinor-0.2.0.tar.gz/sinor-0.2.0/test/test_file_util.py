from sinor.file_util import relative_href_for_file
from nose.tools import assert_equals
from sinor.config import config
from mock import Mock
import os


def test_href_for_file():
    config.build_output_dir = Mock(return_value='build')
    config.blog_base_dir = Mock(return_value='blog')
    os.getcwd = Mock(return_value='/home/foo')
    assert_equals(relative_href_for_file('/home/foo/build/blog/2014/blog.html'),
                  '/blog/2014/blog.html')
