from setuptools import setup
setup(
    name = "pytronix",
    version = "0.8",
    packages = [ 'pytronix' ],
    package_dir = { 'pytronix':'' },
    package_data = { '': ['*.txt','*.md'] },
    install_requires = [ 'telepythic' ],
    
    # metadata for upload to PyPI
    author = "Martijn Jasperse",
    author_email = "m.jasperse@gmail.com",
    description = "A python project to easily and rapidly download data from TekTronix DSOs",
    long_description = "This project provides the ability to quickly downloading scope data from a TekTronix digital oscilloscope using the telnet interface.",
    license = "BSD",
    keywords = "tektronix DSO CRO scope HDF5",
    url = "https://bitbucket.org/martijnj/pytronix",

    # could also include long_description, download_url, classifiers, etc.
)
