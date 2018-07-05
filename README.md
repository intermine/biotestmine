# README

This is an example InterMine for demo and testing.

It's used by the `tutorial <http://intermine.readthedocs.io/en/latest/get-started/tutorial/>`_, and we use it for our continuous integration tests on `Travis <https://travis-ci.org/intermine/intermine/builds>`_.

# Building the mine

This mine can be built with the `./setup.sh` script.  Steps:

1. Create an `.intermine` directory in your $HOME directory
2. Copy this file into `.intermine`:

`$HOME/.intermine` $ `wget https://github.com/intermine/biotestmine/blob/master/data/biotestmine.properties

3. Replace PSQL_USER and PSQL_PWD with your postgres username and password.
4. Run build script in this repository:

`./setup.sh`
