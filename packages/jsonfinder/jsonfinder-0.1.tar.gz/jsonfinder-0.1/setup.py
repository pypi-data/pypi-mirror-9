from setuptools import setup

description = """\
Easily iterate through strings and find and parse embedded JSON objects.
Includes a command-line tool to format JSON within the input, similar to the builtin json.tool."""

setup(name='jsonfinder',
      version='0.1',
      description=description,
      author='Alex Hall',
      author_email='alex.mojaki@gmail.com',
      license='MIT',
      packages=['jsonfinder'],
      zip_safe=False)