'''
`Nested Field Transforms

Take the flat fields structure and attempt to transform it into
a dictionary according to the algorithm at
    http://darobin.github.io/formic/specs/json/

with the extension that if each field starts with a [] it
transforms into a list instead
'''
from collections import OrderedDict
import copy


def group_elements(source):
    names = OrderedDict()
    for item in source:
        field_name = item['name']

        if '[' not in field_name:
            name, remainder = field_name, ''
        else:
            name, remainder = field_name.split('[', 1)

        if len(remainder) > 0:
            remainder = '[' + remainder
        if name not in names:
            names[name] = []
        new_item = copy.copy(item)
        new_item['name'] = remainder
        names[name].append(new_item)
    return names


def split_nested_elements(source):
    solos = OrderedDict()
    singles = OrderedDict()
    multiples = OrderedDict()
    for name, fields in source.items():
        for field in fields:
            field_name = field['name']
            if field_name.startswith('[]['):  # Multiple
                field['name'] = field_name[3:].replace(']', '', 1)
                dest = multiples
            elif field_name.startswith('['):  # Single
                field['name'] = field_name[1:].replace(']', '', 1)
                dest = singles
            elif len(field_name) == 0:  #Field
                field['name'] = name
                dest = solos
            else:
                raise ValueError, 'Incorrectly formatted field name: %s' % \
                                  field_name

            if name not in dest:
                dest[name] = []
            dest[name].append(field)

    return solos, singles, multiples


def transform(source):
    '''
    STEP 1
    Transform the elements into top level names, by stripping the name left
    of the '['
       [][href]                  ''      -> '[][href]'
       email                     email   -> ''
       address[street]           address -> '[street]'
       address[city]                     -> '[city]'
       friends[][name]           friends -> '[][name]'
       friends[][email]                  -> '[][email]'
       friends[][email]                  -> '[][email]'
       telephone                 telephone -> ''
       telephone                           -> ''

    STEP 2
    Iterate the the elements into three groups. Field, Single, Multiple.
        Fields: email -> 'email', telephone -> 'telephone', 'telephone'
        Single: address -> 'street', 'city'
        Multiple: friends -> 'name, email, email', '' -> 'href'

    STEP 3
    Iterate into each group, starting again at STEP 1
        Each

    STEP 4
    IF the final result is a dictionary with a single 0 length key, then we
    take that top level value and return it instead. This deals with the case
        '[][href]'
        '[][rel]'
    '''
    grouped = group_elements(source)
    solos, singles, multiples = split_nested_elements(grouped)
    results = []

    # We want to keep the fields in as close to provided order as possible.
    # So we are going to iterate the original grouped keys, and then do the
    # solos/etc for each one
    for name in grouped.keys():
        if name in solos:
            fields = solos[name]
            if len(fields) == 1:
                results.append(fields[0])
            else:
                for i, field in enumerate(fields):
                    indexed_name = '%s[%d]' % (name, i)
                    field['name'] = indexed_name
                    results.append(field)

        if name in singles:
            results.append({
                'name': name,
                'type': 'nested.single',
                'nested': transform(singles[name]),
                })
        if name in multiples:
            results.append({
                'name': name,
                'type': 'nested.multiple',
                'nested': transform(multiples[name]),
                })

    return results


