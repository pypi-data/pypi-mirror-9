import click
import yaml
import os
import re
import subprocess
from stak.util import DD

# displays a list of data.
# you can control how the data is output by 
def display_list( string, list , transform = ( lambda index,value: click.style( value, bold=True, fg="cyan" ) ) ):
  # list devices
    click.echo( click.style( string , bold=True) )
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
