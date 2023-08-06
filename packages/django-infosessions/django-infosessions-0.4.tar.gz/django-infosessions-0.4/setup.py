import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-infosessions',
    version='0.4',
    packages=['infosessions'],
    include_package_data=True,
    test_suite='runtests.run',
    license='BSD License',  # example license
    description='A simple Django app to capture session information',
    long_description=README,
    author='Aleksandr Razumov',
    author_email='ernado@ya.ru',
    install_requires=['django>=1.6', 'django-redis>=3.8.3', 'hiredis>=0.1.4'],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License', # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        # Replace these appropriately if you are stuck on Python 2.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)