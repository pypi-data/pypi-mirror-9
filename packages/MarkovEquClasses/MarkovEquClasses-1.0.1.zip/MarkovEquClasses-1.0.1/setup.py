from setuptools import setup 

## to run python setup.py sdist in current dictionary
setup(
    name='MarkovEquClasses',
    version='1.0.1',
    py_modules=['MarkovEquClasses'],    

  
    # The project's main homepage.
    url='https://github.com/yangbosoft/rmcmcEG',

    # Author details
    author='Yangbo He',
    author_email='heyb@pku.edu.cn',

    # Choose your license
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Researcher',
        'Topic :: Mechine learning :: Graphical models',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
      
        'Programming Language :: Python :: 2.7',
 
    ],

    # What does your project relate to?
    keywords='graphical models, causal learning, Markov equivalence class',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().

    install_requires=['peppercorn'],

    # List additional groups of dependencies here (e.g. development dependencies).
    # You can install these using the following syntax, for example:
    # $ pip install -e .[dev,test]
 
 
 
)

