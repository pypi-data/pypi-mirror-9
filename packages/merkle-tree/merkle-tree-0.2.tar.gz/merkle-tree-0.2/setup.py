import os.path
from setuptools import setup

setup(
   name = 'merkle-tree',
   version = '0.2',
   description='CLI to calculate Merkle Tree based on botocore implementation.',
   py_modules=['merkle_tree'],
   author='George Yoshida',
   url='https://github.com/quiver/merkle_tree',
   install_requires=[
     'botocore',
     'Click',
   ],
   license='Apache Licenset 2.0',
   classifiers=(
       'Development Status :: 3 - Alpha',
       'Intended Audience :: Developers',
       'Intended Audience :: System Administrators',
       'Natural Language :: English',
       'License :: OSI Approved :: Apache Software License',
       'Programming Language :: Python',
       'Programming Language :: Python :: 2.6',
       'Programming Language :: Python :: 2.7',
       'Programming Language :: Python :: 3',
       'Programming Language :: Python :: 3.3',
   ),
   entry_points='''
       [console_scripts]
       merkle=merkle_tree:cli
   '''
)
