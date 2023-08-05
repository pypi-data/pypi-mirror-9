Filters, unbound fields and callbacks
=====================================

genericimports allows you to use a number of options to overcome complications

Unbound fields
--------------

We call unbound fields all those fields that are required in the model but are
not present in the import file, for example, you want to import people with
first name, last name and the email, but you don't know the username or password.

In that case username and password are required by the auth.User model in django
but since you don't have that data we have to populate it somehow.

Usually the population of those fields is done through a python lambda...

To be written....

Filters
-------

Filters are nothing but functions that will get called upon populating a field
because probably the data type is not recognized by django or you need to
manipulate it before sending it back.

An example on the mapping would be:

::

    {'filter': my_function, 'name': 'field_name'}

That funciton will be called during execution with the parameter _rowdata_. An
example for that function:

::

    def my_function(rowdata):

        # Imagine that we add to add one to the data
        new_rowdata = rowdata + 1

        return new_rowdata

Callbacks
---------

To be written...
