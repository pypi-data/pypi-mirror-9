from setuptools import setup, find_packages

setup(
    name="tools-ark930-0.0.3",
    version="0.0.3",
    keywords='sample setuptools development',
    description='a simple egg for test',
    license='MIT License',

    author='ark930',
    author_email='lark930@gmail.com',
    url='ark.com',
    packages=find_packages(),
    package_data={'': ['*.*']},
    include_package_data=True,
    platforms='any',
    install_requires=[],

    entry_points={
        'console_scripts': [
            'ark930=tools:main',
        ],
    },
)