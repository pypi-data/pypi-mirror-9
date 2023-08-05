#!/usr/bin/env python

from aTXT.version import __version__

VERSION = __version__

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
    description='A friendly Extractor of Text',
    author='Jonathan S. Prieto',
    author_email='prieto.jona@gmail.com',
    url='https://github.com/d555/aTXT',   # use the URL to the github repo
    download_url='https://github.com/d555/aTXT/' + VERSION,
    # arbitrary keywords
    keywords="txt doc docx pdf doc2txt docx2txt pdf2txt data conversion",
    long_description=open('README.rst').read(),
    install_requires=[
            "lxml>=3.2.3",
            "docx>=0.2.0",
            "pdfminer",
            "docopt>=0.6.2"
    ],
    # zip_safe=True,
    entry_points={
        'console_scripts': ['aTXT=aTXT:main']
    },
    requires=['docopt', 'scandir', 'lxml', 'PySide', 'kitchen'],
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

# Pasos para subir a pypi
# python setup.py register -r pypi
# python setup.py sdist upload -r pypi 