
================
Universal Client
================

Python client for https://github.com/robotice/robotice-control and https://github.com/robotice/robotice


Requirements
------------

Robotice Client
---------------

.. code-block:: python

	from roboticeclient import Client

	client = Client(port=8004, host="127.0.0.1")


Robotice Control Client !
-------------------------

.. code-block:: python

	from roboticeclient import Client

	client = Client(type="control", port=9753, host="127.0.0.1")


Actions
-------

.. code-block:: python

	from roboticeclient import Client

	client = Client(port=8004, host="127.0.0.1")

	print client.actions.list()
	print client.actions.get(id)
	print client.actions.do(id)

	client.actions.save(id, action)


Systems
-------

.. code-block:: python

	from roboticeclient import Client

	client = Client(port=8004, host="127.0.0.1")

	print client.systems.list()
	print client.systems.get(id)

	client.systems.save(id, system)


Plans
-----

.. code-block:: python

	from roboticeclient import Client

	client = Client(port=8004, host="127.0.0.1")

	print client.plans.list()
	print client.plans.get(id)

	client.plans.save(id, system)


Devices
-------

.. code-block:: python

	from roboticeclient import Client

	client = Client(port=8004, host="127.0.0.1")

	print client.devices.list()
	print client.devices.get(id)

	client.devices.save(id, system)


Read more
---------

* http://docs.robotice.org
* http://docs.control.robotice.org
* https://github.com/robotice/robotice
* https://github.com/robotice/robotice-control