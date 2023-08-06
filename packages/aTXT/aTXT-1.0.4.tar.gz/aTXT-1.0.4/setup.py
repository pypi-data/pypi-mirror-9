#!/usr/bin/env python

VERSION = "v1.0.4"

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='aTXT',
    packages=['aTXT'],
    # package_data={ '':['*.py'],
    #     'bin': ['bin/*'], 'docx': ['docx/*'], 'pdfminer': ['pdfminer']},
    version=VERSION,
    include_package_data=True,
    license='MIT',
    description='A Data Mining Tool For Extract Text From Files',
    author='Jonathan S. Prieto',
    author_email='prieto.jona@gmail.com',
    url='https://github.com/d555/aTXT',   # use the URL to the github repo
    download_url='https://github.com/d555/aTXT/',
    # arbitrary keywords
    keywords='text txt doc docx pdf doc2txt docx2txt pdf2txt convert',
    long_description=open('README.rst').read(),
    dependency_links=[
    ],
    install_requires=[
        'unidecode',
        'Pillow',
        'lxml>=3.2.3',
        'docx>=0.2.0',
        'pdfminer',
        'docopt',
        'PySide',
        'kitchen>=1.1.1',
        'scandir>=0.8'
    ],
    zip_safe=True,
    entry_points={
        'console_scripts': ['aTXT=aTXT:main']
    },
    classifiers=[
        # 'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: Spanish',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities',
    ],
)

# pandoc --from=markdown_github --to=rst --output=README.rst README.md
# Pasos para subir a pypi
# git tag v...
# python setup.py register -r pypi
# python setup.py sdist upload -r pypi
