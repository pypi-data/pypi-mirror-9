from distutils.core import setup

setup(
    name='Pi-Broadcast-Service',
    version='0.0.1',
    author='Brian Hines',
    author_email='brian@projectweekend.net',
    packages=['pi_broadcast_service'],
    url='http://projectweekend.github.io/Pi-Broadcast-Service',
    license='LICENSE.txt',
    description='Broadcast data from a Raspberry Pi using RabbitMQ & Python.',
    long_description=open('README.txt').read(),
    install_requires=[
        "pika == 0.9.14",
        "Pi-Pin-Manager == 0.1.0",
    ],
)
