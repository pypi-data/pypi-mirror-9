from setuptools import setup, setuptools, find_packages

setup(
    name="stak",
    version="0.1.0a4",
    py_modules=['stak'],
    install_requires=["Click","PyYAML","zeroconf","jinja2<2.8,>=2.7", "honcho", "honcho[export]"],
    description='stak cli tool',
    long_description="Command line interface for the stak development platform",
    url='http://nextthing.co/stak.html',
    author='Next Thing Co.',
    author_email='Ahoyahoy@nextthing.co',
    license='MIT',
    packages=find_packages(exclude=['lib', 'include', 'bin','Stak.egg-info']),
    keywords='sample setuptools development',
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish (should match "license" above)
         'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
    entry_points='''
    [console_scripts]
    stak=stak:stak
    '''
)