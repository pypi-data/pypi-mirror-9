==================================================
importStar - keep you __init__.py files up to date
==================================================

Imagine...

* you need all modules in a package imported
* ... maybe because you want to access them via inspect.getmembers 
* ... or want to do sth. like ``for module in package: ...``

BUT:

* you are to lazy to update all your __init__.py
* you dont want/can't to use automodinit <https://github.com/ned14/automodinit>
* AND/OR you cannot use dynamic imports (maybe because you want to create an application with pyinstaller)

*THAN:* this might be your solution!

install
=======

via pip
-------

``pip install importStar``

ubuntu or simular
-----------------

``sudo python setup.py install``

windows
-------

``python setup.py install``


usage
=====
either:
* use as a script:
``importstar [directorypath]``

* to see help: run importstar without further arguments or with *-h* or *--help* 

* OR call function importStar.importstar.run(args) directly


result
======

importstar add all modules and packages recursively within a given directory 

in all __init__.py files that have the following comments::

    #<<<importStar
    [i will be substitued]
    #>>>importStar

the result might look like::

    #<<<importStar
    import mod1
    import mod2
    import pkg1
    #>>>importStar



