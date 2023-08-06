=========
Packaging
=========

Automated build, packaging and deployment
===========================================

For Windows, make_package.bat is provided to create sdist and windows binary as well as document.



Create .zip package
====================

.. code-block:: console

  python setup.py sdist

Archived packages are created as dist/marlowe_ui-(version).zip .
These packages can be installed using easy_install (a part of setuptools http://pypi.python.org/pypi/setuptools) or pip (http://pypi.python.org/pypi/pip)

with easy_install

.. code-block:: console

  easy_install <path to .zip>

with pip

.. code-block:: console

  pip install <path to .zip>

Create w32 standalone package
=============================

cs_Freeze (http://cx-freeze.sourceforge.net/) and pywin32 (http://sourceforge.net/projects/pywin32/) should be set up to build w32 standalone package

.. code-block:: console

  python setup_cx.py bdist_msi

Standalone package is created as dist/marlowe_ui-(version)-win32.msi or -amd64.msi . 

