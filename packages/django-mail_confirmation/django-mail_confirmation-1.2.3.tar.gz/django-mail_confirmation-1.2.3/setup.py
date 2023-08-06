import os
from setuptools import setup
from setuptools import setup, find_packages

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-mail_confirmation',
    version='1.2.3',
    packages=find_packages(),
    include_package_data=True,
    license='GPLv3 License',  # example license
    description='A general django user mail confirmation app usable with multiple models at the same time.',
    long_description=README,
    url='http://v.licheni.net/drc/django-mail_confirmation.git',
    author='Davide Riccardo Caliendo',
    author_email='davide.licheni.net',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)

