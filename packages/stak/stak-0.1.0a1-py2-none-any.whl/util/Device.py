import click
import subprocess

def get( config, name, parameter ):
  if( "devices" in config and
      name in config["devices"] and
      parameter in config["devices"][name] ):
    return config["devices"][name][parameter]
  else:
    return None

def set( config, name, parameter, value ):
  if( "devices" in config and
      name in config["devices"] and
      parameter in config["devices"][name] ):
    config["devices"][name][parameter] = value

def count( config ):
  if not "devices" in config:
    return 0

  if not config["devices"]:
    return 0

  return len( config["devices"] )

def exists( config, name ):
  if not config:
    return False
  if not "devices" in config:
    return False
  if not config["devices"]:
    return False
  if not name in config["devices"]:
    return False
  return True


def add( config, name, device ):
  if( "devices" in config and
      not name in config["devices"] ):
    config["devices"][name] = device
  return config

def remove( config, name ):
  if( "devices" in config and
      name in config["devices"] ):
    del config["devices"][name]
  return config

def get_attributes( attributes, device, config):
  return_attr = {}

  if not exists( config, device ):
    click.echo(device + " not found")
    click.echo(config)
    return None

  for attr in attributes:
    t_attr = get( config, device, attr[0] )
    if attr[0]:
      return_attr[ attr[0] ] = t_attr
    else:
      click.echo( attr[0]+" not defined for in device config for '"+ device+"'" )
      return_attr[ attr[0] ] = attr[1]
  return return_attr