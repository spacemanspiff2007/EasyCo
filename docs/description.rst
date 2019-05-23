

Goal
==================================
The goal of **EasyCo** is to provide an **easy** way of **Co**\ nfiguration using yaml files for Python programs.
It can automatically create a default configuration from provided default values and will validate the provided data.

Example
------------------------------

.. execute_code::
    :header_code: Program code
    :header_output: Created yml file:

    from EasyCo import ConfigFile, ConfigContainer

    class MyContainer(ConfigContainer):
        SubValueA: int
        SubValueB = 7

    class MyConfigFile(ConfigFile):
        ConfValueA = 5
        ConfValueB = 5.5

        sub_values = MyContainer()

    cfg = MyConfigFile('test')

    # hide
    cfg._print_created_cfg()
    # hide



AutoComplete in the IDE does work, too!

.. image:: /gifs/example.gif

Accessing the loaded values is very easy::

    if cfg.ConfValueA == 'ValueA':
        print('Test')

