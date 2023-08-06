Reactor.am is the most important from marketing automation, crm and user
analytics, in one easy to use service.

This is a python library for reactor.am API.

Installation
============

pip install reactor

Basic usage
===========

.. code:: python

    import reactor
    reactor.APPLICATION_ID = '<your_app_id_hash>'

    response = reactor.collect({
        "session": 1405587905,
        "user_id": "661787707",
        "first_name_s": "John",
        "last_name_s": "Doe",
        "gender_g": "male",
        "share_facebook_b": False,
    })

    assert response.status_code == 200


    response = reactor.event('order', {
        "user_id": "661787707",
        "product_s": "Gizmo",
        "price_f": 10.30 
    })

    assert response.status_code == 200
                                     

Documentation
=============

Full documentation can be found at
`docs.reactor.am <http://docs.reactor.am>`__
