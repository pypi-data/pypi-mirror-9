from setuptools import setup, find_packages

setup(
    name='detektor',
    description='A library for finding similarities in code.',
    version='1.1.0-beta.012',
    url='https://github.com/appressoas/detektor',
    author='Magne Westlie, Espen Angell Kristiansen, Tor Ivar Johansen',
    author_email='magne@appresso.no,espen@appresso.no,tor@appresso.no',
    license='GPL',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=['setuptools'],
    test_suite='detektor.tests',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved',
        'Operating System :: OS Independent',
        'Programming Language :: Python'
    ]
)
