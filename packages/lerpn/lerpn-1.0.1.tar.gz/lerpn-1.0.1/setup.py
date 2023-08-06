from setuptools import setup

setup(  name='lerpn',
        version='1.0.1',
        description='Linux? Engineering RPN calculator',
        url='https://github.com/cpavlina/lerpn',
        download_url = 'https://github.com/cpavlina/lerpn/tarball/1.0.1',
        author='Chris Pavlina',
        author_email='pavlina.chris@gmail.com',
        packages=['LerpnApp'],
        scripts=['lerpn'],
        keywords = ['calculator', 'rpn'],
        classifiers = [
            "Development Status :: 4 - Beta",
            "Topic :: Utilities",
            "License :: Public Domain" ]
        )
