# -*- encoding: utf-8 -*-
from setuptools import setup, find_packages

install_requires = [
    'hatak>=0.2.1',
    'formskit>=0.5.4.8',
    'hatak_jinja2',
    'hatak_beaker',
]

if __name__ == '__main__':
    setup(
        name='Hatak_Formskit',
        version='0.2.3.3',
        description='Formskit plugin for Hatak.',
        license='Apache License 2.0',
        packages=find_packages('src'),
        package_dir={'': 'src'},
        namespace_packages=['haplugin'],
        install_requires=install_requires,
        include_package_data=True,
        zip_safe=False,
        package_data={
            'haplugin': [
                'formskit/templates/*.jinja2'
            ],
        }
    )
