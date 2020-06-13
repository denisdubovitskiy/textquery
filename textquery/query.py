from collections import deque
from typing import (
    List,
    Deque,
    NamedTuple,
    Optional,
    Dict,
)

EMDASH = '—'
PSEUDO_DELIMITER = f'{EMDASH}_{EMDASH}'
RIGHT, LEFT = range(2)
NOT, AND, OR = 'NOT', 'AND', 'OR'
FIELD_DELIMITER = ':'
LEFT_PAREN, RIGHT_PAREN = '(', ')'


class Stack(deque):
    def peek(self):
        return self[-1]


class Token:
    __slots__ = ('key', 'field_name', 'field_operator', 'modifier')

    def __init__(self, key, field_name='', field_operator='', modifier=''):
        self.field_name = field_name
        self.field_operator = field_operator
        self.key = key
        self.modifier = modifier

    def __str__(self) -> str:
        if not self.field_name:
            return self.key
        return f'{self.field_name}:{self.key}'

    __repr__ = __str__


def is_operator(source: str) -> bool:
    return source in {OR, AND, NOT}


def is_operand(source: str) -> bool:
    return source not in {LEFT_PAREN, RIGHT_PAREN, OR, AND, NOT}


def is_open_paren(source: str) -> bool:
    return source == LEFT_PAREN


def is_close_paren(source: str) -> bool:
    return source == RIGHT_PAREN


def is_not(operator: str) -> bool:
    return operator == NOT


def has_delimiter(source: str) -> bool:
    return FIELD_DELIMITER in source


def format_replacer(source: str) -> str:
    return f'{PSEUDO_DELIMITER}{source}{PSEUDO_DELIMITER}'


OPERATOR_REPLACEMENTS = {
    NOT: format_replacer(NOT),
    AND: format_replacer(AND),
    OR: format_replacer(OR),
    LEFT_PAREN: format_replacer(LEFT_PAREN),
    RIGHT_PAREN: format_replacer(RIGHT_PAREN),

}

FIELD_REPLACEMENTS = {
    '[': format_replacer('['),
    ']': format_replacer(']'),
    '{': format_replacer('{'),
    '}': format_replacer('}'),
    FIELD_DELIMITER: format_replacer(FIELD_DELIMITER),
}


def replace(source: str, replacements: Dict[str, str]) -> List[str]:
    replaced = source
    for token, replacement in replacements.items():
        replaced = replaced.replace(token, replacement)
    return [r.strip() for r in replaced.split(PSEUDO_DELIMITER) if r.strip()]


def replace_operators(source: str) -> List[str]:
    return replace(source, OPERATOR_REPLACEMENTS)


def replace_field_parens(query: str) -> List[str]:
    return replace(query, FIELD_REPLACEMENTS)


def tokenize(query: str) -> List[Token]:
    tokens: List[Token] = []

    for part in replace_operators(query):
        if not has_delimiter(part):
            tokens.append(Token(part))
            continue

        field_descriptor = replace_field_parens(part)

        if len(field_descriptor) == 6:
            field, _, operator, _, _, value = field_descriptor
            tokens.append(Token(value, field, operator))
        elif len(field_descriptor) == 3:
            # field:value
            field, _, value = field_descriptor

            tokens.append(Token(value, field, '', ''))
        else:
            field, _, modifier, _, _, operator, _, _, value = field_descriptor
            tokens.append(Token(value, field, operator, modifier))

    return tokens


class Operator(NamedTuple):
    precedence: int
    associativity: int


OPERATORS = {
    NOT: Operator(precedence=3, associativity=RIGHT),
    AND: Operator(precedence=2, associativity=LEFT),
    OR: Operator(precedence=1, associativity=LEFT),
}


class Node:
    def __init__(self, data: Token, left: Optional['Node'] = None, right: Optional['Node'] = None):
        self.data = data
        self.left = left
        self.right = right


def has_precedence(a: Token, b: Token):
    op_a, op_b = OPERATORS[a.key], OPERATORS[b.key]

    is_right_associative = op_b.associativity == RIGHT and op_a.precedence > op_b.precedence
    is_left_associative = op_b.associativity == LEFT and op_a.precedence >= op_b.precedence

    return is_left_associative or is_right_associative


def parse_search_query(tokens: List[Token]) -> Deque[Token]:
    reverse_notation: Deque[Token] = deque()
    operators: Stack[Token] = Stack()

    for token in tokens:
        if is_operand(token.key):
            reverse_notation.append(token)
            continue

        if is_open_paren(token.key):
            operators.append(token)
            continue

        if is_close_paren(token.key):
            while True:
                current_token = operators.pop()

                if is_open_paren(current_token.key):
                    break

                reverse_notation.append(current_token)

            continue

        if is_operator(token.key):
            while operators:

                if not is_operator(operators.peek().key):
                    break

                if not has_precedence(operators.peek(), token):
                    break

                reverse_notation.append(operators.pop())

            operators.append(token)
            continue

    reverse_notation.extend(reversed(operators))

    return reverse_notation


def construct_binary_tree(parts: Deque[Token]) -> Node:
    stack: Deque[Node] = deque()

    for part in parts:
        if not is_operator(part.key):
            stack.append(Node(part))
            continue

        right = stack.pop()

        if is_not(part.key):
            stack.append(Node(part, right=right))
            continue

        left = stack.pop()
        stack.append(Node(part, right=right, left=left))

    return stack.pop()


def parse(query: str) -> Node:
    return construct_binary_tree(parse_search_query(tokenize(query)))
