## Installation

The currently supported Python Version are 3.8.8, 3.8.9 and 3.8.10. For using Uganda-oemof.solph clone the repository to your local machine. Then create a new virtual environment with Python Version 3.8.10. Activate the new virtual environment and move to the repository folder to install the requirements of OWEFE.

     pip install -r requirements.txt


Further, you need to install a solver in your system. To do so, please see the [oemof.solph documentation](https://oemof-solph.readthedocs.io/en/latest/readme.html)

## Documentation

Documentation is currenty done in README files.

## Code linting

In this template, 3 possible linters are proposed:
- flake8 only sends warnings and error about linting (PEP8)
- pylint sends warnings and error about linting (PEP8) and also allows warning about imports order
- black sends warning but can also fix the files for you

You can perfectly use the 3 of them or subset, at your preference. Don't forget to edit `.travis.yml` if you want to deactivate the automatic testing of some linters!

## License

This project is licensed under the GNU Affero General Public License v3.0 - see the [LICENSE.md](https://github.com/rl-institut/Uganda-oemof.solph/blob/master/LICENSE) file for details.

# rli_template

This repository is based on rli-template, a template repository for creating new projects under the RLI's umbrella

