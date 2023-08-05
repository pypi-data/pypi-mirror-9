from setuptools import setup


setup(
    name='bbcli',
    version='0.1.5',
    description='Browse BBC News through the command line (based on pyhackernews)',
    long_description=open('README.rst').read(),
    license=open('LICENSE').read(),
    keywords='bbc news console terminal curses',
    author='Wesley Hill, Calvin Hill',
    author_email='wesley@hakobaito.co.uk',
    url='https://github.com/hako/bbcli',
    packages=['bbcli'],
    install_requires=['urwid'],
    classifiers=[
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: Unix',
        'Programming Language :: Python :: 2.7',
        'Topic :: Terminals',
    ],
    entry_points={
        'console_scripts': ['bbcli = bbcli.core:live']
    })
