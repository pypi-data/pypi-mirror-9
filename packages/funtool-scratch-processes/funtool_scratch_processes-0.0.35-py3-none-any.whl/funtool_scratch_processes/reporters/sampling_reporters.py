# Reporters to output sample states


import funtool.reporter

import pprint
import random
import os.path
import sys

def save_sample(reporter,state_collection,overriding_parameters=None,logging=None):
    reporter_parameters= funtool.reporter.get_parameters(reporter,overriding_parameters)
    reporter_parameters= set_default_parameters({'print_depth': 2 },reporter_parameters)

    sample_state= random.choice(state_collection.states)


    if 'file' in reporter_parameters['output_to']:
        reporter_parameters= set_default_parameters({'file_type':'txt'},reporter_parameters)

        save_path= funtool.reporter.get_default_save_path(reporter_parameters)
        if not os.path.exists(save_path): os.makedirs(save_path)

        if not _can_write(reporter_parameters):
            raise funtool.reporter.ReporterError("Can't write to %s at %s" % (reporter_parameters['filename'], reporter_parameters['save_directory'] ))
       

        path_and_filename= os.path.join(save_path,".".join([reporter_parameters['filename'], reporter_parameters['file_type']]))


        with open( path_and_filename, 'w', newline='') as f:
            pp = pprint.PrettyPrinter(depth=reporter_parameters['print_depth'], indent=2, stream=f )
            print_fields(pp,sample_state)

    if 'stdio' in reporter_parameters['output_to']:
        pp = pprint.PrettyPrinter(depth=reporter_parameters['print_depth'], indent=2 )
        print_fields(pp,sample_state)


    return state_collection


def set_default_parameters(default_parameters, current_parameters): #adds missing default parameters
    default_copy= default_parameters.copy()
    default_copy.update(current_parameters)
    return default_copy


def _can_write(reporter_parameters):
    path_and_filename=  os.path.join(reporter_parameters['save_directory'],".".join([reporter_parameters['filename'], reporter_parameters['file_type']]))
    return os.path.exists(reporter_parameters['save_directory']) and ( not os.path.exists(path_and_filename) or reporter_parameters['overwrite'] )

def print_fields(pp,state):
    pp.pprint('State')
    pp.pprint('=====')
    pp.pprint('')
    pp.pprint('id')
    pp.pprint('--')
    pp.pprint('')
    pp.pprint(state.id)
    pp.pprint('')
    pp.pprint('')
    pp.pprint('data')
    pp.pprint('----')
    pp.pprint('')
    pp.pprint(state.data)
    pp.pprint('')
    pp.pprint('')
    pp.pprint('measures')
    pp.pprint('--')
    pp.pprint('')
    pp.pprint(state.measures)
    pp.pprint('')
    pp.pprint('')
    pp.pprint('meta')
    pp.pprint('--')
    pp.pprint('')
    pp.pprint(state.meta)
    pp.pprint('')
    pp.pprint('')
    pp.pprint('groups_dict')
    pp.pprint('--')
    pp.pprint('')
    pp._depth=1       # set firm limit to keep recursive printing from exploding
    pp.pprint(state.groups_dict)
