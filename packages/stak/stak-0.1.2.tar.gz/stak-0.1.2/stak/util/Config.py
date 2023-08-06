import click
import yaml
import os

global_config_file = os.path.expanduser( "~/.stak/config.yml" )
example_languages = [ 'c', 'c++', 'python', 'javascript' ]
global_data = {}
local_data = {}
verbose = False
stak_directory = click.Path('~')

def load_globals():
  global global_data, global_config_file
  if os.path.isfile( global_config_file ):
    global_file = click.open_file( global_config_file, "r+", lazy=True, encoding = "utf-8")
    if global_file:
      config_data = yaml.safe_load( global_file.read() )
      global_data = config_data
    #   if config.data is None:
    #     config.data = {}  
    #   if config.data.get('devices', None) is None:
    #     config.data["devices"] = {}
  else:
    global_file = click.open_file("stak.yml", "w", lazy=True, encoding = "utf-8")
    global_data = {}

def save_globals( ):
  global global_data, global_config_file
  config_file = click.open_file( global_config_file, "w", lazy=True, encoding = "utf-8" )
  yaml.safe_dump( global_data, config_file, default_flow_style=False, encoding='utf-8', allow_unicode=True )

def save( directory = None, config_data = None ):
  global local_data
  if not directory:
    directory = os.getcwd()
  if not config_data:
    config_data = local_data

  local_file = click.open_file( directory + "/stak.yml", "w", lazy=True, encoding = "utf-8")
  yaml.safe_dump( config_data, local_file, default_flow_style=False, encoding='utf-8', allow_unicode=True )

def load( directory = None ):
  if not directory:
    directory = os.getcwd()

  if os.path.isfile( directory + "/stak.yml" ):
    local_file = click.open_file( directory + "/stak.yml", "r+", lazy=True, encoding = "utf-8")
    data = None
    if local_file:
      data = yaml.safe_load( local_file.read() )
      config_data = data

    data["devices"] = data["devices"] if ("devices" in config_data and config_data["devices"]) else {}
    config_data = data if (data) else {}
  else:
    config_data = {}
    config_data["devices"] = {}
  return config_data

def get_attributes( attributes, config = None):
  global local_data
  if not config:
    config = local_data

  return_attr = {}

  for attr in attributes:
    if attr[0] in config:
      return_attr[ attr[0] ] = config[attr[0] ]
    else:
      click.echo( attr[0]+" not defined in project config" )
      return_attr[ attr[0] ] = attr[1]
  return return_attr