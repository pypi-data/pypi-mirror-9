from setuptools import setup, find_packages
setup(
    name = "lazymp",
    version = "0.1.0.0.1",
    packages = find_packages(),
    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    install_requires = [
        "pyre>=0.8.2.0-pathos", 
        "processing>=0.52-pathos", 
        "Pillow>=2.8.1", 
        "pathos>=0.2a1.dev0", 
        "pyre>=0.8.2.0-pathos", 
        "processing>=0.52-pathos"    
    ],

    dependency_links = [
        "https://github.com/uqfoundation/pathos/raw/master/external/pyre-0.8.2.0-pathos.zip",
        "https://github.com/uqfoundation/pathos/raw/master/external/processing-0.52-pathos.zip",
        "git+https://github.com/uqfoundation/pathos#egg=pathos-0.2a1.dev0"
    ],

    # metadata for upload to PyPI
    author = "San-Chuan Hung",
    author_email = "sanchuah@andrew.cmu.edu",
    description = "This is an Example Package",
    license = "MIT",
    keywords = "easy lazy openmp parallel",
    url = "http://leohung.net/pymp",   # project home page, if any
    # could also include long_description, download_url, classifiers, etc.
)
