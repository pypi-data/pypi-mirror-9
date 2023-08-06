
import os, time, datetime, getpass, commands
from .Droplet import Droplet

class Backup( object ):
  def __init__( self, dict, droplet ):
    self.droplet          = droplet
    self.route            = self.droplet.name
    self.ssh_user         = ""
    self.ssh_key          = ""
    self.remote_dirs      = []
    self.excludes         = []
    self.remote_dir       = None
    self.backup_dir       = ""
    self.use_ip           = False
    self.user             = getpass.getuser()
    self.home             = os.path.expanduser("~")
    self.snapshot_hour    = 25
    self.snapshots        = 10000

    """ Check the options dict to see if it's for this droplet """
    if self.droplet.name in dict:
      dict = dict[self.droplet.name]

    """ Set the backup options from the dict """
    for attr in dict.keys():
      setattr( self, attr, dict[attr] )
    
    """ We're going to assume root for the ssh_user """
    if self.ssh_user == "": self.ssh_user = "root"

    """ Compatibility for single remote_dir option """
    if self.remote_dir != None:
      self.remote_dirs.append( self.remote_dir )

    """ Connect to the droplet via ip address instead of name """
    if self.use_ip: self.route = droplet.ip_address

    """ Set the default backup_dir to $HOME/Droplets """
    if self.backup_dir == "":
      self.backup_dir = "%s/Droplets" % self.home

    """ Set the default backup_dir to $HOME/Droplets/droplet.name """
    if self.droplet.name not in self.backup_dir:
      self.backup_dir = "%s/%s" % ( self.backup_dir, self.droplet.name )

    """ Create the backup_dir if it doesn't exist """
    if not os.path.exists(self.backup_dir):
      os.makedirs(self.backup_dir)

    """ Find the ssh_key path """
    self.ssh_key = self.__find_ssh_key()

    """ Set snapshot_delete if the user specifies a number of snapshots to keep """
    self.snapshot_delete  = ( self.snapshots >=1 and self.snapshots != 10000 )

    """ Start the droplet backup """
    self.__backup()

  def __log( self, msg ):
    """ Log timestamp  """
    ts = "#####[%s]" % self.droplet.api.timestamp()

    """ Log message  """
    msg = '%s %s\n' % ( ts, msg )

    if self.droplet.freshlog == True:
      log = open( self.droplet.log, 'w' )
      self.droplet.freshlog = False
    else:
      log = open( self.droplet.log, 'a' )

    log.writelines( msg )
    log.close()

  def __which(self, program ):
    """ Find bin program path """
    def is_exe( fpath ):
      return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split( program )
    if fpath:
      if is_exe(program):
        return program
    else:
      for path in os.environ["PATH"].split( os.pathsep ):
        path = path.strip('"')
        exe_file = os.path.join( path, program )
        if is_exe(exe_file):
          return exe_file

    return None

  def __bin_checks( self ):
    """ Programs needed for the backup operations """
    programs = ["ssh", "rsync"]

    """ Check if the programs are installed """
    for program in programs:
      path = self.__which( program )
      if path == None:
        print "%s is not on this system" % program
        return False
    return True

  def __find_ssh_key( self ):
    """ Places to look for the ssh_key """
    this_path = "%s/%s"      % (os.getcwd(), self.ssh_key)
    home_path = "%s/%s"      % (self.home, self.ssh_key)
    ssh_path  = "%s/.ssh/%s" % (self.home, self.ssh_key)

    """ Try to loacate the ssh_key path """
    paths = [ this_path, home_path, ssh_path ]
    for path in paths:
      if os.path.isfile(path):
        return path

  def __options_set( self ):
    """ Make sure that all required options are set """
    options_set = True
    for key in self.__dict__.keys():
      if self.__dict__.get(key) == "":
        options_set = False
        break
    return (self.__bin_checks() and type(self.droplet) == Droplet and options_set)

  def __run_command( self, cmd ):
    """ Return results of running a command """
    return commands.getstatusoutput( cmd )

  def __get_backup_snapshots( self ):
    """
      We're creating a list of droplet snapshots to check
      that only have or template snapshot name in them.
    """
    snapshots = []
    match = "@%s-" % self.droplet.name
    for snapshot in self.droplet.snapshots:
      if match in snapshot.name:
        snapshots.append(snapshot)
    return snapshots
  
  def __remote_dir_check( self, ssh_cmd, remote_dir ):
    result = False
    cmd_result = ""
    """ SSH command to check if remote_dir exists """
    cmd = '%s %s@%s [ -d %s ] && echo True || echo False' % ( ssh_cmd, self.ssh_user, self.route, remote_dir )

    """
      We are going to assume that since the local dir exists of the
      remote_dir, that we don't to need remote in and check that it exists
      anymore. We'll only do this once on the first rsync of the
      remote_dir. (This may bite me in the ass later.)
    """
    local_dir = "%s%s/" % (self.backup_dir, remote_dir)
    if not os.path.exists( local_dir ):
      command, cmd_result = self.__run_command( cmd )
    else:
      command = 0
      cmd_result = "True"

    if "True" in cmd_result:
      """ Create the local_dir of the backup_dir if it doesn't exits """
      local_dir = "%s%s/" % (self.backup_dir, remote_dir)
      if not os.path.exists( local_dir ):
        os.makedirs( local_dir )
      result = True

    return result

  def __rsync( self, ssh_cmd, remote_dir ):
    completed = False
    result = ""
    if self.__remote_dir_check( ssh_cmd, remote_dir ):
      """ SSH option for rsync to use our ssh_key """
      e = '-e "%s"' % ( ssh_cmd )

      excludes = ""
      for x in self.excludes:
        excludes = excludes+" --exclude \"%s\"" % x


      """ The rsync args. some of these may need to be removed. """
      args = '-avz --update%s' % excludes

      cmd = 'rsync %s %s %s@%s:%s/ %s%s' % ( args, e, self.ssh_user, self.route, remote_dir, self.backup_dir, remote_dir )
      command, result = self.__run_command( cmd )
      completed = ( command == 0 )
    else:
      completed = True
      result = "**%s not exist on %s**" % (remote_dir, self.droplet.name)

    
    if completed == False:
      self.__log( "DROPLET_RSYNC_CMD: _%s_" % cmd )
      self.__log( "DROPLET_RSYNC_COMMAND: _%s_" % command )
      self.__log( "DROPLET_RSYNC_RESULT: _%s_" % result )

    else:
      """ Format the output for markdown. """
      if "\nsent" in result: result = result.replace( "\nsent", "sent")

      """ Remove trailing whitespace """
      result = result.replace(" \n", "\n")

      """ More markdown """
      str = "receiving file list ... done"
      if str in result:
        result = result.replace(str,("**%s**" % str) )

      """ Even more markdown """
      if "done**\nsent" not in result:
        result = result.replace("\n", "\n* ")
        self.__log( "DROPLET_RSYNC: _%s_\n* %s\n" % (remote_dir, result) )

    return completed, result

  def __process_rsync( self ):
    completed = False
    result = ""
    if self.__options_set():
      ssh_cmd = 'ssh -oStrictHostKeyChecking=no -i %s' % self.ssh_key

      for remote_dir in self.remote_dirs:
        completed, dir_result = self.__rsync( ssh_cmd, remote_dir )
        if completed: result = result+dir_result
    else:
      result = "MISSING_REMOTE_DIR: %s" % remote_dir
    result = {"id":self.droplet.id,"name":self.droplet.name,"type":"rsync","result":result}
    return completed, result

  def __backup( self ):
    """ Boot the droplet if it's off """
    if self.droplet.status == "off":
      self.droplet.power_on()

    """ Set a start time  for backup operations. """
    self.start = time.time()

    """ Is it time for a snapshot """
    snapshot_hour = ( datetime.datetime.today().hour == self.snapshot_hour )

    """ Set the log file name. """
    self.droplet.log = "%s/%s" % (self.backup_dir, "_backup_log.md")

    """ Clean the log if it's time to create a new snapshot """
    self.droplet.freshlog = snapshot_hour

    """ First log entry """
    self.__log( "DROPLET_BACKUP: _%s_" % self.droplet.name )

    """ Log the route we are using to connect to the droplet. (ip/name) """
    self.__log( "DROPLET_ROUTE: _%s_\n" % self.route )

    """ Run the rsync function """
    completed, result = self.__process_rsync()

    if completed:
      if snapshot_hour:
        """ Set the name of the backup snapshot to be taken. """
        snapshot_name = "@%s-%s" % ( self.droplet.name, self.droplet.api.timestamp() )

        self.__log( "DROPLET_TAKING_SNAPSHOT: _%s_" % snapshot_name )

        """ Take the backup snapshot. """
        completed, result = self.droplet.snapshot( snapshot_name )

        if completed:
          self.__log( "DROPLET_SNAPSHOT_SUCCESS: _%s_" % completed )

          """ Check if we need to delete old snapshots. """
          if self.snapshot_delete == True:

            """ Get a list of backup snapshots only """
            snapshots = self.__get_backup_snapshots()

            """ Get a count of the backup snapshots """
            count = len(snapshots)

            """
              Keep deleting the oldest snapshot, until we have the
              number of snapshots we want to keep.
            """

            while count > self.snapshots:
              """ Delete the first snapshot in the list """
              completed, result = self.droplet.destroy_snapshot( snapshots[0] )

              self.__log( "DROPLET_SNAPSHOT_DELETED: id: _%s_ name: _%s_" % (result["id"], result["name"]) )

              """ Update our backup snapshots list """
              snapshots = self.__get_backup_snapshots()

              """ Update our count """
              count = len(snapshots)
    else:
      """ At this point we don't know, why the rsync failed, so we'll log it. """
      self.__log( "DROPLET_RSYNC_PROBLEM:\n%s" % result )

    """ How long it's taken to backup in rounded seconds """
    backup_time = int((round(( time.time() - self.start ),0)))

    if backup_time > 60:
      """ Let's log pretty minutes """
      backup_time = "time: %s minutes" % int((round((backup_time/60),0)))

    else:
      """ Let's log pretty seconds """
      backup_time = "time: %s seconds" % backup_time

    """ Let the user know how many api calls were used """
    info = "%s - api calls: %s" % (backup_time, self.droplet.api.calls)

    self.__log( "DROPLET_BACKUP_FINISHED: _%s_" % info )
    self.__log( '**=================================**\n' )

    """ We reset this for the next droplet in a for loop """
    self.droplet.api.calls = 1

  @property
  def details(self):
    details = ""
    for key in self.__dict__.keys():
      if "token" not in key:
        details = details+"%s: %s\n" % ( key, self.__dict__.get(key) )
    self._details = details
    return self._details
  