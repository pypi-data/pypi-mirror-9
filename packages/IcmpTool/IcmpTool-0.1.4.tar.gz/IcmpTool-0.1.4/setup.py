from distutils.core import setup

setup(
    name='IcmpTool',
    version='0.1.4',
    author='Riccardo Ravaioli',
    author_email='rickyrav@gmail.com',
    packages=['icmptool'],
    scripts=['bin/icmp_tool.py'],
    url='https://pypi.python.org/pypi/IcmpTool',
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
