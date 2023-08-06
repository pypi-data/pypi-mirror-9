from setuptools import setup
import os.path

ROOT = os.path.dirname(os.path.realpath(__file__))
test_reqs = open('requirements_dev.txt' ,'r').read().splitlines()

setup(
    name = 'item',
    version = '0.0.3',
    description = 'API to describe schema of data to extract them from HTML',
    url = 'https://github.com/lorien/item',
    long_description = open(os.path.join(ROOT, 'README.rst')).read(),
    author = 'Gregory Petukhov',
    author_email = 'lorien@lorien.name',
    install_requires = ['selection', 'weblib'],
    tests_require = test_reqs,
    test_suite = "test",
    packages = ['item', 'item.script', 'script', 'test'],
    license = "MIT",
    classifiers = (
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ),
)
