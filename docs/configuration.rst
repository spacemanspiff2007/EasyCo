

Configuration
==================================
.. autoclass:: EasyCo.EasyCoConfig
   :members:

The configuration can be set by modifying ``EasyCo.DEFAULT_CONFIGURATION`` or
by creating an instance of :class:`~EasyCo.EasyCoConfig` in a container


Example lowercase keys
------------------------------

.. execute_code::

    from EasyCo import ConfigFile, DEFAULT_CONFIGURATION
    DEFAULT_CONFIGURATION.lower_case_keys = True

    class MyConfigFile(ConfigFile):
        ConfValueA = 5
        ConfValueB = 5.5

    #hide
    MyConfigFile('test')._print_created_cfg()
    #hide


Example lowercase keys
------------------------------
This example also shows a per container configuration

.. execute_code::

    from EasyCo import ConfigFile, EasyCoConfig, DEFAULT_CONFIGURATION
    DEFAULT_CONFIGURATION.lower_case_keys = True

    class MyConfigFile(ConfigFile):
        ConfValueA = 5
        ConfValueB = 5.5

        # name of config doesn't matter and can be private so it doesn't show up in auto-complete
        __cfg = EasyCoConfig()
        __cfg.lower_case_keys = False

    #hide
    MyConfigFile('test')._print_created_cfg()
    #hide
