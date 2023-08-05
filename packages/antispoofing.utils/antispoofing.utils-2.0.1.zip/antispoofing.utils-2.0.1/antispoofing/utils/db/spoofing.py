#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tiago de Freitas Pereira <tiagofrepereira@gmail.com>
# Tue 01 Oct 2012 16:48:44 CEST

"""Database API for antispoofing.utils.db.Database"""

import six
from . import __doc__ as long_description
from antispoofing.utils.db import File as FileBase, Database as DatabaseBase

class DatabaseAll(DatabaseBase):
  __doc__ = long_description

  def __init__ (self, args=None):
    self.__kwargs = {}
    if args is not None:

      self.__kwargs = {
       }
  __init__.__doc__ = DatabaseBase.__init__.__doc__

  def create_subparser(self, subparser, entry_point_name):
    from argparse import RawDescriptionHelpFormatter

    import pkg_resources
    desc = ''
    for entrypoint in pkg_resources.iter_entry_points('antispoofing.utils.db'):
      desc = desc + entry_point_name + ', '

    ## remove '.. ' lines from rst
    desc = ''
    p = subparser.add_parser(entry_point_name,
        help=self.short_description(),
        description=desc,
        formatter_class=RawDescriptionHelpFormatter)

    p.set_defaults(name=entry_point_name)
    p.set_defaults(cls=DatabaseAll)

    return
  create_subparser.__doc__ = DatabaseBase.create_subparser.__doc__

  def name(self):
    return 'Fused datasets (all)'
    
  def short_name(self):
    return 'all'  

  def version(self):
    import pkg_resources  # part of setuptools
    return pkg_resources.require('antispoofing.utils')[0].version

  def short_description(self):
    return "Fusion with all antispoofing databases available in this package"
  short_description.__doc__ = DatabaseBase.short_description.__doc__

  def long_description(self):
    return "Fusion with all antispoofing databases available in this package"
  long_description.__doc__ = DatabaseBase.long_description.__doc__

  '''
  def implements_any_of(self, propname):
    if isinstance(propname, (tuple,list)):
      return 'video' in propname
    elif propname is None:
      return True
    elif isinstance(propname, six.string_types):
      return 'video' == propname

    # does not implement the given access protocol
    return False
  '''

  def implements_any_of(self, propname):
    if isinstance(propname, (tuple,list)):
      return 'video' in propname or 'image' in propname
    elif propname is None:
      return True
    elif isinstance(propname, six.string_types):
      return 'video' == propname or 'image' == propname

    # does not implement the given access protocol
    return False

  def set_foldsdir(self, foldsdir):    
    """Sets the directory holding the cross validation protocol for the CASIA_FASD"""
    self.foldsdir = foldsdir

  def get_train_data(self, fold_no=1):
    import pkg_resources
    real_data = []; attack_data = [];
    for entrypoint in pkg_resources.iter_entry_points('antispoofing.utils.db'):
      plugin = entrypoint.load()
      db = plugin()
      if db.short_name() == 'casia_fasd':
        db.set_foldsdir(self.foldsdir)
        r, a = db.get_train_data(fold_no=fold_no)
      else:
        r, a = db.get_train_data()
      real_data = real_data + r
      attack_data = attack_data + a

    return (real_data,attack_data)
  get_train_data.__doc__ = DatabaseBase.get_train_data.__doc__

  def get_devel_data(self, fold_no=1):
    import pkg_resources
    real_data = []; attack_data = [];
    for entrypoint in pkg_resources.iter_entry_points('antispoofing.utils.db'):
      plugin = entrypoint.load()
      db = plugin()
      if db.short_name() == 'casia_fasd':
        db.set_foldsdir(self.foldsdir)
        r, a = db.get_devel_data(fold_no=fold_no)
      else:
        r, a = db.get_devel_data()
      real_data = real_data + r
      attack_data = attack_data + a

    return (real_data,attack_data)
  get_devel_data.__doc__ = DatabaseBase.get_devel_data.__doc__

  def get_test_data(self, fold_no=1):
    import pkg_resources
    real_data = []; attack_data = [];
    for entrypoint in pkg_resources.iter_entry_points('antispoofing.utils.db'):
      plugin = entrypoint.load()
      db = plugin()
      if db.short_name() == 'casia_fasd':
        db.set_foldsdir(self.foldsdir)
        r, a = db.get_test_data(fold_no=fold_no)
      else:
        r, a = db.get_test_data()
      real_data = real_data + r
      attack_data = attack_data + a

    return (real_data,attack_data)
  get_test_data.__doc__ = DatabaseBase.get_test_data.__doc__

  def get_all_data(self):
    import pkg_resources
    real_data = []; attack_data = [];
    for entrypoint in pkg_resources.iter_entry_points('antispoofing.utils.db'):
      plugin = entrypoint.load()
      db = plugin()
      r, a = db.get_all_data()
      real_data = real_data + r
      attack_data = attack_data + a

    return (real_data,attack_data)
  get_all_data.__doc__ = DatabaseBase.get_all_data.__doc__

  def get_clients(self, group):
    raise NotImplementedError("You cannot query for client ids of this database because it is just a dumb fusion of all databases available in your current environment")

  def get_enroll_data(self, group):
    raise NotImplementedError("You cannot query for enrollment data of this database because it is just a dumb fusion of all databases available in your current environment")

  def get_test_filters(self):
    raise NotImplementedError("You cannot query for filters to the test set of this database because it is just a dumb fusion of all databases available in your current environment")

  def get_filtered_test_data(self, filter):
    raise NotImplementedError("You cannot apply a filter to the test set of this database because it is just a dumb fusion of all databases available in your current environment")
    
  def get_filtered_devel_data(self, filter):
    raise NotImplementedError("You cannot apply a filter to the devel set of this database because it is just a dumb fusion of all databases available in your current environment")  
    
  def get_protocols(self):
    raise NotImplementedError("You cannot query for protocols of this database because it is just a dumb fusion of all databases available in your current environment")    
    
  def get_attack_types(self):
    raise NotImplementedError("You cannot query for attack types of this database because it is just a dumb fusion of all databases available in your current environment")    
