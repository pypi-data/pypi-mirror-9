from setuptools import setup

setup(
    name='aiqpy',
    version='0.8.1',
    description='Python bindings for connecting to a AIQ8 server',
    author='Erik Lundberg',
    author_email='lundbergerik@gmail.com',
    packages=['aiqpy', 'tools'],
    install_requires=[
        'requests',
        'six',
        'click'
    ],
    keywords=['aiq8', 'appear', 'rest', 'api'],
    zip_safe=False,
    entry_points={
        'console_scripts': [
           'aiqpyprofile = tools.aiqpyprofile:main'
        ]
    }
)
