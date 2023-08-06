
from .Api import Api
from .Region import Region
from .Size import Size
from .Droplet import Droplet
from .Image import Image
from .Domain import Domain
from .SSHKey import SSHKey

class Manager( object ):
  def __init__( self, token="", ignore_list=[] ):
    if token == "": sys.exit( "NO TOKEN PROVIDED" )
    """
      Pass in an array of droplets you would like to ignore.
      This is great when working on a dev droplet and want
      ignore production droplets.
    """
    self.__token = token
    self.api = Api( token )
    self.ignore_list = ignore_list

  @property
  def droplets(self):
    if hasattr(self, "_droplets") == False:
      self._droplets = self.get_all_droplets()
    return self._droplets
  
  @droplets.setter
  def droplets(self, value):
    self._droplets = value

  @property
  def domains(self):
    if hasattr(self, "_domains") == False:
      self._domains = self.get_all_domains()
    return self._domains
  
  @domains.setter
  def domains(self, value):
    self._domains = value

  @property
  def regions(self):
    if hasattr(self, "_regions") == False:
      self._regions = self.get_all_regions()
    return self._regions
  
  @regions.setter
  def regions(self, value):
    self._regions = value

  @property
  def sizes(self):
    if hasattr(self, "_sizes") == False:
      self._sizes = self.get_all_sizes()
    return self._sizes
  
  @sizes.setter
  def sizes(self, value):
    self._sizes = value

  @property
  def images(self):
    if hasattr(self, "_images") == False:
      self._images = self.get_all_images()
    return self._images
  
  @images.setter
  def images(self, value):
    self._images = value

  @property
  def ssh_keys(self):
    if hasattr(self, "_ssh_keys") == False:
      self._ssh_keys = self.get_all_ssh_keys()
    return self._ssh_keys
  
  @ssh_keys.setter
  def ssh_keys(self, value):
    self._ssh_keys = value

  def __ignore( self, droplet_name="", droplet_id=""  ):
    """
      Function to check if droplet is to be ignored when
      adding droplets to self.droplets.
    """
    match = False
    if len(self.ignore_list):
      for d in self.ignore_list:
        if droplet_name == d or droplet_id == d:
          match = True
          break
    return match

  def get_all_regions( self ):
    self.regions = []
    data = self.api.call("/regions")["regions"]
    for dict in data:
      self.regions.append( Region(dict) )
    return self.regions

  def get_all_sizes( self ):
    self.sizes = []
    data = self.api.call("/sizes")["sizes"]
    for dict in data:
      self.sizes.append( Size( dict ) )
    return self.sizes

  def get_all_droplets( self ):
    """
      Function to return a list of all droplets as well as
      assign them to self.droplets.
    """
    self.droplets = []
    data = self.api.call("/droplets")["droplets"]
    for dict in data:
      if self.__ignore( dict["name"], dict["id"] ) == False:
        droplet = Droplet( self.__token, "", dict, self.api, self.sizes )
        self.droplets.append( droplet )
    return self.droplets

  def get_all_images( self ):
    """
      Function to return a list of all images as well as
      assign them to self.images. This will get default
      images too.
    """
    self.images = []
    data = self.api.call("/images")
    # not going to use pagination... for now
    """
    pages = data["links"]["pages"]["last"].split("=")[-1]
    key, values = data.popitem()
    for page in range(2, int(pages) + 1):
      path = "/images?page=%s" % page
      new_data = self.api.call( path )
      more_values = new_data.values()[0]
      for value in more_values:
        values.append(value)
      data = {}
      data[key] = values
    """
    for dict in data["images"]:
      image = Image( self.__token, "", dict, self.api )
      if image not in self.images:
        self.images.append( image )

    return self.images

  def get_all_domains( self ):
    self.domains = []
    data = self.api.call("/domains")["domains"]
    for dict in data:
      domain = Domain( dict, self.api )
      if domain not in self.domains:
        self.domains.append( domain )
    return self.domains

  def get_all_ssh_keys( self ):
    self.ssh_keys = []
    data = self.api.call("/account/keys/")["ssh_keys"]
    for dict in data:
      ssh_key = SSHKey(dict)
      if ssh_key not in self.ssh_keys:
        self.ssh_keys.append( SSHKey(dict) )
    return self.ssh_keys

  def find_images( self, query ):
    results = []
    for image in self.images:
      if all( i.lower() in image.name.lower() for i in query ) or all( i.lower() in image.distribution.lower() for i in query ):
        results.append( image )

    return results

  def create_droplet( self, name, region, size, image,
    backups=False, ipv6=False, private_networking=False ):
    keys = []
    self.get_all_ssh_keys()
    for key in self.ssh_keys:
      if key.id not in keys:
        keys.append( key.id )
    params = {
      "name":name, "region":region, "size":size, "image":image,
      "ssh_keys":keys, "backups":backups, "ipv6":ipv6,
      "private_networking":private_networking
      }
    data = self.api.call("/droplets", "POST", params )["droplet"]
    self.get_all_droplets()
    for droplet in self.droplets:
      if droplet.name == name:
        while droplet.status != "active":
          droplet.load()
          self.api.wait( 10 )
    return True, data

  def delete_droplet( self, droplet, prompt=True ):
    completed, data = droplet.delete( prompt )
    self.get_all_droplets()
    return completed, data

  def create_domain( self, name, ip_address ):
    completed = False
    for domain in self.domains:
      if domain.name == name: return False, {"message":"domain already exists"}
    path = "/domains"
    params = {"name":name,"ip_address":ip_address}
    data = self.api.call( path, "POST", params )["domain"]
    if data: completed = True
    return completed, data

  @property
  def details(self):
    details = ""
    for key in self.__dict__.keys():
      if "token" not in key:
        details = details+"%s: %s\n" % ( key, self.__dict__.get(key) )
    self._details = details
    return self._details
