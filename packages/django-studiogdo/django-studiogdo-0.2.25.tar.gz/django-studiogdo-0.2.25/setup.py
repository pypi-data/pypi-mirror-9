import os
from setuptools import setup, find_packages

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-studiogdo',
    version='0.2.25',
    packages=find_packages(),
    include_package_data=True,
    license='BSD License',  # example license
    description='Django implementation of StudioGdo MVC extension.',
    long_description=README,
    url='http://www.coworks.pro/',
    author='Guillaume Doumenc',
    author_email='gdoumenc@coworks.pro',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',  # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=[
        'beautifulsoup4>=4.3.2',
        'html5lib>=0.999',
        'ipdb>=0.8',
        'requests>=2.3.0',
    ],
)
