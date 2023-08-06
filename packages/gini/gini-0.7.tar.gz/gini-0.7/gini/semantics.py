from gini.matching import best_match_from_list,matches_from_list
import copy

class ConceptMatch(object):
    def __init__(self,concept):
        #: A back-reference to the original matching concept
        self.concept = concept
        #: The string this concept was matched to
        self.string = None
        #: Matching item
        self.item = None
        #: List of matching example
        self.examples = None
        #: This concept is currently being used in the negative sense (i.e., "not ____")
        self.negative = False
        #: The type of match this was found in (e.g., ``exact`` or ``fuzzy``)
        self.type = None
        #: The degree of match (when using fuzzy matching)
        self.amount = None
    
    def __eq__(self,other):
        '''To make things easy, just follow the :class:`Concept`'''
        return self.concept==other
    
    def __repr__(self):
        return 'ConceptMatch(%s)' % self.concept
        

def sort_matches(matches):
    '''Sorts a ``list`` of matches best to worst'''
    multipliers = {'exact':10**5,'fname':10**4,'fuzzy':10**2,'fuzzy_fragment':1}
    matches = [(multipliers[x.type]*(x.amount if x.amount else 1),x) for x in matches]
    return [x[1] for x in sorted(matches,reverse=True)]    

class Concept(object):
    def __init__(self,name,example_lists,parent=None,action=None,meta=None):
        '''Create a :class:`Concept` named ``name`` using the given examples. 
        
        ``example_lists`` can be given in multiple ways. As a ``list`` of strings, it's interpreted
        as multiple examples of a single item. If it's a ``list`` of ``list``s, each sub-``list`` is treated
        as an item. If a ``dict`` is given, the values of each entry are expected to be ``list``s of 
        examples for each item, named by the key'''
        #: Arbitrary label for concept
        self.name = name
        #: Method to run if this is used as an action
        self.action = action
        #: Any information to attach to this object
        self.meta = meta
        
        #: List of example strings for each item
        self.examples = {}
        if isinstance(example_lists,list):
            if len(example_lists)>0:
                if isinstance(example_lists[0],basestring):
                    self.examples[name] = example_lists
                elif isinstance(example_lists[0],list):
                    self.examples = {x[0]:x for x in example_lists}
                else:
                    raise RuntimeError('Cannot understand example_lists given')
        elif isinstance(example_lists,dict):
            self.examples = example_lists
        else:
            raise RuntimeError('Cannot understand example_lists given')            
        
    def __repr__(self):
        return 'Concept(%s)' % self.name
    
    def __eq__(self,other):
        '''Concepts are equal if their names are equal, or if it is a string with the same name'''
        return (isinstance(other,self.__class__) and other.name==self.name) or (isinstance(other,basestring) and self.name==other)
    
    def matches(self,string,fuzzy=90,fname_match=True,fuzzy_fragment=None,guess=False):
        '''Returns whether this :class:`Concept` matches ``string``'''
        
        matches = []
        for item in self.examples:
            m = best_match_from_list(string,self.examples[item],fuzzy,fname_match,fuzzy_fragment,guess)
            if m:
                match = ConceptMatch(self)
                match.concept = self
                match.string = string
                match.item = item
                match.examples = m[0]
                match.type = m[2]
                match.amount = m[3]
                matches.append(match)
        return sort_matches(matches)


class Bottle(object):
    '''Container for semantic information (and magical creatures)'''
    def __init__(self,vocab=[]):
        #: list of :class:`Concepts` to match with
        self.vocab = vocab
        #: matching options
        self.fname_match = True
        self.fuzzy = 90
        self.fuzzy_fragment = None
        self.guess = False
        #: Allow the use of "not" and a "-" before a term to negate the term
        self.negative = True
    
    def set_action(self,concept_name,action_meth):
        '''helper function to set the ``action`` attr of any :class:`Concept`s in ``self.vocab`` that match ``concept_name`` to ``action_meth``'''
        for concept in self.vocab:
            if concept.name == concept_name:
                concept.action = action_meth
    
    def match_all_concepts(self,string):
        '''Returns sorted list of all :class:`Concept`s matching ``string``'''
        multipliers = {'exact':10**5,'fname':10**4,'fuzzy':10**2,'fuzzy_fragment':1}
        matches = []
        for concept in self.vocab:
            matches += concept.matches(string,self.fuzzy,self.fname_match,self.fuzzy_fragment,self.guess)
        return sort_matches(matches)
    
    def match_concept(self,string):
        '''Find all matches in this :class:`Bottle` for ``string`` and return the best match'''
        matches = self.match_all_concepts(string)
        if len(matches)>0:
            return matches[0]
        return None
    
    def parse_string(self,string,best=False):
        '''Parses ``string`` trying to match each word to a :class:`Concept`. If ``best``, will only return the top matches'''
        if isinstance(string,list):
            items = string
        else:
            items = string.split()
        item_list = []
        not_next = False
        for item in items:
            if self.negative:
                if item=='not':
                    not_next = True
                    continue
                if item[0]=='-':
                    not_next = True
                    item = item[1:]
            concepts = self.match_all_concepts(item)
            if len(concepts)>0:
                if not_next:
                    for concept in concepts:
                        concept.negative = True
                if best:
                    item_list.append(concepts[0])
                else:
                    item_list.append(concepts)
            else:
                item_list.append(item)
            not_next = False
        return item_list
    
    def process_string(self,string):
        '''Searches the string (or list of strings) for an action word (a :class:`Concept` that has and ``action`` attached
        to it), then calls the appropriate function with a dictionary of the identified words (according to ``vocab``).
        
        For examples, see ``demo.py``
        '''
        item_list = self.parse_string(string)
        for item in item_list:
            if len(item)>0 and 'concept' in dir(item[0]) and 'action' in dir(item[0].concept) and item[0].concept.action:
                item[0].concept.action(item_list)