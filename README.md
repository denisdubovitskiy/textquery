# TextQuery

Google-like minimal query parser

## Django working example

```python
from textquery import Parser, Node
from django.db.models import Q

parser = Parser()

def _build_filters(children: Q, node: Node):
    if not node.children:
        return Q(content__contains=node.key.data)

    for child in node.children:
        if node.key.data == 'AND':
            children = children & _build_filters(Q(), child)
        if node.key.data == 'OR':
            children = children | _build_filters(Q(), child)

    return children


def build_filters(node: Node) -> Q:
    return _build_filters(Q(), node)


def search_by_query(queryset, search_term):
    parse_tree = parser.parse(search_term))
    return queryset.filter(build_filters(parse_tree)
```
