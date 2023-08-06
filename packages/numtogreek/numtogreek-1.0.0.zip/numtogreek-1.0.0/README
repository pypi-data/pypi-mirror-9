Numbers To Greek
================

Converts Numbers to Greek words.


Installation
------------

    - **With pip:**
        
        - ``pip install numtogreek`` 

    - **Running setup:**
        
        - ``wget -c https://pypi.python.org/packages/source/n/numtogreek/numtogreek-0.8.0b2.tar.gz``

        - ``tar zxfv numtogreek-x.y.z.tar.gz cd numtogreek-x.y.z.tar.gz``

        - ``python3 setup.py install`` as administrator, or ``sudo python3 setup.py install``

Restrictions:
-------------

   - Float numbers, only with to two decimal digits. More than two digits, will be truncated. 
   - Float numbers max = 99,999,999,999,999.98
   - Integer numbers max = 999,999,999,999,999,999,999,999

Usage
-----

From Script
~~~~~~~~~~~

.. code:: python

    from numtogreek import n2g

    for i in range(20):
        n2g(i)

    n2g(1234.09)
    
    n2g(99999999.99)

    n2g(9.00)



From Python Console
~~~~~~~~~~~~~~~~~~~

.. code:: python

    >>> from numtogreek import n2g
    >>> n2g(848922.01)
    'Οκτακόσιες Σαράντα Οκτώ Χιλιάδες Εννιακόσια Είκοσι Δύο και Ένα'
    >>> n2g(848922.01, True)
    'Οκτακόσιες Σαράντα Οκτώ Χιλιάδες Εννιακόσια Είκοσι Δύο Ευρώ  και Ένα Λεπτό'
    >>> n2g(848922.01, True, 'lower')
    'οκτακόσιες σαράντα οκτώ χιλιάδες εννιακόσια είκοσι δύο ευρώ  και ένα λεπτό'
    >>> n2g(848922.01, True, 'upper')
    'ΟΚΤΑΚΌΣΙΕΣ ΣΑΡΆΝΤΑ ΟΚΤΏ ΧΙΛΙΆΔΕΣ ΕΝΝΙΑΚΌΣΙΑ ΕΊΚΟΣΙ ΔΎΟ ΕΥΡΏ  ΚΑΙ ΈΝΑ ΛΕΠΤΌ'
    >>>  
