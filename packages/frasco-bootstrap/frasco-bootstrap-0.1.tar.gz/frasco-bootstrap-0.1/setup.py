from setuptools import setup, find_packages


setup(
    name='frasco-bootstrap',
    version='0.1',
    url='http://github.com/frascoweb/frasco-bootstrap',
    license='MIT',
    author='Maxime Bouroumeau-Fuseau',
    author_email='maxime.bouroumeau@gmail.com',
    description="Bootstrap (frontend framework) integration for Frasco",
    packages=find_packages(),
    package_data={
        'frasco_bootstrap': [
            'macros/*.html',
            'templates/*.html',
            'templates/users/*.html']
    },
    zip_safe=False,
    platforms='any',
    install_requires=[
        'frasco',
        'frasco-assets'
    ]
)