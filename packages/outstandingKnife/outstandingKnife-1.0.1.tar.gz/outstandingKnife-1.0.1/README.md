# outstandingKnife

## Overview

This is a simple little project which allows you to create github+pypi registered projects very very easily
It gives you a basic framework for setting out your code complete with argument parsing and setup.py working out of the box

## Installation

You should have a github account and an pypi account. Also you should install [hub](hub.github.com)

Then it should be as simple as:

    pip install outstandingKnife

## Example usage

To create a project called 'PersistentIcyNeptune', go to where you usually like to develop your software and type:

    outstandingKnife PersistentIcyNeptune

The tool will print more instructions as it runs. Follow these to set up the repo on github and pypi.

To install your new project, cd into the PersistentIcyNeptune directory and type:

    sudo python setup.py install --prefix=DIRNAME

You can omit the 'sudo' if you are installing locally using '--prefix=DIRNAME' and you can omit the prefix if you want to install the project system-wide.
If the install is system wide then it should all work.
You can test it by typing:

    persistentncyneptune

For a local install you will have to add DIRNAME/bin to your PATH and DIRNAME/lib/python2.7/site-packages to your PYTHONPATH. Of course you should adjust for different python versions.

## Help

If you experience any problems using outstandingKnife, open an [issue](https://github.com/minillinim/outstandingKnife/issues) on GitHub and tell us about it.

## Licence

Project home page, info on the source tree, documentation, issues and how to contribute, see http://github.com/minillinim/outstandingKnife

## Copyright

Copyright (c) 2013 Michael Imelfort. See LICENSE.txt for further details.
