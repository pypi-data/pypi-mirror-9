"""
    libextract.baskets
    ~~~~~~~~~~~~~~~~~~
    Implements functions that "basket" pruned nodes.

    This module provides some common basketting techniques
    that help with predicting tabular data and article
    text.

    The intent of this library can be understood by
    making an analogy with farmers who want to pick
    the best fruit. Instead of meticulously reviewing
    every fruit in his or her orchard, and attempting to
    mentally record the location of the last best fruit,
    the farmer designs special "baskets".

    These baskets allow the farmer to prune appealing
    branches, allowing the fruit to fall into the basket.

    But these baskets are powerful in the sense that they
    can execute a "quality check" of each branch that
    falls into the basket.

    Think of the quality checks as metrics. These metrics
    are associated with the branch (node)* that's currently
    in the basket.

    *Note: because the node is of type lxml.etree, we can
    perform more complex node-metric associations.
"""

from libextract.coretools import prunes
from libextract.metrics import text_length, count_children
from libextract.xpaths import NODES_WITH_CHILDREN, NODES_WITH_TEXT


@prunes(NODES_WITH_TEXT)
def parent_length_pairs(node):
    """
    Pruner that yields parent node to text-length pairs.
    """
    return node.getparent(), text_length(node)


@prunes(NODES_WITH_CHILDREN)
def node_children_pairs(node):
    """
    Pruner to that yields node to child node frequencies
    (collections.Counter) pairs.
    """
    return node, count_children(node)
