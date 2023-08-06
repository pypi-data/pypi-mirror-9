
import sys, json, requests, datetime, time
from .Action import Action

class Api( object ):
  def __init__( self, token="" ):
    if token == "": sys.exit( "NO TOKEN PROVIDED" )
    self.__token    = token
    self.__raw      = None
    self.__base_url = "https://api.digitalocean.com/v2"
    self.user_agent = "python-dio"
    self.response   = {}
    self.calls      = 0
    self.remaining  = 1
    self.delay      = 5

  def __headers( self ):
    return {
      "Authorization" : "Bearer %s" % self.__token,
      "Content-Type": "application/json",
      "User-Agent": self.user_agent
    }

  def __process_action( self, data, path ):
    action = Action( data )
    completed = False
    path = "%s/%s" % (path, action.id)
    while completed == False:
      self.wait( self.delay )
      data = self.__call( path, "GET", {} )
      if data.get("action"):
        action = Action( data["action"] ) 
        completed = (action.status == "completed")
      else:
        completed = True
    return completed, data["action"]

  def __call( self, path, method, params ):
    if self.remaining >= 1:
      """ Going to test this for awhile and return 1000 results per page """
      url = "%s%s?per_page=1000&private=true" % ( self.__base_url, path )

      payload = json.dumps(params)

      if method == "GET":
        self.__raw = requests.get(url, params=None,
          headers=self.__headers(), verify=True )

      elif method == "POST":
        self.__raw = requests.post(url, data=payload,
          headers=self.__headers(), verify=True )

      elif method == "DELETE":
        self.__raw = requests.delete(url, data=payload,
          headers=self.__headers(), verify=True )

      if self.__raw.status_code < 204:
        self.response = self.__raw.json()
      elif self.__raw.status_code == 204:
        self.response = self.completed()
      elif self.__raw.status_code >= 400:
        error_msg = {"message": "ERROR"}
        error_msg.update( {"api_calls": self.calls} )
        error_msg.update( {"remaining_calls": self.remaining} )
        error_msg.update( {"url": url} )
        error_msg.update( {"payload": payload} )
        error_msg.update( {"headers": self.__raw.headers} )
        error_msg.update( {"content": self.__raw.content} )

        """ return a dict if we have errors """
        self.response = error_msg

      if "ratelimit-remaining" in self.__raw.headers:
        self.remaining = self.__raw.headers['ratelimit-remaining']
      self.calls = self.calls+1
    else:
      sys.exit("API Rate limit exceeded.")

    return self.response

  def call( self, path="", method="GET", params={} ):
    data = None
    data = self.__call( path, method, params )
    if data != None:
      if data.get("action"):
        return self.__process_action( data["action"], path )
    return data

  def wait( self, delay=5 ):
    time.sleep( delay )

  def completed( self ):
    return json.loads(json.dumps({"status" : "completed"}))

  def timestamp( self ):
    return str( datetime.datetime.fromtimestamp(
      int( time.time() ) ).strftime( '%Y-%m-%d-%H%M' )
    )

  @property
  def details(self):
    details = ""
    for key in self.__dict__.keys():
      if "token" not in key:
        details = details+"%s: %s\n" % ( key, self.__dict__.get(key) )
    self._details = details
    return self._details
    