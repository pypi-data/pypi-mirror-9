from distutils.core import setup

from setuptools import find_packages


setup(
    name='django_roles',
    version='0.0.3',
    packages=find_packages(exclude=['tests', 'settings', 'requirements']),
    description='Django Roles with Role-Group-Permission-User',
    long_description=open('README.md').read(),
    install_requires=[
        "django >= 1.7.3",
        "django-mptt >= 0.6.1",
    ],
    author='Cenk Bircanoglu',
    author_email='cenk.bircanoglu@gmail.com',
    url='https://github.com/cenkbircanoglu/django-roles',
    download_url='https://github.com/cenkbircanoglu/django_roles/tarball/0.0.3',
    keywords=['django', 'auth', 'user', 'user role', 'user role', 'organization', 'python'],
    classifiers=[],
    include_package_data=True,
    zip_safe=False,
    license='MIT',
    platforms=['any'],
)