

def serialize_tuple(item):
    """serializes a tuple to a string.
       the tuple contains strings mixed with nested tuples which contain strings....

       the output uses brackets to denote tuple 'boundaries', "," is used to seperate
       the items of a tuple and a non-empty tuples conversion must end with a ","
       (so we can distinguis the conversion output of () and ("",) )

       a backslash escapes the interpetation of special charachters (brackets, ",", backslash)
    """
    if isinstance(item, tuple):
        if len(item) == 0:
            return "[]"
        return "[" + ",".join(serialize_tuple(t) for t in item) + ",]"
    assert isinstance(item, basestring), "item is of wrong type %r" % item
    item = item.replace("\\", r"\\")
    return item.replace("[", r"\[").replace("]", r"\]").replace(",", r"\,")


def _parse(ts, i=0):
    """helper function for reversing the output of `serialize_tuple`"""
    rv = []
    item = ""
    assert ts[0] == "["
    i += 1
    while i < len(ts):
        if ts[i] == "]":
            return tuple(rv), i + 1
        if ts[i] not in "[],":
            if ts[i] == "\\":
                i += 1
            item += ts[i]
            i += 1
            continue
        if ts[i] == "[":
            item, i = _parse(ts, i)
        if ts[i] == ",":
            rv.append(item)
            item = ""
            i += 1
            continue
        raise Exception("syntax error in '%s' at position %d" % (ts, i))


def unserialize_tuple(ts):
    """reverses the output of serialize_tuple.

    `unserialize_tuple` creates a (nested) tuple from a string which conforms the structure of the
    output of `serialize_tuple`.
    """
    return _parse(ts, 0)[0]
