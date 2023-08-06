from setuptools import setup, find_packages


setup(
    name='frasco-angular',
    version='0.1.3',
    url='http://github.com/frascoweb/frasco-angular',
    license='MIT',
    author='Maxime Bouroumeau-Fuseau',
    author_email='maxime.bouroumeau@gmail.com',
    description="Angular integration for Frasco",
    packages=find_packages(),
    package_data={
        'frasco_angular': ['templates/*.html', 'static/*.js']
    },
    zip_safe=False,
    platforms='any',
    install_requires=[
        'frasco',
        'frasco-assets'
    ]
)
