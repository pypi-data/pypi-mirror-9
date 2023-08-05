import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'django',
    'djinn_core',
    'djinn_contenttypes'
    ]

setup(name='djinn_forms',
      version="1.3.2",
      description='Djinn Intranet Forms',
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
      url='https://github.com/PythonUnited/djinn-forms',
      keywords='Djinn forms',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=requires,
      test_suite="djinn-forms",
      entry_points="""\
      [djinn.app]
      js=djinn_forms:get_js
      css=djinn_forms:get_css
      urls=djinn_forms:get_urls
      """,
      message_extractors={'.': [
          ('**.html', 'lingua_xml', None),
          ('**.py', 'lingua_python', None)
      ]})
