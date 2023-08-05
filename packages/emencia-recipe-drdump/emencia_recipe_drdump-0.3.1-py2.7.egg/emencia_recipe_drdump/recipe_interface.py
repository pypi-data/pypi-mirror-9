"""
Buildout recipe interface
"""
import logging, os, zc.buildout, zc.recipe.egg
import drdump
from drdump.builder import ScriptBuilder

class DrDumpRecipe(object):
    """
    The buildout recipe's interface for Dr Dump
    """
    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options
        self.installed_eggs = zc.recipe.egg.Egg(buildout, options['recipe'], options)
       
        if 'dependancies_map' not in options:
             raise zc.buildout.UserError('"dependancies_map" variable is required.')
        
        if 'django_instance' not in options:
             raise zc.buildout.UserError('"django_instance" variable is required.')
        
        options.setdefault('eggs', buildout['buildout']['eggs'])
        options.setdefault('bin_directory', buildout['buildout']['bin-directory'])
        options.setdefault('dump_dir', 'drdump_dumps')
        options.setdefault('extra_apps', '')
        options.setdefault('silent', 'false')
        options.setdefault('dump_other_apps', 'false')
        options.setdefault('exclude_apps', '')


    def install(self):
        """
        Called only for the first time the recipe is used
        """
        logging.getLogger(self.name).info('Dr Dump at your service')
       
        return self.build_scripts()

    def update(self):
        """
        Called after the first time the recipe is used
        """
        logging.getLogger(self.name).info('Dr Dump here, nice to see you again')
       
        return self.build_scripts()

    def retrieve_map_file(self, for_name, map_dir, map_file):
        """
        Validate and return path for a map file
        """
        # Try to find the map file directly with the given value
        if os.path.exists(map_file):
            return map_file
        # Try to find the map file as a filename within the package 'datas' directory
        elif os.path.exists(os.path.join(map_dir, map_file)):
            return os.path.join(map_dir, map_file)
        # Nothing finded
        else:
            raise zc.buildout.UserError(u'File from "{for_name}" variable does not exist: {map_file}'.format(map_file=map_file, for_name=for_name))

    def build_scripts(self):
        eggs = self.options['eggs']
        dependancies_map = self.options['dependancies_map']
        extra_apps = self.options['extra_apps'].split()
        dump_dir = os.path.join(self.buildout['buildout']['directory'], self.options['dump_dir'])
        map_dir = os.path.join(os.path.dirname(drdump.__file__), 'maps')
        silent = (self.options['silent'] == 'true')
        dump_other_apps = (self.options['dump_other_apps'] == 'true')
        exclude_apps = self.options['exclude_apps'].split()
        django_instance = self.options['django_instance']
       
        # Check for dump_dir, create it if not exists
        if not os.path.exists(dump_dir):
            os.mkdir(dump_dir)
       
        map_file = self.retrieve_map_file('dependancies_map', map_dir, dependancies_map)
       
        # Get the installed eggs name and extra egg names
        requirements, ws = self.installed_eggs.working_set(['emencia-recipe-drdump'])
        requirements = set(requirements)
        requirements.update(extra_apps)
       
        # Init the builder
        sb = ScriptBuilder('dumps', silent_key_error=silent,
                           django_instance_path=django_instance,
                           dump_other_apps=dump_other_apps,
                           exclude_apps=exclude_apps)
       
        # Dumper script
        dump_script = sb.generate_dumper(map_file, requirements)
        dumpscript_path = os.path.join(self.options['bin_directory'], 'datadump')
        fpd = open(dumpscript_path, 'w')
        fpd.write(dump_script)
        fpd.close()
        os.chmod(dumpscript_path, 0755)
       
        # Loader script
        load_script = sb.generate_loader(map_file, requirements)
        loadscript_path = os.path.join(self.options['bin_directory'], 'dataload')
        fpl = open(loadscript_path, 'w')
        fpl.write(load_script)
        fpl.close()
        os.chmod(loadscript_path, 0755)
       
        return [dump_dir, dumpscript_path, loadscript_path]
       
