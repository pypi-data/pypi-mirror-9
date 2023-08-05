import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'django',
    'django-bootstrap-forms',
    'djinn_contenttypes',
    'djinn_forms',
    'django-haystack',
    'lxml',
    'django-markupfield'
    ]

setup(name='djinn_announcements',
      version="1.4.1",
      description='Djinn Intranet Announcements',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "Framework :: Django",
          "Intended Audience :: Developers",
          "License :: Freely Distributable",
          "Programming Language :: Python",
          "Topic :: Internet :: WWW/HTTP :: Site Management",
          "Topic :: Software Development :: Libraries :: "
          "Application Frameworks"
      ],
      author='PythonUnited',
      author_email='info@pythonunited.com',
      license='beer-ware',
      url='https://github.com/PythonUnited/djinn-announcements',
      keywords='Djinn Core',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=requires,
      test_suite="djinn-announcements",
      entry_points="""\
      [djinn.app]
      urls=djinn_announcements:get_urls
      js=djinn_announcements:get_js
      css=djinn_announcements:get_css
      """
      )
