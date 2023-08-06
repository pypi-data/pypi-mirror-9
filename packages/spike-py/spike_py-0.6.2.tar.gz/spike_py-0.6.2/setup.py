from setuptools import setup, find_packages

try:
    from pypandoc import convert
    read_md = lambda f: convert(f, 'rst')
except ImportError:
    print("warning: pypandoc module not found, could not convert Markdown to RST")
    read_md = lambda f: open(f, 'r').read()

setup(
    name = "spike_py",
    version = "0.6.2",
    description = 'Package for processing datasets obtained with FT analytic tools.',
    packages = find_packages(exclude=["*Miscellaneous*", "dynsubplot.py", "old", "_build", "_templates", "_static"]),
    #packages = 'spike',
    install_requires = ['docutils>=0.3'],
    package_data = {
        # If any package contains *.txt or *.rst files, include them:
        '': ['README.md'],
    },
    author = "Casc4de, Inc",
    author_email = 'lionel.chiron@casc4de.eu',
    long_description=read_md('README.md'),
    license = "Cecill",
    zip_safe=False

)
