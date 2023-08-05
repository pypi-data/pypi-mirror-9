import sys

import setuptools

py26_reqs = ['argparse', 'importlib'] if sys.version_info < (2,7) else []

setuptools.setup(
    name='librarypaste',
    use_hg_version=dict(increment='0.1'),
    author='YouGov, Plc.',
    author_email='open-source@yougov.com',
    url='http://bitbucket.org/jaraco/librarypaste/',
    description='Simple pastebin',
    long_description='Simple pastebin',
    license='MIT',
    packages=['librarypaste'],
    package_dir={'librarypaste': 'librarypaste'},
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'librarypaste=librarypaste.librarypaste:main',
        ],
    },
    install_requires=[
        'pygments',
        'Mako',
        'cherrypy',
        'PyYAML',
        'six',
    ] + py26_reqs,
    setup_requires=[
        'hgtools',
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
        'pymongo',
        'jaraco.test',
    ],
    zip_safe=False,
)
