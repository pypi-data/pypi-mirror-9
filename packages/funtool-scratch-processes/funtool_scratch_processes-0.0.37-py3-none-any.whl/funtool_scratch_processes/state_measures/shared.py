# Functions used within multiple state_measure functions
# NOT intended to be used independently as state_measures

import math
import numbers

def state_scripts(state): 
    """
    returns all the scripts in the state
    """
    json_data= state.data.get('json')
    scripts=[]
    if json_data != None:
        scripts.extend(json_data.get('scripts',[]))  #stage scripts
        for child in json_data.get('children'):
            scripts.extend(child.get('scripts',[]))
    return scripts

def block_counts(scripts):
    """
    Counts all blocks in a script, returns a dict with keys being the block name and values being the counts
    """
    counts={}
    for script in scripts:
        if isinstance(script, list):
            if isinstance(script[0],str):
                counts[script[0]] = counts.get(script[0],0) + 1
            for subvalue in script:
                if isinstance(subvalue, list):
                    for block_type, block_count in block_counts(subvalue).items():
                        counts[block_type] = counts.get(block_type,0) + block_count
    return counts

def compute_ratio(a_value,b_value):
    """
    Computes the ratio between two values, handles divide by zero errors

    """
    if b_value == 0:
        if a_value == 0:
            ratio= float('Nan')
        else:
            ratio= math.copysign(float('inf'),a_value)
    else:
        ratio= a_value/b_value
    return ratio

def all_sprite_scripts(state): 
    """
    Finds all scripts in sprites DOES NOT include stage
    returns a list of lists, each sublist is a list of scripts for each sprite
    """
    json_data= state.data.get('json')
    sprite_scripts=[]
    if json_data != None:
        for child in json_data.get('children'):
            if 'scripts' in child:
                sprite_scripts.append(child.get('scripts',[]))
    return sprite_scripts

def stage_scripts(state): 
    """
    Returns a list of scripts for the stage 
    """
    return state.data.git('json').get('scripts',[])


def all_sprites(state):
    """
    Returns a list of sprites in the state
    """
    json_data= state.data.get('json')
    sprites=[]
    if json_data != None:
        for child in json_data.get('children'):
            if 'spriteInfo' in child:
                sprites.append(child)
    return sprites

def strip_position(script):
    """
    returns the script block list after removing the script position
    """
    if isinstance(script, list) and len(script) == 3 and isinstance(script[0], numbers.Number) and isinstance(script[1], numbers.Number):
        return script[2]
    else:
        return script
