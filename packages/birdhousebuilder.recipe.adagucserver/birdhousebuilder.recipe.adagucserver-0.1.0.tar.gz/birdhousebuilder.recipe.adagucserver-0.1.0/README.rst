************************************
birdhousebuilder.recipe.adagucserver
************************************

.. contents::

Introduction
************

``birdhousebuilder.recipe.adagucserver`` is a `Buildout`_ recipe to install and configure `Adagucserver`_ with `Anaconda`_. `Adagucserver`_ is an implementation of a `Web Mapping Service`_ (WMS). ``Adagucserver`` will be deployed as a `Supervisor`_ service and is available on a `Nginx`_ web server. 

This recipe is used by the `Birdhouse`_ project. 



.. _`Buildout`: http://buildout.org/
.. _`Anaconda`: http://continuum.io/
.. _`Supervisor`: http://supervisord.org/
.. _`Nginx`: http://nginx.org/
.. _`Adagucserver`: https://dev.knmi.nl/projects/adagucserver/wiki
.. _`Web Processing Service`: https://en.wikipedia.org/wiki/Web_Processing_Service
.. _`Birdhouse`: http://bird-house.github.io/


Usage
*****

The recipe requires that Anaconda is already installed. It assumes that the default Anaconda location is in your home directory ``~/anaconda``. Otherwise you need to set the ``ANACONDA_HOME`` environment variable or the Buildout option ``anaconda-home``.

It installs the ``adagucserver`` package from a conda channel in a conda environment named ``birdhouse``. The location of the birdhouse environment is ``.conda/envs/birdhouse``. It deploys a `Supervisor`_ configuration for ``Adagucserver`` in ``~/.conda/envs/birdhouse/etc/supervisor/conf.d/adagucserver.conf``. Supervisor can be started with ``~/.conda/envs/birdhouse/etc/init.d/supervisor start``.

The recipe will install the ``nginx`` package from a conda channel and deploy a Nginx site configuration for ``Adagucserver``. The configuration will be deployed in ``~/.conda/envs/birdhouse/etc/nginx/conf.d/adagucserver.conf``. Nginx can be started with ``~/.conda/envs/birdhouse/etc/init.d/nginx start``.

By default ``Adagucserver`` will be available on http://localhost:9002?service=WMS&version=1.3.0&request=GetCapabilities.

The recipe depends on ``birdhousebuilder.recipe.conda``, ``birdhousebuilder.recipe.supervisor`` and ``birdhousebuilder.recipe.nginx``.

Supported options
=================

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

The following example ``buildout.cfg`` installs ``Adagucserver`` with Anaconda::

  [buildout]
  parts = adaguc

  anaconda-home = /home/myself/anaconda

  [adaguc]
  recipe = birdhousebuilder.recipe.adagucserver

After installing with Buildout start the ``Adagucserver`` service with::

  $ cd /home/myself/.conda/envs/birdhouse
  $ etc/init.d/supervisord start  # start|stop|restart
  $ etc/init.d/nginx start        # start|stop|restart
  $ bin/supervisorctl status      # check that adagucserver is running
  $ less var/log/adaguc.log  # check log file

Open your browser with the following URL:: 

  http://localhost:9002?service=WMS&version=1.3.0&request=GetCapabilities





