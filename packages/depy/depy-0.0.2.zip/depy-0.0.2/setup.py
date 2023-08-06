from setuptools import setup
from textwrap import dedent

VERSION='0.0.2'

setup(
    name='depy',
    version=VERSION,
    py_modules=['depy'],
    entry_points={
        'console_scripts': [
            'depy = depy:run',
        ],
    },
    install_requires=[
        'pydotplus'
    ],
    url='https://gitlab.com/tarcisioe/depy',
    download_url='https://gitlab.com/tarcisioe/depy/repository/archive.tar.gz?ref=' + VERSION,
    keywords=['dependency', 'analysis', 'packages'],
    maintainer='Tarcísio Eduardo Moreira Crocomo',
    maintainer_email='tarcisio.crocomo+pypi@gmail.com',
    description=dedent('''\
        Python non-importing module dependency analysis tool. Aims to be simple.
        Depends on Graphviz executables for rendering images.
        '''),
)
