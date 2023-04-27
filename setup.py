from setuptools import setup

setup(
    name='app',
    packages=['app'],
    include_package_data=True,
    install_requires=[
        'flask',
    ],
    dependency_links=['requirements.txt']
)
