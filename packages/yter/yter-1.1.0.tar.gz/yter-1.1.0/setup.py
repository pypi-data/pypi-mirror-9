import setuptools
import re

setuptools.setup(
    name='yter',
    version='1.1.0',
    license='MIT',
    keywords='iterator itertools',
    description='Clever, quick iterators that make your smile whiter',

    author='Peter Shinners',
    author_email='pete at shinners.org',
    url='https://bitbucket.org/petershinners/yter',
    long_description=re.sub(
                r"\[(`.*?`)\]\(#.+?\)",
                r"\1",
                open("README.txt").read()),

    packages=["yter"],

    zip_safe=True,
    tests_require=['pytest'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries',
    ],   # https://pypi.python.org/pypi?%3Aaction=list_classifiers
)
