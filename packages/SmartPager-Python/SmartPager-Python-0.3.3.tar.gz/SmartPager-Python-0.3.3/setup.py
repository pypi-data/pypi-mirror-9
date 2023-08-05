
from setuptools import setup, find_packages


__version__ = None
with open('smartpager/version.py') as f:
    exec(f.read())

setup(
    name='SmartPager-Python',
    version=__version__,
    description='SmartPager Communications API for Python',
    author='SmartPager',
    keywords=['smartpager', 'telmediq', 'client'],
    packages=find_packages(),
    install_requires=[
        'requests',
        'python-dateutil',
        'Celery'
    ],
    test_suite='tests'
)
