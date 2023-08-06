from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name = "plotutils",
    version = "0.3.2",
    description = "Simple matplotlib-related utility functions.",
    long_description = readme(),
    author = "Timothy D. Morton",
    author_email = "tim.morton@gmail.com",
    url = "https://github.com/timothydmorton/plotutils",
    packages = ['plotutils'],
    classifiers=[
      'Development Status :: 3 - Alpha',
      'Intended Audience :: Science/Research',
      'License :: OSI Approved :: GNU General Public License (GPL)',
      'Operating System :: OS Independent',
      'Programming Language :: Python',
      ],
    zip_safe=False,
    install_requires=['matplotlib']
) 
