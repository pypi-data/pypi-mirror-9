import re
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

version = ''

with open('servy/__init__.py', 'r') as fd:
    regex = re.compile(r'__version__\s*=\s*[\'"]([^\'"]*)[\'"]')
    for line in fd:
        m = regex.match(line)
        if m:
            version = m.group(1)
            break

setup(
    name='servy',
    packages=['servy'],
    package_data={'': ['LICENSE']},
    install_requires=['WebOb==1.4'],
    version=version,
    description='Pythonic RPC over RESTful protocol',
    author='Andrey Gubarev',
    author_email='mylokin@me.com',
    url='https://github.com/mylokin/servy',
    keywords=['rpc'],
    license='MIT',
    classifiers=(
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ),
)
