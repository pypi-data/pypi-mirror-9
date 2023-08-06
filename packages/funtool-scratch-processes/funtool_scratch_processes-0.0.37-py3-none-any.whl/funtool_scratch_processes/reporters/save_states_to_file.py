# This reporter will save all meta and measures for all states in a state_collection to a file
# Reporter should include the following parameters
# save_directory    location of the save file
# filename          basename of the file
# filetype          file type which is added as an extension, either csv or tsv
# overwrite         boolean to overwrite existing file if it exists


import csv
import json

import os.path

import funtool.reporter

def save(reporter,state_collection,overriding_parameters=None,logging=None):
    reporter_parameters= funtool.reporter.get_parameters(reporter,overriding_parameters)

    save_path= funtool.reporter.get_default_save_path(reporter_parameters)
    if not os.path.exists(save_path): os.makedirs(save_path)

    if not _can_write(reporter):
        raise funtool.reporter.ReporterError("Can't write to %s at %s" % (reporter_parameters['filename'], reporter_parameters['save_directory'] ) )

    meta_keys= sorted(_gather_keys(state_collection, 'meta'))
    measures_keys= sorted(_gather_keys(state_collection, 'measures'))

    path_and_filename= os.path.join(save_path,".".join([reporter_parameters['filename'], reporter_parameters['file_type']]))
    
    with open( path_and_filename, 'w', newline='' ) as f:
        writer = _get_writer(reporter,f)
        _write_line(reporter,writer, (meta_keys + measures_keys) )
        for state in state_collection.states:
            state_values= [ state.meta.get(meta_key) for meta_key in meta_keys ] + [ state.measures.get(measure_key) for measure_key in measures_keys ] 
            _write_line(reporter,writer, state_values)
    funtool.reporter.link_latest_output(reporter_parameters['save_directory'])
    return state_collection


# Internal functions

def _gather_keys(state_collection, key_type):
    collection_keys = {} 
    for state in state_collection.states:
        for state_keys in state.__getattribute__(key_type).keys():
            collection_keys[state_keys] = 1
    return list(collection_keys.keys())

def _can_write(reporter):
    path_and_filename=  os.path.join(reporter.parameters['save_directory'],".".join([reporter.parameters['filename'], reporter.parameters['file_type']]))
    return os.path.exists(reporter.parameters['save_directory']) and ( not os.path.exists(path_and_filename) or reporter.parameters['overwrite'] )
    

def _get_writer(reporter, file_handler):
    if reporter.parameters['file_type'].lower() == 'csv' :
        return csv.writer(file_handler)
    elif reporter.parameters['file_type'].lower() == 'tsv' :
        return file_handler
    else :
        return None

def _write_line(reporter, writer, state_values):
    if reporter.parameters['file_type'].lower() == 'csv' :
        writer.writerow(state_values) 
    elif reporter.parameters['file_type'].lower() == 'tsv' :
        writer.write( "\t".join([ _write_value(v) for v in state_values ]))
        writer.write( "\n" )
    return True

def _write_value(value): #converts value in json encoded string if possible and a regular string if not
    try:
        write_value= json.dumps(value)
    except:
        write_value= str(value)
    return write_value
        
   
