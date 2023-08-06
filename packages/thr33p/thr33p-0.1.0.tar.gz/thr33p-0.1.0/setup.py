import re
import setuptools.command.test


class PyTest(setuptools.command.test.test):
    
    user_options = []
    
    def finalize_options(self):
        setuptools.command.test.test.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest

        pytest.main(self.test_args)


extras_require = {
    'tests': [
        'freezegun >=0.3.1,<0.4',
        'pytest >=2.5.2,<3',
        'pytest-cov >=1.7,<2',
        'pytest-pep8 >=1.0.6,<2',
        'vcrpy >=1.3,<2',
    ],
}

setuptools.setup(
    name='thr33p',
    version=(
        re
        .compile(r".*__version__ = '(.*?)'", re.S)
        .match(open('thr33p.py').read())
        .group(1)
    ),
    url='https://github.com/mayfieldrobotics/thr33p',
    license='BSD',
    author='Mayfield Robotics',
    author_email='dev+thr33p@mayfieldrobotics.com',
    description='.',
    long_description=open('README.rst').read(),
    packages=setuptools.find_packages('.', exclude=('tests', 'tests.*')),
    platforms='any',
    install_requires=['certifi', 'urllib3 >=1.10,<2.0'],
    tests_require=extras_require['tests'],
    extras_require=extras_require,
    scripts=['thr33p'],
    cmdclass={'test': PyTest},
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
