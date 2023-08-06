import os
from setuptools import setup
import restart

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-restart',
    version=restart.__version__,
    packages=['restart'],
    include_package_data=True,
    license='BSD License',  # example license
    description='A simple Django app to let admins restart the application',
    long_description=README,
    url='https://bitbucket.org/lvlup/django-restart/overview',
    author='Allan Brown',
    author_email='allan@thisislevelup.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License', # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        # Replace these appropriately if you are stuck on Python 2.
        "Programming Language :: Python :: 2.6",
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=[
        'Django>=1.5',
        'django-classy-tags>=0.5',
    ],
)