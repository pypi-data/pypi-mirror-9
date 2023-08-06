==========
AryaLogger
==========

Use the SimpleAciUiLogServer and arya to convert UI REST API calls to ACI
Python SDK code.

Install
-------

Installation of AryaLogger depends on several other modules that are not part
of the Python standard library.  Here is a basic list of those modules:

1. acicobra - Not yet available on Pypi
2. arya - Not yet available on Pypi
3. SimpleAciUiLogServer - available on Pypi

Installing Dependancies
+++++++++++++++++++++++

The two difficult dependancies to install are aray and acicobra.

Installing acicobra
"""""""""""""""""""

If you have at least APIC version 1.0(3f) installed on your APIC, installation
of acicobra can be done by simply pointing pip at your APIC's cobra/_downloads
directory using the --find-links option using one of these two commands:

    pip install -Z --find-links http://apic/cobra/_downloads acicobra

Or:

    pip install -Z --find-links https://apic/cobra/_downloads acicobra

If your APIC has http disabled (the default), you must either use https or
enable http on the APIC.

If you have an older version of software on your APIC, you can either download
acicobra from the Cisco.com software download site (APIC specific contract
required to be tied to the Cisco.com id doing the download) or you can download
the acicobra egg from the APIC itself and rename it:

    https://developer.cisco.com/media/apicDcPythonAPI_v0.1/install.html

Installing arya
"""""""""""""""

Arya is currently (as of March 2015) contained in a subdirectory of the ACI
repo on github.  Installation of arya simply requires you to clone that
repository, change to the arya directory and run python against arya's setup.py
with the install option:

    cd some/directory/you/want/
    git clone https://github.com/datacenter/ACI.git
    cd ACI/arya
    python setup.py install

Installing AryaLogger
+++++++++++++++++++++

AryaLogger is available on pypi so installation is fairly straight forward:

    pip install AryaLogger

This should also pull in SimpleAciUiLogServer if you don't have it installed
already.

Run AryaLogger
--------------

There are two possible commands to run AryaLogger on your system.  You only need
to run one of these commands:

    aryalogger

Or:

    AryaLogger

There are additional options available that can be seen via the -h option:

    * -h: Help
    * -a/--apicip: The ip address or hostname of an APIC to help resolve which
      ip address to print when showing the server is started.
    * -po/--port: The port for the HTTP server to listen on - default is 8987
    * -l/--location: The URI path to listen for - default is apiinspector
    * -s/--sslport: The port for the HTTPS server to listen on - default is
      8443
    * -c/--cert: The certificate file to use for TLS/SSL negotiation.
    * -e/--exclude: There are three types of queries the GUI doe constantly
      to keep the session up or to request information to update the GUI.  This
      option allows you to selectively exlude these queries from the output.
      options are: 

      - subscriptionRefresh - Refreshes a subscription request for the GUI.
      - aaaRefresh - Refreshes the GUI connection to the APIC.
      - topInfo - Retrieves basic info from the APIC to update the GUI.

    * -r/--logrequests: Log the HTTP request along with the CobraSDK code.
    * -n/--nice-output: Pretty print any XML or JSON (has no affect currently
      in AryaLogger)
    * -i/--indent: The number of spaces to indent when pretty printing (has
      no affect currently in AryaLogger)

For HTTPS, AryaLogger does come with a default certificate file but it should
not be used for production.  Instead you should create your own certificate file
using openssl and pass it to the server:

    openssl req -new -x509 -keyout server.pem -out server.pem -days 36500 -nodes

Pass it in to AryaLogger using the -c/--cert option.

Setup your APIC
---------------

Setting up your APIC to send log messages to AryaLogger is very simple as well.
When you run AryaLogger it will output the addresses and ports it is listening
to:

    $ aryalogger
    serving at:
    http://10.1.1.100:8987/apiinspector
    https://10.1.1.100:8443/apiinspector

If you connect to the APIC graphical user interface (GUI) via http, take note of
the http URL otherwise if you connect to the GUI using https take note of
the https URL.

Use this URL in the 'Start Remote Logging' pop-up that is available from the 
'Welcome' menu at the top right of the GUI.

Once you have started remote logging to the URL provided by AryaLogger, when you
click around the APIC GUI you should see auto generated Cobra SDK code from
AryaLogger.

