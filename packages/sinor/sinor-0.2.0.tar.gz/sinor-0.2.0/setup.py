__author__ = 'mahnve'

from setuptools import setup
from setuptools.command.test import test as TestCommand


# Inspired by the example at https://pytest.org/latest/goodpractises.html
class NoseTestCommand(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # Run nose ensuring that argv simulates running nosetests directly
        import nose
        nose.run_exit(argv=['nosetests'])

setup(description='Simple blog tool for static websites',
      author='Marcus Ahnve',
      url='http://github.com/mahnve/sinor',
      download_url='https://github.com/mahnve/sinor/releases',
      author_email='m@hnve.org',
      version='0.2.0',
      install_requires=['Markdown',
                        'pystache',
                        'pyatom',
                        'Pygments',
                        'pyyaml',
                        'setuptools',
                        'lxml',
                        'toml'],
      packages=[
          'sinor',
          'test'],
      scripts=['scripts/sinor'],
      name='sinor',
      tests_require=['nose', 'mock'],
      cmdclass={'test': NoseTestCommand})
