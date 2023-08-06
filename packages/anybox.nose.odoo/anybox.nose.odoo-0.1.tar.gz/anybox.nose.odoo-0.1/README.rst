Nosetests and Odoo
==================

This is an alternative test runner that prevents confusing situations
due to the special ``openerp.addons`` namespace for Odoo addons.

At the time being, it is meant to be used in conjunction with the
`buildout recipe <http://pythonhosted.org/anybox.recipe.odoo/>`_ only.

Use case
--------
Odoo overrides the python importer for the *Odoo addons* (also called
*modules* but we'll avoid this terminology here for confusion with
Python modules), to place them into the ``openerp.addons`` namespace.

For instance, some ``foo`` Odoo addon will be set in the sys.modules as
``openerp.addons.foo`` instead of just ``foo``.

The issue is that nose imports the test modules directly, with the
effect that they aren't in the ``openerp.addons`` namespace. This
leads to overall duplication of the Odoo addon as a Python module,
which can in some cases confuse the code. For instance, some
``isinstance()`` calls might fail, depending on the execution path.

Notably, this runner is necessary for tests related to the `Odoo
connector framework <http://odoo-connector.com/>`_. Historically this
is the context in which the above mentionned issue arose. Anybox had
been using the ordinary ``nosetests`` for several years before
actually stumbling on this.


Invocation
----------

This runner relies on the assumption that all relevant Odoo addons
have already been imported when the nose importer kicks in. This
condition is always true if used `through the
buildout recipe
<http://pythonhosted.org/anybox.recipe.odoo/scripts.html#command-line-options>`_

Therefore, the standard way of using the runner is to declare it in
the buildout configuration::

  eggs = anybox.nose.odoo
  openerp_scripts = odoo_nosetests=odoo_nosetests command-line-options=-d

and then run, e.g::

  bin/odoo_nosetests -d TESTING_DB -- some/module/tests

Credits
-------
Copyright (c) 2015 Anybox SAS <http://anybox.fr>
Released under GPLv3+ license

:Author: Jean-Sébastien SUZANNE <jssuzanne@anybox.fr>
