=================
Flask-RESTful-DRY
=================


Allows the declaration of RESTful APIs using simple declarations so that you
don't need to write executable code for every HTTP method on every API.
Introduces:

* Inheritable declarations at the class level, including the ability to
  modify the base class declarations.
* Dynamic creation of Flask-RESTful_ API Resource classes, so that you
  can automatically generate the same pattern of URLs many times.
* Reducing HTTP method code to a series of re-usable steps.  These are
  automatically ordered for each HTTP method to meet ordering
  constraints specified on each step.  This allows the requirements for
  the HTTP method code to be reduced to a simple declaration of what
  steps to include.  Because these steps are automatically ordered,
  they may be specified in any order, making it easy to add or remove
  steps from inherited standard recipes.
* Adds column validation and introspection to Flask-SQLAlchemy_ tables,
  and automatically generates metadata descriptions of what colums are
  allowed to be POSTed or PUT, including the server validation rules
  that will be applied to each column.  This lets you specify the
  validation rules in one place for both server and client.
* Provides column-level authorization for all HTTP methods.
* Supports nested child rows (relationships) in APIs (and nested
  column-level authorization).


The documentation is on ReadTheDocs.org here_.


.. _here: http://flask-restful-dry.readthedocs.org/en/latest/dry.html
.. _Flask-RESTful: https://flask-restful.readthedocs.org
.. _Flask-SQLAlchemy: https://pythonhosted.org/Flask-SQLAlchemy/


