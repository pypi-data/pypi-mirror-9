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

   - Float numbers, only with to two decimal digits.
   - Integer numbers max = 99,000,000,000,000

Usage
-----

.. code:: python

    from numtogreek.numtogreek import n2g

    for i in range(20):
        n2g(i)

    n2g(1234.09)
    
    n2g(99999999.99)

    n2g(9.00) 
