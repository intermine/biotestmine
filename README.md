# README

This is an example InterMine for demo and testing

# Building the mine

This mine can be built with the `build-mine.py` script.  Steps:

1. Install required modules with

`sudo pip3 install -r requirements.txt`

2. Run script using mine properties file, e.g.

`./build-mine.py ~/.intermine/biotestmine.properties`

By default, this creates checkpoint databases in postgres so that a build can be resumed at various stages. However,
these checkpoints can also be made as Postgres dumps to the filesystem instead.

For more information please see this (wiki page)[https://github.com/intermine/intermine/wiki/build-mine.py]
