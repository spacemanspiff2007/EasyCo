

Goal
==================================
The goal of **EasyCo** is to provide an **easy** way of **Co**\ nfiguration using yaml files for Python programs.
It can automatically create a default configuration from provided default values and will validate the provided data.

Usage
------------------------------
Just derive a class from :class:`~EasyCo.ConfigContainer` or :class:`~EasyCo.ConfigFile`.
On Instantiation all class variables with type-hints are used.
If you want more control over validators, default values or even add a description as a comment to the generated file
use :class:`~EasyCo.ConfigEntry`.

Examples
------------------------------

Simple Example
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. execute_code::
    :header_code: Program code
    :header_output: Created .yml file:

    from EasyCo import ConfigFile, ConfigContainer

    class MyContainer(ConfigContainer):
        SubValueA: int
        SubValueB: int = 7

    class MyConfigFile(ConfigFile):
        ConfValueA: int = 5
        ConfValueB: float = 5.5

        sub_values = MyContainer()

    cfg = MyConfigFile('test')
    # skip
    cfg.load()
    # skip

    # hide
    cfg._print_created_cfg()
    # hide



AutoComplete in the IDE does work, too!

.. image:: /gifs/example.gif

Accessing the loaded values is very easy::

    if cfg.ConfValueA == 'ValueA':
        print('Test')


Example ConfigEntry
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. execute_code::
    :header_code: Program code
    :header_output: Created .yml file:

    from EasyCo import ConfigFile, ConfigContainer, ConfigEntry

    class MyContainer(ConfigContainer):
        SubValueA: int = ConfigEntry(required=True, default=5, description='This is SubValueA')
        SubValueB: int = 7

    class MyConfigFile(ConfigFile):
        ConfValueA: int = 5
        ConfValueB: float = 5.5

        sub_values = MyContainer()

    cfg = MyConfigFile('test')
    # skip
    cfg.load()
    # skip

    # hide
    cfg._print_created_cfg()
    # hide

