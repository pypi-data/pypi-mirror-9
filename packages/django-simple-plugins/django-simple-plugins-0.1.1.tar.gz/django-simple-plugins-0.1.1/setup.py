import os
from setuptools import setup

try:
    from pypandoc import convert
    read_md = lambda f: convert(f, 'rst')
except ImportError:
    print("warning: pypandoc module not found, could not convert Markdown to RST")
    read_md = lambda f: open(f, 'r').read()

setup(
    # name, version, ...
    long_description=read_md('README.md'),
    install_requires=[]
)

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-simple-plugins',
    version='0.1.1',
    packages=['plugins'],
    include_package_data=True,
    license='MIT License',  # example license
    description='A simple yet powerful and configurable tool for adding plugins to your Django project.',
    url='https://github.com/pistacchio/django-simple-plugins',
    long_description=read_md('README.md'),
    author='Gustavo Di Pietro',
    author_email='pistacchio@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License', # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        # Replace these appropriately if you are stuck on Python 2.
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)