# coding=utf-8
from __future__ import unicode_literals

import poco.utils.six as six
from poco.utils.simplerpc.pocofilter import *


__all__ = ['query_expr']


TranslatePred = {
    'attr=': '=',
    'attr.*=': ' matches ',
}


TranslateOp = {
    'and': '&',
    'or': '|',
    '/': '/',
    '>': '>',
    '-': '-',
}


ComparableTypes = six.integer_types + six.string_types + (six.binary_type, bool, float)


def query_expr(query):
    op = query[0]
    if op in ('/', '>', '-'):
        return TranslateOp[op].join([query_expr(q) for q in query[1]])
    elif op == 'index':
        return '{}[{}]'.format(query_expr(query[1][0]), query[1][1])
    elif op in ('and', 'or'):
        exprs = []
        for subquery in query[1]:
            pred, (k, v) = subquery
            if k == 'name':
                exprs.append(v)
            else:
                exprs.append('{}{}{}'.format(k, TranslatePred[pred], v))
        return TranslateOp[op].join(exprs)
    else:
        raise RuntimeError('Bad query format. "{}"'.format(repr(query)))


def ensure_text(value):
    if not isinstance(value, six.text_type):
        return value.decode("utf-8")
    else:
        return value

def getFilter(dictionary):
    if 'NodeType' in dictionary.keys():
        PocoFilter.NodeType = dictionary['NodeType']
        dictionary.__delitem__('NodeType')
        if 'SubType' in dictionary.keys():
            PocoFilter.SubType = dictionary['SubType']
            dictionary.__delitem__('SubType')
        else:
            PocoFilter.SubType = '*'

        if dictionary.__len__() > 0:
            PocoFilter.Condition = dictionary
    else:
        raise SyntaxError("Filter is missing NodeType field")


def get_node_code(name):
    __node_type = {
        'Unknown' : -1,
        'None' : 0,
        'Creature' : 1,
        'Building' : 2,
        'Soldier' : 3,
        'Hero' : 4,
        'Magic' : 5,
        'Pet' : 6,
        'ST_Field' : 7,
        'UNC_Field' : 8,
        'Goblin' : 9,
        'Protector' : 10,
        'Control' : 50,
        'Layer' : 51,
        'MenuItem': 52,
        'Scene' : 53,
        'AtlasNode': 54,
        'LabelTTF': 55,
        'SpriteBatchNode': 56,
        'Sprite': 57
    }

    __sub_type = {
        'Normal' : 0,
        'Defend' : 1,
        'Ornament' : 2,
        'Weed' : 3,
        'Pitfall' : 4,
        'Gravestone' : 5,
        'Goblin' : 6,
        'Unknown' : 7,
        'None' : 20,
        'Button' : 21,
        'EditBox': 22,
        'Label': 23,
        'LabelTTF': 24,
        'Progress': 25,
        'Image': 26,
        'Canvas': 27,
        'ListBox': 28,
        'LabelBMP': 29,
        'CheckBox': 30,
        'TimerImage': 31,
        'ProgressEx': 32,
        'ScrollView': 33,
        'ScrollViewEx': 34,
        'Custom': 35,
        'ResImage': 36,

        'Hero' : 80,
        'Pet' : 81,
        'Boss' : 82
    }
    types = name.split('-')
    PocoFilter.NodeType = __node_type[types[0]]
    PocoFilter.SubType = __sub_type[types[1]]


def build_query(name, **attrs):
    query = []
    init_filter()
    if name is not None:
        if not isinstance(name, six.string_types):
            raise ValueError("Name selector should only be string types. Got {}".format(repr(name)))
        name = ensure_text(name)
        attrs['name'] = name

    for attr_name, attr_val in attrs.items():
        if attr_name.lower() == 'NodeFilter'.lower():
            get_node_code(attr_val)
            continue

        if not isinstance(attr_val, ComparableTypes):
            raise ValueError('Selector value should be one of the following types "{}". Got {}'
                             .format(ComparableTypes, type(attr_val)))
        if isinstance(attr_val, six.string_types):
            attr_val = ensure_text(attr_val)
        if attr_name.startswith('_'):
            raise NameError("Cannot use private attribute '{}' in your Query Expression as private attributes do not "
                            "have stable values.".format(attr_name))
        elif attr_name.endswith('Matches'):
            attr_name = attr_name[:-7]  # textMatches -> (attr.*=, text)
            op = 'attr.*='
        else:
            op = 'attr='
        PocoFilter.Condition[attr_name]=attr_val
        query.append((op, (attr_name, attr_val)))
    return 'and', tuple(query)
