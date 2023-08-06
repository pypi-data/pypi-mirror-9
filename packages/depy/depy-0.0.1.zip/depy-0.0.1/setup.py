from setuptools import setup
from textwrap import dedent

VERSION='0.0.1'

setup(
    name='depy',
    version=VERSION,
    package_dir={'': 'src'},
    packages=['depy'],
    entry_points={
        'console_scripts': [
            'depy = depy.__main__:run',
        ],
    },
    install_requires=[
        'pydot3k',
    ],
    url='https://gitlab.com/tarcisioe/depy',
    download_url='https://gitlab.com/tarcisioe/depy/repository/archive.tar.gz?ref=' + VERSION,
    keywords=['testing', 'mock', 'file'],
    maintainer='Tarcísio Eduardo Moreira Crocomo',
    maintainer_email='tarcisio.crocomo+pypi@gmail.com',
    description=dedent('''\
        Python non-importing module dependency analysis tool. Aims to be simple.
        Depends on Graphviz executables for rendering images.
        '''),
)
