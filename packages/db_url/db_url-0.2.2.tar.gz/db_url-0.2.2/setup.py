from setuptools import setup

setup(
    name='db_url',
    version='0.2.2',
    license='Public Domain',
    long_description=open('README.md').read(),
    py_modules=['db_url'],
    entry_points={
        'console_scripts': [
            'db=db_url:connect_to_database'
        ]
    }
)
