"""https://github.com/akhavr/42cc-pystyle"""

from setuptools import setup


def get_long_description():
    descr = []
    for fname in ('README.md', ):
        with open(fname) as f:
            descr.append(f.read())
    return '\n\n'.join(descr)

setup(
    name="42cc-pystyle",
    version="0.0.3",
    description="flake8 checks for 42 Coffee Cups style guide",
    long_description=get_long_description(),
    license=open('LICENSE').read(),
    author='Andriy Khavryuchenko',
    author_email='akhavr@khavr.com',
    maintainer='Andriy Khavryuchenko',
    maintainer_email='akhavr@khavr.com',
    url='https://github.com/akhavr/42cc-pystyle',
    classifiers=['Intended Audience :: Developers',
                 'Environment :: Console',
                 'Programming Language :: Python :: 2',
                 'Programming Language :: Python :: 3',
                 'Operating System :: OS Independent',
                 'License :: OSI Approved :: '
                 'GNU General Public License v2 (GPLv2)'],
    keywords='docstrings, flake8',
    entry_points={'flake8.extension': [
        '42cc = 42cc_pystyle.test_docstrings:TestDocstrings',
        ], },
    install_requires=['flake8'],
    py_modules=['42cc_pystyle'],
)
