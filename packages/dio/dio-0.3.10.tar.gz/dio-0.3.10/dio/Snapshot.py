from .Image import Image

class Snapshot( Image ):
  def __init__( self, token="", id="", dict={}, api=None ):
    super(Snapshot, self).__init__( token, id, dict, api )
  @property
  def details(self):
    details = ""
    for key in self.__dict__.keys():
      if "token" not in key:
        details = details+"%s: %s\n" % ( key, self.__dict__.get(key) )
    self._details = details
    return self._details
