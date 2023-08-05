import os
from setuptools import setup


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as fd:
        return fd.read()

setup(
    name="jingerly",
    version="0.0.1",
    author="William Mayor",
    author_email="jinjerly@williammayor.co.uk",
    description=("Project templating using Jinja2."),
    license="MIT",
    keywords="project management template",
    url="https://github.com/WilliamMayor/jingerly",
    py_modules=['jingerly'],
    install_requires=['jinja2', 'requests'],
    scripts=['bin/jingerly'],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Topic :: Software Development :: Code Generators'
    ],
)
