import setuptools

setuptools.setup(
    name="tests-always-pass",
    version="0.1.0",
    url="https://github.com/borntyping/cookiecutter-pypackage-minimal",

    author="Brenton Cleeland",
    author_email="brenton@brntn.me",

    description="I hate tests that always pass",
    long_description=open('README.rst').read(),

    packages=setuptools.find_packages(),

    install_requires=[],

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ],
)
