from setuptools import setup, find_packages
# from codecs import open  # To use a consistent encoding
# from os import path

# here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
# with open(path.join(here, 'DESCRIPTION.rst'), encoding='utf-8') as f:
    # long_description = f.read()

setup(
    name='rabbitman',

    version='0.1.0',

    description='Python interface to the RabbitMQ management api',
    # long_description=long_description,

    # The project's main homepage.
    url='https://github.com/davidszotten/rabbitman',

    # Author details
    author='David Szotten',
    author_email='davidszotten@gmail.com',

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
        'Intended Audience :: Developers',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        # 'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        # 'Programming Language :: Python :: 3.2',
        # 'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],

    # What does your project relate to?
    # keywords='sample setuptools development',

    py_modules=['rabbitman'],

    install_requires=['requests'],

    extras_require = {
        'codegen': ['html2rst'],
    },

)
