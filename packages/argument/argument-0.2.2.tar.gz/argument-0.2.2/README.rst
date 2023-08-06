arguments
=========

Argument parsing for python developers

Usage:
------

.. code:: python

    import argument
    f = argument.Arguments()
    #Requried arguments, first argument will be stored as "candy"
    f.required("candy", help="Candy name")
    #optional value, set a default, can be changed by adding: --num=30, or -n=30
    f.option("num", 
        25,
        help="How many pieces?", 
        abbr="n"
        )
    #add a switch, a flag with no argument
    f.switch("reverse", 
        help="Reverse ordering", 
        abbr="r"
    )
    #Process data before saving it
    f.process("candy", lambda x: x.upper())

    #get data
    arguments = f.parse()

Example:
--------

*python tests/demo.py bubblegum*

{'num': 25, 'reverse': False, 'candy': 'BUBBLEGUM'}

*python tests/demo.py bubblegum -r -n=123*

{'num': 123, 'reverse': True, 'candy': 'BUBBLEGUM'}

