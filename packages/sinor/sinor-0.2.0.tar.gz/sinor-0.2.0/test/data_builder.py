class MarkdownPostBuilder:

    def __init__(self):
        self.content = 'Content not set'
        self.status = ''
        self.title = 'Title not set'
        self.date = ''

    def with_content(self, content=""):
        self.content = content
        return self

    def with_status(self, status):
        self.status = status
        return self

    def with_title(self, title=''):
        self.title = title
        return self

    def with_date(self, date=''):
        self.date = date

    def build(self):
        return {'content': self.content,
                'status': self.status,
                'date': self.date,
                'title': self.title}


class HTMLContentBuilder:

    def __init__(self):
        self.post_date = ''
        self.draft = ''
        self.title = ''
        self.content = ''
        self.status = ''

    def with_post_date(self, date):
        self.post_date = "<div id='post-date'>{}</div>".format(date)
        return self

    def with_draft_status(self):
        self.status = '<div class="draft"></div>'
        return self

    def with_title(self, title):
        self.title = "<div id='post-title'>{}</div>".format(title)
        return self

    def with_content(self, content):
        self.content = "<div id=post-content>{}</div>".format(content)
        return self

    def build(self):
        return self.status + self.post_date + self.title + self.content
