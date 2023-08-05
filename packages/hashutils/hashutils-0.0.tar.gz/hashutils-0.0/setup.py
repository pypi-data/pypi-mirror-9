from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(name = "hashutils",
    version = "0.0",
    description = "Utility functions for hashing arrays, combining hashes.",
    long_description = readme(),
    author = "Timothy D. Morton",
    author_email = "tim.morton@gmail.com",
    url = "https://github.com/timothydmorton/hashutils",
    packages = ['hashutils'],
    classifiers=[
      'Development Status :: 3 - Alpha',
      'Intended Audience :: Science/Research',
      'License :: OSI Approved :: GNU General Public License (GPL)',
      'Operating System :: OS Independent',
      'Programming Language :: Python',
      ],
    zip_safe=False,
    install_requires=['']
) 
