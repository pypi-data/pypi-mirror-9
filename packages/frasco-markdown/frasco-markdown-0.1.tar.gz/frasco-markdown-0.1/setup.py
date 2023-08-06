from setuptools import setup


setup(
    name='frasco-markdown',
    version='0.1',
    url='http://github.com/frascoweb/frasco-markdown',
    license='MIT',
    author='Maxime Bouroumeau-Fuseau',
    author_email='maxime.bouroumeau@gmail.com',
    description="Markdown integration for Frasco",
    py_modules=['frasco_markdown'],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'frasco',
        'Markdown>=2.4.1'
    ]
)