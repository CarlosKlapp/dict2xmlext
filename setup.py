"""
Setup information for the library.
"""

from setuptools import find_packages, setup  # type: ignore

setup(
    name='dict2xmlext',
    packages=find_packages(),
    version='1.0.0',
    description='An extensible library for converting a python dictionary to an XML string',
    long_description=open('README.md').read(),  # Include the README for the long description  # type: ignore
    long_description_content_type="text/markdown",  # Type of content in README (Markdown)    author='Carlos Klapp',
    author_email='CarlosK.Github@gmail.com',
    license='MIT',
    maintainer='Carlos Klapp',
    maintainer_email='CarlosK.Github@gmail.com',
    keywords=['dict', 'dictionary', 'dictionaries', 'xml', 'convert'],
    packages=find_packages(),              # Automatically find the package directories  # type: ignore
    python_requires=">= 3.12",
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Markup :: XML",
        "Intended Audience :: Developers",
    ]
)
