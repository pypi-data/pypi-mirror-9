from setuptools import setup, find_packages
setup(
    name = 'AnritsuTools',
    version = '0.1',
    packages = find_packages(),
	py_modules = ['AnritsuTools'],
    
    # metadata for upload to PyPI
    author = 'David Judge',
	author_email = 'djudge@anritsu.com',
	description = 'Script running tools for Anritsu VNAs',
)