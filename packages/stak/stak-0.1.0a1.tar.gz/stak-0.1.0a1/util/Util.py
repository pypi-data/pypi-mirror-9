import click
import yaml
import os
import re
import subprocess

# displays a list of data.
# you can control how the data is output by 
def display_list( string, list , transform = ( lambda index,value: click.style( value, bold=True, fg="cyan" ) ) ):
  # list devices
    click.echo( click.style( string , bold=True) )
    for index, value in enumerate( list ):
      click.echo( "  " + str(index) + ") " + transform( index, value ) )

# calls a shell command and returns the output
def call_and_return( *args ):
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