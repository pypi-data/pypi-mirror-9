import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, 'README.rst')).read()
    CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()
except:
    README = CHANGES = ''

docs_extras = [
        'Sphinx',
    ]

tests_require = [
        '',
    ]

testing_extras = tests_require + [
        'nose',
        'coverage',
        'virtualenv',
        'tox',
    ]

requires = [
        'pyramid',
        'python-keystoneclient',
    ]

setup(name='pyramid_keystone',
        version='0.0.1.dev0',
        description='OpenStack keystone bindings for Pyramid',
        long_description=README + '\n\n' + CHANGES,
        classifiers=[
            "Development Status :: 1 - Planning",
            "Intended Audience :: Developers",
            "Programming Language :: Python",
            "Programming Language :: Python :: 3.4",
            "Framework :: Pyramid",
            "License :: OSI Approved :: MIT License",
            ],
        keywords='web wsgi pyramid keystone',
        author="Bert JW Regeer",
        author_email="bertjw@regeer.org",
        url="https://github.com/bertjwregeer/pyramid_keystone",
        license="MIT",
        packages=find_packages(),
        include_package_data=True,
        zip_safe=False,
        install_requires=requires,
        extras_require = {
            'testing': testing_extras,
            'docs': docs_extras,
            },
        tests_require=tests_require,
        test_suite="pyramid_keystone.tests",
        entry_points="""""",
        )
