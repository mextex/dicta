import setuptools

with open("README.md", "r") as fh:
    description = fh.read()

setuptools.setup(
    name="dicta",
    version="0.8.143",
    author="peterwendl",
    author_email="dev@peterwendl.de",
    description="A dict subclass to observe data changes in the nested data-tree.",
    long_description=description,
    long_description_content_type="text/markdown",
    url="https://github.com/mextex/dicta",
    license='MIT',
    python_requires='>=3.8',
    package_dir = {"": "dicta"},
    packages = setuptools.find_packages(where="dicta"),
    install_requires=[]
)