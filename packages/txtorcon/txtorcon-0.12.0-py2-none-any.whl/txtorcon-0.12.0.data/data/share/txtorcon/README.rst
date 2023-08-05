README
======

Documentation at https://txtorcon.readthedocs.org

.. image:: https://travis-ci.org/meejah/txtorcon.png?branch=master
    :target: https://www.travis-ci.org/meejah/txtorcon

.. image:: https://coveralls.io/repos/meejah/txtorcon/badge.png
    :target: https://coveralls.io/r/meejah/txtorcon

.. image:: http://api.flattr.com/button/flattr-badge-large.png
    :target: http://flattr.com/thing/1689502/meejahtxtorcon-on-GitHub


quick start
-----------

For the impatient, there are two quick ways to install this::

   $ pip install txtorcon

... or, if you checked out or downloaded the source::

   $ python setup.py install

To avoid installing, you can just add the base of the source to your
PYTHONPATH::

   $ export PYTHONPATH=`pwd`:$PYTHONPATH

Then, you will want to explore the examples. Try "python
examples/stream\_circuit\_logger.py" for instance.

On Debian testing (jessie), or with wheezy-backports (big thanks to
Lunar^ for all his packaging work) you can install easily::

    $ apt-get install python-txtorcon

You may also like `this asciinema demo <http://asciinema.org/a/5654>`_
for an overview.

Tor configuration
-----------------

You'll want to have the following options on in your ``torrc``::

   CookieAuthentication 1
   CookieAuthFileGroupReadable 1

If you want to use unix sockets to speak to tor::

   ControlSocketsGroupWritable 1
   ControlSocket /var/run/tor/control

The defaults used by :meth:`txtorcon.build_local_tor_connection` will
find a Tor on ``9051`` or ``/var/run/tor/control``


overview
--------

txtorcon is a Twisted-based asynchronous Tor control protocol
implementation. Twisted is an event-driven networking engine written
in Python and Tor is an onion-routing network designed to improve
people's privacy and anonymity on the Internet.

The main abstraction of this library is txtorcon.TorControlProtocol
which presents an asynchronous API to speak the Tor client protocol in
Python. txtorcon also provides abstractions to track and get updates
about Tor's state (txtorcon.TorState) and current configuration
(including writing it to Tor or disk) in txtorcon.TorConfig, along
with helpers to asynchronously launch slave instances of Tor including
Twisted endpoint support.

txtorcon runs all tests cleanly on:

-  Debian "squeeze", "wheezy" and "jessie"
-  OS X 10.4 (naif)
-  OS X 10.8 (lukas lueg)
-  OS X 10.9 (kurt neufeld)
-  Fedora 18 (lukas lueg)
-  FreeBSD 10 (enrique fynn) (**needed to install "lsof"**)
-  RHEL6
-  Reports from other OSes appreciated.

If instead you want a synchronous (threaded) Python controller
library, check out Stem at https://stem.torproject.org/

quick implementation overview
-----------------------------

txtorcon provides a class to track Tor's current state -- such as
details about routers, circuits and streams -- called
txtorcon.TorState and an abstraction to the configuration values via
txtorcon.TorConfig which provides attribute-style accessors to Tor's
state (including making changes). txtorcon.TorState provides
txtorcon.Router, txtorcon.Circuit and txtorcon.Stream objects which
implement a listener interface so client code may receive updates (in
real time) including Tor events.

txtorcon uses **trial for unit-tests** and has 96% test-coverage --
which is not to say I've covered all the cases, but nearly all of the
code is at least exercised somehow by the unit tests.

Tor itself is not required to be running for any of the tests. There are
no integration tests. ohcount claims around 2000 lines of code for the
core bit; around 4000 including tests. About 37% comments in the
not-test code.

dependencies / requirements
---------------------------

- `twisted <http://twistedmatrix.com>`_: txtorcon should work with any
   Twisted 11.1.0 or newer. I am working against Twisted 13.2.0 on
   Debian with Python 2.7.6. Twisted 12 works fine as well. Twisted
   does not yet support Python 3.

-  `GeoIP <https://www.maxmind.com/app/python>`_: **optional** provides location
   information for ip addresses; you will want to download GeoLite City
   from `MaxMind <https://www.maxmind.com/app/geolitecity>`_ or pay them
   for more accuracy. Or use tor-geoip, which makes this sort-of
   optional, in that we'll query Tor for the IP if the GeoIP database
   doesn't have an answer. It also does ASN lookups if you installed that MaxMind database.

-  `python-ipaddr <http://code.google.com/p/ipaddr-py/>`_: **optional**.
   Google's IP address manipulation code.

-  development: `Sphinx <http://sphinx.pocoo.org/>`_ if you want to build the
   documentation. In that case you'll also need something called
   ``python-repoze.sphinx.autointerface`` (at least in Debian) to build
   the Interface-derived docs properly.

-  development: `coverage <http://nedbatchelder.com/code/coverage/>`_ to
   run the code-coverage metrics

-  optional: GraphViz is used in the tests (and to generate state-machine
   diagrams, if you like) but those tests are skipped if "dot" isn't
   in your path

.. BEGIN_INSTALL
In any case, on a `Debian <http://www.debian.org/>`_ wheezy, squeeze or
Ubuntu system, this should work::

    apt-get install -y python-setuptools python-twisted python-ipaddr python-geoip graphviz tor
    apt-get install -y python-sphinx python-repoze.sphinx.autointerface python-coverage # for development

.. END_INSTALL

Using pip this would be::

    pip install Twisted ipaddr pygeoip
    pip install GeoIP Sphinx repoze.sphinx.autointerface coverage  # for development

or::

    pip install -r requirements.txt
    pip install -r dev-requirements.txt

or for the bare minimum::

    pip install Twisted  # will install zope.interface too

documentation
-------------

It is likely that you will need to read at least some of
`control-spec.txt <https://gitweb.torproject.org/torspec.git/blob/HEAD:/control-spec.txt>`_
from the torspec git repository so you know what's being abstracted by
this library.

Run "make doc" to build the Sphinx documentation locally, or rely on
ReadTheDocs https://txtorcon.readthedocs.org which builds each tagged
release and the latest master.

There is also a directory of examples/ scripts, which have inline
documentation explaining their use. You may also use pydoc::

    pydoc txtorcon.TorControlProtocol
    pydoc txtorcon.TorState
    pydoc txtorcon.TorConfig

...for the main classes. If you're using TorState, you will also be
interested in the support classes for it::

    pydoc txtorcon.Circuit
    pydoc txtorcon.Stream
    pydoc txtorcon.Router
    pydoc txtorcon.AddrMap

There are also Zope interfaces for some things, if you wish to listen
for events for your own purposes (the best example of the use of these
being TorState itself)::

    txtorcon.ITorControlProtocol
    txtorcon.IStreamAttacher
    txtorcon.ICircuitListener
    txtorcon.IStreamListener

For launching Tor and Twisted integration, you will want to look at::

    txtorcon.launch_tor (in torconfig.py)
    txtorcon.TCPHiddenServiceEndpoint (in torconfig.py)
    txtorcon.TorProtocolFactory (in torcontrolprotocol.py)
    txtorcon.build_tor_connection (in torstate.py)
    txtorcon.build_local_tor_connection (in torstate.py)

IStreamAttacher affects Tor's behaviour, allowing one to customize how
circuits for particular streams are selected. You can build your own
circuits via ITorControlProtocol.build\_circuit(). There is an example
of this called custom\_stream\_attacher.py which builds (or uses)
circuits exiting in the same country as the address to which the
stream is connecting.


contact information
-------------------

For novelty value, the Web site (with built documentation and so forth)
can be viewed via Tor at https://timaq4ygg2iegci7.onion although the
code itself is hosted via git::

    torsocks git clone git://timaq4ygg2iegci7.onion/txtorcon.git

or::

    git clone git://github.com/meejah/txtorcon.git

You may contact me via ``meejah at meejah dot ca`` with GPG key
`0xC2602803128069A7
<http://pgp.mit.edu:11371/pks/lookup?op=get&search=0xC2602803128069A7>`_
or see ``meejah.asc`` in the repository. The fingerprint is ``9D5A
2BD5 688E CB88 9DEB CD3F C260 2803 1280 69A7``.

It is often possible to contact me as ``meejah`` in #tor-dev on `OFTC
<http://www.oftc.net/oftc/>`_ but be patient for replies (I do look at
scrollback, so putting "meejah: " in front will alert my client).

More conventionally, you may get the code at GitHub and documentation
via ReadTheDocs:

-  https://github.com/meejah/txtorcon
-  https://txtorcon.readthedocs.org

Please do **use the GitHub issue-tracker** to report bugs. Patches,
pull-requests, comments and criticisms are all welcomed and
appreciated.
