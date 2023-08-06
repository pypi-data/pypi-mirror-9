from setuptools import setup


setup(
    name='frasco-images',
    version='0.1',
    url='http://github.com/frascoweb/frasco-images',
    license='MIT',
    author='Maxime Bouroumeau-Fuseau',
    author_email='maxime.bouroumeau@gmail.com',
    description="Image manipulation for Frasco",
    py_modules=['frasco_images'],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'frasco',
        'Pillow>=2.5.1'
    ]
)