import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-dashing-custom-torsten',
    version='0.2.5b2',
    packages=['dashing'],
    include_package_data=True,
    license='MIT License',
    description='A simple Django dashboard app to visualize interesting data about your project. '
                'Custom for testing by Torsten Feld',
    long_description=README,
    url='https://github.com/torstenfeld/django-dashing',
    author='Torsten Feld (Original: Mauricio Reyes)',
    author_email='torsten.feld@avira.com (Original: mreyes@talpor.com)',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Localization',
        'Topic :: Utilities',
    ],
    keywords=[],
)