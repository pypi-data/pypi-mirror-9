
|License badge|

==========================
Horizon Dashboard API Mask
==========================

Plugin replace IP and protocol in EndpointsTable

Usefull if you have OpenStack API behind proxies.

Reuired
-------

* Python 2.6 +
* Horizon Icehouse +

Installation
------------

.. code-block:: bash

	pip install horizon-api-mask

Required Configuration
----------------------

.. code-block:: python

	INSTALLED_APPS += ('api_mask',)

	HORIZON_CONFIG['customization_module'] = 'api_mask.overrides'

Optional Configuration
----------------------

.. code-block:: python

	API_MASK_URL = 'public-domain.com' # default is socket.getfqdn()
	API_MASK_PROTOCOL = 'https' # default is https

.. |License badge| image:: http://img.shields.io/badge/license-Apache%202.0-green.svg?style=flat