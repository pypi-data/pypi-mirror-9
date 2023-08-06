import functools


def mark(name, value):
    """Marks an object with a given mark (name/value pair)
    """
    return functools.partial(_mark, name=name, value=value)

def get_marks(obj):
    returned = _get_marks(obj)
    if returned is not None:
        returned = returned.copy()
    return returned

def try_get_mark(obj, mark_name):
    """Tries getting a specific mark by name from an object, returning None if no such mark is found
    """
    marks = get_marks(obj)
    if marks is None:
        return None
    return marks.get(mark_name, None)

def _get_marks(obj):
    return getattr(obj, _MARKS_CONTAINER_ATTR, None)

def _set_marks(obj, marks):
    setattr(obj, _MARKS_CONTAINER_ATTR, marks)
    return marks

def _mark(obj, name, value):
    marks = _get_marks(obj)
    if marks is None:
        marks = _set_marks(obj, {})
    marks[name] = value
    return obj

_MARKS_CONTAINER_ATTR = "__slashmarks__"
