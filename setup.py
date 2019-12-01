from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='pymixconsole',
      version='0.0.1',
      description='Headless multitrack mixing console in Python',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='https://github.com/csteinmetz1/pymixconsole',
      author='Christian Steinmetz',
      author_email='cjstein@clemson.edu',
      packages=find_packages(),
      install_requires=['scipy>=1.0.1',
                        'numpy>=1.14.2',
                        'numba>=0.46.0'],
      classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
      )
)