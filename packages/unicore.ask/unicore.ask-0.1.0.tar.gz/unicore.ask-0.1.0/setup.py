import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()

with open(os.path.join(here, 'requirements.txt')) as f:
    requires = filter(None, f.readlines())

with open(os.path.join(here, 'VERSION')) as f:
    version = f.read().strip()

setup(name='unicore.ask',
      version=version,
      description='Universal Core REST service for Questions and Surveys.',
      long_description=README,
      classifiers=[
          "Programming Language :: Python",
          "Framework :: Pyramid",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
      ],
      author='Praekelt Foundation',
      author_email='dev@praekelt.com',
      url='https://github.com/universalcore/unicore.ask.git',
      license='BSD',
      keywords='question, survey, poll, universal, core',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      namespace_packages=['unicore'],
      install_requires=requires,
      tests_require=requires,
      entry_points="""\
      [paste.app_factory]
      main = unicore.ask.service:main
      """)
