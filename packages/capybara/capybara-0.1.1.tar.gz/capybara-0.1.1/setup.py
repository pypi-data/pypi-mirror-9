from setuptools import setup, find_packages
version = '0.1.1'

try:
    import pypandoc
    read_md = lambda f: pypandoc.convert(f, 'rst')
except ImportError:
    print("warning: pypandoc module not found, could not convert Markdown to RST")
    read_md = lambda f: open(f, 'r').read()

setup(name='capybara',
        version=version,
        description="A simple wrapper for multiple tokens of multiple APIs",
        # http://pypi.python.org/pypi?:action=list_classifiers
        classifiers=[
            "Development Status :: 3 - Alpha",
            "Environment :: Console",
            "Intended Audience :: Developers",
            "Natural Language :: English",
            "Operating System :: OS Independent",
            "Programming Language :: Python",
            "Topic :: Software Development :: Libraries :: Python Modules",
            "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries",
            "Topic :: Utilities",
            "License :: OSI Approved :: MIT License",
            ],
        keywords='amazon, product advertising, rakuten, item search, api',
        author='ITOH Akihiko',
        author_email='akihiko.mus+pypi@gmail.com',
        url='https://github.com/AkihikoITOH/capybara',
        license='MIT',
        packages=find_packages(exclude=['examples', 'tests']),
        include_package_data=True,
        zip_safe=True,
        long_description=read_md('README.md'),
        install_requires=["python-amazon-simple-product-api", "requests"],
    )
