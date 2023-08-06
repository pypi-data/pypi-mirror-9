"""Main subclassing of nose importer and entry point.

Odoo specific changes have been explicitely tagged as such.
Works under the general assumption that Odoo addons have already been imported,
which is the case in the intended invocation (see main README)
"""

from nose import main
from nose.loader import TestLoader
from nose.importer import Importer, add_path
import os
import sys
from imp import find_module, load_module, acquire_lock, release_lock
from logging import getLogger
log = getLogger(__name__)


class OdooImporter(Importer):

    def importFromDir(self, dir, fqname):
        """Import a module *only* from path, ignoring sys.path and
        reloading if the version in sys.modules is not the one we want.
        """
        dir = os.path.normpath(os.path.abspath(dir))
        log.debug("Import %s from %s", fqname, dir)

        # FIXME reimplement local per-dir cache?

        # special case for __main__
        if fqname == '__main__':
            return sys.modules[fqname]

        if self.config.addPaths:
            add_path(dir, self.config)

        path = [dir]
        parts = fqname.split('.')
        part_fqname = ''
        mod = parent = fh = None

        for part in parts:
            if part_fqname == '':
                part_fqname = part
            else:
                part_fqname = "%s.%s" % (part_fqname, part)
            try:
                acquire_lock()
                log.debug("find module part %s (%s) in %s",
                          part, part_fqname, path)
                fh, filename, desc = find_module(part, path)
                old = sys.modules.get(part_fqname)

                # start Odoo specific part
                odoo_fqname = 'openerp.addons.%s' % part_fqname
                odoo_old = sys.modules.get(odoo_fqname)
                odoo_module_fqname = 'openerp.addons.%s' % part_fqname.split(
                    '.')[0]
                odoo_module_old = sys.modules.get(odoo_module_fqname)
                # end Odoo specific part

                if old is not None:
                    # test modules frequently have name overlap; make sure
                    # we get a fresh copy of anything we are trying to load
                    # from a new path
                    log.debug("sys.modules has %s as %s", part_fqname, old)
                    if (self.sameModule(old, filename)
                        or (self.config.firstPackageWins and
                            getattr(old, '__path__', None))):
                        mod = old
                    else:
                        del sys.modules[part_fqname]
                        mod = load_module(part_fqname, fh, filename, desc)
                # start Odoo specific part
                elif odoo_old:
                    # Module already imported by openerp
                    mod = sys.modules[part_fqname] = odoo_old
                elif odoo_module_old:
                    # Module not imported by openerp
                    mod = sys.modules[part_fqname] = load_module(
                        'openerp.addons.' + part_fqname, fh, filename, desc)
                # end Odoo specific part
                else:
                    mod = load_module(part_fqname, fh, filename, desc)
            finally:
                if fh:
                    fh.close()
                release_lock()
            if parent:
                setattr(parent, part, mod)
            if hasattr(mod, '__path__'):
                path = mod.__path__
            parent = mod
        return mod


def run_exit():
    testLoader = TestLoader(importer=OdooImporter())
    return main(testLoader=testLoader)
