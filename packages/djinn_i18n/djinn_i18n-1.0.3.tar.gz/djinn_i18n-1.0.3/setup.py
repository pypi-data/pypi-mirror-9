import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'django',
    'djinn_core',
    'polib'
    ]

setup(name='djinn_i18n',
      version="1.0.3",
      description='Djinn i18n',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
          "Development Status :: 3 - Alpha",
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
      url='https://github.com/PythonUnited/djinn-i18n',
      keywords='Djinn i18n',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=requires,
      test_suite="djinn-i18n",
      entry_points="""\
      [djinn.tool]
      info=djinn_i18n:get_info
      [djinn.app]
      js=djinn_i18n:get_js
      urls=djinn_i18n:get_urls
      css=djinn_i18n:get_css
      """,
      message_extractors={'.': [
          ('**.html', 'lingua_xml', None),
          ('**.py', 'lingua_python', None)
      ]})
