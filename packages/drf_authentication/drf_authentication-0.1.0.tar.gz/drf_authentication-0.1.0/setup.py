from distutils.core import setup

from setuptools import find_packages


setup(
    name='drf_authentication',
    version='0.1.0',
    packages=find_packages(exclude=['tests', 'settings', 'requirements']),
    description='Django Rest Framework Authentication Module with Angular',
    long_description=open('README.md').read(),
    install_requires=[
        "djangorestframework >= 3.0.0",
        "jack_bower>=0.1.8"
    ],
    author='Cenk Bircanoglu',
    author_email='cenk.bircanoglu@gmail.com',
    url='https://github.com/cenkbircanoglu/drf_authentication',
    download_url='https://github.com/cenkbircanoglu/drf_authentication/tarball/0.1.0',
    keywords=['django', 'auth', 'rest', 'angular', 'login', 'logput', 'password' 'python'],
    classifiers=[],
    include_package_data=True,
    zip_safe=False,
    license='MIT',
    platforms=['any'],
)