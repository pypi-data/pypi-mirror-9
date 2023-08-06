.. _result_processors:

Result_processors
=================

csv
---

Creates a ``results.csv`` in the output directory containing results for
all iterations in CSV format, each line containing a single metric.

parameters
~~~~~~~~~~

modules : list  
    Lists the modules to be loaded by this extension. A module is a plug-in that
    further extends functionality of an extension.


dvfs
----

Reports DVFS state residency data form ftrace power events.

This generates a ``dvfs.csv`` in the top-level results directory that,
for each workload iteration, reports the percentage of time each CPU core
spent in each of the DVFS frequency states (P-states), as well as percentage
of the time spent in idle, during the execution of the workload.

.. note:: ``trace-cmd`` instrument *MUST* be enabled in the instrumentation,
          and at least ``'power*'`` events must be enabled.

parameters
~~~~~~~~~~

modules : list  
    Lists the modules to be loaded by this extension. A module is a plug-in that
    further extends functionality of an extension.


json
----

Creates a ``results.json`` in the output directory containing results for
all iterations in JSON format.

parameters
~~~~~~~~~~

modules : list  
    Lists the modules to be loaded by this extension. A module is a plug-in that
    further extends functionality of an extension.


mongodb
-------

Uploads run results to a MongoDB instance.

MongoDB is a popular document-based data store (NoSQL database).

parameters
~~~~~~~~~~

modules : list  
    Lists the modules to be loaded by this extension. A module is a plug-in that
    further extends functionality of an extension.

uri : str  
    Connection URI. If specified, this will be used for connecting
    to the backend, and host/port parameters will be ignored.

host : str (mandatory)
    IP address/name of the machinge hosting the MongoDB server.

    default: ``'localhost'``

port : int (mandatory)
    Port on which the MongoDB server is listening.

    default: ``27017``

db : str (mandatory)
    Database on the server used to store WA results.

    default: ``'wa'``

extra_params : dict  
    Additional connection parameters may be specfied using this (see
    pymongo documentation.

authentication : dict  
    If specified, this will be passed to db.authenticate() upon connection;
    please pymongo documentaion authentication examples for detail.


sqlite
------

Stores results in an sqlite database. The following settings may be
specified in config.py:

This may be used accumulate results of multiple runs in a single file.

parameters
~~~~~~~~~~

modules : list  
    Lists the modules to be loaded by this extension. A module is a plug-in that
    further extends functionality of an extension.

database : str  
    Full path to the sqlite database to be used.  If this is not specified then
    a new database file will be created in the output directory. This setting can be
    used to accumulate results from multiple runs in a single database. If the
    specified file does not exist, it will be created, however the directory of the
    file must exist.

    .. note:: The value must resolve to an absolute path,
                relative paths are not allowed; however the
                value may contain environment variables and/or
                the home reference ~.

overwrite : boolean  
    If ``True``, this will overwrite the database file
    if it already exists. If ``False`` (the default) data
    will be added to the existing file (provided schema
    versions match -- otherwise an error will be raised).


standard
--------

Creates a ``result.txt`` file for every iteration that contains metrics
for that iteration.

The metrics are written in ::

    metric = value [units]

format.

parameters
~~~~~~~~~~

modules : list  
    Lists the modules to be loaded by this extension. A module is a plug-in that
    further extends functionality of an extension.


status
------

Outputs a txt file containing general status information about which runs
failed and which were successful

parameters
~~~~~~~~~~

modules : list  
    Lists the modules to be loaded by this extension. A module is a plug-in that
    further extends functionality of an extension.


summary_csv
-----------

Similar to csv result processor, but only contains workloads' summary metrics.

parameters
~~~~~~~~~~

modules : list  
    Lists the modules to be loaded by this extension. A module is a plug-in that
    further extends functionality of an extension.


syeg_csv
--------

Generates a CSV results file in the format expected by SYEG toolchain.

Multiple iterations get parsed into columns, adds additional columns for mean
and standard deviation, append number of threads to metric names (where
applicable) and add some metadata based on external mapping files.

parameters
~~~~~~~~~~

modules : list  
    Lists the modules to be loaded by this extension. A module is a plug-in that
    further extends functionality of an extension.

outfile : str  
    The name of the output CSV file.

    default: ``'syeg_out.csv'``


