# -*- encoding: utf-8 -*-
from setuptools import setup, find_packages

install_requires = [
    'hatak>=0.2.7.8',
    'Hatak_Formskit>=0.2.3.1',
    'Hatak_Sql>=0.1.11',
    'Hatak_Jinja2',
]

if __name__ == '__main__':
    setup(
        name='Hatak_Auth',
        version='0.2.2.2',
        description='Auth plugin for Hatak.',
        license='Apache License 2.0',
        packages=find_packages('src'),
        package_dir={'': 'src'},
        namespace_packages=['haplugin'],
        install_requires=install_requires,
        include_package_data=True,
        zip_safe=False,
        package_data={
            'haplugin': [
                'auth/templates/*.jinja2',
                'auth/templates/forms/*.jinja2',
            ],
        }
    )
