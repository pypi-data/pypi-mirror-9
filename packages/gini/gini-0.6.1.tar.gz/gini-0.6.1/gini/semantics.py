from gini.matching import best_match_from_list

class Concept(object):
    def __init__(self,name,example_list=None):
        #: Arbitrary label
        self.name = name
        #: List of example strings
        self.examples = []
        if example_list:
            self.examples = example_list
        #: Method to run if this is used as an action
        self.action = None
        #: Any information to attach to this object
        self.meta = None
        #: [return value] Name of the matching item
        self.match = None
        #: [return value] This concept is currently being used in the negative sense (i.e., "not ____")
        self.negative = False
        #: [return value] The type of match this was found in (e.g., ``exact`` or ``fuzzy``)
        self.match_type = None
        #: [return value] The degree of match (when using fuzzy matching)
        self.match_amount = None
    
    def match_string(self,string,fuzzy=90,fname_match=True,fuzzy_fragment=None,guess=False):
        m = best_match_from_list(string,self.examples,fuzzy,fname_match,fuzzy_fragment,guess)
        if m:
            self.match = m[0]
            self.match_type = m[2]
            self.match_amount = m[3]
            return self
        return None

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
    
    def match_word(self,string):
        multipliers = {'exact':10**5,'fname':10**4,'fuzzy':10**2,'fuzzy_fragment':1}
        matches = []
        for concept in self.vocab:
            match = concept.match_string(string,self.fuzzy,self.fname_match,self.fuzzy_fragment,self.guess)
            if match:
                matches.append((multipliers[match.match_type]*(match.match_amount if match.match_amount else 1),match))
        if len(matches)>0:
            return sorted(matches,reverse=True)[0][1]
        return None
    
    def matches_from(self,string):
        if isinstance(string,list):
            items = string
        else:
            items = string.split()
        item_dict = {}
        not_next = False
        for item in items:
            if self.negative:
                if item=='not':
                    not_next = True
                    continue
                if item[0]=='-':
                    not_next = True
                    item = item[1:]
            concept = self.match_word(item)
            if concept:
                if not_next:
                    concept.negative = True
                if concept.name not in item_dict:
                    item_dict[concept.name] = []
                item_dict[concept.name].append(concept)
            else:
                if 'other' not in item_dict:
                    item_dict['other'] = []
                item_dict['other'].append(item)
            not_next = False
        return item_dict
    
    def process(self,string):
        '''Searches the string (or list of strings) for an action word (a :class:`Concept` that has and ``action`` attached
        to it), then calls the appropriate function with a dictionary of the identified words (according to ``vocab``).
        
        For example, if you have your ``vocab`` set like::
        
            print_concept = Concept('print', ['print','show','list','blah'])
            print_concept.action = print_me
            bottle.vocab = [
                print_concept,
                Concept('say', ['say','speak','sprechen']),
                Concept('money', ['money','moolah','cash','denaros']),
                Concept('self', ['me','user'])
            ]
        
        Then this command::
        
            bottle.process('Show me the money')
        
        Would result in this function being called::
        
            print_me({'money': [Concept('money')], 'self': [Concept('me')], 'other': ['the']})
        
        '''
        item_dict = self.matches_from(string)
        for item in item_dict:
            if 'action' in dir(item_dict[item][0]) and item_dict[item][0].action:
                item_dict[item][0].action(item_dict)