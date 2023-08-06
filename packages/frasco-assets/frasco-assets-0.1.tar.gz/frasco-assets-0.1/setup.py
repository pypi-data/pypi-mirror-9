from setuptools import setup, find_packages


setup(
    name='frasco-assets',
    version='0.1',
    url='http://github.com/frascoweb/frasco-assets',
    license='MIT',
    author='Maxime Bouroumeau-Fuseau',
    author_email='maxime.bouroumeau@gmail.com',
    description="Assets management using easywebassets for Frasco",
    packages=find_packages(),
    package_data={
        'frasco_assets': ['layout.html']
    },
    zip_safe=False,
    platforms='any',
    install_requires=[
        'frasco',
        'easywebassets',
        'Flask-Assets>=0.10',
        'cssmin',
        'jsmin'
    ]
)