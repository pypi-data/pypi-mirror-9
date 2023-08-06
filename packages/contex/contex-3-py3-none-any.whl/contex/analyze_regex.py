from sre_constants import *
import sre_parse
from collections import namedtuple

def group_parents(regex):
    """
    Return a dict of the form {<group-index>: <parents>}

    where <parents> is a set of the group-indices of all the groups the <group-index> is
    nested in.
    """
    tree = sre_parse.parse(regex)
    info = {}
    _fill_group_info(tree, info, frozenset([0])) # All groups has 0 as a parent
    info[0] = frozenset()
    return info
    
def _fill_group_info(subpattern, info, parents):
    """
    Based on the algorithm of `sre_parse.SubPattern.dump`. This is not desirable, as the internal
    workings of `sre_parse` might be changed one day, though this seems to work fine in both
    python2.7 and 3.4. What else am I to do? Make my own parser for python regexes? That could
    easily introduce new bugs.

    Here's why I need to do this: https://mail.python.org/pipermail/python-list/2015-April/701611.html
    """
    for op, av in subpattern:
        if op == IN:
            pass
        elif op == SUBPATTERN:
            group_number, content = av
            if group_number is None: # Non-capturing groups etc
                _fill_group_info(content, info, parents)
            else:
                info[group_number] = parents
                _fill_group_info(content, info, parents | frozenset([group_number]))
        elif op == BRANCH:
            for i, a in enumerate(av[1]):
                _fill_group_info(a, info, parents)
        elif op == GROUPREF_EXISTS:
            condgroup, item_yes, item_no = av
            _fill_group_info(item_yes, info, parents)
            if item_no:
                _fill_group_info(item_no, info, parents)
        elif isinstance(av, (tuple, list)):
            for a in av:
                if isinstance(a, sre_parse.SubPattern):
                    _fill_group_info(a, info, parents)
