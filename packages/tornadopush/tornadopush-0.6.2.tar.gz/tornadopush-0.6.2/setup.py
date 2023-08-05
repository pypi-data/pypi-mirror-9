from setuptools import setup, find_packages


setup(
    name='tornadopush',
    version='0.6.2',
    url='http://github.com/frascoweb/tornadopush',
    license='MIT',
    author='Maxime Bouroumeau-Fuseau',
    author_email='maxime.bouroumeau@gmail.com',
    description='Push and presence server built with Tornado and Redis',
    packages=find_packages(),
    package_data={
        'tornadopush': ['static/*.js'],
    },
    zip_safe=False,
    platforms='any',
    install_requires=[
        'tornado>=4.0.2',
        'redis>=2.10.3',
        'itsdangerous>=0.24',
        'PyYAML>=3.11',
        'jsmin>=2.0.11',
        'tornado-redis>=2.4.18',
        'toredis==0.1.2'
    ],
    entry_points='''
        [console_scripts]
        tornadopush=tornadopush.cli:main
    '''
)
