from setuptools import find_packages, setup

setup(
    name='dict2xmlext',
    packages=find_packages(),
    version='1.0.0',
    description='An extensible library for converting a python dictionary to an XML string',
    long_description='',
    author='Carlos Klapp',
    author_email='CarlosK.Github@gmail.com',
    license='MIT',
    maintainer='Carlos Klapp',
    maintainer_email='CarlosK.Github@gmail.com',
    keywords=['dict', 'dictionary', 'dictionaries', 'xml', 'convert'],
    python_requires=">= 3.10",
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Markup :: XML",
        "Intended Audience :: Developers",
    ]
)
