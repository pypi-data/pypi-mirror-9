# -*- coding: utf-8 -*-
from pprint import pprint

from .mapper import SimpleMapper


if __name__ == '__main__':
    config = {
        'previous_address': {
            'address_months': (
                'address_data.address.{find:type=previous}.months_at_address'
            ),
            'address_years': (
                'address_data.address.{find:type=previous}.years_at_address'
            ),
        },
        'foo': 'deal_data.some_list.0.key',
    }
    data = {
        'address_data': {
            'address': [
                {
                    'type': 'current',
                    'months_at_address': 40,
                },
                {
                    'type': 'previous',
                    'months_at_address': 50,
                },
                {
                    'type': 'foo',
                    'months_at_address': 60,
                },
            ]
        },
        'deal_data': {
            'some_list': [
                {'key': 'hello world'}
            ],
        }
    }

    mapper = SimpleMapper(config, fail_mode='default', default=None)()

    print('config')
    pprint(config)
    print('*' * 50)

    print('compiled config')
    pprint(mapper.config)
    print('*' * 50)

    print('data')
    pprint(data)
    print('*' * 50)

    mapped = mapper(data)

    print('mapped data')
    pprint(mapped)
