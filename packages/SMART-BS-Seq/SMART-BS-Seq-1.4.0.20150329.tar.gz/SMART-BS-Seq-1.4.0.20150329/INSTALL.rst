======================
INSTALL Guide For SMART-BS-Seq
======================
Time-stamp: <2014-08-01 22:17:24 Hongbo Liu>

Please check the following instructions to complete your installation.

Prerequisites
=============

Python version must be equal to *2.7* to run SMART-BS-Seq. I recommend
using the version *2.7.6*.

scipy (>=0.13) are required to run SMART-BS-Seq. 


.. _scipy: http://www.scipy.org/Download

Easy installation through PyPI
==============================

The easiest way to install SMART-BS-Seq is through PyPI system. Get pip_ if
it's not available in your system. *Note* if you have already
installed numpy and scipy system-wide, you can use ```virtualenv
--system-site-packages``` to let your virtual Python environment have
access to system-wide numpy and scipy libraries so that you don't need
to install them again.  

Then under command line, type ```pip install SMART-BS-Seq```. PyPI will
install Numpy and Scipy automatically if they are absent.  

To upgrade SMART-BS-Seq, type ```pip install -U SMART-BS-Seq```. It will check
currently installed SMART-BS-Seq, compare the version with the one on PyPI
repository, download and install newer version while necessary.

Note, if you do not want pip to fix dependencies. For example, you
already have a workable Scipy and Numpy, and when 'pip install -U
SMART-BS-Seq', pip downloads newest Scipy and Numpy but unable to compile and
install them. This will fail the whole installation. You can pass
'--no-deps' option to pip and let it skip all dependencies. Type
```pip install -U --no-deps SMART-BS-Seq```.

.. _pip: http://www.pip-installer.org/en/latest/installing.html

Install from source
===================

SMART-BS-Seq uses Python's distutils tools for source installations. To
install a source distribution of SMART-BS-Seq, unpack the distribution tarball
and open up a command terminal. Go to the directory where you unpacked
SMART-BS-Seq, and simply run the install script::

 $ python setup.py install

By default, the script will install python library and executable
codes globally, which means you need to be root or administrator of
the machine so as to complete the installation. Please contact the
administrator of that machine if you want their help. If you need to
provide a nonstandard install prefix, or any other nonstandard
options, you can provide many command line options to the install
script. Use the ¨Chelp option to see a brief list of available options::

 $ python setup.py --help

For example, if I want to install everything under my own HOME
directory, use this command::

 $ python setup.py install --prefix /home/hbliu/

Configure enviroment variables
==============================

After running the setup script, you might need to add the install
location to your ``PYTHONPATH`` and ``PATH`` environment variables. The
process for doing this varies on each platform, but the general
concept is the same across platforms.

PYTHONPATH
~~~~~~~~~~

To set up your ``PYTHONPATH`` environment variable, you'll need to add the
value ``PREFIX/lib/pythonX.Y/site-packages`` to your existing
``PYTHONPATH``. In this value, X.Y stands for the major¨Cminor version of
Python you are using (such as 2.7 ; you can find this with
``sys.version[:3]`` from a Python command line). ``PREFIX`` is the install
prefix where you installed SMART-BS-Seq. If you did not specify a prefix on
the command line, SMART-BS-Seq will be installed using Python's sys.prefix
value.

On Linux, using bash
 $ export PYTHONPATH=/usr/local/lib/python2.7/dist-packages/SMART:$PYTHONPATH

Using Windows, you need to open up the system properties dialog, and
locate the tab labeled Environment. Add your value to the ``PYTHONPATH``
variable, or create a new ``PYTHONPATH`` variable if there isn't one
already.

PATH
~~~~

Just like your ``PYTHONPATH``, you'll also need to add a new value to your
PATH environment variable so that you can use the SMART-BS-Seq command line
directly. Unlike the ``PYTHONPATH`` value, however, this time you'll need
to add ``PREFIX/bin`` to your PATH environment variable. The process for
updating this is the same as described above for the ``PYTHONPATH``
variable::

 $ export PATH=/usr/local/bin:$PATH

--
Hongbo Liu <hongbo919@gmail.com>

