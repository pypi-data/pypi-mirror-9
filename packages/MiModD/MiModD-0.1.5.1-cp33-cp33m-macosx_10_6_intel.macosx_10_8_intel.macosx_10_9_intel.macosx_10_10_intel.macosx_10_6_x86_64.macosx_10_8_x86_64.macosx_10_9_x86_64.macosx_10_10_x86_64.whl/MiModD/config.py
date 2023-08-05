import os, sys
from . import cfg

class Config (object):
    __file__ = __file__
    _configurable_params = (
        'tmpfiles_path',
        'max_memory',
        'snpeff_path',
        'multithreading_level')
    _path_params = (
        'tmpfiles_path',
        'snpeff_path')
        
    tmpfiles_path = cfg.tmpfiles_path
    max_memory = cfg.max_memory
    multithreading_level = cfg.multithreading_level
    snpeff_path = cfg.snpeff_path

    bin_path = os.path.normpath(os.path.join(cfg.__file__, cfg.bin_path))
    samtools_exe = os.path.join(bin_path, 'samtools')
    bcftools_exe = os.path.join(bin_path, 'bcftools')
    samtools_legacy_exe = os.path.join(bin_path, 'samtools_legacy')
    snap_exe = os.path.join(bin_path, 'snap')

    def __init__ (self):
        new_config = os.getenv('MIMODD_CONFIG_UPDATE')
        if new_config:
            settings = {}
            for setting in new_config.split(':'):
                try:
                    param, value = setting.split('=') 
                except ValueError:
                    raise ValueError('Bad format of $MIMODD_CONFIG_UPDATE. Expected specifications of type "PARAM=VALUE".')
                settings[param] = value
            self.update_config(settings)
            
        # see if we are running inside Galaxy
        # if so respect the framework's multithreading settings
        # otherwise use cfg file setting
        galaxy_slots = os.getenv('GALAXY_SLOTS')
        if galaxy_slots:
            # Galaxy uses a default of "1" for GALAXY_SLOTS
            # if no value was specifed through the job runner.
            # to distinguish the default "1" (which we want to ignore)
            # from an explicitly requested "1" (which should be respected)
            # we can look at GALAXY_SLOTS_CONFIGURED, which is only set in the
            # second case. This environmental variable is currently
            # undocumented (communicated by John Chilton), we use it only
            # when GALAXY_SLOTS == "1", but do not generally rely on it.
            if galaxy_slots != '1' or (galaxy_slots == '1' and
                                       os.getenv('GALAXY_SLOTS_CONFIGURED')):
                try:
                    self.multithreading_level = int(galaxy_slots)
                except ValueError:
                    pass

    def update_config (self, new_settings, verbose = False):
        config_changes = False
        for param, value in new_settings.items():
            if param.lower() not in self._configurable_params:
                raise ValueError('Unknown config parameter', param)
            if param.lower() in self._path_params:
                value = os.path.abspath(os.path.expanduser(value))
            old_value = getattr(self, param.lower())
            try:
                value = type(old_value)(value)
            except ValueError:
                raise ValueError('Expected value of {0} for parameter {1}'
                                 .format(T, param))
            if value != old_value:
                config_changes = True
                setattr(self, param.lower(), value)
        if config_changes:
            self.write_config()
        if verbose:
            self.display_config(title = 'new MiModD settings')                

    
    def write_config (self):
        # read current config file
        cfg_path = cfg.__file__
        with open(cfg_path, 'r') as cfg_file:
            old_config = cfg_file.readlines()
        # write new config file
        cfg_file = open(cfg_path, 'w')
        try:
            for line_no, line in enumerate(old_config):
                if line.strip() and line[0] != '#':
                    try:
                        param, _value = [_.strip() for _ in line.split('=')]
                    except ValueError:
                        raise ValueError(
                            'Error in config file at line {0}: "{1}".\nExpected PARAM = VALUE format.'.format(line_no, line.strip()))
                    if param in self._configurable_params:
                        current_value = getattr(self, param)
                        cfg_file.write(
                            '{0} = {1}\n'.format(
                                param, "r'{0}'".format(current_value) if isinstance(
                                    current_value, str) else current_value))
                        continue
                cfg_file.write(line)
            cfg_file.close()
        except:
            cfg_file.close()
            # restore old config file version
            with open(cfg_path, 'w') as cfg_file:
                for line in old_config:
                    cfg_file.write(line)
            raise

    def display_config (self, title = 'current MiModD settings'):
        print ()
        print (title.upper())
        print ('-' * len(title))
        print ('PARAMETER : VALUE')
        print ('.' * len(title))

        for param in self._configurable_params:
            print ('{0} : {1}'.format(param.upper(), getattr(self, param)))

config_object = Config()

if __name__ == '__main__':
    print()
    print ('Settings for package MiModD in:', os.path.dirname(config_object.__file__), end = '')
    config_object.display_config (title = '                       ')
else:
    # do not attempt this when __name__ == '__main__' on Python 3.3
    sys.modules[__name__] = config_object
