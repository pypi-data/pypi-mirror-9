Stak-cli
========

Command line interface for the stak development platform


usage:

    stak < create | { device < add | remove | list > [ device ] } >
    
to install:

  - from pip ( osx ):
    - install homebrew

    brew install python
    pip install stak

  - from repo:

    git clone git@github.com:NextThingCo/stak-cli.git
    cd stak-cli
    virtualenv .
    pip install --editable .
    mkdir -p ~/.stak/

to start using:

    source bin/activate

to create an OS image, insert an SD card and run:

    stak device setup-card

Once completed, put the sd card into your pi and wait 15-30 seconds

Then cd into the example python project and run the following:

    stak device discover
    stak deploy
    
Your pi should now be running a simple python-bottle webserver!


To update stak-cli:

    pip install stak -U