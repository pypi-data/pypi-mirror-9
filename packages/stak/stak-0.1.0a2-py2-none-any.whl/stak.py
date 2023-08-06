import os
import click
import time
import sys
from util import Config
from util import Project
from util import Util
from distutils import spawn
from commands import *

#
# Stak command group
#
@click.group()
@click.option('--verbose', is_flag=True , help="Prints extra information for each command.")
@click.option('--stak-directory', type=click.Path(), help="Location of your .stak directory.")
def stak( verbose, stak_directory):
  """STAK is a collection of tools for building projects on embedded Linux"""

  Config.verbose = verbose
  Config.stak_directory = stak_directory
  Config.local_data = Config.load( )
  Config.load_globals( )
  Config.current_device = None

  # make sure we have the following directories
  # ~/.stak
  # ~/.stak/images
  Util.create_folders_if_nonexistent( "~/.stak", "~/.stak/images" )


  # test if honcho exists
  if not spawn.find_executable("honcho"):
    click.echo("Could not find honcho executable. Exiting...")
    sys.exit()


#def iterate():
#  number = 0
#  while number < 1000:
#    yield number
#    number+=1
#
#def show_iteration(item):
#  if item:
#    return "Iteration: %d" % item
#
#@stak.command()
#def jump():
#  with click.progressbar(iterable=iterate(), width=10, show_percent=False,
#                          show_eta=False, item_show_func=show_iteration,
#                          fill_char=click.style('#', fg='magenta')) as bar:
#    for item in bar:
#      time.sleep(0.0313)

#
# Create command
#
@stak.command()
@click.argument('project')
@click.option('--language',
              default=None,
              type=click.Choice( Config.example_languages )
  )
def create( project, language ):
  """Creates a new STAK project."""
  Create.create( project, language )

#
# device [command]
#
@stak.group()
def device():
  """Tools for managing hardware running STAK OS"""
  pass


@device.command("setup-card")
def setup_card():
  """Downloads and flashes the STAK OS"""
  Devices.setup_card()
#
# device add [device]
#
@device.command()
@click.argument('device')
def add( device ):
  Devices.add( device )
#
# device remove [device]
#
@device.command()
@click.argument('device')
def remove( device ):
  """Remove device from project"""
  Devices.remove( device )

@device.command("set-default")
@click.argument('device')
def set_default( device ):
  Devices.set_default_device( device )
#
#
# device list
#
@device.command()
def list( ):
  """List all STAK devices on your network"""
  Devices.list( )

#
# device discover
#
#   search the network for any devices broadcasting a stak zeroconf service
#
@device.command()
def discover( ):
  Devices.discover()


@device.command()
@click.argument('name', default=None, required=False)
@click.argument('parameter', type=click.STRING)
@click.argument('value', type=click.STRING)
def set( name, parameter, value ):
  if name:
    Devices.set_property(name, parameter, value)

@device.command()
@click.argument('name', default=None, required=False)
@click.argument('parameter', type=click.STRING)
def get( name, parameter ):
  if name:
    Devices.get_property(name, parameter)


#
# Build command
#
@stak.command()
@click.argument('project',
                required=False,
                default=os.getcwd(),
                type=click.Path()
  )
@click.option('--target',
                required=False,
                default="debug",
                type=click.STRING
  )
def build( project, target ):
  """Cross-compile your project"""
  Project.build( project, target )
  # click.echo("Comming Soon to Terminal Near You...")
#
# Run command
#
@stak.command()
@click.argument('project',
                required=False,
                default=os.getcwd(),
                type=click.Path()
  )
@click.option('--target',
                required=False,
                default="debug",
                type=click.STRING
  )
@click.option('--device',type=click.STRING)
def run( project, target, device ):
  """Run code built with STAK BUILD on device"""
  Project.run( project, target )

#
# ssh command
#
@stak.command()
@click.argument('project',
                required=False,
                default=os.getcwd(),
                type=click.Path()
  )
@click.option('--target',
                required=False,
                default="debug",
                type=click.STRING
  )
@click.option('--device',type=click.STRING)
def ssh( project, target, device ):
  """Open SSH session on device"""
  Project.ssh( project, target )


#
# Deploy command
#
@stak.command()
@click.argument('project',
                required=False,
                default=os.getcwd(),
                type=click.Path()
  )
@click.option('--target',
                required=False,
                default="debug",
                type=click.STRING
  )
@click.option('--device',type=click.STRING)
def deploy( project, target, device ):
  """Installs project as system service that runs on BOOT"""
  Project.deploy( project, target )