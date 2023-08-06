=====================================
 Setup Kerberos based authentication
=====================================

CubicWeb_ 's authentication can be easily customized writing a
dedicated cube. This cube is such en example which has been developepd
to be used behind an Apache_ reverse proxy managing Kerberos authentication.

The assumption is that the CubicWeb_ application do trust the reverse
proxy behing which it lies.

This tutorial explains how to setup such a Kerberos_ based
authentication using this cube.


Prerequisites
=============

We assume that you already have a CubicWeb_ application running,
listening on the port 8080 of the machine ``myserver.mydomain`` (see
the tutorial_ to setup a simple CubicWeb_ application.)

We want to expose this application by the Apache_ server named
``webserver.mydomain`` under the name ``myblog.mydomain`` using an
`Apache virtual host`_ on a secured https connection.

We also assume you already have a working Kerberos_ infrastructure.


Setup Kerberos_
===============

Authentication on a service (here, a web server) using Kerberos
require to have an entry (a principal) in the Kerberos keys
database. For a web server, it is a principal like
``HTTP/webserver.mydomain@MYREALM``. So we need to create this
principal in the Kerberos key server. We also need the keytab file.
For example, creating such a principal for the `MIT Kerberos`_ server:

.. sourcode:: bash

   root@webserver:~# kadmin
   kadmin: addprinc HTTP/myblog.mydomain
   WARNING: no policy specified for HTTP/myblog.mydomain@MYREALM; defaulting to no policy
   Enter password for principal "HTTP/myblog.mydomain@MYREALM":
   Re-enter password for principal "HTTP/myblog.mydomain@MYREALM":
   Principal "HTTP/myblog.mydomain@MYREALM" created.

   kadmin:  ktadd -k /etc/apache2/myblog.keytab HTTP/myblog.mydomain
   Entry for principal HTTP/myblog.mydomain with kvno 4, encryption type AES-256 CTS mode with 96-bit SHA-1 HMAC added to keytab WRFILE:/etc/apache2/myblog.keytab.
   Entry for principal HTTP/myblog.mydomain with kvno 4, encryption type ArcFour with HMAC/md5 added to keytab WRFILE:/etc/apache2/myblog.keytab.
   Entry for principal HTTP/myblog.mydomain with kvno 4, encryption type Triple DES cbc mode with HMAC/sha1 added to keytab WRFILE:/etc/apache2/myblog.keytab.
   Entry for principal HTTP/myblog.mydomain with kvno 4, encryption type DES cbc mode with CRC-32 added to keytab WRFILE:/etc/apache2/myblog.keytab.

   kadmin:  quit

The keytab file has been saved in ``/etc/apache2/myblog.keytab``.

.. Warning:: The keytab of a principal can only be exported in the
   same ``kadmin`` session as the one used to create this former.


Setup Apache_
=============

Installation
------------

You need Apache_ with the module `mod_auth_kerb`_.

On a Debian_ system, one would type:

.. sourcecode:: bash

   root@webserver:~# apt-get install apache2 libapache2-mod-auth-kerb \
                     a2enmod rewrite ssl proxy_http proxy_balancer proxy \
                     headers auth_kerb


Configuration
-------------

Create a file for the virtual host named `/etc/apache2/sites-available/myblog`::

  <VirtualHost _default_:443>
         ServerName myblog.mydomain
         ServerAdmin webmaster@mydomain

         ErrorLog /var/log/apache2/error.log

         # Possible values include: debug, info, notice, warn, error, crit,
         # alert, emerg.
         LogLevel warn

         CustomLog /var/log/apache2/ssl_access.log combined

         #   SSL Engine Switch:
         #   Enable/Disable SSL for this virtual host.
         SSLEngine on

         BrowserMatch ".*MSIE.*" \
                 nokeepalive ssl-unclean-shutdown \
                 downgrade-1.0 force-response-1.0

     <Location />
         AuthType Kerberos
         AuthName "Cubicweb Myblog"
         # either use the KDC or keytabs
         KrbVerifyKDC On
         # Krb5Keytab /etc/apache2/apache.keytab

         # turn it on to enable Basic Auth failover if client
         # does not support kerberos auth.
         KrbMethodK5Passwd On

         KrbServiceName HTTP/myblog.mydomain@MYREALM
         KrbMethodNegotiate On
         KrbAuthRealms MYREALM
         # XXX miss arg to remove @MYREALM
         Require valid-user
         RequestHeader set X-REMOTE-USER %{remoteUser}e
     </Location>

     RewriteEngine On
     # Put Apache-specified username in headers:
     RewriteRule ^/(.*) http://myserver.mydomain:8080/https/$1 [L,P,E=remoteUser:%{LA-U:REMOTE_USER}]
  </VirtualHost>


Setup your blog app
===================

You now need to make your blog application use this ``trustedauth``
cube. For this, it is only a matter of telling your application cube
to use the ``trustedauth`` cube and to add a configration option to
your application ``all-in-one.conf`` file.


Modify your ``all-in-one.conf``
-------------------------------

Add the ``trustedauth-secret-key-file`` option in the ``trustedauth``
option group. The value should point to a file containing the secret key
that is used to secure the connection between the web part of the CubicWeb
application and the data part of the application (they may live on
different machines, communicating via pyro). Do not forget to create the
file. The secret key should be between 1 and 32 characters long.

.. sourcecode:: ini

   # ...

   [TRUSTEDAUTH]
   trustedauth-secret-key-file="/etc/application/secret-key"

   # ...


Modify your blog cube
---------------------

While your application is running, modify the components it depends on
and use:

.. sourcecode:: bash

   root@cwserver:~# cubicweb-ctl shell myblog
   entering the migration python shell
   just type migration commands or arbitrary python code and type ENTER to execute it
   type "exit" or Ctrl-D to quit the shell and resume operation
   >>> add_cube('trustedauth')
   >>> ^D
   root@cwserver:~#

That's it. You should be able to authenticate using your Kerberos
ticket on the application.

Configure your web browser
==========================

If you followed the instructions above but your web browser does not
trust your web server for Kerberos authentication, you should have a
BasicAuth authentication login dialog.

This is because we configured Apache to fallback into BasicAuth
(setting option `KrbMethodK5Passwd On` in the Apache config file of
the virtual host).

.. Note:: The asked password is your Kerberos password. Since your
   browser does not trust the web server, it refused to send him your
   Kerberos ticket. So it is Apache itself that tries to get a ticket
   for you (in fact for the Kerberos principal ``username@MYREALM``
   using the username and the password you entered in the auth form).

.. Warning:: Be sure to use SSL encrypted connection to the web
   server.


Telling your web browser to trust your web server depends on the
browser you are using.


Firefox
-------

Go to URL ``about:config``, filter entries on "uris", then modifye::

  network.negotiate-auth.trusted-uris: myblog.mydomain,other.trusted.sites

.. Note:: To get log data on the negotiate auth mechanism between your
   Firefox client and the server, you can do::

      export NSPR_LOG_MODULES=negotiateauth:5
      export NSPR_LOG_FILE=/tmp/moz.log
      firefox &
      tail -f /tmp/moz.log

   For a failed negociation due to missing Kerberos ticket::

      -1219798832[805d668]:   service = myblog.mydomain
      -1219798832[805d668]:   using negotiate-gss
      -1219798832[805d668]: entering nsAuthGSSAPI::nsAuthGSSAPI()
      -1219798832[805d668]: Attempting to load gss functions
      -1219798832[805d668]: entering nsAuthGSSAPI::Init()
      -1219798832[805d668]: nsHttpNegotiateAuth::GenerateCredentials() [challenge=Negotiate]
      -1219798832[805d668]: entering nsAuthGSSAPI::GetNextToken()
      -1219798832[805d668]: gss_init_sec_context() failed: Unspecified GSS failure.  Minor code may provide more information
      Unknown code H 1

   For a failed negociation due to the server ot being known by Kerberos::

      -1219798832[805d668]:   service = toto.logilab.fr
      -1219798832[805d668]:   using negotiate-gss
      -1219798832[805d668]: entering nsAuthGSSAPI::nsAuthGSSAPI()
      -1219798832[805d668]: entering nsAuthGSSAPI::Init()
      -1219798832[805d668]: nsHttpNegotiateAuth::GenerateCredentials() [challenge=Negotiate]
      -1219798832[805d668]: entering nsAuthGSSAPI::GetNextToken()
      -1219798832[805d668]: gss_init_sec_context() failed: Unspecified GSS failure.  Minor code may provide more information
      Server not found in Kerberos database

   An finally, a succeful one::

      -1250670912[b5517060]:   using REQ_DELEGATE
      -1250670912[b5517060]:   service = toto.logilab.fr
      -1250670912[b5517060]:   using negotiate-gss
      -1250670912[b5517060]: entering nsAuthGSSAPI::nsAuthGSSAPI()
      -1250670912[b5517060]: entering nsAuthGSSAPI::Init()
      -1250670912[b5517060]: nsHttpNegotiateAuth::GenerateCredentials_1_9_2() [challenge=Negotiate]
      -1250670912[b5517060]: entering nsAuthGSSAPI::GetNextToken()
      -1250670912[b5517060]:   leaving nsAuthGSSAPI::GetNextToken [rv=0]
      -1250670912[b5517060]:   Sending a token of length 1230


Chromium/Google chrome
----------------------

You have to start your browser with a command line option::

   me@mylaptop:~/chromium-browser --auth-server-whitelist="myblog.mydomain,*foobar.com"

For more informations, see the `chromium documentation`_


Go further
==========

It is possible to combine the Apache Kerberos authentication mechanism
with the ``authnz-ldap`` module, so the definition a valid user and
its access to a portion of the web site can be defined in an LDAP tree.

.. Note:: Using this configuration, the CubicWeb application has no
   idea of which LDAP group the user belongs to. Thus any restriction
   to a part of the web application using ``<Location /XXX>`
   statements must be carefully checked to be sure the restricted
   information is not available otherwise. Do not forget that it is
   very easy with CubicWeb to find alternate ways to access a piece of
   data.


.. _Apache: http://www.apache.org
.. _CubicWeb: http://www.cubicweb.org
.. _mod_auth_kerb: http://http://modauthkerb.sourceforge.net/
.. _tutorial: http://docs.cubicweb.org/tutorials/base/index.html
.. _Kerberos: http://en.wikipedia.org/wiki/Kerberos
.. _`Apache virtual host`: http://httpd.apache.org/docs/2.2/vhosts/
.. _`MIT Kerberos`: http://web.mit.edu/kerberos/
.. _`chromium documentation`: http://sites.google.com/a/chromium.org/dev/developers/design-documents/http-authentication .
.. _Debian: http://www.debian.org

