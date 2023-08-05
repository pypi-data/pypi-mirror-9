from setuptools import setup

setup(
    name='cron-runner',
    version='0.0.1',
    packages=['cronrunner'],
    package_dir={'cronrunner': 'cronrunner'},
    package_data={'cronrunner': ['config/*']},
    url='https://github.com/marijngiesen/cron-runner',
    license='Apache 2.0',
    author='Marijn Giesen',
    author_email='marijn@studio-donder.nl',
    description='Runner of cron jobs with logging and duration timing',
    entry_points={
        'console_scripts': [
            'cron-runner = cronrunner.main:main',
        ]
    },
    requires=['requests', 'peewee', 'pyyaml', 'commandr'],
)
