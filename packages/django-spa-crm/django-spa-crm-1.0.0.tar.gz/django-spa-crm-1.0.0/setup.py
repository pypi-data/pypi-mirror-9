import sys
from setuptools import find_packages
from setuptools import setup


assert sys.version_info >= (3, 4), "Python 3.4+ required."


with open("requirements.txt") as file:
    install_requires = file.read().splitlines()


with open("README.md") as file:
    long_description = file.read()


with open("PKG-INFO") as file:
    classifiers = [x.split("Classifier: ")[1] for x in file.read().splitlines() if x.startswith("Classifier: ")]


setup(
    name="django-spa-crm",
    description="Django SPA CRM",
    long_description=long_description,
    license="Apache License 2.0",
    version="1.0.0",

    author="Matt Harasymczuk",
    author_email="code@mattagile.com",
    url="http://mattagile.com/",
    download_url="https://github.com/MattAgile/django-spa-crm",

    packages=find_packages(),
    package_data={"": ["LICENSE", "README.md"], "crm": ["*.py"]},
    package_dir={"crm": "crm"},
    include_package_data=True,
    install_requires=install_requires,
    zip_safe=False,
    classifiers=classifiers
)



