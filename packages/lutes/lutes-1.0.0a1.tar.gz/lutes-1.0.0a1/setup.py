from setuptools import setup
from lutes import __version__

setup(
    name='lutes',
    version=__version__,
    description='A lightweight component-entity-system engine',
    url='https://github.com/greizgh/lutes',
    download_url='https://github.com/greizgh/lutes/releases',
    author='Greizgh',
    author_email='greizgh@ephax.org',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='component entity system',
    packages=['lutes'],
    zip_safe=True,
)
