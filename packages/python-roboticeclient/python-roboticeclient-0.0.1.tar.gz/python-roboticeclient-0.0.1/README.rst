
=======================
Robotice Control Client
=======================

Python client for https://github.com/robotice/robotice-control and https://github.com/robotice/robotice

Installation
------------------------

.. code-block:: bash

	pip install python-roboticeclient

	roboticeclient 
	DEBUG (client) GET - http://127.0.0.1:8004/device - {}
	INFO (connectionpool) Starting new HTTP connection (1): 127.0.0.1
	DEBUG (connectionpool) "GET /device HTTP/1.1" 200 839
	{u'control-single.robotice.dev.mjk.robotice.cz': {u'actuators': {u'dummy1': {u'device': u'dummy', u'metric': u'random', u'type': u'dummy', u'port': u'bcm18'}}, u'sensors': {u'dummy1': {u'device': u'dummy', u'metric': u'random', u'type': u'dummy', u'port': u'bcm18'}, u'hygro_case1_do': 

	roboticeclient -h
	usage: robotice [-t TYPE] [--host HOST] [-p PORT] [-a ACTION] [-c COLLECTION]
	                [--version] [-d] [-v]
	Optional arguments:
	  -t TYPE, --type TYPE  type robotice or control
	  --host HOST           host
	  -p PORT, --port PORT  port
	  -a ACTION, --action ACTION
	                        list, get, create, update
	  -c COLLECTION, --collection COLLECTION
	                        collection


Usage as Robotice Client
------------------------

.. code-block:: python

	from roboticeclient import Client

	# listings

	client = Client(port=8004, host="127.0.0.1")

	print client.devices.list()
	print client.plans.list()
	print client.systems.list()
	print client.actions.list()

	client.actions.save(id, action)


Usage as Robotice Control Client !
----------------------------------

.. code-block:: python

	from roboticeclient import Client

	# listings

	client = Client(type="control", port=9753, host="127.0.0.1")

	print client.devices.list()
	print client.plans.list()
	print client.systems.list()
	print client.actions.list()

	client.actions.save(id, action)


Advance usage with Django or Openstack Horizon Dashboard !
----------------------------------------------------------

.. code-block:: python

    # local_settings.py

    ROBOTICE_HOST default is localhost
    ROBOTICE_PORT default is 9753
    ROBOTICE_PROTOCOL default is http

    from roboticeclient.common.horizon import HorizonClient
    from roboticeclient.common.horizon import DjangoClient
    from roboticeclient.control.v1.base import RoboticeControlClient

    RoboticeControlClient.client_class = HorizonClient # or plain DjangoClient

    robotice_client = RoboticeControlClient(type="control")

    robotice_client.devices.list()


Read more
---------

* http://docs.robotice.org
* http://docs.control.robotice.org
* https://github.com/robotice/robotice
* https://github.com/robotice/robotice-control