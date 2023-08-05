from setuptools import setup, find_packages
    
setup(
    name = 'AnritsuTools',
    version = "1.0.3",
    packages = find_packages(),
	py_modules = ['djscript', 'ni_iotrace'],
    
    # metadata for upload to PyPI
    author = 'David Judge',
	author_email = 'djudge@anritsu.com',
	description = 'Script running for Anritsu VNAs',
)