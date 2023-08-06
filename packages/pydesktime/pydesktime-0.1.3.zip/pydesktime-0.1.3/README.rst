*********************************************************
PyDeskTime
*********************************************************

Module used to simplify usage of DeskTime_ API_

============
Installation
============

From PyPI::

    pip install pydesktime

============
Usage
============

.. code-block:: python

    from pydesktime import DeskTime

    desktime = DeskTime(app_key=<your app key>, username=<your username>,
                        password=<your password>)

    # data is dictionary with data for all employees
    # on every work day (except Saturday and Sunday)
    # in provided year, month
    data = desktime.getMonth(2015, 1)


.. _DeskTime: https://desktime.com/
.. _API: https://desktime.com/about/api/


