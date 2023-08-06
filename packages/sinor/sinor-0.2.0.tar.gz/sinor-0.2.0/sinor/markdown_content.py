import markdown
from sinor import file_util


def from_file(content_file):
    content = file_util.read_file(content_file)
    return from_string(content)


def from_string(content):
    md_converter = markdown.Markdown(extensions=['codehilite', 'meta'])
    html = md_converter.convert(content)

    meta_data = md_converter.Meta

    return {'content': html,
            'title': _single_meta_data_value(meta_data, 'title'),
            'status': _draft_status(meta_data),
            'date': _single_meta_data_value(meta_data, 'date')}


def _single_meta_data_value(dictionary, key):
    value_list = dictionary.get(key, [''])
    return value_list[0]


def _draft_status(meta_data):
    if _single_meta_data_value(meta_data, 'draft') in ('true', 'True'):
        return 'draft'
    else:
        return 'published'
