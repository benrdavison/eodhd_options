from setuptools import setup, find_packages

setup(
    name="eodhd_options",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
        "pandas>=1.2.0",
        "python-dateutil>=2.8.0",
        "python-dotenv>=0.19.0"
    ],
    author="Castellan Group",
    author_email="",  # Add your email
    description="A Python wrapper for the EODHD Options API",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="",  # Add your repository URL
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
) 