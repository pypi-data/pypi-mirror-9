import toml
from sys import exit


class Config:

    _config_map = None
    config_filename = ''

    def blog_url(self):
        return self.config_map()['blog']['url']

    def feed_url(self):
        return self.blog_url() + self.feed_path()

    def feed_path(self):
        return self.config_map()['feed']['path']

    def blog_title(self):
        return self.config_map()['blog']['title']

    def blog_date_format(self):
        return self.config_map()['blog']['date_format']

    def feed_title(self):
        try:
            return self.config_map()['feed']['title']
        except (KeyError, TypeError):
            return self.blog_title()

    def feed_subtitle(self):
        try:
            return self.config_map()['feed']['subtitle']
        except KeyError:
            return self.blog_subtitle()

    def blog_subtitle(self):
        return self.config_map()['blog']['subtitle']

    def author(self):
        return self.config_map()['blog']['author']

    def posts_base_path(self):
        return self.config_map()['posts']['base_path']

    def build_output_dir(self):
        return self.config_map()['build']['output_dir']

    def build_partials_dir(self):
        try:
            return self.config_map()['build']['partials_dir']
        except (KeyError, TypeError):
            return ""

    def load_toml_file(self):
        try:
            self._config_map = toml.load(self.config_filename)
        except IOError:
            print("Could not load sinor.toml file")
            exit(1)

    def config_map(self):
        if self._config_map is None:
            self.load_toml_file()
        return self._config_map

config = Config()
