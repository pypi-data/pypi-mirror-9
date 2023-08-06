Colosseum
=========

A (partial) implementation of the CSS box and flexbox layout algorithm.

The following CSS attributes and value types are supported:

=================================================================================  =========================================================
Name                                                                               Value
=================================================================================  =========================================================
width, height                                                                      positive number
left, right, top, bottom                                                           number
margin, marginLeft, marginRight, marginTop, marginBottom                           number
padding, paddingLeft, paddingRight, paddingTop, paddingBottom                      positive number
borderWidth, borderLeftWidth, borderRightWidth, borderTopWidth, borderBottomWidth  positive number
flexDirection                                                                      ``"column"``, ``"row"``
justifyContent                                                                     ``"flex-start"``, ``"center"``, ``"flex-end"``, ``"space-between"``, ``"space-around"``
alignItems, alignSelf                                                              ``"flex-start"``, ``"center"``, ``"flex-end"``, ``"stretch"``
flex                                                                               positive number
flexWrap                                                                           ``"wrap"``, ``"nowrap"``
position                                                                           ``"relative"``, ``"absolute"``
=================================================================================  =========================================================

Quickstart
----------

In your virtualenv, install Colosseum::

    $ pip install colosseum

Then, you can instantiate CSS nodes, and query the layout that results::

    >>> from colosseum import CSSNode
    >>> node = CSSNode(width=1000, height=1000, flexDirection='row')
    >>> node.children.add(CSSNode(width=100, height=200))
    >>> node.children.add(CSSNode(width=300, height=150))
    >>> layout = node.layout
    >>> print(layout)
    <Layout (1000x1000 @ 0,0)>
    >>> layout.width
    1000
    >>> layout.height
    1000
    >>> layout.top
    0
    >>> layout.left
    0
    >>> for child in node.children:
    ...     print(child.layout)
    <Layout (100x200 @ 0,0)>
    <Layout (300x150 @ 100,0)>

Requesting the ``layout`` attribute of a CSSNode forces the box model to be
evaluated. Once evaluated, the layout will be cached. Modifying any CSS
property on a node will mark the layout as dirty, and the layout will be
recomputed the next time the layout is accessed. For example, if we switch
the outer node to be a "column" flexBox, rather than a "row" flexBox,
you'll see the coordinates of the child boxes update to reflect a vertical,
rather than horizontal layout::

    >>> node.flexDirection = 'column'
    >>> print(node.layout)
    <Layout (1000x1000 @ 0,0)>
    >>> for child in node.children:
    ...     print(child.layout)
    <Layout (100x200 @ 0,0)>
    <Layout (300x150 @ 0,200)>

Community
---------

Colosseum is part of the `BeeWare suite`_. You can talk to the community through:

 * `@pybeeware on Twitter`_

 * The `BeeWare Users Mailing list`_, for questions about how to use the BeeWare suite.

 * The `BeeWare Developers Mailing list`_, for discussing the development of new features in the BeeWare suite, and ideas for new tools for the suite.

Contributing
------------

If you experience problems with Colosseum, `log them on GitHub`_. If you
want to contribute code, please `fork the code`_ and `submit a pull request`_.

.. _BeeWare suite: http://pybee.org
.. _Read The Docs: http://colosseum.readthedocs.org
.. _@pybeeware on Twitter: https://twitter.com/pybeeware
.. _BeeWare Users Mailing list: https://groups.google.com/forum/#!forum/beeware-users
.. _BeeWare Developers Mailing list: https://groups.google.com/forum/#!forum/beeware-developers
.. _log them on Github: https://github.com/pybee/colosseum/issues
.. _fork the code: https://github.com/pybee/colosseum
.. _submit a pull request: https://github.com/pybee/colosseum/pulls

Acknowledgements
----------------

The algorithm and test suite for this library is a language port of
`CSS-layout`_ project, open-sourced by Facebook.

.. _CSS-layout: https://github.com/facebook/css-layout
