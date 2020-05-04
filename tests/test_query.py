import pytest

from textquery import Parser

parser = Parser()


def only_data(key, data):
    return key.data == data and key.field_name == '' and key.field_operator == ''


def with_field(key, data, field):
    return key.data == data and key.field_name == field and key.field_operator == ''


def with_operator(key, data, field, operator):
    return key.data == data and key.field_name == field and key.field_operator == operator


@pytest.mark.parametrize('query,expected', [
    ('simple text', 'simple text'),
    ('(simple text)', 'simple text'),
    # ('simple text)', 'simple text'),
    # ('(simple text', 'simple text'),
])
def test_simple_query(query, expected):
    tree = parser.parse(query)

    assert len(tree.children) == 0
    assert only_data(tree.key, expected)


def test_field():
    tree = parser.parse('field_1:test')

    assert len(tree.children) == 0
    assert with_field(tree.key, 'test', 'field_1')


def test_field_operator():
    tree = parser.parse('field_1[exact]:test')

    assert len(tree.children) == 0
    assert with_operator(tree.key, 'test', 'field_1', 'exact')


def test_complex_query():
    # tree = parser.parse('(a-1 AND a-2 AND a-3 OR a-4')
    tree = parser.parse('(a-1 AND a-2 AND a-3) OR a-4')

    assert len(tree.children) == 2
    assert only_data(tree.key, 'OR')

    ands, ors = tree.children
    assert only_data(ors.key, 'a-4')
    assert only_data(ands.key, 'AND')

    a1, a2, a3 = ands.children
    assert only_data(a1.key, 'a-1')
    assert only_data(a2.key, 'a-2')
    assert only_data(a3.key, 'a-3')


def test_complex_query_with_fields():
    tree = parser.parse('(field1:a-1 AND field2:a-2 AND field3:a-3) OR field4:a-4')

    assert len(tree.children) == 2
    assert only_data(tree.key, 'OR')

    ands, ors = tree.children
    assert only_data(ands.key, 'AND')
    assert with_field(ors.key, 'a-4', 'field4')

    a1, a2, a3 = ands.children
    assert with_field(a1.key, 'a-1', 'field1')
    assert with_field(a2.key, 'a-2', 'field2')
    assert with_field(a3.key, 'a-3', 'field3')


def test_complex_query_with_fields_and_operators():
    tree = parser.parse('(field1[op1]:a-1 AND field2[op2]:a-2 AND field3[op3]:a-3) OR field4[op4]:a-4')

    assert len(tree.children) == 2
    assert only_data(tree.key, 'OR')

    ands, ors = tree.children
    assert only_data(ands.key, 'AND')
    assert with_operator(ors.key, 'a-4', 'field4', 'op4')

    a1, a2, a3 = ands.children
    assert with_operator(a1.key, 'a-1', 'field1', 'op1')
    assert with_operator(a2.key, 'a-2', 'field2', 'op2')
    assert with_operator(a3.key, 'a-3', 'field3', 'op3')
