from distutils.core import setup

setup(
    name='RMQ-Utils',
    version='0.0.2',
    author='Brian Hines',
    author_email='brian@projectweekend.net',
    packages=['rmq_utils'],
    url='https://github.com/projectweekend/RMQ-Utils',
    license='LICENSE.txt',
    description='Utilities for managing RabbitMQ.',
    long_description=open('README.txt').read(),
    install_requires=[
        "pika == 0.9.14",
        "pyrabbit == 1.1.0",
    ],
)
