
class Network( object ):
  def __init__( self, dict={}, ipv=None):
    for attr in dict.keys(): setattr( self, attr, dict[attr] )
    self.ipv = ipv
  @property
  def details(self):
    details = ""
    for key in self.__dict__.keys():
      if "token" not in key:
        details = details+"%s: %s\n" % ( key, self.__dict__.get(key) )
    self._details = details
    return self._details
    