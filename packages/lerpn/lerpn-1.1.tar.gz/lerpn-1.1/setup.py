from setuptools import setup

import sys
def EXTRAS():
    extras = {
        'units': ['pint'],
        }
    if sys.platform != 'linux':
        extras['clip'] = ['pyperclip']
    else:
        extras['clip'] = []
    return extras

setup(  name='lerpn',
        version='1.1',
        description='Linux? Engineering RPN calculator',
        url='https://github.com/cpavlina/lerpn',
        download_url = 'https://github.com/cpavlina/lerpn/tarball/1.1',
        author='Chris Pavlina',
        author_email='pavlina.chris@gmail.com',
        packages=['LerpnApp'],
        entry_points = {
            'console_scripts': [
                'lerpn = LerpnApp:main',
                ],
        },
        extras_require = EXTRAS(),
        keywords = ['calculator', 'rpn'],
        classifiers = [
            "Development Status :: 5 - Production/Stable",
            "Environment :: Console :: Curses",
            "Topic :: Utilities",
            "License :: Public Domain" ]
        )
