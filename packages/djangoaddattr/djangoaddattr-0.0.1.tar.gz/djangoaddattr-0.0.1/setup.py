from setuptools import setup, find_packages

setup(
    name='djangoaddattr',
    version=str('0.0.1'),
    description="djangoaddattr",
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: Django",
        "Environment :: Web Environment",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
    ],
    keywords='bootstrap,django',
    author='neuman',
    author_email='soloptimus@gmail.com',
    url='http://github.com/neuman/django-template-addattr',
    license='BSD',
    test_suite='tests',
    install_requires = [
        "django>=1.3",
    ],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
)
