# These are default grouping_selector functions
# A grouping selector function should accept a grouping_selector, and a state_collection
# and return an updated state_collection

import funtool.group
import funtool.grouping_selector
import collections

def all(grouping_selector,state_collection,overriding_parameters,loggers=None):
    state_collection.groups_dict[grouping_selector.name]= [ 
        funtool.group.create_group( grouping_selector.name, state_collection.states, {}, {} )
    ]
    return state_collection

def by_measures_and_meta(grouping_selector,state_collection,overriding_parameters,loggers=None):
    """
    Creates a grouping based on the values of a list of measures and metas specified in parameters

    Example Process
    ---------------
    total_sprites:
      selector_module: funtool_scratch_processes.grouping_selectors.default
      selector_function: by_measures_and_meta
      parameters: 
        measures: 
          - total_sprites 
        metas: !!null
    """
    selector_parameters= funtool.grouping_selector.get_selector_parameters(grouping_selector, overriding_parameters)
    grouped_states= collections.defaultdict(list)

    if selector_parameters.get('measures') is None:
        selector_parameters['measures']=[] 
    if selector_parameters.get('meta') is None:
        selector_parameters['meta']=[] 
    for state in state_collection.states:
        key_values=[]
        for measure_name in selector_parameters.get('measures'):
            key_values.append(state.measures.get(measure_name))
        for meta_name in selector_parameters.get('meta'):
            key_values.append(state.meta.get(meta_name))
        grouped_states[tuple(key_values)].append(state)
    state_collection.groups_dict[grouping_selector.name]= [ 
        funtool.group.create_group( 
            grouping_selector.name, 
            states, 
            {}, 
            dict(zip( (selector_parameters.get('measures') + selector_parameters.get('meta')) ,grouping_value)) 
        ) 
        for grouping_value, states in grouped_states.items() 
    ]
    return state_collection

