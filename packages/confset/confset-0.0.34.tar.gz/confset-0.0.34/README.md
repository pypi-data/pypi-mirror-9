confset
=======

Set and view values for package default settings from the command line.

Examples
=======
See the settings and current values for the kerneloops daemon
-------
    $ confset kerneloops
    kerneloops.enabled=0 - Whether the daemon should be started at boot time.
                           Set to 1 to start.
    $

Enable the kerneloops daemon
-------
    $ sudo confset kerneloops.enabled=1
    $ confset kerneloops
    kerneloops.enabled=1 - Whether the daemon should be started at boot time.
                           Set to 1 to start.
    $ 