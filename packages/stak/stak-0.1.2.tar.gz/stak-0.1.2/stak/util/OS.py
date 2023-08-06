import click
import yaml
import os, sys
import re
import subprocess
import pwd, grp
from stak.util import Util
from stak.util import DD
from stak.util import Config
import zipfile

supported_operating_systems = [
    { "name": "Stak",               "url": "http://stak-images.s3.amazonaws.com/stak-rpi-base.iso.bz2" },
    { "name": "Raspbian",           "url": "http://downloads.raspberrypi.org/raspbian_latest" },
    { "name": "OpenElec",           "url": "http://downloads.raspberrypi.org/openelec_latest" },
    { "name": "Pidora",             "url": "http://downloads.raspberrypi.org/pidora_latest" },
    { "name": "Ubuntu Snappy Core", "url": "http://downloads.raspberrypi.org/ubuntu_latest" },
    { "name": "Raspbmc",            "url": "http://downloads.raspberrypi.org/raspbmc_latest" },
    { "name": "RISC OS",            "url": "http://downloads.raspberrypi.org/riscos_latest" },
]

#
#
#
def get_download_url( os_number = 0 ):
    global supported_operating_systems
    url = supported_operating_systems[ os_number ]["url"]
    info = Util.get_http_header( url )

    if "Location" in info:
        return info["Location"]
    return url

#
#
#
def get_image_filename( os_number = 0 ):
    # handle things differently for Stak OS
    if os_number == 0:
        return Util.strip_end(os.path.basename( supported_operating_systems[ os_number ]["url"] ), ".bz2")
    else:
        return supported_operating_systems[ os_number ]["name"]+".img"

#
#
#
def get_image_compressed_filepath( os_number = 0 ):
    return os.path.expanduser( "~/.stak/images/" + os.path.basename( supported_operating_systems[ os_number ]["url"] ) )

#
#
#
def get_image_filepath( os_number = 0 ):
    # handle things differently for Stak OS
    image_name = get_image_filename( os_number )
    return os.path.expanduser( "~/.stak/images/" + image_name )

#
#
#
def get_image_exists( os_number = 0 ):
    global supported_operating_systems
    
    image_name = get_image_filename( os_number )
    image_path = os.path.expanduser("~/.stak/images/" + image_name)

    return os.path.exists(image_path)

#
#
#
def download_os_image( os_number = 0 ):
    
    image_path = get_image_filepath( os_number )
    image_compressed_filepath = get_image_compressed_filepath( os_number )
    image_url = get_download_url( os_number )

    if not get_image_exists( os_number ):
        if not os.path.exists( image_compressed_filepath ):
            Util.dd( image_url, image_compressed_filepath )
        
        click.echo("Decompressing image...")
        
        if ".bz2" in image_compressed_filepath:
            if os.path.exists( image_path ):
                os.remove( image_path )
            Util.call_and_return("bunzip2", image_compressed_filepath )
        else:
            if os.path.exists( image_path ):
                os.remove( image_path )
            # Util.call_and_return("unzip", image_compressed_filepath )
            fh = open(image_compressed_filepath, 'rb')
            z = zipfile.ZipFile(fh)
            for name in z.namelist():
              click.echo("file: "+ name )
              outfile = open(image_path, 'wb')
              outfile.write( z.read(name) )
              outfile.close()
            fh.close()

#
#
#
def get_latest_image( os_number = 0 ):
    url = get_download_url( os_number )
    info = Util.get_http_header( url )
    image_path = get_image_filepath( os_number )

    # does the image contain ETag information?
    if "ETag" in info:

        # if so, we'll use that as a checksum
        info["ETag"] = info["ETag"].replace("\"", "").rstrip()
        if( "latest-checksum" in Config.global_data and
            Config.global_data["latest-checksum"] == info["ETag"] and
            os.path.exists( image_path ) ):
            return image_path
        else:
            Config.global_data["latest-checksum"] = info["ETag"]
    else:

        # if not, make sure the file exists
        # TODO(Wynter): we need to compare the
        #   filename for date information.
        if os.path.exists( image_path ):
            return image_path

    # we will only get to this point if we need to download a new image
    download_os_image( os_number )

    # we should also save the globals if the new image was created
    if os.path.exists( image_path ):
        Config.save_globals()
    return False

#
#
#
def burn_os( os_number, disk ):
    # we need to unmount all partitions on the specified disk
    # or the os will complain about the disks being in use
    Util.call_and_return( "diskutil","unmountDisk", disk )

    # find the location of the raspbian image.
    # this is located inside of a hidden folder in the user directory for now
    # TODO(Wynter): we should also verify that the file exists and if not download it
    raspbian_image = os.path.expanduser("~/.stak/images/stak-rpi-base.iso")

    # output some information for the user to see that something is going on
    # TODO@Wynter: get some sort of progress output from DD
    click.echo("Writing to "+disk+"...")

    # flash the disk
    rdisk = disk.replace("/dev/disk", "/dev/rdisk")

    if rdisk:
        Util.dd( raspbian_image, rdisk )
    else:
        Util.dd( raspbian_image, disk )

    Util.call_and_return( "diskutil","eject", disk )

# locate and set up an sd card with a new stak os image
def burn( os_number ):

  if not os_number:
    Util.display_list( "Supported OSes", supported_operating_systems, (
        lambda index,value: click.style( value["name"], bold=True, fg="cyan" )
          + ": "
          + (click.style( "Downloaded", fg="green") if get_image_exists(index) else click.style( "Not Downloaded", fg="red" ))
      )
    )
    os_number = click.prompt("Please select the OS to install", type=int)

  get_latest_image( os_number )

  euid = os.geteuid()
  if euid != 0:
    click.secho('Super user privileges are required to flash an sd card.', reverse=True)
    Util.raise_privileges(["--image="+str(os_number)])
   
  inserted=False
  cards = None

  # find and verify that the card is inserted
  while not inserted:
    if not click.confirm('Is the SD card inserted?'):
      click.echo("Please insert the SD card now.")
      click.pause()
    else:
      cards = Util.find_valid_sd_cards()
      if not cards:
        click.echo("No sd card found!")
        click.echo("Please insert the SD card now.")
        click.pause()
      else:
        inserted = True

  # have user select the disk to use
  Util.display_list( "Cards found", cards, (
      lambda index,value: click.style( value["name"], bold=True, fg="cyan" )
        + ": "
        + click.style( value["size"], fg="green" )
    )
  )
  selected_index = click.prompt("Please select the card to flash", type=int)
  selected_card = cards[ selected_index ]["name"]
 
  click.wrap_text("text\x08", width=78, initial_indent='', subsequent_indent='', preserve_paragraphs=True)
  click.secho('WARNING!! Make SURE this is the correct card, this command will delete EVERYTHING on the target volume '+selected_card + " of size " + cards[ selected_index ]["size"], reverse=True)
  if not click.confirm('Are you sure you wish to continue?'):
    return
 
  # flash the selected sd card with the stak os base image
  burn_os( os_number, selected_card )
  Util.drop_privileges()
