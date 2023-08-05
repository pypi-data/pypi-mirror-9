#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Ivana Chingovska <ivana.chingovska@idiap.ch>
# Mon Mar  5 15:38:22 CET 2012

"""
The CASIA-FASD database is a spoofing attack database which consists of three
types of attacks: warped printed photographs, printed photographs with cut eyes
and video attacks. The samples are taken with three types of cameras: low
quality, normal quality and high quality.

The actual raw data for the database should be downloaded from the original
URL. This package only contains the Bob accessor methods to use the DB directly
from python, with our certified protocols.

References:

  1. Z. Zhang, J. Yan, S. Lei, D. Yi, S. Z. Li: "A Face Antispoofing Database
  with Diverse Attacks", In proceedings of the 5th IAPR International
  Conference on Biometrics (ICB'12), New Delhi, India, 2012."""

import os
import six
import numpy
from bob.db.base import utils
from .models import *

class Database(object):

  def __init__(self, foldsdir=None):

    from .driver import Interface
    self.info = Interface()
    self.groups = ('train', 'test')
    self.classes = ('attack', 'real')
    self.qualities = ('low','normal','high')
    self.types = ('warped', 'cut', 'video')
    self.ids = list(range(1, 51))
    package_directory = os.path.dirname(os.path.abspath(__file__))
    if foldsdir == None:
      self.foldsdir = os.path.join(package_directory, 'newfolds')
    else:
      self.foldsdir = foldsdir

  def set_foldsdir(self, foldsdir):
    """Sets the directory holding the cross validation protocol of the database"""
    self.foldsdir = foldsdir

  def check_validity(self, l, obj, valid, default):
      """Checks validity of user input data against a set of valid values"""
      if not l: return default
      elif isinstance(l, six.string_types) or isinstance(l, six.integer_types): return self.check_validity((l,), obj, valid, default)
      for k in l:
        if k not in valid:
          raise RuntimeError('Invalid %s "%s". Valid values are %s, or lists/tuples of those' % (obj, k, valid))
      return l

  def get_file(self, pc):
    '''Returns the full file path given the path components pc'''
    from pkg_resources import resource_filename
    if os.path.isabs(pc):
      return pc
    return resource_filename(__name__, os.path.join(pc))

  def files(self, directory=None, extension=None, ids=[], groups=None, cls=None, qualities=None, types=None):
    """Returns a set of filenames for the specific query by the user.

    .. deprecated:: 1.1.0

      This function is *deprecated*, use :py:meth:`.Database.objects` instead.

    Keyword Parameters:

    directory
      A directory name that will be prepended to the final filepath returned

    extension
      A filename extension that will be appended to the final filepath returned

    ids
      The id of the client whose videos need to be retrieved. Should be an integer number in the range 1-50 (the total number of client is 50

    groups
      One of the protocolar subgroups of data as specified in the tuple groups, or a
      tuple with several of them.  If you set this parameter to an empty string
      or the value None, we use reset it to the default which is to get all.

    cls
      Either "attack", "real" or a combination of those (in a
      tuple). Defines the class of data to be retrieved.  If you set this
      parameter to an empty string or the value None, it will be set to the tuple ("real", "attack").

    qualities
      Either "low", "normal" or "high" or any combination of those (in a
      tuple). Defines the qualities of the videos in the database that are going to be used. If you set this
      parameter to the value None, the videos of all qualities are returned ("low", "normal", "high").

    types
      Either "warped", "cut" or "video" or any combination of those (in a
      tuple). Defines the types of attack videos in the database that are going to be used. If you set this
      parameter to the value None, the videos of all the attack types are returned ("warped", "cut", "video").

    Returns: A dictionary containing the resolved filenames considering all
    the filtering criteria. The keys of the dictionary are just pro-forma (for uniformity with the other databases).
    """

    import warnings
    warnings.warn("The method Database.files() is deprecated, use Database.objects() for more powerful object retrieval", DeprecationWarning)

    def make_path(stem, directory, extension):
      if not extension: extension = ''
      if directory: return os.path.join(directory, stem + extension)
      return stem + extension

    # check if groups set are valid
    VALID_GROUPS = self.groups
    groups = self.check_validity(groups, "group", VALID_GROUPS, VALID_GROUPS)

    # by default, do NOT grab enrollment data from the database
    VALID_CLASSES = self.classes
    VALID_TYPES = self.types
    if cls == None and types != None: # types are strictly specified which means we don't need the calss of real accesses
      cls = ('attack',)
    else:
      cls = self.check_validity(cls, "class", VALID_CLASSES, ('real', 'attack'))

    # check if video quality types are valid
    VALID_QUALITIES = self.qualities
    qualities = self.check_validity(qualities, "quality", VALID_QUALITIES, VALID_QUALITIES)

    # check if attack types are valid

    if cls != ('real',): # if the class is 'real' only, then there is no need for types to be reset to the default (real accesses have no types)
      types = self.check_validity(types, "type", VALID_TYPES, VALID_TYPES)

    VALID_IDS = self.ids
    ids = self.check_validity(ids, "id", VALID_IDS, VALID_IDS)

    retval = {}
    key = 0

    db_mappings = {'real_normal':'1', 'real_low':'2', 'real_high':'HR_1', 'warped_normal':'3', 'warped_low':'4', 'warped_high':'HR_2', 'cut_normal':'5', 'cut_low':'6', 'cut_high':'HR_3', 'video_normal':'7', 'video_low':'8', 'video_high':'HR_4'}

    # identitites in the training set are assigned ids 1-20, identities in the test set are assigned ids 21-50
    for i in ids:
      for g in groups:
        if (g == 'train' and i > 20) or (g == 'test' and i <= 20): continue;
        cur_id = i
        if g == 'test': cur_id = i - 20; # the id within the group subset
        folder_name = g + '_release'
        for q in qualities:
          if cls == ('real',) and types != None: continue; # category real + any type does not exist
          for c in cls:
            if c == 'real': # the class real doesn't have any different types, only the attacks can be of different type
              name = os.path.join(folder_name, "%d" % cur_id, db_mappings[c + '_' + q])
              retval[key] = make_path(name, directory, extension)
              key = key + 1
            else:
              for t in types:
                name = os.path.join(folder_name, "%d" % cur_id, db_mappings[t + '_' + q])
                retval[key] = make_path(name, directory, extension)
                key = key + 1

    return retval


  def objects(self, ids=[], groups=None, cls=None, qualities=None, types=None):
    """Returns a list of unique :py:class:`.File` objects for the specific query by the user.

    Keyword Parameters:

    ids
      The id of the client whose videos need to be retrieved. Should be an integer number in the range 1-50 (the total number of client is 50

    groups
      One of the protocolar subgroups of data as specified in the tuple groups, or a
      tuple with several of them.  If you set this parameter to an empty string
      or the value None, we use reset it to the default which is to get all.

    cls
      Either "attack", "real" or a combination of those (in a
      tuple). Defines the class of data to be retrieved.  If you set this
      parameter to an empty string or the value None, it will be set to the tuple ("real", "attack").

    qualities
      Either "low", "normal" or "high" or any combination of those (in a
      tuple). Defines the qualities of the videos in the database that are going to be used. If you set this
      parameter to the value None, the videos of all qualities are returned ("low", "normal", "high").

    types
      Either "warped", "cut" or "video" or any combination of those (in a
      tuple). Defines the types of attack videos in the database that are going to be used. If you set this
      parameter to the value None, the videos of all the attack types are returned ("warped", "cut", "video").

    Returns: A list of :py:class:`.File` objects.
    """

    # check if groups set are valid
    VALID_GROUPS = self.groups
    groups = self.check_validity(groups, "group", VALID_GROUPS, VALID_GROUPS)

    # by default, do NOT grab enrollment data from the database
    VALID_CLASSES = self.classes
    VALID_TYPES = self.types
    if cls == None and types != None: # types are strictly specified which means we don't need the calss of real accesses
      cls = ('attack',)
    else:
      cls = self.check_validity(cls, "class", VALID_CLASSES, ('real', 'attack'))

    # check if video quality types are valid
    VALID_QUALITIES = self.qualities
    qualities = self.check_validity(qualities, "quality", VALID_QUALITIES, VALID_QUALITIES)

    # check if attack types are valid

    if cls != ('real',): # if the class is 'real' only, then there is no need for types to be reset to the default (real accesses have no types)
      types = self.check_validity(types, "type", VALID_TYPES, VALID_TYPES)

    VALID_IDS = self.ids
    ids = self.check_validity(ids, "id", VALID_IDS, VALID_IDS)

    retval = []

    db_mappings = {'real_normal':'1', 'real_low':'2', 'real_high':'HR_1', 'warped_normal':'3', 'warped_low':'4', 'warped_high':'HR_2', 'cut_normal':'5', 'cut_low':'6', 'cut_high':'HR_3', 'video_normal':'7', 'video_low':'8', 'video_high':'HR_4'}

    # identitites in the training set are assigned ids 1-20, identities in the test set are assigned ids 21-50
    for i in ids:
      for g in groups:
        if (g == 'train' and i > 20) or (g == 'test' and i <= 20): continue;
        cur_id = i
        if g == 'test': cur_id = i - 20; # the id within the group subset
        folder_name = g + '_release'
        for q in qualities:
          if cls == ('real',) and types != None: continue; # category real + any type does not exist
          for c in cls:
            if c == 'real': # the class real doesn't have any different types, only the attacks can be of different type
              filename = os.path.join(folder_name, "%d" % cur_id, db_mappings[c + '_' + q])
              retval.append(File(filename, c, g))
            else:
              for t in types:
                filename = os.path.join(folder_name, "%d" % cur_id, db_mappings[t + '_' + q])
                retval.append(File(filename, c, g))
    return retval

  def cross_valid_gen(self, numpos, numneg, numfolds=10, outfilename=None):
    """ Performs N-fold cross-validation on a given number of samples. Generates the indices of the validation subset for N folds, and writes them into a text file (the indices of the training samples are easy to compute once the indices of the validation subset are known). This method is intended for 2-class classification problems, therefore the number of both positive and negative samples should be given at the beginning. The method generates validation indices for both positive and negative samples separately. Each row of the output file are the validation indices of one fold; validation indices for the positive class are in the odd lines, and validation indices for the negative class are in the even lines.

    Keyword parameters:

    numpos
      Number of positive samples

    numneg
      Number of negative samples

    numfold
      Number of folds

    outfilename
      The filename of the output file
    """
    if outfilename == None:
      outfilename = self.get_file(os.path.join(self.foldsdir, 'cross_valid.txt'))
    f = open(outfilename, 'w')

    def cross_valid(numsamples, numfolds):
      ''' The actual cross-validation function, returns the validation indices in a tab-delimited null-terminated string'''
      from random import shuffle
      X = list(range(0, numsamples))
      shuffle(X)
      retval = []
      for k in range(numfolds):
        tr = [X[i] for i in range(0, numsamples) if i % numfolds != k]
        vl = [X[i] for i in range(0, numsamples) if i % numfolds == k]
        valid = ""
        for ind in vl:
          valid += "%d\t" % ind
        retval.append(valid)
      return retval

    valid_pos = cross_valid(numpos, numfolds) # the validation indices of the positive set
    valid_neg = cross_valid(numneg, numfolds) # the validation indices of the negative set
    # it is enough to save just the validation indices, training indices are all the rest
    for i in range(0, numfolds):
      f.write(valid_pos[i] + '\n') # write the validation indices for the real samples (every odd line in the file)
      f.write(valid_neg[i] + '\n') # write the validation indices for the attack samples (every even line in the file)
    f.close()
    return 0

  def cross_valid_read(self):
    """ Reads the cross-validation indices from a file and returns two lists of validation indices: for the positive and for the negative class. Each list actually consists of sublists; one sublist with validation indices for each fold.

    Keyword parameters:

  """
    infilename = self.get_file(os.path.join(self.foldsdir, 'cross_valid.txt'))
    lines = open(infilename, 'r').readlines()
    subsets_pos = []
    subsets_neg = []
    linenum = 1
    for line in lines:
      ind_list = [int(i) for i in line.rstrip('\n\t').split('\t')]
      if linenum % 2 == 1: subsets_pos.append(ind_list) # odd lines: validation indices for the positive class
      else: subsets_neg.append(ind_list) # even lines: validation indices for the negative class
      linenum += 1
    return subsets_pos, subsets_neg

  def cross_valid_foldfiles(self, cls, types=None, fold_no=0, directory=None, extension=None):
    """ Returns two dictionaries: one with the names of the files of the validation subset in one fold, and one with the names of the files in the training subset of that fold. The number of the cross_validation fold is given as a parameter.

    .. deprecated:: 1.1.0

      This function is *deprecated*, use :py:meth:`.Database.objects` instead.

    Keyword parameters:

    cls
      The class of the samples: 'real' or 'attack'

    types
      Type of the database that is going to be used: 'warped', 'cut' or 'video' or a tuple of these

    fold_no
      Number of the fold

    directory
      This parameter will be prepended to all the filenames which are going to be returned by this procedure

    extension
      This parameter will be appended to all the filenames which are going to be returned by this procedure
  """

    import warnings
    warnings.warn("The method Database.cross_valid_foldfiles() is deprecated, use Database.cross_valid_foldobjects() for more powerful object retrieval", DeprecationWarning)

    VALID_TYPES = self.types

    if cls == 'real':
      infilename = self.get_file(os.path.join(self.foldsdir, 'real.txt'))
    else:
      types = self.check_validity(types, "type", VALID_TYPES, VALID_TYPES)
      if 'warped' in types and 'cut' in types and 'video' in types:
        infilename = self.get_file(os.path.join(self.foldsdir, 'cut_warped_video_attack.txt'))
      elif 'warped' in types and 'cut' in types:
        infilename = self.get_file(os.path.join(self.foldsdir, 'cut_warped_attack.txt'))
      else:
        infilename = self.get_file(os.path.join(self.foldsdir, types[0]+'_attack.txt'))

    lines = open(infilename, 'r').readlines()
    files_val = {} # the keys in the both dictionaries are just pro-forma, for compatibility with other databases
    files_train = {}
    k_val = 0; k_train = 0 # simple counters

    def make_path(stem, directory, extension):
      if not extension: extension = ''
      if directory: return os.path.join(directory, stem + extension)
      return stem + extension

    for line in lines:
      words = line.rstrip('\n\t').split('\t')
      if int(words[1]) == fold_no:
        files_val[k_val] = make_path(words[0], directory, extension); k_val += 1
      else:
        files_train[k_train] = make_path(words[0], directory, extension); k_train += 1

    return files_val, files_train

  def cross_valid_foldobjects(self, cls, types=None, qualities=None, fold_no=0):
    """ Returns two dictionaries: one with the names of the files of the validation subset in one fold, and one with the names of the files in the training subset of that fold. The number of the cross_validation fold is given as a parameter.

    Keyword parameters:

    cls
      The class of the samples: 'real' or 'attack'

    types
      Type of the database that is going to be used: 'warped', 'cut' or 'video' or a tuple of these

    qualities
      Either "low", "normal" or "high" or any combination of those (in a
      tuple). Defines the qualities of the videos in the database that are going to be used. If you set this
      parameter to the value None, the videos of all qualities are returned ("low", "normal", "high").

    fold_no
      Number of the fold
  """

    VALID_TYPES = self.types

    VALID_QUALITIES = self.qualities
    qualities = self.check_validity(qualities, "quality", VALID_QUALITIES, VALID_QUALITIES)

    if cls == 'real':
      infilename = self.get_file(os.path.join(self.foldsdir, 'real.txt'))
    else:
      types = self.check_validity(types, "type", VALID_TYPES, VALID_TYPES)
      if 'warped' in types and 'cut' in types and 'video' in types:
        infilename = self.get_file(os.path.join(self.foldsdir, 'cut_warped_video_attack.txt'))
      elif 'warped' in types and 'cut' in types:
        infilename = self.get_file(os.path.join(self.foldsdir, 'cut_warped_attack.txt'))
      else:
        infilename = self.get_file(os.path.join(self.foldsdir, types[0]+'_attack.txt'))

    lines = open(infilename, 'r').readlines()
    obj_val = []
    obj_train = []

    for line in lines:
      words = line.rstrip('\n\t').split('\t')

      if int(words[1]) == fold_no:
        f = File(words[0], cls, 'dev')
        if f.get_quality() in qualities:
          obj_val.append(f) # the file still belongs to the training set, but is in dev set in cross-validation
      else:
        f = File(words[0], cls, 'train')
        if f.get_quality() in qualities:
          obj_train.append(f)

    return obj_val, obj_train

  def save_by_filename(self, filename, obj, directory, extension):
    """Saves a single object supporting the bob save() protocol.

    .. deprecated:: 1.1.0

      This function is *deprecated*, use :py:meth:`.File.save()` instead.

    This method will call save() on the the given object using the correct
    database filename stem for the given filename

    Keyword Parameters:

    filename
      The unique filename under which the object will be saved. Before calling this method, the method files() should be called (with no directory and extension arguments passed) in order to obtain the unique filenames for each of the files to be saved.

    obj
      The object that needs to be saved, respecting the bob save() protocol.

    directory
      This is the base directory to which you want to save the data. The
      directory is tested for existence and created if it is not there with
      os.makedirs()

    extension
      The extension determines the way each of the arrays will be saved.
    """

    import warnings
    warnings.warn("The method Database.save() is deprecated, use the File object directly as returned by Database.objects() for more powerful object manipulation.", DeprecationWarning)

    from bob.io.base import save

    fullpath = os.path.join(directory, filename + extension)
    fulldir = os.path.dirname(fullpath)
    utils.makedirs_safe(fulldir)
    save(obj, fullpath)

def get_config():
  """Returns a string containing the configuration information.
  """

  import pkg_resources

  packages = pkg_resources.require(__name__)
  this = packages[0]
  deps = packages[1:]

  retval =  "%s: %s (%s)\n" % (this.key, this.version, this.location)
  retval += "  - python dependencies:\n"
  for d in deps: retval += "    - %s: %s (%s)\n" % (d.key, d.version, d.location)

  return retval.strip()

# gets sphinx autodoc done right - don't remove it
__all__ = [_ for _ in dir() if not _.startswith('_')]

