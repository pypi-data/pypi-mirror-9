from setuptools import setup, find_packages


setup(
    name='frasco-aws',
    version='0.1',
    url='http://github.com/frascoweb/frasco-aws',
    license='MIT',
    author='Maxime Bouroumeau-Fuseau',
    author_email='maxime.bouroumeau@gmail.com',
    description="Amazon Web Services integration for Frasco",
    packages=find_packages(),
    zip_safe=False,
    platforms='any',
    install_requires=[
        'frasco',
        'boto'
    ]
)