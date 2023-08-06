from os.path import join
from setuptools import setup, find_packages


long_description = (open('README.rst').read() +
                    open('CHANGES.rst').read() +
                    open('TODO.rst').read())


def get_version():
    with open('__init__.py') as f:
        for line in f:
            if line.startswith('__version__ ='):
                return line.split('=')[1].strip().strip('"\'')


setup(
    name='djChoices',
    version=get_version(),
    description='Alternative to django-model-util\'s Choices',
    long_description=long_description,
    author='Tom Leo',
    author_email='tom@tomleo.com',
    url='https://github.com/tomleo/djChoices',
    license='GPL',
    packages=find_packages(),
    install_requires=['Django>=1.6.0'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Framework :: Django',
    ],
    keywords='django model choices',
    zip_safe=False,
    test_suite='runtests.runtests'
)

