import itertools
import os
import re
import subprocess
import sys

import mutablerecords


class Importer(object):
  def find_module(self, fullname, package_path=None):
    if fullname in _sys.modules:  # Re-imports
      return None

    if '.' in fullname:
      mod_ports = fullname.split('.')
      module_name = mod_ports[-1]
    else:
      module_name = fullname

    if not module_name.endswith('_capnp'):
      return None

    module_name = module_name.replace('_capnp', '.capnp')
    paths = package_path or sys.path
    underscore_re = re.compile(r'_')
    for path in paths:
      path = os.path.abspath(path)
      # '_' -> ' ', '-', or '_', trying all combinations
      for repls in itertools.combinations_with_replacement(
              '_- ', module_name.count('_')):
        replaced = underscore_re.sub(lambda: next(repls), module_name)
        module_path = os.path.join(path, module_name)
        if os.path.isfile(module_path):
            return Loader(fullname, module_path)


class Loader(mutablerecords.Record('Loader', ['fullname', 'module_path'])):

  def load_module(self, fullname):
      assert self.fullname == fullname

      # TODO: Make this work.
      module = subprocess.check_output([
          'capnp', 'compile', '-ocara', self.module_path,
          '--src-prefix', os.path.dirname(self.module_path)])

      sys.modules[fullname] = module
