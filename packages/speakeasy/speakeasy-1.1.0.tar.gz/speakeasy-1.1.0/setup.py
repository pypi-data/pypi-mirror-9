from setuptools import setup

setup(
    name='speakeasy',
    version='1.1.0',
    description='Metrics aggregation server',
    author='Eric Wong',
    install_requires=[
        'argparse',
        'pyzmq',
        'ujson',
    ],
    packages=['speakeasy', 'speakeasy.emitter'],
    scripts=['bin/speakeasy'],
)
