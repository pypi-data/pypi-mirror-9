"""
Copyright (C) 2015  Mattias Ugelvik
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

__all__ = ['StringContext', 'MatchContext', 'match', 'search', 'find', 'T', 'rules']

from . import analyze_regex
import collections
import itertools
import fnmatch
import re

    
def T(string):
    """ Returns a `StringContext` version of `string`. The focus point is the whole string. """
    return StringContext(focus=string)


def search(string, pattern, flags=0):
    """ Short for `T(string).search(pattern, flags)` """
    return T(string).search(pattern, flags)


def match(string, pattern, flags=0):
    """ Short for `T(string).match(pattern, flags)` """
    return T(string).match(pattern, flags)


def find(string, substring, right_side=False):
    """ Short for `T(string).find(substring, right_side=right_side)` """
    return T(string).find(substring, right_side=right_side)



def positive_index(i, length):
    """ Convert a negative index to a positive one. """
    return i if i >= 0 else length + i

def ensure_str(val):
    """
    Used to convert things that might be either `StringContext` or `str` into `str`.
    I could use just `str(val)`, that would work, but I want to keep open the possibility
    of `val` being something else, like a bytes object.
    """
    return str(val) if isinstance(val, StringContext) else val


class StringContext:
    """
    A StringContext is like a string, but has three parts: the `before`, the `focus`,
    and the `after`.

    The `focus` is the part which you are currently 'working on'.

    StringContext's are immutable (or are treated as such, that's probably a more
    accurate statement), and any method that makes 'changes' returns a new copy.

    All methods operate on the whole string (i.e. not just the `focus`) unless
    otherwise noted.
    
    Indices refer to the whole string, not just `focus`.
    """
    def __init__(self, before='', focus='', after=''):
        self.before, self.focus, self.after = self.tup = (before, focus, after)
        self._out = None

    def parts(self):
        """ Return a tuple of the form `(<before>, <focus>, <after>)`. """
        return self.tup
        
    def replace(self, replacement):
        """
        This will do one of two things:

          * If `callable(replacement)`, then return a new version of the
            string in which the new `focus` is `str(replacement(old_focus))`.
          * When it is a string it will replace `focus` with `str(replacement)`.
            
        """
        return StringContext(focus=str(replacement(self.focus) if callable(replacement)
                                       else replacement),
                             before=self.before, after=self.after)
        
    def focus_point(self, do_tuple=False):
        """
        Return a slice object that identifies the current `focus`. Return it
        as a tuple of the form `(start, stop)` if `do_tuple`.
        """
        start = len(self.before)
        stop  = start + len(self.focus)
        return (start, stop) if do_tuple else slice(start, stop)


    def find(self, string, right_side=False):
        """
        Find the first location of `string` and set that to be the `focus`.
        Returns None if it doesn't find the string. If `right_side` then it
        will search from right to left.
        """
        result = (str.rfind if right_side else str.find)(str(self), string)

        # Using __getitem__ manually because MatchContext compliance
        return None if result == -1 else StringContext.__getitem__(self, slice(result, result+len(string)))


    def search(self, regex, flags=0):
        """
        Search for the regular expression `regex` in the string with the regex
        flags `flags` and return a `MatchContext`, which is like a `StringContext`
        but with information pertaining to the match. It uses `re.search` for the
        matching.

        Returns `None` if the search is unsuccessful.
        """
        return MatchContext.new(regex, str(self), re.search, flags)

    def match(self, regex, flags=0):
        """ Like `StringContext.search`, but uses `re.match` for the matching. """
        return MatchContext.new(regex, str(self), re.match, flags)

    
    def __getitem__(self, key):
        """
        This will return a new string where `key` designates the focus point.
        Slicing works like with normal strings, except that the 'step' isn't
        supported.
        """
        string = str(self)

        if isinstance(key, int):
            key = positive_index(key, len(string))
            return StringContext(focus=string[key], before=string[:key], after=string[key+1:])

        elif isinstance(key, slice):
            assert key.step is None, "`step` isn't supported"
            return StringContext(focus=string[key],
                                 before=string[:0 if key.start is None else key.start],
                                 after=string[len(string) if key.stop is None else key.stop:])
        
        return key

    def __iter__(self):
        """ Returns `iter(str(self))` """
        return iter(str(self))

    def __hash__(self):
        """ Returns `hash(str(self))` """
        return hash(str(self))

    def __len__(self):
        """ The total length of the string, including the `before` and `after`. """
        return len(str(self))

    def __repr__(self):
        return '{}({!r}, {!r}, {!r})'.format(self.__class__.__name__, *self.tup)

    def __eq__(self, other):
        """
        Will compare equal to `str` and `StringContext` instances where the
        content of the strings matches. So the current `focus` doesn't matter.
        """
        return str(self) == ensure_str(other)

    def __str__(self):
        """ Stitch together `before`, `focus` and `after` to make a normal string. """
        if self._out:
            return self._out
        else:
            self._out = ''.join(self.tup)
            return self._out




def get_index_groups(match):
    """
    I need to do this because `match.lastindex` isn't reliable (the last,
    nested subgroup doesn't count for some reason).
    """
    i = 0
    while True:
        try:
            yield (i, match.span(i))
        except IndexError:
            break
        i += 1
    
def get_groups(match):
    """
    `match` is a match object from the `re` module.
    
    Returns a dict of the form {<group-id>: (<start>, <stop>)} where the <group-id>'s
    are positional regex groups like 0, 1, 2, etc. or named regex groups. <start> and
    <stop> are the indices, and together they form the `span` over the string,
    which may have to be transformed in the course of string manipulation.

    <start> and <stop> are both called `points`, and the rules of transforming them are
    the same, which is helpful for code clarity.

    Regex groups that didn't match will not be present.
    """
    groups = {name: match.span(name)
              for name in match.groupdict()
              if match.span(name) != (-1, -1)}
    groups.update({i: span
                   for i, span in get_index_groups(match)
                   if span != (-1, -1)})
    # Removing (-1, -1), because those groups didn't match

    return groups

def change_groups(groups, changefunc):
    """
    Change every point with the function `changefunc`. `groups` is a
    mapping from group->span returned by `get_groups`.
    """
    return {name: changefunc(name, start, stop)
            for name, (start, stop) in groups.items()}

        
        
class MatchContext(StringContext):
    """
    `MatchContext` is like `StringContext`, but also keeps track of
    matched regex groups and moves them around to the appropriate
    places when the string is manipulated.
    """
    @staticmethod
    def new(regex, string, method, flags=0, group_parents=None):
        match = method(regex, string, flags)

        if match:
            group_span = get_groups(match)
            group_index = {g: g for g in group_span if isinstance(g, int)}
            group_index.update(match.re.groupindex)

            start, stop = group_span[0]

            group_parents = analyze_regex.group_parents(regex) if group_parents is None else group_parents
            
            return MatchContext.new_focus(string, group_parents, group_span, group_index, 0)

            
    @staticmethod
    def new_focus(string, group_parents, group_span, group_index, focus_group):

        span = group_span.get(focus_group)
        if span is None:
            raise ValueError("Regex group {!r} didn't match anything (or it doesn't exist)".format(focus_group))
        else:
            start, stop = span
            return MatchContext(before=string[:start],
                                focus=string[start:stop],
                                after=string[stop:],
                                group_parents=group_parents,
                                group_span=group_span,
                                group_index=group_index,
                                focus_group=focus_group)
        
    
    def __init__(self, before, focus, after, group_parents, group_span, group_index, focus_group):
        StringContext.__init__(self, before=before, focus=focus, after=after)

        self.group_parents = group_parents
        self.group_span    = group_span
        self.group_index   = group_index

        self.focus_group = focus_group

    def parents(self, group_id):
        """ Return a set of group-indexes of the parent regex groups of `group_id`. """
        return self.group_parents[self.group_index[group_id]]

    def __getitem__(self, key):
        """
        `MatchContext` doesn't support slicing. This will return a `StringContext`
        object, and will thus lose the regex group information
        """
        return StringContext.__getitem__(self, key)

    def replace(self, replacement):
        """
        This will do one of two things:

          * If `callable(replacement)`, then return a new version of the
            string in which the new `focus` is `str(replacement(old_focus))`.
          * Else it will replace `focus` with `str(replacement)`.

        This will move around the points of the matched regex groups to keep
        them relevant. Lets say that the ()'s signify the various groups in
        this string: '(He)ll(o)(!)'. If your `focus` is the second group (which
        it would be if you did `str.group(2)`) and you did `str.replace('')`,
        then the result would be '(He)ll()(!)'. The logic for the points in the
        third group is: 'looks like the replaced focus lost 1 char, and I am
        ahead in the string, so I better move back one char too'.

        If your `focus` is the outer-most regex group here: 'Hay, ((ho ho), yolo) yoyo',
        and you replace the focus with 'ho', then the result will be this:
        'Hay, ((ho)) yoyo'. The nested group shrinks.

        But if your `focus` is the outer-most regex group here: 'Hay, ((ho)) yoyo',
        and you replace the focus with 'YOYO', then the result will be this:
        'Hay, ((YO)YO) yoyo'. The nested group doesn't see any reason to expand.
        """

        replacement = str(replacement(self.focus) if callable(replacement) else replacement)

        length = len(self.focus)
        change = len(replacement) - length
        start  = len(self.before)
        newstop = start+length+change
        focus_idx = self.group_index[self.focus_group]

        def change_span(group, span_start, span_stop):
            gindex = self.group_index[group]
            
            if gindex == focus_idx:
                # Same group
                return (span_start, span_stop+change)
            elif gindex in self.group_parents[focus_idx]:
                # group is a parent of focus_group
                return (span_start, span_stop+change)
            elif focus_idx in self.group_parents[gindex]:
                # group is a child of focus_group
                return (min(newstop, span_start), min(newstop, span_stop))
            else:
                # The groups aren't nested in any way
                if gindex > focus_idx:
                    return (span_start+change, span_stop+change)
                else:
                    return (span_start, span_stop)

        new_group_span = change_groups(self.group_span, change_span)

        return MatchContext(group_span=new_group_span,
                            before=self.before,
                            focus=replacement,
                            after=self.after,
                            group_parents=self.group_parents,
                            group_index=self.group_index,
                            focus_group=self.focus_group)
        
    def group(self, group_id):
        """
        Sets the focus point to the part which the regex group `group_id`
        matched. `group_id` can be  an integer signifying a positional
        regex group (0 is the whole string, 1 is first group, 2 second,
        and so on) or a string signifying a named regex group.
        """
        return MatchContext.new_focus(str(self), self.group_parents, self.group_span, self.group_index, group_id)

    def apply_rules(self, rules):
        """
        Apply the `rules` and return the resulting MatchContext (with focus changed).
        The form of the rules are described in the docstring for `contex.rules`.
        """
        result = self
        for area, replacement in sorted(rules.items(),
                                        key=lambda rule: len(self.parents(rule[0])),
                                        # ^ Replace the areas with the most amount of parents first. This way,
                                        # the innermost regex groups are always replaced first.
                                        reverse=True):
            result = result.group(area).replace(replacement)
        return result
        
    
    def expand(self, template, **kwargs):
        """
        Like `str.format` but the indices in the template are the positional
        regex groups and the names are either named regex groups or keyword
        arguments to `expand` (the latter take precedence).

        For example:

        >>> name = contex.match('Bob Bobbison!', r'(?P<forename>\w+) (?P<surname>\w+)(!)?')
        >>> name.expand('{3:+<4} {surname} {hey} {forename} {1}', hey='YoYo', forename='Argh')
        '!+++ Bobbison YoYo Argh Bob'

        The `{3}` refer to the third regex group which is the exclam; `forename`
        did refer to the regex group but was overwritten by the keyword argument to
        `expand`; The `forename` group was available through `{1}` however, because
        that group was also regex group #1.
        """
        out = str(self)

        # I distribute the groups into the named groups and the index groups to use them
        # with `str.format`.
            
        named_groups = {
            group: out[slice(*span)]
            for group, span in self.group_span.items()
            if isinstance(group, str)
        }
        named_groups.update(kwargs)
        
        index_groups = tuple(string
                             for (index, string)
                             in sorted({
                                 group: out[slice(*span)]
                                 for group, span in self.group_span.items()
                                 if isinstance(group, int)
                             }.items()))
        
        return template.format(*index_groups, **named_groups)

    def __repr__(self):
        return '<{} object; group={!r}, tup={!r}>'.format(self.__class__.__name__, self.focus_group, self.tup)


class Transformer:
    def __init__(self, regex, rules, method, flags=0):
        self.regex = re.compile(regex, flags=flags)
        self.group_parents = analyze_regex.group_parents(regex)
        self.rules = rules
        self.method = method
                

    def _apply(self, string):
        view = MatchContext.new(self.regex, string, self.method, group_parents=self.group_parents)
        if not view:
            raise ValueError("Regex {!r} didn't match string {!r}".format(self.regex, string))
        else:
            return view.apply_rules(self.rules)

    def apply(self, string):
        """ Performs the replacements according to the rules and returns the resulting string """
        return str(self._apply(string))

    def expand(self, string, template, **kwargs):
        """
        Like `str.format` but the indices in the template are the positional regex
        groups and the names are either named regex groups or keyword arguments to
        `expand` (the latter take precedence).

        For example:

            >>> t = contex.rules(r'(?P<first_name>\w+) (?P<last_name>\w+)', {})
            >>> t.expand('Bob Bobbington', '{greeting}, Mr. {last_name}!', greeting='Welcome')
            'Welcome, Mr. Bobbington!'

        It will also apply the rules (in the example above there are none) before
        expanding.

        More info can be found in `MatchContext.expand`.
        """
        return self._apply(string).expand(template, **kwargs)

    def __repr__(self):
        return '<{} object; regex={!r}, rules={!r}, method={}.{}>'.format(
            self.__class__.__name__, self.regex, self.rules,
            self.method.__module__, self.method.__name__
        )

        
        
def rules(regex, rules, method=None, flags=0):
    """
    Usage: contex.rules(regex, rule_dict, method=re.fullmatch, flags=0)

    Returns a `Transformer` object ready to transform strings according to the rules
    you have set in `rule_dict`.

    The optional `regex` will be matched against strings using `re.fullmatch` (or an
    equivalent behaviour will be arranged for earlier versions of python), and you can
    refer to matched regex groups in the `rule_dict`. If you want to use a different
    function to search with, such as `re.search`, then you can pass that in as the
    `method` argument. Although the `regex` might match only a substring if you use
    `re.search`, you will still manipulate the string as a whole.

    `regex` must be a `str`, and it will be compiled with `re.compile`, along with
    the `flags` you pass in.

    The rule dict is of the form {<area>: <replacement>}. <area> can be:
      * int, designating a regular expression group.
      * str, designating a named regular expression group.
    The <replacement> can be:
      * str, designating a verbatim string replacement.
      * unary function. It will be passed the text of <area> to modify, and should
        return the new replacement which will automatically be converted to a str.

    If one <area> is inside another <area> in the same rule_dict, then the innermost
    <area> will be replaced first. This replacement will be visible to the replacement
    for the outer <area> if it happens to be a function.

    You can then use the `.apply` or `.expand` methods of the `Transformer` object to
    manipulate the string.

      * Transformer.apply(string) will merely do the replacements and return the
        resulting string.
      * Transformer.expand(string, template, **kwargs) also does the replacements, but
        will fill in the `template` string with info from the match and from keyword
        arguments. The format for the template string is the same as with `str.format`,
        but the numbers refer to positional regex group and the strings to named regex
        groups (unless overwritten by the **kwargs).
    
    
    Here is an example:

        >>> contex.rules(r'(Photo)(\d+)_(?P<year>\d{4})\.(?P<suffix>jpg)', {
            1: 'Foto',                      # I like to spell it this way better
            2: lambda num: int(num) + 1,    # Turns out the numbers should be 1 higher
            'year': lambda year: year[-2:], # I don't need all 4 digits
            'suffix': 'jpeg'
        }).apply('Photo25_2009.jpg')
        'Foto26_09.jpeg'

    Pretty readable huh, considering how complicated and numerous those replacements are?

    Now lets say that you want to make the changes like above, but that you also want to
    change the layout of the filename to `<year>-<number>-Foto.<suffix>`. This is how:

        >>> contex.rules(r'Photo(\d+)_(?P<year>\d{4})\.jpg', {
            1: lambda num: int(num) + 1,    # Turns out the numbers should be 1 higher
            'year': lambda year: year[-2:]  # I don't need all 4 digits
        }).expand('Photo25_2009.jpg', '{year}-{1}-Foto.jpeg')
        '09-26-Foto.jpeg'

    This also allowed me to remove a couple of rules.

    Here is an example of using regex flags and specifying a method:

        >>> contex.rules(r"FEEL", {0: "YOLO"}, method=re.search, flags=re.I).apply("I feel great")
        'I YOLO great'

    The 0th regex group designates the whole match, as is tradition, but the whole match
    in this case is only a substring of the string you're manipulating. If you want only
    the match area returned, you can use `.expand(string, "{0}")` to extract it.
    """

    if method is None:
        if not hasattr(re, 'fullmatch'):
            # Needed for earlier versions of python that doesn't have `re.fullmatch`
            # \Z matches end-of-string, together with `re.match` it should work just
            # like `re.fullmatch`. \Z\Z still matches the end-of-string.
            regex = regex+'\Z'
            method = re.match
        else:
            method = re.fullmatch
        
    return Transformer(regex, rules, method, flags)
