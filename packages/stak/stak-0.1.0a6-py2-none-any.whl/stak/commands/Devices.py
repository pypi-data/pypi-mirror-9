import os
import click
import time
import signal
import re
from stak.util import Config
from stak.util import Device
from stak.util import Util
import zeroconf as Zeroconf

devices_found = []

# discovers all devices exposing stak on local network and
# returns information about them
def discover():

  # callback to add devices to a list when stak devices are found
  def zc_service_change(zeroconf, service_type, name, state_change):
    if state_change is Zeroconf.ServiceStateChange.Added:
      info = zeroconf.get_service_info(service_type, name)
      dev_type = "generic"
      if "rpi" in name:
        dev_type = "Raspberry Pi"
      devices_found.append( { "name": name, "info": info, "type": dev_type } )
    elif state_change is Zeroconf.ServiceStateChange.Removed:
      pass

  # create a zeroconf object
  zeroconf = Zeroconf.Zeroconf()

  # stup a zeroconf browser to search for _stak._tcp.local.
  browser = Zeroconf.ServiceBrowser(zeroconf, "_stak._tcp.local.", handlers=[zc_service_change] )
  click.echo("Searching for stak-enabled devices on local network...")

  # show a progress bar for 5 seconds while we search
  with click.progressbar( length=40, width=10, show_percent=True,
                          show_eta=False,
                          fill_char=click.style('#', fg='magenta')) as bar:
    for item in bar:
      time.sleep(0.125)

  # end zeroconf communications
  zeroconf.close()

  # if we found any devices
  if len(devices_found) == 0:
    click.echo( click.style("Error: No stak devices found!", bold=True, fg="red" ) )
    return

  Util.display_list( "Devices found:", devices_found,
    ( lambda index,value:
      click.style( value["info"].server, bold=True, fg="cyan" )
      + ": "
      + click.style( value["type"], bold=True, fg="red" )
    )
  )

  # ask the user to select one
  new_device = devices_found[ click.prompt("Please select the device to add", type=int) ]
  click.echo("Selected: " + new_device["name"])

  #
  new_device["name"] = re.sub('\._stak\._tcp\.local.$', '', new_device["name"])

  #
  uuid = new_device["info"].properties["uuid"] if ( "uuid" in new_device["info"].properties ) else ""

  #
  add ( new_device["name"], uuid, new_device["info"].server, "root")


# add a device to the project configuration
# 
def add( device, uuid=None, address=None, user=None, key_file=None):

  # if the device already exists in the configuration
  # then we don't want to add it again.
  # otherwise, prep data for adding device
  if not Device.exists( Config.local_data, device ):

    set_as_default = False
    if Device.count( Config.local_data ) == 0:
      set_as_default = True

    # create base device data structure
    device_data = {}

    # if any of the data we specified was None,
    # we want to set the data to sane defaults
    device_data['uuid'] = uuid if uuid else str( Util.call_and_return("uuidgen") ).rstrip()
    device_data['address'] = address if address else "stak.local"
    device_data['user'] = user if user else "root"
    device_data['key-file'] = key_file if key_file else os.path.expanduser("~/.ssh/id_rsa.pub")
    
    # add device to local data
    Config.local_data = Device.add( Config.local_data, device, device_data )

    if set_as_default:
      set_default_device( device )

    # save local project config data/Users/zerotri/Development/ntc/stak-cli/util/Device.py
    Config.save( )

def set_default_device( device ):
  if not Device.exists( Config.local_data, device ):
    click.echo("Device "+device+" doesn't exist!")
    return
  if not Config.local_data:
    click.echo("Config data not being set properly!")
    return
  Config.local_data["default-device"] = device
  Config.save( )

def set_property( device, parameter, value ):
  if Device.exists( Config.local_data, device ):
    Device.set( Config.local_data, device, parameter, value )
    Config.save( )

def get_property( device, parameter ):
  if Device.exists( Config.local_data, device ):
    prop = Device.get( Config.local_data, device, parameter )
    if prop:
      click.echo( prop )
    else:
      click.echo( "Property doesn't exist!" )

def remove( device ):
  if Device.exists( Config.local_data, device ):
    Config.local_data = Device.remove( Config.local_data, device )
    Config.save( )
        
#
# device list
#
def list( ):
  if Config.verbose:
    print("Verbose")

  if len( Config.local_data['devices'] ) < 1:
    click.echo( "No devices found" )
    return

  Util.display_list( "Listing devices:", Config.local_data['devices'],
    (
      lambda index,value: click.style( value, bold=True, fg="cyan" )
        + ": "
        + click.style( Device.get( Config.local_data, value, 'uuid' ), fg="green" )
    )
  )

# finds valid sd cards inserted in the current system
# currently OSX only as it relies on diskutil
# TODO@Wynter: Add support for Linux and Windows
def find_valid_sd_cards():
  sd_cards = []
  diskutil_output = Util.call_and_return("diskutil", "list")
  disks = Util.find_list_items_containing( "^\/dev\/disk[0-9]$", diskutil_output )
  for disk in disks:
    diskutil_output = Util.call_and_return("diskutil", "info", disk)
    if Util.find_list_items_containing("(Protocol:\s+Secure Digital)", diskutil_output):
      sd_cards.append( disk )
    if Util.find_list_items_containing("(Protocol:\s+USB)", diskutil_output):
      sd_cards.append( disk )
  return sd_cards

# finds all fat32 partitions inserted in the system
# you may optionally pass a disk name in to have it
# only find fat partitions on the specified disk
def find_fat_partitions(disk=None):
  valid_paths = []
  diskutil_args = ["diskutil", "list"]
  if disk:
    diskutil_args.append( disk )

  diskutil_output = Util.call_and_return( *diskutil_args )
  search_regex = "\d\:\s+.*FAT_32\s+(.+)\s+\d+\.\d+\s+[kKgGmM]B+.*(disk[0-9]s[0-9])"
  fat_partitions = Util.find_list_items_containing( search_regex,
    diskutil_output,
    ( lambda m: [m.group(1).strip(), m.group(2)] )
  )
  return fat_partitions

# flash the specified disk with the stak os image.
def flash_card( disk ):

  # we need to unmount all partitions on the specified disk
  # or the os will complain about the disks being in use
  Util.call_and_return( "diskutil","unmountDisk", disk )

  # find the location of the raspbian image.
  # this is located inside of a hidden folder in the user directory for now
  # TODO@Wynter: we should also verify that the file exists and if not download it
  raspbian_image = os.path.expanduser("~/.stak/images/netinst-image.iso")

  # output some information for the user to see that something is going on
  # TODO@Wynter: get some sort of progress output from DD
  click.echo("Writing...")

  # flash the disk
  rdisk = disk.replace("/dev/disk", "/dev/rdisk")

  if rdisk:
    Util.dd( raspbian_image, rdisk )
  else:
    Util.dd( raspbian_image, disk )

def get_latest_os_image():
  http_header = Util.call_and_return( "curl", "-I", "http://stak-images.s3.amazonaws.com/netinst-image.iso.bz2")
  etag = Util.find_list_items_containing("^ETag:\s\"(.*)\"", http_header,
    ( lambda m: m.group(1) ))
  if not etag:
    click.echo( "Nothing in etag" )
    return
  
  image_path = os.path.expanduser("~/.stak/images/netinst-image.iso.bz2")
  if( "latest-checksum" in Config.global_data and
      Config.global_data["latest-checksum"] == etag[0] and
      os.path.exists( os.path.expanduser("~/.stak/images/netinst-image.iso") ) ):
    click.echo("Using the latest image. Continuing...")
  else:
    click.echo("Downloading image...")
    Util.dd( "http://stak-images.s3.amazonaws.com/netinst-image.iso.bz2", image_path )

    click.echo("Decompressing image...")
    Util.call_and_return("bunzip2", image_path )
    Config.global_data["latest-checksum"] = etag[0]
    Config.save_globals()

# locate and set up an sd card with a new stak os image
def setup_card():

  if os.getuid() != 0:
    click.echo("Not running as super user. Please relaunch as super user")
    return

  inserted=False

  cards = None
  click.wrap_text("text\x08", width=78, initial_indent='', subsequent_indent='', preserve_paragraphs=True)
  click.echo(click.style('WARNNING!! This command will delete EVERYTHING on the target volume', reverse=True))

  # find and verify that the card is inserted
  while not inserted:
    if not click.confirm('Is the SD card inserted?'):
      click.echo("Please insert the SD card now.")
      click.pause()
    else:
      cards = find_valid_sd_cards()
      if not cards:
        click.echo("No sd card found!")
        click.echo("Please insert the SD card now.")
        click.pause()
      else:
        inserted = True

  # have user select the disk to use
  Util.display_list( "Cards found", cards )
  selected_card = cards[ click.prompt("WARNNING!! Make SURE this is the correct card, this command will delete EVERYTHING on the target volume. Please select the card to use", type=int) ]
  click.echo("Selected: " + selected_card)

  get_latest_os_image()

  # flash the selected sd card with the stak os base image
  flash_card( selected_card )

  # sleep for five seconds to make sure the os has time to
  # register and mount the new partitions on the volume
  time.sleep(20.0)

  # find fat partitions on the selected disk
  fat_partitions = find_fat_partitions( selected_card )
  if not fat_partitions:
    click.echo("No partitions found! Card likely corrupt.")
    return

  # begin copying extra files over to new volume
  volume = "/Volumes/" + fat_partitions[0][0]
  click.echo("Writing to card: " + volume)

  # copy the post-install.txt and installer-config.txt used by
  # raspbian-ua-netinst
  #post_install = os.path.expanduser("~/.stak/post-install.txt")
  #install_config = os.path.expanduser("~/.stak/installer-config.txt")
  
  #Util.cp( post_install, volume+"/post-install.txt" )
  #Util.cp( install_config, volume+"/installer-config.txt" )

  # copy the current user's public key to the sd card
  key_file = os.path.expanduser("~/.ssh/id_rsa.pub")
  
  # if volume:
  if not os.path.exists(key_file):
    Util.call_and_return( "ssh-keygen","-t", "rsa" "-f", key_file )
  click.echo("Writing key file: " + key_file)
  Util.cp( key_file, volume+"/id_rsa.pub" )
  if not os.path.exists( volume+"/id_rsa.pub" ):
    click.echo("ERROR COPYING KEY!")
  click.echo("Copied key!")
