# TextQuery

Google-like minimal query parser

## Django working example

```python
from django.db.models import Q, QuerySet
import textquery


def build_filters(node: textquery.Node) -> Q:
    if not node:
        return Q()

    left = build_filters(node.left)
    right = build_filters(node.right)

    if node.data.key == 'AND':
        return left & right

    if node.data.key == 'OR':
        return left | right

    if node.data.key == 'NOT':
        return ~right

    return Q(**{resolve_field_name(node): node.data.key})


ALLOWED_FIELDS = {'title', 'content'}
DEFAULT_FIELD = 'content'

ALLOWED_OPERATORS = {'eq', 'contains', 'icontains'}
DEFAULT_OPERATOR = 'contains'


def resolve_field(field_name: str) -> str:
    if field_name not in ALLOWED_FIELDS:
        return DEFAULT_FIELD

    return field_name


def resolve_operator(field_operator: str) -> str:
    if field_operator not in ALLOWED_OPERATORS:
        return DEFAULT_OPERATOR

    return field_operator


def resolve_field_name(node: textquery.Node) -> str:
    return resolve_field(node.data.field_name) + '__' + resolve_operator(node.data.field_operator)

def search_by_query(queryset: QuerySet, search_term: str):
    query_tree = textquery.parse(search_term)
    return queryset.filter(build_filters(query_tree))

filtered_queryset = search_by_query(
    your_queryset_here, 
    '(field_1:a AND b) OR (field_2[eq]:c AND d OR e) AND NOT (a OR c)',
)
    

```