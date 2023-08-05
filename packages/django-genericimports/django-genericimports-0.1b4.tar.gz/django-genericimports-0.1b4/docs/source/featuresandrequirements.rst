Features and requirements
=========================

Features
--------

- Support CSV, XLS and XLSX
- Agnostic to data types or headers
- Non estandard fields are supported trough functions
- Support required unbound fields (fields required in your model but absent in your import file)
- Support callbacks to apply after a succesful import
- Support for optional data in the import file (columns that repeat themselves)
- Support Foreignkeys
- ***Report system with statistics and records on each import***
- ***Failed entries are saved in a separate file and accesible through the report***
- ***Third party access to the imports with email reports.***
- Support django CMS
- Available as management command or admin action

Future improvements
...................

- Speed (really difficult, this one)
- Support ManyToMany fields
- Remove lambdas to remove eval() from the code and replace it with functions
- Optional logging (forced right now)
- Optional profiling (so you can know how well did this do in your box)
- pip support
- Figure out a way of doing bulk_inserts with ID's

Supports
--------

- Django 1.5/1.6/1.7
- Python 2.7.x/3.3.x up

Requirements
------------

- redis
