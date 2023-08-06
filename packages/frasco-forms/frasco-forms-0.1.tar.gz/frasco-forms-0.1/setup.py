from setuptools import setup, find_packages


setup(
    name='frasco-forms',
    version='0.1',
    url='http://github.com/frascoweb/frasco-forms',
    license='MIT',
    author='Maxime Bouroumeau-Fuseau',
    author_email='maxime.bouroumeau@gmail.com',
    description="WTForms integration for Frasco",
    packages=find_packages(),
    package_data={
        'frasco_forms': ['*.html']
    },
    zip_safe=False,
    platforms='any',
    install_requires=[
        'frasco',
        'Flask-WTF>=0.9.5',
        'inflection'
    ]
)