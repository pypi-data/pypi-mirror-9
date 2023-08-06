from setuptools import setup, find_packages

version = "0.1"

setup(
    name="anybox.nose.odoo",
    version=version,
    author="Jean-Sebastien Suzanne",
    author_email="jssuzanne@anybox.fr",
    description="Console script to run nose with the good import",
    license="GPLv3",
    long_description=open('README.rst').read(),
    url="https://bitbucket.org/anybox/anybox.nose.odoo",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    namespace_packages=['anybox', 'anybox.nose'],
    install_requires=['setuptools', 'nose'],
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 "
            "or later (GPLv3+)",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
        "Topic :: System :: Benchmark",
    ],
    entry_points={
        'console_scripts': [
            'odoo_nosetests = anybox.nose.odoo:run_exit',
        ],
    },
)
