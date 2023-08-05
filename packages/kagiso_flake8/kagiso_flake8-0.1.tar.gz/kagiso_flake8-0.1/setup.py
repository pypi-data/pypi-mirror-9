from setuptools import setup, find_packages


setup(
    name="kagiso_flake8",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'flake8',
        'pep8-naming',
        'flake8-import-order',
        'flake8-quotes'
    ]
)
