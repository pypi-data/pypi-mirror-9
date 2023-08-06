
from .Records import Records

class Domain( object ):
  def __init__( self, dict={}, api=None ):
    for attr in dict.keys():
      setattr( self, attr, dict[attr] )
    if api != None: self.api = api
    self.path = "/domains/%s" % self.name
    self.records_path = "%s/records" % self.path

  @property
  def records(self):
    ivar = "_%s" % sys._getframe().f_code.co_name
    if hasattr(self, ivar) == False:
      self._records = self.get_all_records()
    return self._records

  @records.setter
  def records(self, value):
    self._records = value

  def get_all_records( self ):
    self.records = []
    data = self.api.call( self.records_path )["domain_records"]
    for dict in data:
      record = Records(dict)
      if record not in self.records:
        self.records.append( record )
    return self.records

  @property
  def details(self):
    details = ""
    for key in self.__dict__.keys():
      if "token" not in key:
        details = details+"%s: %s\n" % ( key, self.__dict__.get(key) )
    self._details = details
    return self._details
