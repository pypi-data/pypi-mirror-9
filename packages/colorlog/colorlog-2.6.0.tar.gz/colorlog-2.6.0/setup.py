from setuptools import setup

setup(
    name='colorlog',
    version='2.6.0',

    description='Log formatting with colors!',
    long_description=open("README.rst").read(),

    author='Sam Clements',
    author_email='sam@borntyping.co.uk',
    url='https://github.com/borntyping/python-colorlog',
    license='MIT License',

    packages=[
        'colorlog'
    ],

    extras_require={
        'windows': [
            'colorama'
        ]
    },

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Terminals',
        'Topic :: Utilities',
    ],
)
