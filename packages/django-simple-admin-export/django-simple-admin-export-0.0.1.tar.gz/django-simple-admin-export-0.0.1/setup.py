# Use setuptools if we can
try:
    from setuptools.core import setup
except ImportError:
    from distutils.core import setup

setup(
    name='django-simple-admin-export',
    version="0.0.1",
    description='',
    long_description='',
    author='Albert O\'Connor',
    author_email='info@albertoconnor.ca',
    url='https://bitbucket.org/albertoconnor/django-simple-admin-export',
    download_url='',
    install_requires=[
        'unicodecsv == 0.9.4',
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Django",
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development",
    ],
    packages=[
        'admin_export',
    ],
)
