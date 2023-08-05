import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()
VERSION = open(os.path.join(here, 'VERSION')).read().strip()

setup(
    name='euganke-latex-importer',
    version=VERSION,
    description='euganke importer',
    long_description=README,
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
    ],
    author='Jaka Hudoklin',
    author_email='jakahudoklin@gmail.com',
    url='',
    keywords='web wsgi bfg pylons pyramid',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=['requests'],
    entry_points="""\
    [console_scripts]
    euganke_import_exercises = importer:main
    """
)
