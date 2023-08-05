from fuzzywuzzy import fuzz
import fnmatch,glob

def matches_from_list(item,options,fuzzy=90,fname_match=True,fuzzy_fragment=None,guess=False):
    '''Returns the indices of the members of ``options`` that best matches ``item``. Will prioritize
    exact matches, then filename-style matching, then fuzzy matching.
    
         :item:             string to match
         :options:          list of examples to test against
         :fuzzy:            integer (out of 100) describing how close to match string
         :fname_match:      use filename globbing to match files?
         :fuzzy_fragment:   if not ``None``, will accept substring matches of
                            at least ``fuzzy_fragment`` fuzziness
         :guess:            if ``True``, shortcut for setting ``fuzzy`` and ``min_fragment``
                            to very lenient options
    '''
    matches = []
    
    if guess:
        fuzzy = min(fuzzy,80)
        fuzzy_fragment = min(fuzzy_fragment,70)
    
    # Exact matches
    if item in options:
        matches += [i for i in xrange(len(options)) if options[i].lower()==item.lower()]
    
    # Filename-style matches
    if fname_match:
        matches += [options.index(x) for x in fnmatch.filter(options,item) if options.index(x) not in matches]
    
    # Fuzzy matches
    if fuzzy:
        sub_matches = []
        for i in xrange(len(options)):
            r = fuzz.ratio(item.lower(),options[i].lower())
            if r>=fuzzy and i not in matches:
                sub_matches.append((r,i))
        matches += [x[1] for x in sorted(sub_matches)]
    
    # Fragment matches
    if fuzzy_fragment:
        sub_matches = []
        for i in xrange(len(options)):
            r = fuzz.partial_ratio(item.lower(),options[i].lower())
            if r>=fuzzy_fragment and i not in matches:
                sub_matches.append((r,i))
        matches += [x[1] for x in sorted(sub_matches)]
    
    # Even looser matching
    if guess and len(matches)==0:
        sub_matches = []
        for i in xrange(len(options)):
            r = fuzz.partial_token_set_ratio(item.lower(),options[i].lower())
            if r>=fuzzy_fragment and i not in matches:
                sub_matches.append((r,i))
        matches += [x[1] for x in sorted(sub_matches)]
    
    return matches

def best_match_from_list(item,options,fuzzy=90,fname_match=True,fuzzy_fragment=None,guess=False):
    '''Returns the best match from :meth:`matches_from_list` or ``None`` if no good matches'''
    matches = matches_from_list(item,options,fuzzy,fname_match,fuzzy_fragment,guess)
    if len(matches)>0:
        return matches[0]
    return None

def match_and_classify(item,option_dict,fuzzy=90,fname_match=True,fuzzy_fragment=None,guess=False):
    '''Takes a dict where keys are an abstract name of a type, and the values are lists of
    examples (name of type is not included). Will try to match the ``item`` to one of the examples, and then return a tuple
    of the matching (type,example). If ``fname_match``, and no good match can be found in ``option_dict``,
    will try to glob-match a filename and return type of ``file`` for any matches'''
    
    examples = [a for b in option_dict.values() for a in b]
    best_match_i = best_match_from_list(item,examples,fuzzy,fname_match,fuzzy_fragment,guess)
    if best_match_i!=None:
        best_match = examples[best_match_i]
        for item_type in option_dict:
            if best_match==item_type or best_match in option_dict[item_type]:
                return (item_type,best_match)
    if fname_match:
        file_matches = glob.glob(item)
        if len(file_matches):
            return ('file',file_matches[0])
    return None

class Bottle(object):
    '''Container for semantic information (and magical creatures)'''
    def __init__(self):
        #: dict of possible actions, and corresponding methods
        self.actions = {}
        #: dict of abstract names and exemplars
        self.vocab = {}
        #: matching options
        self.fname_match = True
        self.fuzzy = 90
        self.fuzzy_fragment = None
        self.guess = False
    
    def process(self,string):
        '''Searches the string (or list of strings) for an action word (using ``vocab`` and ``actions``), then calls the appropriate function with a dictionary
        of the remaining identified words (according to ``vocab``).
        
        For example, if you have your ``actions`` and ``vocab`` set like::
        
            bottle.actions = {'print':print_me}
            bottle.vocab = {
                'print': ['print','show','list','blah'],
                'say': ['say','speak','sprechen'],
                'money': ['money','moolah','cash','denaros'],
                'self': ['me','user']
            }
        
        Then this command::
        
            bottle.process('Show me the money')
        
        Would result in this function being called::
        
            print_me({'money': ['money'], 'self': ['me'], 'other': ['the']})
        
        '''
        action = None
        if isinstance(string,list):
            items = string
        else:
            items = string.split()
        item_dict = {}
        for item in items:
            c = match_and_classify(item,self.vocab,self.fuzzy,self.fname_match,self.fuzzy_fragment,self.guess)
            if c:
                if c[0] in self.actions and not action:
                    action = self.actions[c[0]]
                else:
                    if c[0] not in item_dict:
                        item_dict[c[0]] = []
                    item_dict[c[0]].append(c[1])
            else:
                if 'other' not in item_dict:
                    item_dict['other'] = []
                item_dict['other'].append(item)
        if action:
            action(item_dict)