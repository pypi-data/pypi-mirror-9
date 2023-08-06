from setuptools import setup, find_packages
from setuptools.command.test import test as _test

class test(_test):
    def finalize_options(self):
        _test.finalize_options(self)
        self.test_args.insert(0, 'discover')

setup(
    name='FileDistribution',
    version='0.1.1',
    author='Adam Kubica',
    author_email='caffecoder@kaizen-step.com',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries',
        ],
    scripts=[],
    url='http://github.org/caffecoder/fdist-python',
    license='MIT',
    description='Simple file distribution library.',
    long_description='Simple library that allows organize distribution of files within hex based tree.',
    install_requires=[],
    platforms=['darwin','linux2','freebsd7'],
    test_loader="unittest:TestLoader",
    test_suite = "filedistribution.test",
    cmdclass={
        'test': test,
    }
)
