import click
import yaml
import os, sys
import re
import subprocess
import pwd, grp
from stak.util import DD

# displays a list of data.
# you can control how the data is output by 
def display_list( string, list , transform = ( lambda index,value: click.style( value, bold=True, fg="cyan" ) ) ):
  # list devices
    click.secho( string , bold=True)
    for index, value in enumerate( list ):
      click.echo( "  " + str(index) + ") " + transform( index, value ) )

# calls a shell command and returns the output
def call_and_return( *args, **kwargs ):
  if "directory" in kwargs:
    return subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=kwargs["directory"]).stdout.readlines()
  else:
    return subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.readlines()


# utility function for searching a list for a regex.
# you can also pass a lambda in to control how the data
# is transformed before being added to the resulting list
def find_list_items_containing( needle, haystack, transform=( lambda m: m.group() ) ):
  output = []
  for item in haystack:
    matches = re.search( needle, item )
    if matches:
      output.append( transform( matches ) )
  if len(output) == 0:
    return None
  return output


def cp( src, dest ):
  call_and_return( "cp",src, dest )

def create_folders_if_nonexistent( *folders ):
  for folder in folders:
    folder_expanded = os.path.expanduser( folder )
    if not os.path.exists( folder_expanded ):
      os.mkdir( folder_expanded )


def dd( src, dst ):
  # defaults
  iput  = DD.FileIo('/dev/stdin', 'r')
  oput  = DD.FileIo('/dev/stdout', 'a')
  ts    = None
  bs    = 2048000 # 4000KB
  count = None
  skip  = None
  quiet = False

  if os.path.isfile(src):
    iput = DD.FileIo(src, 'r')
  else:
    if src.find('http'):
      iput = DD.HttpIo( src )
    elif src.find('ftp'):
      iput = DD.FtpIo ( src )

  oput = DD.FileIo(dst, 'w+')
  
  obj = DD.Transfer(iput, oput, ts, bs, count, skip, quiet)
  obj.start()

def raise_privileges():
  args = ['sudo', sys.executable] + sys.argv + [os.environ]
  # the next line replaces the currently-running process with the sudo
  os.execlpe('sudo', *args)

#Throws OSError exception (it will be thrown when the process is not allowed
#to switch its effective UID or GID):
def drop_privileges():
    if os.getuid() != 0:
        # We're not root so, like, whatever dude
        return

    # Get the uid/gid from the name
    user_name = os.getenv("SUDO_USER")
    pwnam = pwd.getpwnam(user_name)

    # Remove group privileges
    os.setgroups([])

    # Try setting the new uid/gid
    os.setgid(pwnam.pw_gid)
    os.setuid(pwnam.pw_uid)

    #Ensure a reasonable umask
    old_umask = os.umask(0o22)