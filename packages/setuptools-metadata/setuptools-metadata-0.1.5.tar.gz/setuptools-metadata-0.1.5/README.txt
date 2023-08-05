
setuptools-metadata - Adds metadata command to setup.py

Using custom_metadata in setup call

    from setuptools import setup
    setup(
        name='spam',
        custom_metadata={
            'x_str': 'bla',
            'x_int': 23,
            'x_list': ['a', 'b', 'c']})

Using 'setup.py metadata'

        ./setup.py metadata --key=install_requires
        pygraphviz
        lxml
        another-package

    This prints out the 'install_requires' setup keyword argument.

    If it can't find the requested key, it will also search the custom_metadata dict:

        ./setup.py metadata --key=x_str
        bla

        ./setup.py metadata --key=x_int
        23

        ./setup.py metadata --key=x_list
        a
        b
        c

Installing

    Install it into your system Python like this:

        sudo pip install setuptools-metadata
