*******************************
birdhousebuilder.recipe.mongodb
*******************************

.. contents::

Introduction
************

``birdhousebuilder.recipe.mongodb`` is a `Buildout`_ recipe to install and setup `MongoDB`_ with `Anaconda`_.
This recipe is used by the `Birdhouse`_ project. 


.. _`Buildout`: http://buildout.org/
.. _`Anaconda`: http://continuum.io/
.. _`MongoDB`: http://www.mongodb.org/
.. _`Supervisor`: http://supervisord.org/
.. _`Birdhouse`: http://bird-house.github.io/

Usage
*****

The recipe requires that Anaconda is already installed. It assumes that the default Anaconda location is in your home directory ``~/anaconda``. Otherwise you need to set the ``ANACONDA_HOME`` environment variable or the Buildout option ``anaconda-home``.

It installs the ``mongodb`` package from a conda channel in a conda environment named ``birdhouse``. The location of the birdhouse environment is ``.conda/envs/birdhouse``. It setups a `MongoDB`_ database in ``~/.conda/envs/birdhouse/var/lib/mongodb``. It deploys a `Supervisor`_ configuration for MongoDB in ``~/.conda/envs/birdhouse/etc/supervisor/conf.d/mongodb.conf``. Supervisor can be started with ``~/.conda/envs/birdhouse/etc/init.d/supervisor start``.

The recipe depends on ``birdhousebuilder.recipe.conda`` and ``birdhousebuilder.recipe.supervisor``.

Supported options
=================

The recipe supports the following options:

The recipe supports the following options:

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

The following example ``buildout.cfg`` installs MongoDB with Anaconda::

  [buildout]
  parts = myapp_mongodb

  anaconda-home = /opt/anaconda

  [myapp_mongodb]
  recipe = birdhousebuilder.recipe.mongodb


