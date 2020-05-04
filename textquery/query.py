from collections import deque
from typing import List, Deque


class QueryPart:
    __slots__ = ('data', 'field_name', 'field_operator')

    def __init__(self, key, field_name='', field_operator=''):
        self.field_name = field_name
        self.field_operator = field_operator
        self.data = key

    def __str__(self):
        if not self.field_name:
            return self.data
        return f'{self.field_name}:{self.data}'


class Node:
    __slots__ = ('key', 'children')

    def __init__(self, key: QueryPart):
        self.key: QueryPart = key
        self.children: Deque[Node] = deque()

    def __str__(self):
        return self.key

    def insert_left(self, key):
        self.children.appendleft(Node(key))

    def insert_right(self, key):
        self.children.append(Node(key))

    def access_left_child(self) -> 'Node':
        return self.children[0]

    def access_right_child(self) -> 'Node':
        return self.children[-1]


class Parser:

    def __init__(self, **options):
        self.operators = options.get('operators', {'OR', 'AND'})
        self.open_parenthesis = options.get('open_parenthesis', '(')
        self.close_parenthesis = options.get('open_parenthesis', ')')
        self.field_delimiter = options.get('field_delimiter', ':')
        self.field_open_parenthesis = options.get('field_open_parenthesis', '[')
        self.field_close_parenthesis = options.get('field_close_parenthesis', ']')

        self.operators_or_close_parenthesis = {*self.operators, self.close_parenthesis}
        self.parentheses = {self.open_parenthesis, self.close_parenthesis}
        self.operator_startswith = {operator[0]: operator for operator in self.operators}

    def _split_query_to_parts(self, query: str) -> List[QueryPart]:
        if not query.startswith(self.open_parenthesis) or not query.endswith(self.close_parenthesis):
            query = f'{self.open_parenthesis}{query}{self.close_parenthesis}'

        query_parts: List[QueryPart] = []

        field_name = ''
        field_operator = ''
        word = ''
        char_index = 0

        while char_index < len(query):
            character = query[char_index]
            if character in self.operator_startswith:
                operator = self.operator_startswith[character]
                next_characters = query[char_index:char_index + len(operator)]
                if next_characters == operator:
                    query_parts.append(
                        QueryPart(
                            field_name=field_name.strip(),
                            field_operator=field_operator.strip(),
                            key=operator,
                        )
                    )
                    word, field_name, field_operator = '', '', ''
                    char_index += len(operator)
                    continue

            if character in self.parentheses:
                query_parts.append(
                    QueryPart(
                        field_name=field_name.strip(),
                        field_operator=field_operator.strip(),
                        key=character,
                    )
                )
                word, field_name, field_operator = '', '', ''
                char_index += 1
                continue

            part_index = char_index
            while part_index < len(query):
                character = query[part_index]
                if character in self.parentheses:
                    word = word.strip()
                    if word:
                        query_parts.append(
                            QueryPart(
                                field_name=field_name.strip(),
                                field_operator=field_operator.strip(),
                                key=word,
                            )
                        )
                    word, field_name, field_operator = '', '', ''
                    char_index = part_index - 1
                    break

                if character in self.operator_startswith:
                    operator = self.operator_startswith[character]
                    next_characters = query[part_index:part_index + len(operator)]
                    if next_characters == operator:
                        word = word.strip()
                        if word:
                            query_parts.append(
                                QueryPart(
                                    field_name=field_name.strip(),
                                    field_operator=field_operator.strip(),
                                    key=word,
                                )
                            )
                        word, field_name, field_operator = '', '', ''
                        char_index = part_index - 1
                        break

                if character == self.field_delimiter:
                    field_name = word
                    if field_name.endswith(self.field_close_parenthesis):
                        try:
                            open_parenthesis_index = field_name.index(self.field_open_parenthesis)
                        except ValueError:
                            # TODO: handle validation error
                            raise

                        field_operator = field_name[open_parenthesis_index + 1:len(field_name) - 1]
                        field_name = field_name[:open_parenthesis_index]
                    word = ''
                    part_index += 1
                    continue

                word += character
                part_index += 1
            char_index += 1
        return query_parts

    def parse(self, query: str) -> Node:
        splitted_query = self._split_query_to_parts(query)
        stack = deque()
        tree = Node(QueryPart(''))
        stack.append(tree)
        current_node = tree

        for component in splitted_query:
            if component.data == self.open_parenthesis:
                current_node.insert_left('')
                stack.append(current_node)
                current_node = current_node.access_left_child()

            elif component.data not in self.operators_or_close_parenthesis:
                current_node.key = component
                parent = stack.pop()
                current_node = parent

            elif component.data in self.operators:
                current_node.key = component
                current_node.insert_right('')
                stack.append(current_node)
                current_node = current_node.access_right_child()

            elif component.data == self.close_parenthesis:
                current_node = stack.pop()

            else:
                raise ValueError()

        # Regular text query
        if len(splitted_query) == 3:
            return tree.access_left_child()

        # Advanced text query
        return tree
