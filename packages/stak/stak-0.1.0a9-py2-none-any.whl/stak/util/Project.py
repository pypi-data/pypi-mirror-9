import click
import os
import subprocess
from stak.util import Config
from stak.util import Device
from stak.util import Util
from distutils import spawn

def push_to_device( project, attributes ):
  click.echo( "Pushing project " + click.style( project, bold=True, fg="blue") )
  click.echo( "target: " + click.style( attributes["target"], bold=True, fg="green") )

  # find ssh and rsync executables
  ssh = spawn.find_executable("ssh")
  rsync = spawn.find_executable("rsync")

  # store device address info( user@hostname ) in a variable
  device_address = attributes["device"]["user"]+"@"+attributes["device"]["address"]
  ssh_identity_arg = "'" + ssh+" -o CheckHostIP=no -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -i " + attributes["device"]["key-file"]+ "'"

  # create the rsync command by joining a list of the arguments, separated by a space
  rsync_comand = " ".join([
      rsync,
      "-avz",
      "-e",
      ssh_identity_arg,
      "--delete",
      attributes["output-directory"]+"/",
      device_address+":"+project
    ])

  # run the rsync command
  subprocess.Popen(rsync_comand,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    shell=True).stdout.readline()

def run_on_device( project, attributes ):
  click.echo( "Running project " + click.style( project, bold=True, fg="blue") )
  click.echo( "target: " + click.style( attributes["target"], bold=True, fg="green") )

  # find ssh executable
  ssh = spawn.find_executable("ssh")

  # store device address info( user@hostname ) in a variable
  device_address = attributes["device"]["user"]+"@"+attributes["device"]["address"]
  click.echo("Running")
  with open("stak.log","wb") as log, open("stak-errors.log","wb") as err:
      subprocess.Popen([ ssh,"-o","CheckHostIP=no","-o", "UserKnownHostsFile=/dev/null", "-o", "StrictHostKeyChecking no", "-i", attributes["device"]["key-file"], device_address, "'"+project+"/" + attributes["executable"]+ "'"], stdout=log, stderr=err)

def is_project( directory ):
  if( os.path.exists( directory ) and
      os.path.isdir ( directory ) and
      os.path.exists( directory + "/stak.yml" ) and
      os.path.isfile( directory + "/stak.yml" ) ):
    return True;
  else:
    return False

def get_project_run_attributes( project, target ):
  
  # get attributes from config
  project_config = Config.get_attributes( [
    [ "default-device", ""],
    [ "executable", project+".sh"],
    [ "output-directory", "build"],
    [ "language", "python"],
    ], Config.local_data)

  if not project_config:
    click.echo("project_config is None")
    return

  # get device attributes from config
  project_config["device"] = Device.get_attributes(
    [
      ["address", ""],
      ["user", "root"],
      ["key-file", ""]
    ],
    project_config["default-device"],
    Config.local_data)

  project_config["target"] = target
  if not project_config["device"]:
    click.echo("device is None")
    return

  return project_config

def create( project, example_options ):

  config = {}
  if "create" in example_options and example_options['create']:
    if "language" in example_options:
      if "python" in example_options["language"]:
        Util.call_and_return("git","clone","git@github.com:NextThingCo/stak-example-python.git", project )
      else:
        os.mkdir( project )
        open( project + "/stak.yml" , 'w')
      config['language'] = example_options['language']
  Config.save( project, config )

def build( project, target ):
  if is_project( project ):
    click.echo( "Building project " + click.style( os.path.basename( project ), bold=True, fg="blue") )
    click.echo( "target: " + click.style( target, bold=True, fg="green") )
    # make sure we have all of the attributes requried to deploy and run the project on a device
    proj_attr = get_project_run_attributes( project, target )

    if not proj_attr:
      click.echo("proj_attr is None")
      return
    if "python" in proj_attr["language"]:
      click.echo("No need to build a python project")
    elif "c++" in proj_attr["language"]:
        Util.call_and_return( "cmake","..", directory="./build")
        Util.call_and_return( "make", directory="./build")
  else:
    click.echo( "Project '" + click.style( os.path.basename( project ), bold=True, fg="blue") +"' not found!")

def ssh( project, target ):
  # verify that we are trying to run a valid project
  if is_project( project ):

    # make sure we have all of the attributes requried to deploy and run the project on a device
    proj_attr = get_project_run_attributes( project, target )

    if not proj_attr:
      click.echo("proj_attr is None")
      return

    project_name = os.path.basename( project )

    # find ssh executable
    ssh = spawn.find_executable("ssh")

    # store device address info( user@hostname ) in a variable
    device_address = proj_attr["device"]["user"]+"@"+proj_attr["device"]["address"]
    with open("stak.log","wb") as log, open("stak-errors.log","wb") as err:
        subprocess.Popen([
            ssh,
            "-o","CheckHostIP=no",
            "-o", "UserKnownHostsFile=/dev/null",
            "-o", "StrictHostKeyChecking no",
            "-i", proj_attr["device"]["key-file"],
            device_address
          ])
  else:
    click.echo( "Project '" + click.style( os.path.basename( project ), bold=True, fg="blue") +"' not found!")

def run_ssh_command(project, attributes, command):

  # store device address info( user@hostname ) in a variable
  device_address = attributes["device"]["user"]+"@"+attributes["device"]["address"]

  # find ssh executable
  ssh = spawn.find_executable("ssh")
  return subprocess.Popen([
      ssh,
      "-o","CheckHostIP=no",
      "-o", "UserKnownHostsFile=/dev/null",
      "-o", "StrictHostKeyChecking=no",
      "-i", attributes["device"]["key-file"],
      device_address,
      "%s" % (command)
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE
  ).stderr.readlines()
  # return " ".join([
  #     ssh,
  #     "-o","CheckHostIP=no",
  #     "-o", "UserKnownHostsFile=/dev/null",
  #     "-o", "StrictHostKeyChecking=no",
  #     "-i", attributes["device"]["key-file"],
  #     device_address,
  #     "'%s'" % (command)
  #   ])


def run( project, target ):

  # verify that we are trying to run a valid project
  if is_project( project ):

    # make sure we have all of the attributes requried to deploy and run the project on a device
    proj_attr = get_project_run_attributes( project, target )

    if not proj_attr:
      click.echo("proj_attr is None")
      return

    project_name = os.path.basename( project )

    push_to_device( project_name, proj_attr )
    run_on_device( project_name, proj_attr )
  else:
    click.echo( "Project '" + click.style( os.path.basename( project ), bold=True, fg="blue") +"' not found!")

def deploy( project, target ):
  if is_project( project ):
    # make sure we have all of the attributes requried to deploy and run the project on a device
    proj_attr = get_project_run_attributes( project, target )

    if not proj_attr:
      click.echo("proj_attr is None")
      return

    project_name = os.path.basename( project )

    Util.call_and_return("honcho", "export", "-f", os.getcwd()+"/build/Procfile", "-d", "/root/" + project_name + "/", "-l", "/root/" + project_name + "/", "-a", "stak", "supervisord", os.getcwd()+"/build" )
    
    push_to_device( project_name, proj_attr )
    
    run_ssh_command( project_name, proj_attr, "mv "+project_name+"/stak.conf /etc/supervisor/conf.d/" )
    run_ssh_command( project_name, proj_attr, "/usr/bin/supervisorctl update" )
  else:
    click.echo( "Project '" + click.style( os.path.basename( project ), bold=True, fg="blue") +"' not found!")