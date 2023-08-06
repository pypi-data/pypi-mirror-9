******************************
birdhousebuilder.recipe.tomcat
******************************

.. contents::

Introduction
************

``birdhousebuilder.recipe.tomcat`` is a `Buildout`_ recipe to install ``Apache Tomcat`` application server with `Anaconda`_. This recipe is used by the `Birdhouse`_ project. 

.. _`Buildout`: http://buildout.org/
.. _`Anaconda`: http://www.continuum.io/
.. _`Supervisor`: http://supervisord.org/
.. _`Apache Tomcat`: https://tomcat.apache.org/
.. _`Birdhouse`: http://bird-house.github.io/

Usage
*****

The recipe requires that Anaconda is already installed. It assumes that the default Anaconda location is in your home directory ``~/anaconda``. Otherwise you need to set the ``ANACONDA_HOME`` environment variable or the Buildout option ``anaconda-home``.

It installs the ``apache-tomcat`` package from a conda channel in a conda enviroment named ``birdhouse``. The location of the birdhouse environment is ``.conda/envs/birdhouse``. It deploys a `Supervisor`_ configuration in ``~/.conda/envs/birdhouse/etc/supervisor/conf.d/tomcat.conf``. Supervisor can be started with ``~/.conda/envs/birdhouse/etc/init.d/supervisord start``.

By default Tomcat will be available on http://localhost:8080/thredds.

The recipe depends on ``birdhousebuilder.recipe.conda`` and ``birdhousebuilder.recipe.supervisor``.

Supported options
=================

This recipe supports the following options:

``anaconda-home``
   Buildout option with the root folder of the Anaconda installation. Default: ``$HOME/anaconda``.
   The default location can also be set with the environment variable ``ANACONDA_HOME``. Example::
     export ANACONDA_HOME=/opt/anaconda

   Search priority is:
   1. ``anaconda-home`` in ``buildout.cfg``
   2. ``$ANACONDA_HOME``
   3. ``$HOME/anaconda``

Example usage
=============

The following example ``buildout.cfg`` installs ``tomcat`` as a Supervisor service::

  [buildout]
  parts = tomcat

  anaconda-home = /home/myself/anaconda

  [tomcat]
  recipe = birdhousebuilder.recipe.tomcat



