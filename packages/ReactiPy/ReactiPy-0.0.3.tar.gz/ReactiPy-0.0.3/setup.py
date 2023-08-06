from setuptools import setup, find_packages


setup(
    name='ReactiPy',

    version='0.0.3',

    description='Compiles React Components server side using python',

    # The project's main homepage.
    url='https://github.com/logandhead/ReactiPy',

    # Author details
    author='Logan Head',
    author_email='logandhead@gmail.com',

    # Choose your license
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[

        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        'License :: OSI Approved :: MIT License',
    ],

    # What does your project relate to?
    keywords='react jsx compile react.js reactjs facebook',
    packages=find_packages(),
    include_package_data=True,
    packages_data={'reactipy':
                       ['package.json', 'reactipy.js']
                   },

    install_requires=['nodeenv==0.13.1'],


)