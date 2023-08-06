
from .Action import Action
from .Api import Api
import sys

class Image( object ):
  def __init__( self, token="", id="", dict={}, api=None ):
    """
      Image id can also be an image slug such as "ubuntu-14-04-x64".
    """
    self.__token = token
    self.id = id
    self.load( token, id, dict, api )
    self.path = "/images/%s" % self.id
    self.actions_path = "/images/%s/actions" % self.id

  @property
  def actions(self):
    if hasattr(self, "_actions") == False:
      self._actions = self.get_actions()
    return self._actions
  
  @actions.setter
  def actions(self, value):
    self._actions = value

  def load( self, token="", id="", dict={}, api=None ):
    if dict == {} and self.__token != "" and id != "":
      self.api = Api( self.__token )
      dict = self.api.call( "/images/%s" % id )["image"]
    elif hasattr(self, "api"):
      dict = self.api.call( "/images/%s" % self.id )["image"]
    elif api != None:
      self.api = api
    elif dict == {} and id == "" and token == "":
      if token == "":
        sys.exit("NO TOKEN PROVIDED")
      sys.exit("NO IMAGE ID PROVIDED")
    if dict != {}:
      for attr in dict.keys():
        setattr( self, attr, dict[attr] )

  def destroy( self ):
    params = {"type":sys._getframe().f_code.co_name}
    data = self.api.call(
      self.path, "DELETE",
      params
    )
    self.api.wait( 1 )
    info = {"id":self.id,"name":self.name}
    data.update(info)
    data.update(params)
    completed = ( data["status"] == "completed" )
    return completed, data

  def transfer( self, new_region ):
    completed, data = self.api.call(
      self.actions_path, "POST",
      {"type":sys._getframe().f_code.co_name,
      "region":new_region}
    )
    return completed, data

  def name( self, new_name ):
    completed, data = self.api.call(
      self.path, "POST",
      {sys._getframe().f_code.co_name:new_name}
    )
    return completed, data

  def get_actions( self ):
    self.actions = []
    data = self.api.call( self.actions_path )["actions"]
    for dict in data:
      self.actions.append( Action(dict) )
    return self.actions

  @property
  def details(self):
    details = ""
    for key in self.__dict__.keys():
      if "token" not in key:
        details = details+"%s: %s\n" % ( key, self.__dict__.get(key) )
    self._details = details
    return self._details
    