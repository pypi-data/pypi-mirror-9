def Metastruct(d):
  """Convert a :class:`dict` to an object.

  Recursively convert a :class:`dict` into an object with attributes matching
  the keys of the original :class:`dict`.

  :param d: The :class:`dict` to convert.

  """
  top = type('MetastructElement', (object,), d)
  seqs = tuple, list, set, frozenset
  for key, value in d.items():
    if isinstance(value, dict):
      setattr(top, key, Metastruct(value))
    elif isinstance(value, seqs):
      setattr(top, key, type(value)(Metastruct(sub_value) if isinstance(sub_value, dict) else sub_value for sub_value in value))
    else:
      setattr(top, key, value)
  return top
