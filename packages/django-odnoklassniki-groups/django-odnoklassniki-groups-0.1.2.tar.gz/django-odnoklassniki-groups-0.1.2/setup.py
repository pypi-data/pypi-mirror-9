from setuptools import find_packages, setup

setup(
    name='django-odnoklassniki-groups',
    version=__import__('odnoklassniki_groups').__version__,
    description='Django implementation for odnoklassniki API Groups',
    long_description=open('README.md').read(),
    author='ramusus',
    author_email='ramusus@gmail.com',
    url='https://github.com/ramusus/django-odnoklassniki-groups',
    download_url='http://pypi.python.org/pypi/django-odnoklassniki-groups',
    license='BSD',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False, # because we're including media that Django needs
    install_requires=[
        'django-odnoklassniki-api>=0.1.0',
        'django-m2m-history>=0.2.0',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
