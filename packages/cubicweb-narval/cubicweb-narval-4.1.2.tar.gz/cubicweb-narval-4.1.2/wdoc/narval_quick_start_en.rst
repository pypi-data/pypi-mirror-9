====================
 Narval Quick Start
====================

Narval is a cubicweb-based framework to run automated tests. It
consists of 2 parts:

- the narval cube which implements the schema and some web UIs to
  create, configure and run test campaigns, and

- the narval bot which waits for jobs to execute. It polls the
  cubicweb application for new tasks to run (called Plans in narval's
  jargon), and executes them when some are waiting for execution.

The narval bot communicates with the web application by doing HTTP(S)
requests.

As of itself, Narval is limited in features; it is generally not used
alone, but instead via a higher-level testing platform like
Apycot_. However, let's get started with Narval and make it run simple
Python code.

.. _Apycot: http://www.cubcweb.org/project/apycot


The best way to install Narval is to install it via the provided
Debian packages. So the simplest way to play with it is to start a
couple of virtual machines or cloud instances (it's possible to run
everything on the same machine but in real life, it's often a good
idea to have a dedicated server to run tests, so let's do this).


First, let's create a couple of wheezy VMs on an OpenStack cloud,
narvalweb and narvalbot:

.. sourcecode:: bash

  user@perseus:~$ nova boot narvalbot --flavor m1.small --image debian-wheezy-x86_64 --key_name main
  user@perseus:~$ nova add-floating-ip narvalbot 172.17.16.42
  user@perseus:~$ nova boot narvalweb --flavor m1.small --image debian-wheezy-x86_64 --key_name main
  user@perseus:~$ nova add-floating-ip narvalbot 172.17.16.94

On `narvalweb`, we will install everything required to run a cubicweb
web application using the `cubicweb-narval` cube:

.. sourcecode:: bash

  user@perseus:~$ ssh root@172.17.16.94
  root@narvalweb:~# echo "deb http://download.logilab.org/acceptance wheezy/" > /etc/apt/sources.list.d/logilab.list
  root@narvalweb:~# wget -q http://www.logilab.fr/logilab-dists-key.asc  -O - | apt-key add -
  root@narvalweb:~# apt-get update
  root@narvalweb:~# apt-get install cubicweb cubicweb-narval
  [...]
  Do you want to continue [Y/n]? Y
  [...]
  root@narvalweb:~#

Now, we need to create a cubicweb instance (the application) of the
`cubicweb-narval` cube:

.. sourcecode:: bash

  root@narvalweb:~# cubicweb-ctl create narval narvalapp
  Creating the instance narvalapp
  -------------------------------
  -> created directory /etc/cubicweb.d/narvalapp

  Configuring the instance (all-in-one.conf)
  ------------------------------------------

  Configuring the repository
  --------------------------

  Configuring the sources
  -----------------------
  :db-driver:
  database driver (postgres, mysql, sqlite, sqlserver2005)
  (default: postgres): sqlite
  :db-name:
  path to the sqlite database
  (default: /var/lib/cubicweb/instances/narvalapp/narvalapp.sqlite):

  :login:
  cubicweb manager account's login (this user will be created)
  (default: admin): admin
  :password:
  cubicweb manager account's password
  (required): *****
  confirm: *****
  -> set permissions to 0600 for /etc/cubicweb.d/narvalapp/sources

  Generic web configuration
  -------------------------
  :port: 8080
  http server port number (default to 8080)
  :
  Allow anonymous access ? [y/N]: N
  -> generated config /etc/cubicweb.d/narvalapp/all-in-one.conf
  -> created directory /etc/cubicweb.d/narvalapp/i18n
  -> compiling message catalogs to /etc/cubicweb.d/narvalapp/i18n
  -> created directory /etc/cubicweb.d/narvalapp/i18n/fr/LC_MESSAGES
  -> created directory /etc/cubicweb.d/narvalapp/i18n/en/LC_MESSAGES
  -> no need to create existing directory /var/lib/cubicweb/instances/narvalapp
  -> created directory /var/lib/cubicweb/instances/narvalapp/backup

  -> creation done for /etc/cubicweb.d/narvalapp

  Run db-create to create the system database ? [Y/n]: Y
  -> connecting to sqlite database /var/lib/cubicweb/instances/narvalapp/narvalapp.sqlite -> database for instance narvalapp created and necessary extensions installed.

  Run db-init to initialize the system database ? [Y/n]: Y

  Initializing the system database
  --------------------------------
  /usr/lib/pymodules/python2.7/yams/schema.py:198: Warning: [yams 0.38] no targettype specified and there are several relation definitions for rtype wf_info_for: ['CWUser', 'Plan']. Yet you get the first rdef.
    rschema = self.rdef(name)
  -> creating tables  [====================]
  -> inserting default user and default groups.
  /usr/lib/pymodules/python2.7/yams/schema.py:198: Warning: [yams 0.38] no targettype specified and there are several relation definitions for rtype wf_info_for: ['Plan', 'CWUser']. Yet you get the first rdef.
    rschema = self.rdef(name)
  -> storing the schema in the database  [=================== ]
  -> database for instance narvalapp initialized.
  Enter another source ? [y/N]: N
  root@narvalweb:~# cubicweb-ctl status
  [narvalapp-all-in-one] doesn't seem to be running

Before starting the web app, we need to setup the `base-url` config
option:

.. sourcecode:: bash

  root@narvalweb:~# cat /etc/cubicweb.d/narvalapp/all-in-one.conf | grep -C 1 base-url
  # web server root url
  #base-url=
  root@narvalweb:~# sed -i -e "s&#base-url=&base-url=http://172.17.16.94:8080/&" /etc/cubicweb.d/narvalapp/all-in-one.conf /etc/cubicweb.d/narvalapp/all-in-one.conf
  root@narvalweb:~# # or use vi if you prefer

Now we are ready to start the cubicweb application:

.. sourcecode:: bash

  root@narvalweb:~# cubicweb-ctl start narvalapp
  instance narvalapp started
  root@narvalweb:~#

Ok now we have a running cubicweb application which can be browsed on
`http://172.17.16.94:8080` (172.17.16.94 being the public IP of the
`narvalweb` cloud machine). The first thing to do is to login as
`narval` user and change the password.

The `narval` user also needs a authentication token (``AuthToken``) so
the narval bot can connect using signed requests::

  http://172.17.16.94:8080/add/AuthToken

Fill the form by choosing a name for the token, and ensure the token
is enabled. Write down the generated secret, since it's required for
the next step.

Now, on `narvalbot`, we need to install the `narval-bot` package:

.. sourcecode:: bash

  root@narvalbot:~# echo "deb http://download.logilab.org/acceptance wheezy/" > /etc/apt/sources.list.d/logilab.list
  root@narvalbot:~# wget -q http://www.logilab.fr/logilab-dists-key.asc  -O - | apt-key add -
  root@narvalbot:~# apt-get update
  root@narvalbot:~# apt-get install narval-bot
  [...]
  Do you want to continue [Y/n]? Y
  [...]
  root@narvalbot:~#

the setup some configuration options by editing the
`/etc/narval/narval-cw-sources.ini` file ; replace the example
configuration by::

  [narvalapp]
  url=http://172.17.16.94:8080/
  token_id=The token name
  secret=<generated secret you wrote down>

Note that the section name can be anything, but it's a good idea to
give the name of the web application.

Let's try to run the bot and see if it can connect to the web application:

.. sourcecode:: bash

  root@narvalbot:~# service narval restart
  [ ok ] Stopping Narval bot server: narval.
  [ ok ] Starting Narval bot server: narval.
  root@narvalbot:~# tail /var/log/narval/narval.log
  2013-10-28 23:17:44 - (narval.bot) INFO: installing signal handlers
  2013-10-28 23:17:44 - (narval.bot) INFO: get pending plan from narvalapp
  2013-10-28 23:17:44 - (requests.packages.urllib3.connectionpool) INFO: Starting new HTTP connection (1): 172.17.16.94
  root@narvalbot:~#

Looks good (connection seems successful, no error message).

Ok we are almost done. The last step is to create a `Recipe` and start
it to see if our narval bot will take care of it.

In the web application create a new `Recipe` entity, eg. by visiting::

  http://172.17.16.94:8080/add/Recipe

Pick up a name for it, and fill the `script` section with something like:

.. sourcecode:: python

  print "I am running!!!"

  import sys
  print "sys.path=", sys.path


and validate. You should now see your newly created `Recipe` with a
"start plan" button at the bottom of the page. Click it. You should be
redirected to the automatically created `Plan` (a `Plan` is the entity
managing the execution process of a `Recipe`). Wait a little bit (the
max time you have to wait can be configured in
``narvalbot:/etc/narval/narval.ini``) then reload the page. An
execution report should be available in the page. Set the debug level
to 'Debug' to see your print statements.

That's it, you have a working narval platform.

As stated above, it's mainly designed as a low-level engine to power
more advanced tools like Apycot_, so if you want to see more, take a
look at Apycot_!


