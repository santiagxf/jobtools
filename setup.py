import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="jobtools",
    version="0.0.1",
    author="Facundo Santiago",
    author_email="@santiagof",
    description="Facilitates the use of Python from the command line",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],                                      
    python_requires='>=3.6',                
    packages=setuptools.find_packages(where='src', exclude=("tests",)),   
    package_dir={'':'src'},  
    include_package_data=True,   
    install_requires=[]
)