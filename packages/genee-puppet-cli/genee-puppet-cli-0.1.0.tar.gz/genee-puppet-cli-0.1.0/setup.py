from setuptools import setup

setup(

    name='genee-puppet-cli',

    version='0.1.0',

    description='Genee Puppet Tools',

    url='https://github.com/iamfat/genee-puppet-cli',

    author="Jia Huang",
    author_email="iamfat@gmail.com",

    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Utilities',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',
    ],

    keywords='genee puppet',

    packages=['genee_puppet'],

    entry_points={
        'console_scripts': [
            'genee-puppet=genee_puppet:main',
        ],
    },
)
