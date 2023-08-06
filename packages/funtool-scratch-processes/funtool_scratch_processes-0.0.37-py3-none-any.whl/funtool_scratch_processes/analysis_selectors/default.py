# These are a default set of analysis_selector functions
# A state selector function should accept three parameters a AnalysisSelector, an AnalysisCollection and a StateCollection
#  it should return an AnalysisCollection
# All functions that don't accept (AnalysisSelector,AnalysisCollection,StateCollection) and return AnalysisCollection should
#  be internal functions

import funtool.analysis
import random

def trivial(analysis_selector, analysis_collection, state_collection):
    return analysis_collection

def random_state(analysis_selector, analysis_collection, state_collection):
    return funtool.analysis.AnalysisCollection(random.choice(state_collection.states),None,[])
