from distutils.core import setup

setup(
    name='IcmpTool',
    version='0.1.0',
    author='Riccardo Ravaioli',
    author_email='rickyrav@gmail.com',
    packages=['icmptool'],
    license='LICENSE.txt',
    description='Characterizes ICMP responsiveness of routers.',
    long_description=open('README.txt').read(),
    install_requires=[
        "scapy >= 2.0.0",
        "scipy >= 0.7.0",
        "numpy",
        "prettytable >= 0.7.2"
    ],
)
