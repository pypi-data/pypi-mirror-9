
=======================
MysqlSimpleQueryBuilder
=======================

Following the rule *simple easy, complex possible*, the package provides API for simple queries,
nested transactions and aid for complex query building and profiling. It's a small wrapper
around a Python MySQL driver.

The package is written on the following assumptions:

#. SQL is feasible and representative DSL
#. Simple SQL is simple but tedious to write by hand
#. Complex SQL is possible and should be written by hand or constructed elaborately
#. Unit/integration testing of domain logic against database is necessary
#. Database abstraction in the age of SaaS is a waste

`Package documentation <https://mysqlsimplequerybuilder.readthedocs.org/>`_.
