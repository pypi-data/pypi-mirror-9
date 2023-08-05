from setuptools import setup, find_packages

setup(
    name='bosrvclient',
    version='0.1.7',
    packages=find_packages(),

    install_requires=[
        'thrift'
    ],

    author='MacroData Inc',
    author_email='info@macrodatalab.com',
    description='BigObject service client for python',
    license='Apache 2.0',
    keywords=[
        'bigobject',
        'macrodata',
        'analytics'
    ],
    url='https://bitbucket.org/macrodata/bosrvclient-py.git',

    zip_safe=False
)
