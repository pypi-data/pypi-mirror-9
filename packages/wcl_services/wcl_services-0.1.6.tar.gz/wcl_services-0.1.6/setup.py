from setuptools import setup, find_packages

setup(
    name="wcl_services",
    version="0.1.6",
    url='http://github.com/westerncapelabs/wcl-services',
    license='None',
    description="A client library for the Western Cape Labs HTTP Services APIs",
    long_description=open('README.rst', 'r').read(),
    author='Western Cape Labs',
    author_email='devops@westerncapelabs.com',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'demands',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Networking',
    ],
)
