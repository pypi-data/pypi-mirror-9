**********************************
birdhousebuilder.recipe.supervisor
**********************************

.. contents::

Introduction
************

``birdhousebuilder.recipe.supervisor`` is a `Buildout`_ recipe to configure `Supervisor`_ services with `Anaconda`_.
This recipe is used by the `Birdhouse`_ project. 

.. _`Buildout`: http://buildout.org/
.. _`Anaconda`: http://continuum.io/
.. _`Supervisor`: http://supervisord.org/
.. _`Birdhouse`: http://bird-house.github.io/


Usage
*****

The recipe requires that Anaconda is already installed. It assumes that the default Anaconda location is in your home directory ``~/anaconda``. Otherwise you need to set the ``ANACONDA_HOME`` environment variable or the Buildout option ``anaconda-home``.

The recipe will install the ``supervisor`` package from a conda channel in a conda enviroment named ``birdhouse``. The location of the birdhouse environment is ``.conda/envs/birdhouse``. It deploys a supervisor configuration of a given service. The configuration will be deployed in the birdhouse enviroment ``~/.conda/envs/birdhouse/etc/supervisor/conf.d/myapp.conf``. Supervisor can be started with ``~/.conda/envs/birdhouse/etc/init.d/supervisord start``.

The recipe depends on ``birdhousebuilder.recipe.conda``.

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

``supervisor-port``
   Buildout option (optional) to set the supervisor port. Default is 9001 (http://localhost:9001).

``program``
   The name of the supervisor service.

``command``
   The command to start the service.

``directory``
   The directory where the command is started.

Example usage
=============

The following example ``buildout.cfg`` installs a Supervisor configuration for ``myapp`` web application::

  [buildout]
  parts = myapp

  anaconda-home = /home/myself/anaconda
  supervisor-port = 9001

  [myapp]
  recipe = birdhousebuilder.recipe.supervisor
  program = myapp
  command = ${buildout:bin-directory}/gunicorn -b unix:///tmp/myapp.socket myapp:app 
  directory = /tmp




