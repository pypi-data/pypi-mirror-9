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

import re
import fnmatch


def T(string):
    """
    Returns a `StringContext` version of `string`. The focus point is the whole string.
    """
    return StringContext(focus=string)

def search(string, pattern, flags=0):
    """
    Short for `T(string).search(pattern, flags)`
    """
    return T(string).search(pattern, flags)
    
def match(string, pattern, flags=0):
    """
    Short for `T(string).match(pattern, flags)`
    """
    return T(string).match(pattern, flags)

def find(string, substring):
    """
    Short for `T(string).find(substring)`
    """
    return T(string).find(substring)



def ensure_string(val):
    """
    Used to convert things that might be either `StringContext` or `str` into `str`.
    I could use just `str(val)`, that would work, but I want to keep open the possibility
    of `val` being something else, like a bytes object.
    """
    if isinstance(val, StringContext):
        return str(val)
    else:
        return val

def get_groups(match):
    """
    `match` is a match object from the `re` module.
    
    Returns a dict of the form {<group-id>: (<start>, <stop>)} where the <group-id>'s
    are positional regex groups like 0, 1, 2, etc. or named regex groups. <start> and
    <stop> are the indices, and together they form the `span` over the string,
    which may have to be transformed in the course of string manipulation.

    <start> and <stop> are both called `points`, and the rules of transforming them are
    the same, which is helpful for code clarity.

    The span can also be (-1, -1), which means that the regex group didn't match, though
    not all positional regex groups that didn't match are guaranteed to be present, as a
    consequence of the way `match.lastindex` works.
    """
    groups = {name: match.span(name) for name in match.groupdict()}
    groups.update({i: match.span(i) for i in range(0, (match.lastindex or 0)+1)})

    return groups


def change_groups(groups, changefunc):
    """
    Change every point with the unary function `changefunc`, except for regex groups
    that didn't match (those that are (-1, -1))

    This function will sort the regex group after the points has been changed so the
    smalles comes first.
    """
    return {name: tuple(sorted(map(changefunc, span)))
            if not span == (-1, -1) else span for name, span in groups.items()}

    
def make_point_mover(start, length, change):
    """
    This will return a unary function that will know how points in regex groups shall be moved
    when there has been changes in the MatchContext.

    `(start, start+length)` is the span of the original "focus point" that has been changed, and
    `change` is an int that represents how much that area has grown or shrunken.
    Thus `(start, start+length+change)` is the new span.
    """
    def change_point(point):
        if point <= start:
            return point
        elif point >= start+length:
            return point+change
        else:
            """ In this case, point is *between* start and start+length.
            point is changed only if the focus point has shrunken
            so much that point is pointing outside of the focus point.
            Otherwise it should remain the same.

            For example in this string: "|hello(123)abc|lala"
            if the |'s signify the focus point and the ()'s signify the
            span of a regex group. If you were to remove everything in the focus point,
            then it wouldn't be very cool for the regex group to contain any of the "lala"
            stuff; the result ought to be this: "|()|lala". So you ought to shrink the points
            of the regex group.
            
            """
            
            new_stop = start+length+change
            return min(new_stop, point)
    
    return change_point



    
class StringContext:
    """
    A StringContext is like a string, but has three parts: the `before`, the `focus`, and the `after`.

    The `focus` is the part which you are currently "working on".

    StringContext's are immutable, and any method that makes "changes" returns a new copy.

    All methods operate on the whole string (i.e. not just the `focus`) unless otherwise noted.
    
    Indices refer to the whole string, not just `focus`.
    """
    def __init__(self, before="", focus="", after=""):
        (self.before, self.focus, self.after) = self.tup = (ensure_string(before),
                                                            ensure_string(focus),
                                                            ensure_string(after))
        self._out = None

    def _new_focus(self, focus, before, after):
        return StringContext(before=before, focus=focus, after=after)

    def parts(self):
        """
        Return a tuple of the form `(<before>, <focus>, <after>)`.
        """
        return self.tup
        
    def replace(self, replacement):
        """
        This will do one of two things:

          * If `callable(replacement)`, then return a new version of the string in which the
            new `focus` is `replacement(old_focus)`. If the callable returns a `StringContext`,
            then it will be converted to a `str` automatically.
          * When it is a string it will replace `focus` with that string verbatim.
            
        """
        return StringContext(focus=ensure_string(replacement(self.focus) if callable(replacement) else replacement),
                             before=self.before, after=self.after)

    def set_before(self, replacement):
        """
        Like `StringContext.replace`, but for `before`.
        """
        return StringContext(before=ensure_string(replacement(self.before) if callable(replacement) else replacement),
                             focus=self.focus, after=self.after)
        
    def set_after(self, replacement):
        """
        Like `StringContext.replace`, but for `after`.
        """
        return StringContext(after=ensure_string(replacement(self.after) if callable(replacement) else replacement),
                             before=self.before, focus=self.focus)
        
    def forget(self):
        """
        Forget the context, or the `before` and the `after`, and remember only `focus`.
        """
        return StringContext(focus=self.focus)

    def fullview(self):
        """
        Let `focus` expand and take over the whole string.
        """
        return StringContext(focus=str(self))
        
    def focus_point(self, do_tuple=False):
        """
        Return a slice object that identifies the current `focus`. Return it as a tuple
        of the form `(start, stop)` if `do_tuple`.
        """
        start = len(self.before)
        stop  = start + len(self.focus)
        return (start, stop) if do_tuple else slice(start, stop)


    def find(self, string, right_side=False):
        """
        Find the first location of `string` and set that to be the `focus`. Returns None if
        it doesn't find the string. If `right_side` then it will search from right to left.
        """
        string = ensure_string(string)
        method = str.rfind if right_side else str.find
        result = method(str(self), string)

        if result == -1:
            return None
        else:
            return self[result:result + len(string)]

    def search(self, regex, flags=0, _match=False):
        """
        Search for the regular expression `regex` in the string with the regex flags `flags` and return a
        `MatchContext`, which is like a `StringContext` but with information pertaining to the match.

        Return `None` if the search is unsuccessful.

        It uses `re.search` for the searching.

        The focus point of the `MatchContext` will be the area that matched.
        """
        match = (re.match if _match else re.search)(ensure_string(regex), str(self), flags)

        if match:
            return MatchContext(focus=str(self), _group_spans=get_groups(match)).group(0)

    def match(self, regex, flags=0):
        """
        Like `StringContext.search`, but it doesn't search forward and will have to match from the first
        character in the string.

        It uses `re.match` for the matching.

        The focus point of the `MatchContext` will be the area that matched.
        """
        return self.search(ensure_string(regex), flags, _match=True)
            

    def glob(self, pattern):
        """
        Checks if the glob `pattern` matches the string and returns a `bool`.
        It uses `fnmatch.fnmatch` to do this.
        """
        return fnmatch.fnmatch(str(self), ensure_string(pattern))

    def reverse(self, reverse_meta=True):
        """
        Reverse the string, including the current focus. So if you reverse this string: "H(el)lo", in which
        the ()'s signify the focus point, then the result will be "ol(le)H".

        If not `reverse_meta` then the focus will "stay put".
        """
        result = StringContext(focus=str(self)[::-1])
        if reverse_meta:
            new_focus = sorted(map(lambda point: len(self) - point,
                                   self.focus_point(do_tuple=True)))
            return result[slice(*new_focus)]
        else:
            return result[self.focus_point()]

    def __getitem__(self, key):
        """
        This will return a new string where `key` designates the focus point. The two forms s[<int>] and s[<int>:<int>]
        are supported, and slice the same part as in normal strings.
        """
        string = str(self)

        if isinstance(key, int):
            if key < 0:
                key = len(string) + key
            return self._new_focus(string[key], before=string[:key], after=string[key+1:])

        elif isinstance(key, slice):
            assert key.step is None, "`step` isn't supported"
            return self._new_focus(string[key],
                                   before=string[:0 if key.start is None else key.start],
                                   after=string[len(string) if key.stop is None else key.stop:])
        
        return key

    def __iter__(self):
        """
        Returns `iter(str(self))`
        """
        return iter(str(self))

    def __hash__(self):
        """
        Returns `hash(str(self))`
        """
        return hash(str(self))

    def __len__(self):
        """
        The total length of the string, including the `before` and `after`.
        """
        return len(str(self))

    def __repr__(self):
        return "{}({!r}, {!r}, {!r})".format(type(self).__name__, *self.tup)

    def __eq__(self, other):
        """
        Will compare equal to `str` and `StringContext` instances where the content of the strings matches. So
        the current `focus` doesn't matter.
        """
        return str(self) == ensure_string(other)

    def __str__(self):
        """
        Stitch together `before`, `focus` and `after` to make a normal string.
        """
        if self._out:
            return  self._out
        else:
            self._out = "".join(self.tup)
            return self._out


        
class MatchContext(StringContext):
    """
    `MatchContext` is like `StringContext`, but also keeps track of matched regex groups and
    moves them around to the appropriate places when the string is manipulated.
    """
    def __init__(self, before="", focus="", after="", _group_spans={}):
        StringContext.__init__(self, before=before, focus=focus, after=after)
        self.group_spans = _group_spans




    def fullview(self):
        """
        Let `focus` expand and take over the whole string.
        """
        return MatchContext(focus=str(self), _group_spans=self.group_spans)

    def _new_focus(self, focus, before="", after=""):
        return MatchContext(before=before, focus=focus, after=after, _group_spans=self.group_spans)

    def replace(self, replacement):
        """
        This will do one of two things:

          * If `callable(replacement)`, then return a new version of the string in which the
            new `focus` is `replacement(old_focus)`.
          * When it is a string it will replace `focus` with that string verbatim.

        This will move around the points of the matched regex groups to keep them relevant.
        Lets say that the ()'s signify the various groups in this string: "(He)ll(o)(!)",
        if the span of your `focus` is identical to the second group (which it would be if
        you did `str.group(2)`) and you did `str.replace("")`, then the result would be
        "(He)ll()(!)". The logic for the points in the third group is: "looks like the replaced
        focus lost 1 char, and I am ahead in the string, so I better move back one char too".

        If the |'s signify the focus in this string: "Hay, |(ho ho), yolo| yoyo", and you replace
        the focus with "ho", then the result will be this: "Hay, |(ho)| yoyo". The group shrinks
        because it wouldn't make any sense for the `ho ho` to contain any of dat `yoyo`, if
        you know what I mean.
        """
        return self._replace(replacement, "focus")

    def set_before(self, replacement):
        """
        Like `MatchContext.replace`, but for `before`.
        """
        return self._replace(replacement, "before")
                
    def set_after(self, replacement):
        """
        Like `MatchContext.replace`, but for `after`.
        """
        return self._replace(replacement, "after")

    def _replace(self, ment, which_part):

        parts = {
            "before": self.before,
            "focus":  self.focus,
            "after":  self.after
        }
        sizes = {
            "before": len(self.before),
            "focus":  len(self.focus),
            "after":  len(self.after)
        }
        start_indices = {
            "before": 0,
            "focus":  len(self.before),
            "after":  len(self.before) + len(self.focus)
        }
        
        replacement = ment(parts[which_part]) if callable(ment) else ensure_string(ment)
        
        original_size = sizes[which_part]
        size_change = len(replacement) - original_size


        new_group_spans = change_groups(self.group_spans,
                                        make_point_mover(start_indices[which_part],
                                                         original_size,
                                                         size_change))
        parts[which_part] = replacement
        
        return MatchContext(_group_spans=new_group_spans, **parts)

    def reverse(self, reverse_meta=True):
        """
        Reverse the string, including the current focus. So if you reverse this string: "H(el)lo", in which
        the ()'s signify the focus point, then the result will be "ol(le)H".

        This will also reverse the regex groups in the same way that the focus point is reversed.

        If not `reverse_meta`, then it will not reverse the focus point and the regex groups.
        """
        if not reverse_meta:
            return MatchContext(_group_spans=self.group_spans, focus=str(self)[::-1])[self.focus_point()]
        else:
            out_len = len(self)
            def reverse_point(point):
                return out_len - point
        
            new_group_spans = change_groups(self.group_spans, reverse_point)
            new_focus = tuple(sorted(map(reverse_point,
                                         self.focus_point(do_tuple=True))))

            return MatchContext(_group_spans=new_group_spans, focus=str(self)[::-1])[slice(*new_focus)]
        
    def group(self, group_id):
        """
        Sets the focus point to the part which the regex group `group_id` matched. `group_id` can be
        an integer signifying a positional regex group (0 is the whole string, 1 is first group, 2 second,
        and so on) or a string signifying a named regex group.
        """
        span = self.group_spans.get(group_id, (-1, -1))
        if span == (-1, -1): # Regex group didn't match anything
            raise ValueError("Regex group {!r} didn't match anything (or it doesn't exist)".format(group_id))
        else:
            return self[slice(*span)]

    def expand(self, template, **kwargs):
        """
        Like `str.format` but the indices in the pattern are the positional regex groups and the
        names are either named regex groups or keyword arguments to `expand` (the latter take precedence).
        For example:

        >>> name = contex.T("Bob Bobbison!").match(r"(?P<first_name>\w+) (?P<last_name>\w+)(!)?")
        >>> name.expand("{3:+<4} {last_name} {hey} {first_name} {1}", hey="YoYo", first_name="Argh")
        '!+++ Bobbison YoYo Argh Bob'

        The `{3}` refer to the third regex group which is the exclam; `first_name` did refer to the regex
        group but was overwritten by the keyword argument to `expand`; The `first_name` group was available
        through `{1}` however, because that group was also regex group #1.
        """
        out = str(self)
        
        matched = lambda span: not span == (-1, -1)

        """
        I distribute the groups into the named groups and the index groups to use them
        with `str.format`
        """
            
        named_groups = {
            group: out[slice(*span)]
            for group, span in self.group_spans.items()
            if matched(span) and isinstance(group, str)
        }
        named_groups.update(kwargs)
        
        index_groups = tuple(string
                             for (index, string)
                             in sorted({
                                 group: out[slice(*span)]
                                 for group, span in self.group_spans.items()
                                 if matched(span) and isinstance(group, int)
                             }.items()))
        
        return ensure_string(template).format(*index_groups, **named_groups)
