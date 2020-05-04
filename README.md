# TextQuery

Google-like minimal query parser

## Django working example

```python
from textquery import Parser, Node
from django.db.models import Q

parser = Parser()

def _build_filters(children: Q, node: Node):
    default_field = 'content'
    default_operator = 'contains'

    if not node.children:
        field_name = default_field
        if node.key.field_name:
            field_name = node.key.field_name

        field_operator = default_operator
        if node.key.field_operator:
            field_operator = node.key.field_operator

        return Q(**{field_name + '__' + field_operator: node.key.data})

    for child in node.children:
        if node.key.data == 'AND':
            children = children & build_filters_from_parse_tree(Q(), child)
        if node.key.data == 'OR':
            children = children | build_filters_from_parse_tree(Q(), child)
        if node.key.data == 'NOT':
            children = children & ~build_filters_from_parse_tree(~Q(), child)

    return children


def build_filters(node: Node) -> Q:
    return _build_filters(Q(), node)


def search_by_query(queryset, search_term):
    parse_tree = parser.parse(search_term))
    return queryset.filter(build_filters(parse_tree)
```
