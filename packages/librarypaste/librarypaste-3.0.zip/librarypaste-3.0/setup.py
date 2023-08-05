import setuptools

with open('README.txt') as readme_stream:
    long_description = readme_stream.read()

setup_params = dict(
    name='librarypaste',
    use_hg_version=dict(increment='0.1'),
    author='YouGov, Plc.',
    author_email='open-source@yougov.com',
    url='http://bitbucket.org/yougov/librarypaste/',
    description='A simple pastebin implementation in Python',
    long_description=long_description,
    license='MIT',
    packages=setuptools.find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'librarypaste=librarypaste.launch:main',
        ],
    },
    install_requires=[
        'pygments',
        'genshi',
        'cherrypy',
        'PyYAML',
    ],
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

if __name__ == '__main__':
    setuptools.setup(**setup_params)
