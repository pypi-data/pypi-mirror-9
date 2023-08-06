import os
from setuptools import setup

version = '0.0.0'

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

try:
    import pypandoc
    README = pypandoc.convert('README.md', 'rst')
    CHANGES = pypandoc.convert('CHANGES.md', 'rst')
except:
    README = read('README.md')
    CHANGES = read('CHANGES.md')

setup(
    name='pyteamcity',
    version=version,
    description='Use the TeamCity REST API from Python',
    long_description='%s\n\n%s' % (README, CHANGES),
    url='https://github.com/SurveyMonkey/pyteamcity',
    author='Marc Abramowitz',
    author_email='marca@surveymonkey.com',
    py_modules=['pyteamcity'],
    zip_safe=False,
    install_requires=['requests'],
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Natural Language :: English',
        'Intended Audience :: Developers',
    ],
)
