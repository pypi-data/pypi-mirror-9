from setuptools import setup, find_packages

setup(
    name='aja',
    version='0.9.0',
    description='Buildout-based deployment made safe and easy',
    long_description=(open('README.rst').read() + '\n' +
                      open('CHANGES.rst').read()),
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
    ],
    author='Jukka Ojaniemi',
    author_email='jukka.ojaniemi@gmail.com',
    url='https://github.com/pingviini/aja',
    keywords='deploy buildout',
    license='GPL',
    package_dir={"": "src"},
    packages=find_packages('src'),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'zc.buildout',
        'fabric',
    ],
    extras_require={
        'docs': ['Sphinx']
    },
    test_suite='aja.tests',
)
