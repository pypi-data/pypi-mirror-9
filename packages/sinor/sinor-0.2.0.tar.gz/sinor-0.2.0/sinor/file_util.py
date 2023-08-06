from sinor.config import config
import os


def read_file(file_name):
    with open(file_name) as template_file:
        return template_file.read().decode("utf8")


def relative_href_for_file(file_name):
    return file_name.lstrip(os.getcwd()).lstrip(config.build_output_dir())


def absolute_href_for_file(file_name):
    return config.blog_url() + relative_href_for_file(file_name)
