import codecs

from os import path
from setuptools import find_packages, setup


def read(*parts):
    filename = path.join(path.dirname(__file__), *parts)
    with codecs.open(filename, encoding="utf-8") as fp:
        return fp.read()


setup(
    author="Pinax Developers",
    author_email="developers@pinaxprojects.com",
    description="User notification management for the Django web framework",
    name="django-notification",
    long_description=read("README.rst"),
    version="1.3.1",
    url="http://django-notification.rtfd.org/",
    license="MIT",
    packages=find_packages(),
    package_data={
        "notification": [
            "locale/*",
            "templates/*"
        ]
    },
    install_requires=[
        "django-user-accounts>=1.0.1"
    ],
    test_suite="runtests.runtests",
    tests_require=[
        "django-user-accounts>=1.0.1"
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Framework :: Django",
    ],
    zip_safe=False
)
