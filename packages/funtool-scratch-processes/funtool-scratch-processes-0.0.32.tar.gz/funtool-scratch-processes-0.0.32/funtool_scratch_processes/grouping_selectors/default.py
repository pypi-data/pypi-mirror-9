# These are default grouping_selector functions
# A grouping selector function should accept a grouping_selector, and a state_collection
# and return an updated state_collection

import funtool.group

def all(grouping_selector,state_collection,overriding_parameters,loggers=None):
    state_collection.groups_dict[grouping_selector.grouping_selector_name]= [ 
        funtool.group.create_group( grouping_selector.grouping_selector_name, state_collection.states, {}, {} )
    ]
    return state_collection

