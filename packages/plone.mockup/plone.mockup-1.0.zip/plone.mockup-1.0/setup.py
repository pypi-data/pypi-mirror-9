from setuptools import find_packages
from setuptools import setup


setup(
    name='plone.mockup',
    version='1.0',
    description="Plone integration package for mockup",
    long_description=open("README.rst").read(),
    classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords='plone mockup',
    author='Plone Foundation',
    author_email='plone-developers@lists.sourceforge.net',
    url='https://github.com/plone/mockup',
    license='BSD',
    packages=find_packages(),
    namespace_packages=['plone'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[],
    entry_points='''
        [z3c.autoinclude.plugin]
        target = mockup
    ''',
)
