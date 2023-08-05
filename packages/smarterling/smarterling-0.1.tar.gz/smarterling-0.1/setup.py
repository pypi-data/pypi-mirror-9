from setuptools import setup

setup(

    # general meta
    name='smarterling',
    version='0.1',
    author='Brian C. Dilley - Flipagram',
    author_email='brian@flipagram.com',
    description='Python based command line tool for performing automated tasks with Smartling (http://www.smartling.com).',
    platforms='any',
    url='https://github.com/Cheers-Dev/smarterling',
    download_url='https://github.com/Cheers-Dev/smarterling',

    # packages
    packages=[
        'smarterling'
    ],

    # dependencies
    install_requires=[
        'SmartlingApiSdk>=1.2.5',
        'pyyaml>=3.10'
    ],
    # additional files to include
    include_package_data=True,

    # the scripts
    scripts=['scripts/smarterling'],

    # wut?
    classifiers=['Intended Audience :: Developers']
)
