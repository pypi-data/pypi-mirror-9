from setuptools import setup, find_packages

setup(
    name='django-sniplates',
    version='0.2.2',
    description='Efficient template macro sets for Django',
    author='Curtis Maloney',
    author_email='curtis@tinbrain.net',
    url='http://github.com/funkybob/django-sniplates',
    keywords=['django', 'templates',],
    packages = find_packages(exclude=('tests*',)),
    zip_safe=False,
    classifiers = [
        'Environment :: Web Environment',
        'Framework :: Django',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    requires = [
        'Django (>=1.4)',
    ],
    install_requires = [
        'Django>=1.4',
    ],
)
