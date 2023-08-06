import lxml.html
from lxml import etree
from sinor import file_util


EMPTY_RESULT = {'title': '',
                'date': '',
                'content': '',
                'status': ''}


def _get_text_value(html, id_name):
    tags = _find_id_nodes(html, id_name)
    if(len(tags) > 0):
        return tags[0].text
    else:
        return ''


def _find_id_nodes(html, id_name):
    xpath_expression = "//*[contains(@id, '{}')]".format(id_name)
    return html.xpath(xpath_expression)


def _get_sub_tree(html, id_name):
    tags = _find_id_nodes(html, id_name)
    if(len(tags) > 0):
        return etree.tostring(tags[0])
    else:
        return ''


def from_file(file_name):
    return from_string(file_util.read_file(file_name),
                       {'file_name': file_name,
                        'absolute_url': file_util.absolute_href_for_file(file_name),
                        'relative_url': file_util.relative_href_for_file(file_name)})


def from_string(html_string, to_return={}):
    try:
        html = lxml.html.document_fromstring(html_string)
    except:
        return EMPTY_RESULT
    to_return['title'] = _get_text_value(html, 'post-title')
    to_return['date'] = _get_text_value(html, 'post-date')
    to_return['content'] = _get_sub_tree(html, 'post-content')
    to_return['status'] = _status(html)
    return to_return


def _status(html):
    xpath_expression = "//*[contains(@class, 'draft')]"
    if len(html.xpath(xpath_expression)) == 0:
        return 'published'
    else:
        return 'draft'
