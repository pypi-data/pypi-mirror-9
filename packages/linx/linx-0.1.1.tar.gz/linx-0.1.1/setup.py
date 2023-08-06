from setuptools import setup


setup(
    name='linx',
    version='0.1.1',
    author='Andrei Marcu',
    author_email='andrei@marcu.net',
    url='https://github.com/andreimarcu/linx-cli',
    license='LICENSE.txt',
    description='Command line interface for Linx.li',
    install_requires=[
        "requests",
    ],
    scripts=['linx/linx']

)
