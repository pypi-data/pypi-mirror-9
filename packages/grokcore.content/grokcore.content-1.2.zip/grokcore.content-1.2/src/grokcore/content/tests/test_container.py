"""

The grokcore.content.Container is a a model that is also a container.
It has a dictionary API. It in fact stores its information in a BTree so
you can store a lot of items in a scalable way.

    >>> from zope.container.interfaces import IContainer
    >>> bag = BoneBag()
    >>> IContainer.providedBy(bag)
    True

    >>> from zope.container.btree import BTreeContainer
    >>> isinstance(bag, BTreeContainer)
    True
     
We had problems when switching to grokcore.content.Container
with the __parent__ attribute being set, we better make sure
this doesn't happen again:

    >>> skull = Bone()
    >>> print skull.__parent__
    None
    >>> print skull.__name__
    None
    >>> bag['skull'] = skull
    >>> skull.__parent__
    <grokcore.content.tests.test_container.BoneBag object at 0x...>
    >>> skull.__name__
    u'skull'

"""

from grokcore.content import Model, Container

class BoneBag(Container):
    pass
    
class Bone(Model):
    pass



def test_suite():
    from zope.testing import doctest
    suite = doctest.DocTestSuite(
        optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS
        )
    return suite
