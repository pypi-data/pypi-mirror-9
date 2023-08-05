from metastruct import Metastruct


def test_stuff():
  s = Metastruct({
    'a': 'a',
    'b': {
      'a': 'ba',
      'b': 'bb',
      'c': {
        'a': 'bca',
      },
    },
    'c': [1, 2, 3],
  })
  assert s.a == 'a'
  assert s.b.a == 'ba'
  assert s.b.b == 'bb'
  assert s.b.c.a == 'bca'
  assert s.c == [1, 2, 3]
