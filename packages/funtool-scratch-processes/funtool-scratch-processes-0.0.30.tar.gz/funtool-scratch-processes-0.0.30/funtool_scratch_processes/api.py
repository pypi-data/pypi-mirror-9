# API functions for the funtool_scratch_processes
# This file contains functions that give information about the functions in the module
# Most sub modules have functions that are intended to be called directly by the funtool engine


import funtool_scratch_processes
import pkgutil

def function_modules():
    """
    Lists all the modules which have functions to be used to create funtool processes
    """
    return [ module_name 
            for (module_path,module_name,clear_cache) in pkgutil.walk_packages(funtool_scratch_processes.__path__,funtool_scratch_processes.__name__+".") 
            if not clear_cache  #directories are cached but files should not be so this should give all files
            and module_name is not 'funtool_scratch_processes.api']
