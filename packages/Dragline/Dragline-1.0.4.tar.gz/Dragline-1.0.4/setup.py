from glob import glob
from setuptools import setup, find_packages


setup(
    name='Dragline',
    version=open('dragline/VERSION').read().strip(),
    description='Distributed Python web crawling framework',
    author='Ashwin Rajeev, Shimil Rahman',
    author_email='ashwin@inzyte.com, shimil@inzyte.com',
    url='http://www.inzyte.com',
    packages=find_packages(exclude=['docs', 'tests*']),
    scripts=glob("scripts/*"),
    data_files=[('dragline/templates', glob("dragline/templates/*"))],
    include_package_data=True,
    install_requires=[i.strip() for i in open('requirements.txt')],
    test_suite='tests',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: Linux',
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Environment :: Console',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet :: WWW/HTTP']
)
