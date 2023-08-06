from setuptools import setup, find_packages

setup(
    name='pybossa-client',
    version='1.0.0',
    packages=find_packages(),
    install_requires=['requests>=0.13.0'],
    # metadata for upload to PyPI
    author='Open Knowledge Foundation Labs',
    # TODO: change
    author_email='okfnlabs@okfn.org',
    description='pybossa-client is a tiny Python library makes it easy to work with PyBossa.',
    long_description='''PyBossa is a crowdsourcing framework. This tiny library allows you to interact with it.''',
    license='MIT',
    url='https://github.com/pybossa/pybossa-client',
    download_url='https://github.com/PyBossa/pybossa-client/zipball/master',
    include_package_data=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    entry_points=''''''
)
