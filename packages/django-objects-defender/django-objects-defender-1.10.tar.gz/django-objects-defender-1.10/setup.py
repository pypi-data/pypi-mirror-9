from setuptools import setup, find_packages

setup(
    name="django-objects-defender",
    version='1.10',
    requires=['django (>=1.4)'],
    packages=find_packages(),
    author="Mikhail Andreev",
    author_email="datysho@gmail.com",
    description="Easy solution to make undeleteble objects.",
    url="https://bitbucket.org/datysho/django-objects-defender/",
    include_package_data=True,
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Topic :: Utilities',
    ]
)