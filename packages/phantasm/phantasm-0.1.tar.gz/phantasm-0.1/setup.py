from setuptools import setup
from pip.req import parse_requirements
import sys, os

if sys.argv[-1] == 'publish':
    os.system("python setup.py sdist bdist_wheel upload; git push")
    sys.exit()

setup(name="phantasm",
        version='0.1',
        description='Python tools for dynamic clustering',
        author='Eric Rasche',
        author_email='esr@tamu.edu',
        install_requires=['python-levenshtein', 'numpy', 'scikit-learn', 'biopython'],
        packages=["phantasm"],
        scripts=[],
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Operating System :: OS Independent',
            'Intended Audience :: Science/Research',
            'Environment :: Console',
            'License :: OSI Approved :: Apache Software License',
            ],
        )
