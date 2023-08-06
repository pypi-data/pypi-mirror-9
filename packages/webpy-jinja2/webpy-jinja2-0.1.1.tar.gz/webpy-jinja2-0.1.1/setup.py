from setuptools import setup, find_packages

setup(
    name='webpy-jinja2',
    version="0.1.1",
    description="Library to provide Jinja2 templating support for web.py applications.",
    license="BSD",
    install_requires=[
        'web.py',
        'Jinja2',
    ],
    py_modules=['webpy_jinja2'],
    author='Anand Chitipothu',
    author_email="anandology@gmail.com",
    platforms='any',
)
