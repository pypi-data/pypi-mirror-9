from collections import defaultdict
class TypeClass(object):
  registry = defaultdict(dict)

  @classmethod
  def instance(cls, t, **funs):
    cls.registry[t] = funs



class Functor(TypeClass):
  # (a->b) -> b
  @classmethod
  def fmap(cls,f,a):
    return cls.registry[type(a)]['fmap'](f,a)

Functor.instance(
  list,
  fmap=map
)


Functor.instance(
  type(lambda:None),
  fmap=lambda f,g: lambda x: f(g(x)) 
)


if __name__ == "__main__":
  assert Functor.fmap(lambda x: x+1, [1,2,3]) == [2,3,4]

  assert Functor.fmap(lambda x: x+1, lambda y: y+1)(2) == 4

