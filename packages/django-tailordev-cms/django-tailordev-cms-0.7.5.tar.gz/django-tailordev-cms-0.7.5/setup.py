# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

try:
    from pypandoc import convert
    read_md = lambda f: convert(f, 'rst')
except ImportError:
    print(
        "warning: pypandoc module not found, could not convert Markdown to RST"
    )
    read_md = lambda f: open(f, 'r').read()


setup(
    name='django-tailordev-cms',
    version=__import__('td_cms').__version__,
    author='Julien Maupetit',
    author_email='julien@tailordev.com',
    packages=find_packages(),
    include_package_data=True,
    url='https://bitbucket.org/tailordev/django-tailordev-cms',
    license='MIT',
    description=u' '.join(__import__('td_cms').__doc__.splitlines()).strip(),
    long_description=read_md('README.md'),
    classifiers=[
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Framework :: Django',
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
    ],
    install_requires=[
        'purl',
        'South>=0.8.4',
        'django-grappelli',
        'django-filebrowser',
        'django-reversion',
        'django-modeltranslation',
        'django-mptt',
    ],
    test_suite="runtests.runtests",
    zip_safe=False,
)
