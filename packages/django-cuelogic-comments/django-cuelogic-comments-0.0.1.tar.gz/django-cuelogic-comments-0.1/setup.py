import os
from setuptools import setup,find_packages

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-cuelogic-comments',
    version='0.1',
    license='BSD License',  # example license
    description='A simple Django app for manage comments.',
    packages = ['django_cuelogic_comments','django_cuelogic_comments.templates','django_cuelogic_comments.static','django_cuelogic_comments.docs'],
    package_data={'django_cuelogic_comments.templates':['comments/*'],'django_cuelogic_comments.static':['*'],'django_cuelogic_comments.docs':['*'],},
    long_description=README,
    url='#',
    author='Dadaso Zanzane',
    author_email='dadaso.zanzane@cuelogic.co.in',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License', # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    )