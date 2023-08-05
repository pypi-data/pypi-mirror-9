import sys
import os.path

# make sure this is run from inside the package
from . import config as mimodd_settings

CONFIG_FILE_GUESSES = [ 'config/galaxy.ini',
                        'universe_wsgi.ini' ]
TOOL_CONFIG_FILE_REF = 'tool_config_file'
MIMODD_TOOL_CONF = 'mimodd_tool_conf.xml'

def get_config_file (galaxydir):
    for location_guess in CONFIG_FILE_GUESSES:
        config_file = os.path.join(galaxydir, location_guess)
        if os.path.isfile(config_file):
            return config_file
    raise OSError('Could not find Galaxy configuration file in default location.')

def add_to_galaxy (galaxydir, config_file = None, line_token = None, force = False):
    """Register and install MiModD's tool wrappers for Galaxy.

    Adds a MiModD section to the Galaxy installation's tool_conf.xml file
    or updates the file.
    Copies the xml tool wrappers from the Python package to a new
    directory mimodd in the Galaxy installation's tools directory."""
    
    if not os.path.isdir(galaxydir):
        raise OSError('{0} does not seem to be a valid directory.'.format(galaxydir))
    if config_file is None:
        config_file = get_config_file(galaxydir)
    if line_token is None:
        line_token = TOOL_CONFIG_FILE_REF
        
    pkg_path = os.path.dirname(mimodd_settings.__file__)
    pkg_galaxy_data_path = os.path.join(pkg_path, 'galaxy_data')

    tool_conf_file = os.path.join(pkg_galaxy_data_path, MIMODD_TOOL_CONF)

    # update the mimodd_tool_conf.xml file
    # installed as part of the package
    # with an absolute tool_path to the package xml wrappers
    with open(tool_conf_file, 'r') as sample:
        template = sample.readlines()[1:]
    with open(tool_conf_file, 'w') as out:
        out.write ('<toolbox tool_path="' + pkg_galaxy_data_path + '">\n')
        out.writelines(template)

    # update Galaxy's configuration file
    # to include mimodd_tool_conf.xml
    # as a tool_config_file
    with open(config_file, 'r') as config_in:
        config_data = config_in.readlines()
    for line_no, line in enumerate(config_data):
        if line.startswith(line_token + ' ='):
            try:
                key, value = line.split('=')
            except ValueError:
                raise OSError('Unexpected format of configuration file line {0}: {1}.'
                              .format(line_no, line))
            conf_files = [file.strip() for file in value.split(',')]
            if tool_conf_file in conf_files:
                print ('Galaxy is already configured correctly. No changes needed.')
                print ('If Galaxy is currently running, you may still want to restart to make sure all changes are effective.')
                sys.exit(0)
            config_data[line_no] = line.rstrip() + ',' + tool_conf_file + '\n'
            break
    else:
        raise OSError('Galaxy configuration file {0} has no {1} setting. Maybe the line "{2}" has been commented out ?'
                      .format(config_file, line_token, line_token + '= ...'))
    
    # ask for user backup before making changes to Galaxy config file
    print ('We recommend to back up the Galaxy configuration file {0} before proceeding !'
           .format(config_file))
    confirm = input ('Proceed (y/n)? ')
    if confirm != 'y' and confirm != 'Y':
        print ('No changes made to Galaxy configuration file. Aborting.')
        sys.exit(0)

    # write changes to config file    
    with open(config_file, 'w') as config_out:
        try:
            config_out.writelines(config_data)
        except:
            raise OSError('We are very sorry, but an error has occurred while making changes to the Galaxy configuration file {0}. If you have made a backup of the file, you may want to use it now.'
                          .format(config_file))
            
    print ('Successfully updated the Galaxy configuration file {0} to include the MiModD tools.'
           .format(config_file))
    print ('If Galaxy is currently running, you will have to restart it for changes to take effect.')
