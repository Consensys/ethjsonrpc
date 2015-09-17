try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='ethjsonrpc',
    version='0.2.1',
    description='Ethereum JSON-RPC client',
    long_description='Ethereum JSON-RPC client',
    author='ConsenSys',
    author_email=['info@consensys.net'],
    url='https://github.com/ConsenSys/ethjsonrpc',
    packages=['ethjsonrpc'],
    license='Unlicense',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: Public Domain',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
    ],
    install_requires=[
        'ethereum==1.0.0',
        'ethereum-serpent==2.0.0',
        'requests==2.7.0',
    ],
)
