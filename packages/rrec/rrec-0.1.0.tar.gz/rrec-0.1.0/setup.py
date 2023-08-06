#!/usr/bin/env python

from setuptools import setup


with open('rrec.py') as fh:
    docstring = []
    docstring_started = False
    docstring_done = False

    for line in fh:
        line = line.rstrip()

        if docstring_started:
            if line == '"""':
                docstring_done = True
            elif not docstring_done:
                docstring.append(line)
        elif line.startswith('"""'):
            docstring_started = True
            docstring.append(line[3:])

    name, description = docstring[0].split(' - ')
    docstring = '\n'.join(docstring)


setup(
    name=name,
    version='0.1.0',
    description=description,
    long_description=docstring,
    author='Tobias Bengfort',
    author_email='tobias.bengfort@gmx.net',
    py_modules=['rrec'],
    install_requires=[
        'argparse',
        'python-crontab',
    ],
    entry_points={'console_scripts': [
        'rrec=rrec:main',
    ]},
    license='GPLv3+',
    classifiers=[
        'Intended Audience :: End Users/Desktop',
        'Programming Language :: Python',
        'Operating System :: POSIX :: Linux',
        'License :: OSI Approved :: GNU General Public License v3 or later '
            '(GPLv3+)',
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Topic :: Multimedia :: Sound/Audio :: Capture/Recording',
    ])
