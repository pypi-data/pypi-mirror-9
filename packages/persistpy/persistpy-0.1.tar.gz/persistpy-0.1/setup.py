from setuptools import setup, find_packages


setup(
    name='persistpy',
    version='0.1',
    url='http://github.com/frascoweb/persistpy',
    license='MIT',
    author='Maxime Bouroumeau-Fuseau',
    author_email='maxime.bouroumeau@gmail.com',
    description="Easy object persistence with MongoDb",
    packages=find_packages(),
    zip_safe=False,
    platforms='any',
    install_requires=[
        'pymongo>=2.7.1',
        'inflection',
        'jsonpickle>=0.8.0'
    ]
)