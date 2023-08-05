from setuptools import setup, find_packages

from wsa_cli import __version__

def read(fname):
    with open(fname) as fp:
        content = fp.read()
    return content

setup(
    name='wsa_cli',
    version=__version__,
    author='Eric Bower',
    author_email='neurosnap@gmail.com',
    url='https://github.com/neurosnap/wsa-cli',
    packages=find_packages(),
    license=read('LICENSE.rst'),
    description='Command line tool to generate basic folder, file structure for a WSA module.',
    long_description=read('README.rst') + '\n\n' + read('CHANGES.rst'),
    py_modules=['wsa'],
    install_requires=[
        'six',
        'Click',
    ],
    entry_points='''
        [console_scripts]
        mkwsa=wsa_cli.wsa:mkwsa
    ''',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'License :: OSI Approved :: MIT License'
    ],
    keywords=['gannett', 'web-standard-apps']
)
