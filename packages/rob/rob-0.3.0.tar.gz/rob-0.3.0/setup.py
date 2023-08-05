from setuptools import setup, find_packages


def _read_long_description():
    try:
        import pypandoc
        return pypandoc.convert('README.md', 'rst', format='markdown')
    except Exception:
        return None


setup(
    name="rob",
    version='0.3.0',
    description='Make python objects persistent with Redis.',
    long_description=_read_long_description(),
    url='http://github.com/relekang/rob',
    author='Rolf Erik Lekang',
    packages=find_packages(),
    install_requires=[
        'redis',
    ]
)
