import click
import os
from util import Config
from util import Project

#
# create
#   should 
#
def create( project, language ):
  # set directory variable
  directory = project

  # setup example options
  example_options = {}

  # make sure directory doesn't already exist
  if os.path.exists(directory):
    click.echo( "Cannot create directory " + directory
              + " because it already exists")
    return

  # prompt to create an example project
  example_options['create'] = click.confirm("Would you like an example project created for you?")
  if example_options['create']:
    if language is not None:
      example_options['language'] = language
    else:
      click.echo( click.style("Supported languages:", bold=True) )
      for index, lang in enumerate( Config.example_languages ):
        click.echo( "  "
          + str(index)
          + ") "
          + click.style(lang, bold=True, fg="cyan")
        )
      example_options['language'] = Config.example_languages[click.prompt("Please select the language to use", type=int)]
      click.echo("Selected: " + example_options['language'])

  # create directory
  Project.create( project, example_options )