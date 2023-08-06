# These are default state_measure functions
# A state_measure function shoudl accept a StateMeasure, an AnalysisCollection, a StateCollection, and
#   an optional overriding_parameters
# It should return an AnalysisCollection and update Measure for the state in the AnalysisCollection


import math
import os.path
import datetime
import re

import funtool.state_measure
import funtool_scratch_processes.state_measures.shared as shared



"""

Useful list of blocks

{'Control': ['wait:elapsed:from:',
             'doRepeat',
             'doForever',
             'doIf',
             'doIfElse',
             'doUntil',
             'stopScripts',
             'whenCloned',
             'createCloneOf',
             'deleteClone'],
 'Events': ['whenGreenFlag',
            'whenKeyPressed',
            'whenClicked',
            'whenSceneStarts',
            'whenSensorGreaterThan',
            'whenIReceive',
            'broadcast:',
            'doBroadcastAndWait'],
 'Looks': ['say:duration:elapsed:from:',
           'say:',
           'think:duration:elapsed:from:',
           'think:',
           'show',
           'hide',
           'lookLike:',
           'nextCostume',
           'startScene',
           'changeGraphicEffect:by:',
           'setGraphicEffect:to:',
           'filterReset',
           'changeSizeBy:',
           'setSizeTo:',
           'comeToFront',
           'goBackByLayers:'],
 'More Blocks and Data': ['procDef',
                          'readVariable',
                          'setVar:to:',
                          'changeVar:by:',
                          'showVariable:',
                          'hideVariable:'],
 'Operators': ['+',
               '-',
               '*',
               '/',
               'randomFrom:to:',
               '<',
               '=',
               '>',
               '&',
               '|',
               'not',
               'concatenate:with:',
               'letter:of:',
               'stringLength:',
               '%',
               'rounded',
               'computeFunction:of:',
               'computeFunction:of:'],
 'Pen': ['clearPenTrails',
         'stampCostume',
         'putPenDown',
         'putPenUp',
         'penColor:',
         'changePenHueBy:',
         'setPenHueTo:',
         'changePenShadeBy:',
         'setPenShadeTo:',
         'changePenSizeBy:',
         'penSize:'],
 'Sensing': ['touching:',
             'touchingColor:',
             'color:sees:',
             'distanceTo:',
             'doAsk',
             'keyPressed:',
             'mousePressed',
             'setVideoState',
             'setVideoTransparency',
             'timerReset'],
 'Sound': ['playSound:',
           'doPlaySoundAndWait',
           'stopAllSounds',
           'playDrum',
           'playDrum',
           'rest:elapsed:from:',
           'noteOn:duration:elapsed:from:',
           'instrument:',
           'changeVolumeBy:',
           'setVolumeTo:',
           'changeTempoBy:',
           'setTempoTo:'],
 'motion': ['forward:',
            'turnRight:',
            'turnLeft:',
            'heading:',
            'pointTowards:',
            'gotoX:y:',
            'gotoSpriteOrMouse:',
            'glideSecs:toX:y:elapsed:from:',
            'changeXposBy:',
            'xpos:',
            'changeYposBy:',
            'ypos:']}

"""




def record_parameters(state_measure, analysis_collection, state_collection, overriding_parameters=None):
    """
    Adds a number of fixed values to a state's measure values
        Parameters:
            values: a list dicts with two keys parameter_name and parameter_value


    Example Process:
    ---------------
    store_value:
      measure_module: funtool_scratch_processes.state_measures.default
      measure_function: record_parameters
      analysis_selectors: !!null
      grouping_selectors: !!null
      parameters:
        values: 
          - parameter_name: test_value
            parameter_value: hello
    """
    measure_parameters = funtool.state_measure.get_measure_parameters(state_measure, overriding_parameters)
    state= analysis_collection.state
    for measure_parameter in measure_parameters['values']:
        state.measures[measure_parameter['parameter_name']]=measure_parameter['parameter_value']
    return analysis_collection

def block_counts(state_measure, analysis_collection, state_collection, overriding_parameters=None):
    """
    Counts all different types of blocks in a State

    
    Example Process:
    ---------------
    count_blocks:
      measure_module: funtool_scratch_processes.state_measures.default
      measure_function: block_counts
      analysis_selectors: !!null
      grouping_selectors: !!null
      parameters: !!null
    """
    measure_parameters = funtool.state_measure.get_measure_parameters(state_measure, overriding_parameters)
    block_counts= shared.block_counts( shared.state_scripts(analysis_collection.state) )
    for block_type,block_count in block_counts.items():
        analysis_collection.state.measures[block_type+"_count"]=block_count
    return analysis_collection


@funtool.state_measure.state_and_parameter_measure
def sum_measures(state,parameters):
    """
    Sums all the measures listed
        Parameters:
            measures: a list of measures to sum
            default_value: (optional) set default value when measure is absent, default is 0
   
        control_blocks:
          measure_module: funtool_scratch_processes.state_measures.default
          measure_function:  sum_measures
          analysis_selectors: !!null
          grouping_selectors: !!null
          parameters:
            measures:
              - wait:elapsed:from:_count
              - doRepeat_count
              - doForever_count
              - doIf_count
              - doIfElse_count
              - doUntil_count
              - stopScripts_count
              - whenCloned_count
              - createCloneOf_count
              - deleteClone_count
    """
    total=0
    default_value= 0
    if parameters.get('default_value'):
        default_value= parameters.get('default_value')
    for measure in parameters.get('measures',[]):
        total += state.measures.get(measure,default_value)
    return total


@funtool.state_measure.state_and_parameter_measure
def measure_ratio(state,parameters):
    """
    Computes the ratio between two measures
        Parameters:
            first_measure: the first value in the ratio
            second_measure: the second value in the ratio
            measure_default: (optional) sets the default value for a state if the measure is missing, default is 0
        

    Example Process:
    ---------------
    broadcasts_sent_to_received:
      measure_module: funtool_scratch_processes.state_measures.default
      measure_function: measure_ratio
      analysis_selectors: !!null
      grouping_selectors: !!null
      parameters:
        first_measure: broadcast:_count 
        second_measure: whenIReceive_count 
        measure_default: 0

    """
    a_measure = parameters['first_measure']
    b_measure = parameters['second_measure']
    measure_default = parameters.get('measure_default',0)
    a_value= state.measures.get(a_measure,measure_default)
    b_value= state.measures.get(b_measure,measure_default)
    return shared.compute_ratio(a_value,b_value)

@funtool.state_measure.state_and_parameter_measure
def creation_time_from_filename(state,parameters):
    """
    Function 

    Example Process:
    ----------------
    creation_time:
      measure_module: funtool_scratch_processes.state_measures.default
      measure_function: creation_time_from_filename
      analysis_selectors: !!null
      grouping_selectors: !!null
      parameters: !!null

    """
    filename_base = os.path.basename(state.meta.get('filename','')).split('.')[0]
    if filename_base.isnumeric():
        if len(filename_base)== 10:
            seconds_since_epoch= int(filename_base)
        else:
            seconds_since_epoch= int(filename_base)/1000.0
    else:
        seconds_since_epoch= 0
    return datetime.datetime.fromtimestamp(seconds_since_epoch)

@funtool.state_measure.state_and_parameter_measure
def total_scripts(state,parameters):
    """
    Counts the total number of scripts in a state, including the stage

    Example Process:
    ----------------
    total_scripts:
      measure_module: funtool_scratch_processes.state_measures.default
      measure_function: total_scripts 
      analysis_selectors: !!null
      grouping_selectors: !!null
      parameters: !!null
    """
    return len( shared.state_scripts(state))

@funtool.state_measure.state_and_parameter_measure
def scripts_with_block(state,parameters): #includes stage
    """
    Counts the number of scripts with a particular block, includes stage scripts
        Parameters:
            block_name: the name of the block to look for

    Example Process:
    ----------------
    green_flag_scripts:
      measure_module: funtool_scratch_processes.state_measures.default
      measure_function:  scripts_with_block
      analysis_selectors: !!null
      grouping_selectors: !!null
      parameters:
        block_name: whenGreenFlag 
    """
    block_name = parameters['block_name']
    count = 0
    for script in shared.state_scripts(state):
        if block_name in str(script):
            count += 1
    return count


@funtool.state_measure.state_and_parameter_measure
def total_sprites(state,parameters): 
    """
    Counts the total number of sprites, does not include the state

    Example Process:
    ----------------
    total_sprites:
      measure_module: funtool_scratch_processes.state_measures.default
      measure_function: total_sprites 
      analysis_selectors: !!null
      grouping_selectors: !!null
      parameters: !!null
    """
    return len( shared.all_sprites(state))


@funtool.state_measure.state_and_parameter_measure
def number_of_scripted_sprites(state,parameters): 
    """
    Counts the total number of sprites with scripts, does not include the state

    Example Process:
    ----------------
    total_sprites_with_scripts:
      measure_module: funtool_scratch_processes.state_measures.default
      measure_function: number_of_scripted_sprites 
      analysis_selectors: !!null
      grouping_selectors: !!null
      parameters: !!null
    """
    return len([ sprite for sprite in shared.all_sprites(state) if 'scripts' in sprite ] )


@funtool.state_measure.state_and_parameter_measure
def number_of_sprites_with_block(state,parameters):
    """
    Counts the number of sprites with a particular block, DOES NOT include the stage
        Parameters:
            block_name: the name of the block to look for

    Example Process:
    ----------------
    green_flag_sprites:
      measure_module: funtool_scratch_processes.state_measures.default
      measure_function:  number_of_sprites_with_block
      analysis_selectors: !!null
      grouping_selectors: !!null
      parameters:
        block_name: whenGreenFlag 
    """
    count= 0
    for sprite in shared.all_sprites(state):
        for script in sprite.get('scripts',[]):
            if parameters['block_name'] in str(script):
                count += 1
    return count
    
@funtool.state_measure.state_and_parameter_measure
def scripted_stage(state,parameters):
    """
    Determines if the stage is scripted, returns 1 or 0 

    Example Process:
    ----------------
    scripted_stage
      measure_module: funtool_scratch_processes.state_measures.default
      measure_function: scripted_stage 
      analysis_selectors: !!null
      grouping_selectors: !!null
      parameters: !!null
    """
    return ( 1 if len( shared.stage_scripts) > 0 else 0 )

@funtool.state_measure.state_and_parameter_measure
def number_of_blocks_of_type(state,parameters):
    """
    Counts the total number of blocks  

    Example Process:
    ----------------
    total_sprites_with_scripts:
      measure_module: funtool_scratch_processes.state_measures.default
      measure_function: number_of_scripted_sprites 
      analysis_selectors: !!null
      grouping_selectors: !!null
      parameters: !!null
    """
    return sum([ str( shared.state_scripts(state)).count(block) for block in parameters.get('blocks',[]) ])


