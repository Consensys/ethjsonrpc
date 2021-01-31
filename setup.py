try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='ethjsonrpc',
    version='0.3.0',
    description='Ethereum JSON-RPC client',
    long_description=open('README.rst').read(),
    author='ConsenSys',
    author_email='info@consensys.net',
    url='https://github.com/ConsenSys/ethjsonrpc',
    packages=['ethjsonrpc'],
    license='Unlicense',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: Public Domain',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
    install_requires=[
        'ethereum==1.5.2',
        'requests==2.11.1',
        'future==0.15.2',
    ],
)
