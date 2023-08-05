"""
Flask-Phrase
------------

Connect your Flask apps to PhraseApp, the powerful in-context-translation solution.

"""

from setuptools import setup

setup(
    name='Flask-Phrase',
    version='0.1.0',
    url='http://github.com/phrase/Flask-Phrase',
    license='BSD',
    author='Kevin Kennell',
    author_email='kevin.kennell@dynport.de',
    description='Connect your Flask apps to PhraseApp, the powerful in-context-translation solution.',
    packages=['flask_phrase'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask-Babel'
    ],
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Internationalization',
        'Topic :: Software Development :: Localization'
    ]
)