from setuptools import setup, find_packages


setup(
    name='aiomas',
    version='0.3.0',
    author='Stefan Scherfke',
    author_email='stefan.scherfke at offis.de',
    description=('A library for multi-agent systems, based on asyncio'),
    long_description=(open('README.txt', encoding='utf-8').read() + '\n\n' +
                      open('CHANGES.txt', encoding='utf-8').read() + '\n\n' +
                      open('AUTHORS.txt', encoding='utf-8').read()),
    url='',
    install_requires=[
        'arrow>=0.4.4',
    ],
    extras_require={
        'MsgPack': ['msgpack-python>=0.4.4'],
        'MsgPackBlosc': ['blosc>=1.2.4', 'msgpack-python>=0.4.4'],
    },
    packages=find_packages(exclude=['tests*']),
    include_package_data=True,
    entry_points={
        'console_scripts': [
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
