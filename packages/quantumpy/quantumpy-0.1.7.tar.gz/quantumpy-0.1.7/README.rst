Quantumpy
======

	An ultra simple wrapper for the Socialmetrix Quantum API, with basic functionality

Usage
-----

::

    from quantumpy import QuantumAPI

    # Initialize connection with the api, providing account_id and your JWT token
    c = QuantumAPI(account_id, jwt_token)

    # Get all projects associated with account
    projects = c.get_projects()


Installation
------------

::

		$ pip install quantumpy
