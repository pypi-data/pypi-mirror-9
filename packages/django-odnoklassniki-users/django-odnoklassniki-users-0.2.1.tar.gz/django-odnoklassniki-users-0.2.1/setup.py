from setuptools import setup, find_packages

setup(
    name='django-odnoklassniki-users',
    version=__import__('odnoklassniki_users').__version__,
    description='Django implementation for odnoklassniki API Users',
    long_description=open('README.md').read(),
    author='ramusus',
    author_email='ramusus@gmail.com',
    url='https://github.com/ramusus/django-odnoklassniki-users',
    download_url='http://pypi.python.org/pypi/django-odnoklassniki-users',
    license='BSD',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,  # because we're including media that Django needs
    install_requires=[
        'django-odnoklassniki-api>=0.2.0',
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
