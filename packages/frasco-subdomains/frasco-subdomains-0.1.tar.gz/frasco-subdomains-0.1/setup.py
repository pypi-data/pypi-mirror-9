from setuptools import setup


setup(
    name='frasco-subdomains',
    version='0.1',
    url='http://github.com/frascoweb/frasco-subdomains',
    license='MIT',
    author='Maxime Bouroumeau-Fuseau',
    author_email='maxime.bouroumeau@gmail.com',
    description="Subdomains awareness for Frasco",
    py_modules=['frasco_subdomains'],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'frasco'
    ]
)