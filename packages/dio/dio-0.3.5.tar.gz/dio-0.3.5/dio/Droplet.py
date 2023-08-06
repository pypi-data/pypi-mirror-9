
import sys

from .Action import Action
from .Api import Api
from .Kernel import Kernel
from .Region import Region
from .Size import Size
from .Image import Image
from .Snapshot import Snapshot
from .Network import Network

class Droplet( object ):
  def __init__( self, token="", id="", dict={}, api=None, sizes=None, options={} ):
    self.__token = token
    self.id = id
    self.load( token, id, dict, api, sizes )
    self.path = "/droplets/%s" % self.id
    self.actions_path = "/droplets/%s/actions" % self.id
    self.kernels_path = "/droplets/%s/kernels" % self.id

  @property
  def snapshots(self):
    if hasattr(self, "_snapshots") == False:
      self._snapshots = self.get_snapshots()
    return self._snapshots
  
  @snapshots.setter
  def snapshots(self, value):
    self._snapshots = value

  @property
  def available_kernels(self):
    if hasattr(self, "_available_kernels") == False:
      self._available_kernels = self.get_available_kernels()
    return self._available_kernels
  
  @available_kernels.setter
  def available_kernels(self, value):
    self._available_kernels = value

  @property
  def available_sizes(self):
    if hasattr(self, "_available_sizes") == False:
      self._available_sizes = self.get_available_sizes()
    return self._available_sizes

  @available_sizes.setter
  def available_sizes(self, value):
    self._available_sizes = value

  @property
  def actions(self):
    if hasattr(self, "_actions") == False:
      self._actions = self.get_actions()
    return self._actions
  
  @actions.setter
  def actions(self, value):
    self._actions = value

  def __status( self, status):
    """
      Private function to check the droplet status against
      the desired status. This means that after performing
      an action on the droplet, it will check to make sure
      the droplet.status is equal to the desired status
      before continuing.
    """
    self.load()
    completed = (self.status == status)
    while completed == False:
      self.api.wait()
      self.load()
      completed = (self.status == status)
    return completed

  def __networks( self ):
    """
      Function to assign network properties to the droplet.
    """
    networks = []
    for key in self.networks:
      arr = self.networks[key]
      for dict in arr:
        nic = Network( dict, ("%s"%key) )
        networks.append( nic )
    self.networks = networks
    for nic in self.networks:
      if nic.ipv == "v4" and nic.type == "public":
        self.ip_address = nic.ip_address
      if nic.ipv == "v4" and nic.type == "private":
        self.private_ip_address = nic.ip_address
      if nic.ipv == "v6" and nic.type == "public":
        self.ipv6_address = nic.ip_address
      if nic.ipv == "v6" and nic.type == "private":
        self.private_ipv6_address = nic.ip_address

  def load( self, token="", id="", dict={}, api=None, sizes=None ):
    if sizes is None:
      sizes = self.available_sizes
    if dict == {} and token != "" and id != "":
      self.api = Api( token )
      dict = self.api.call( "/droplets/%s" % id )["droplet"]
    elif hasattr(self, "api"):
      dict = self.api.call( "/droplets/%s" % self.id )["droplet"]
    elif api != None:
      self.api = api
    else:
      if token == "": sys.exit("NO TOKEN PROVIDED")
      sys.exit("NO DROPLET ID PROVIDED")
    if dict != {}:
      for attr in dict.keys():
        if attr == 'size_slug':
          setattr( self, 'size', dict[attr] )
        else:
          setattr( self, attr, dict[attr] )
      self.kernel     = Kernel( self.kernel )
      self.region     = Region( self.region )
      #self.size       = filter( lambda size: size.slug == self.size, sizes )[0]
      # changed back
      self.size       = Size( self.size )
      self.image      = Image( self.image )
      self.__networks()

  def reboot( self ):
    if self.status == "off":
      completed, data = self.power_on()
    else:
      completed, data = self.api.call(
        self.actions_path, "POST",
        {"type":sys._getframe().f_code.co_name}
      )
      completed = self.__status( "active" )
    return completed, data

  def restart( self ):
    """ just because """
    return self.reboot()

  def power_cycle( self ):
    if self.status == "off":
      completed, data = self.power_on()
    else:
      completed, data = self.api.call(
        self.actions_path, "POST",
        {"type":sys._getframe().f_code.co_name}
      )
      completed = self.__status( "active" )
    return completed, data
  
  def shutdown( self ):
    expected_status = "off"
    if self.status == expected_status:
      completed = True
      data = self.api.completed()
    else:
      completed, data = self.api.call(
        self.actions_path, "POST",
        {"type":sys._getframe().f_code.co_name}
      )
      completed = self.__status( expected_status )
    return completed, data

  def power_off( self ):
    expected_status = "off"
    if self.status == expected_status:
      completed = True
      data = self.api.completed()
    else:
      completed, data = self.api.call(
        self.actions_path, "POST",
        {"type":sys._getframe().f_code.co_name}
      )
      completed = self.__status( expected_status )
    return completed, data

  def power_on( self ):
    expected_status = "active"
    if self.status == expected_status:
      completed = True
      data = self.api.completed()
    else:
      completed, data = self.api.call(
        self.actions_path, "POST",
        {"type":sys._getframe().f_code.co_name}
      )
      completed = self.__status( expected_status )
    return completed, data
  
  def password_reset( self ):
    completed, data = self.api.call(
      self.actions_path, "POST",
      {"type":sys._getframe().f_code.co_name}
    )
    return completed, data
  
  def resize( self, size ):
    self.shutdown()
    completed, data = self.api.call(
      self.actions_path, "POST",
      {"type":sys._getframe().f_code.co_name,
      "size":size}
    )
    self.power_on()
    return completed, data
  
  def restore( self, image_id ):
    completed, data = self.api.call(
      self.actions_path, "POST",
      {"type":sys._getframe().f_code.co_name,
      "image":image_id}
    )
    self.load()
    return completed, data
  
  def rebuild( self, image_id ):
    completed, data = self.api.call(
      self.actions_path, "POST",
      {"type":sys._getframe().f_code.co_name,
      "image":image_id}
    )
    self.load()
    return completed, data
  
  def rename( self, new_name ):
    completed, data = self.api.call(
      self.actions_path, "POST",
      {"type":sys._getframe().f_code.co_name,
      "name":new_name}
    )
    self.load()
    return completed, data
  
  def change_kernel( self, new_kernel ):
    self.shutdown()
    completed, data = self.api.call(
      self.actions_path, "POST",
      {"type":sys._getframe().f_code.co_name,
      "name":new_kernel}
    )
    self.power_on()
    return completed, data
  
  def enable_ipv6( self ):
    completed, data = self.api.call(
      self.actions_path, "POST",
      {"type":sys._getframe().f_code.co_name}
    )
    self.load()
    completed = self.__status( "active" )
    return completed, data
  
  def disable_backups( self ):
    completed, data = self.api.call(
      self.actions_path, "POST",
      {"type":sys._getframe().f_code.co_name}
    )
    self.load()
    return completed, data
  
  def enable_private_networking( self ):
    completed, data = self.api.call(
      self.actions_path, "POST",
      {"type":sys._getframe().f_code.co_name}
    )
    return completed, data
  
  def snapshot( self, snapshot_name="" ):
    """
      Create a default snapshot name using a time stamp
    """
    if snapshot_name == "":
      snapshot_name = "%s-%s" % ( self.name, self.api.timestamp() )
    """
      Function to create a snapshot of the droplet. No need
      to power off the droplet first, the function will do
      it for you.
    """
    self.shutdown()
    """
      Creating snapshots take awhile, and can use a lot of api
      calls while checking action status. So we up the api.delay
      to 30 seconds and set it back to it's original value after
      the action is complete.
    """
    delay = self.api.delay
    self.api.delay = 30
    completed, data = self.api.call(
        self.actions_path, "POST",
        {"type":sys._getframe().f_code.co_name,
        "name":snapshot_name}
      )
    """
      When creating snapshots, we also have to wait for the droplet
      to power up, so let's do a check for that befor returning the data.
    """
    self.api.delay = delay
    completed = self.__status( "active" )
    """
      We have snapshots, so let's retrieve them.
    """
    self.get_snapshots()
    data.update({"snapshot_name":snapshot_name})
    return completed, data

  def destroy_snapshot( self, snapshot ):
    """
      destroying the snapshot this way allows us to update the
      droplet.snapshots
    """
    completed, data = snapshot.destroy()
    data.update({"id":snapshot.id, "name":snapshot.name})
    self.load()
    self.get_snapshots()
    return completed, data

  def get_snapshots( self ):
    self.snapshots = []
    for id in self.snapshot_ids:
      data = self.api.call( "/images/%s" % id)["image"]
      snapshot = Snapshot( self.__token, "", data, self.api )
      self.snapshots.append( snapshot )
    return self.snapshots

  def get_actions( self ):
    self.actions = []
    data = self.api.call( self.actions_path )["actions"]
    for dict in data:
      self.actions.append( Action(dict) )
    return self.actions
  
  def get_available_kernels( self ):
    self.available_kernels = []
    data = self.api.call( self.kernels_path)["kernels"]
    for dict in data:
      kernel = Kernel( dict )
      self.available_kernels.append( kernel )
    return self.available_kernels

  def get_available_sizes( self ):
    self.available_sizes = []
    data = self.api.call( '/sizes')["sizes"]
    for dict in data:
      size = Size( dict )
      self.available_sizes.append( size )
    return self.available_sizes

  def delete( self, prompt=True ):
    """
      After extensivly testing digitalocean's droplet restore function
      to restore a production droplet that was deleted, I decided to
      require user input to delete a droplet. ;-)
      
      However, if you're are really confident, you can bypass the prompt.
      [ YOU HAVE BEEN WARNED!!! ]
    """
    info = {"id":self.id,"name":self.name}
    delete_droplet = False
    if prompt == True:
      droplet_name = "%s" % raw_input("[WARNING] IF YOU ARE SURE YOU WANT TO DELETE %s TYPE THE DROPLET NAME: " % self.name)
      if droplet_name == self.name:
        delete_droplet = True
    else:
      delete_droplet = True

    if delete_droplet == True:
      data = self.api.call(
        self.path, "DELETE", {}
      )
      self.api.wait( 1 )
      params = {"type":sys._getframe().f_code.co_name}
      data.update(info)
      data.update(params)
      completed = ( data["status"] == "completed" )
    else:
      data = {"status":"user_rejected","type":"delete"}
      data.update(info)
      completed = ( data["status"] == "completed" )
    return completed, data

  @property
  def details(self):
    details = ""
    for key in self.__dict__.keys():
      if "token" not in key:
        details = details+"%s: %s\n" % ( key, self.__dict__.get(key) )
    self._details = details
    return self._details
