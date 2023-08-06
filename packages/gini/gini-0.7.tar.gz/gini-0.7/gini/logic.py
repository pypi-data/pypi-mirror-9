def and_sets(*sets):
    return sets[0].intersection(*sets[1:])

def or_sets(*sets):
    return sets[0].union(*sets[1:])

def not_sets(*sets):
    return sets[-1].difference(*sets[:-1])

def bool_set(operation,*sets):
    '''combine ``sets`` with ``operation``
    
    :and:       combine sets with AND
    :or:        combine sets with OR
    :not:       NOT sets versus the last given set'''
    if len(sets)<=1:
        return sets
    if operation=='and':
        return and_sets(*sets)
    if operation=='or':
        return or_sets(*sets)
    if operation=='not':
        return not_sets(*sets)