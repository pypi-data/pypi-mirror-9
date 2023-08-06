import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-vagrantize',
    version='0.1.0',
    packages=['vagrantize','vagrantize.management','vagrantize.management.commands'],
    include_package_data=True,
    install_requires=['django'],
    license='MIT License',
    description='Run Django dev server from VM',
    long_description=README,
    author='Chuck Bassett',
    author_email='iamchuckb@gmail.com',
    keywords='vagrant django runserver',
    classifiers=[
	'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
