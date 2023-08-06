ecmcli - CLI for Cradlepoint ECM
===========

Installation provides a command line utility (ecm) which can be used to
interact with Cradlepoint's ECM service.  Commands are subtasks of the
ECM utility.  The full list of subtasks are visible by running 'ecm --help'.


Walkthrough Video
--------
[![Walkthrough Video](http://share.gifyoutube.com/y7nLaZ.gif)](http://www.youtube.com/watch?v=fv4dWL03zPk)


Requirements
--------

* Syndicate Python Library
* humanize Python Library
* ECM Login


Installation
--------

    python3 ./setup.py build
    python3 ./setup.py install


Compatibility
--------

* Python 3.4+


Mac OSX Notes
--------

I feel compelled to make a note about OSX as I've decided to only support
Python 3.4+ for this tool.  In my experience, using Python 3 as installed by
Homebrew and setuptools as installed by pip, a usable PATH is not provided
and/or symlinking behavior for python3 setuptools scripts is not handled.

To work around this I'm simply adding the 'bin' directory used for the Python
3 framework to my PATH variable, a la..

```shell
PATH=$PATH:/usr/local/Cellar/python3/3.4.2_1/Frameworks/Python.framework/Versions/3.4/bin
```

I welcome someone explaining to me a better solution.


Example Usage
--------

**Viewing Device Logs**

```shell
$ ecm logs
```


**Monitoring WAN Rates**

```shell
$ ecm wanrate
 Home 2100(24400): [device is offline],          Home Router(138927): 68.1 KiB,                Home 1400(669): 0 Bytes
 Home 2100(24400): [device is offline],          Home Router(138927): 43.6 KiB,                Home 1400(669): 0 Bytes
 Home 2100(24400): [device is offline],          Home Router(138927): 40.6 KiB,                Home 1400(669): 0 Bytes
 Home 2100(24400): [device is offline],          Home Router(138927): 49.7 KiB,                Home 1400(669): 0 Bytes
```


**Rebooting a specific router**

```shell
$ ecm reboot --routers 669
Rebooting:
    Home 1400 (669)
```
