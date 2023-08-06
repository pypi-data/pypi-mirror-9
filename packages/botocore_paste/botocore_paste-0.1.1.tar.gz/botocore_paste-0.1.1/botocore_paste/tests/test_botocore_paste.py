# -*- coding: utf-8 -*-

import unittest


class NormalizeConfigTestCase(unittest.TestCase):

    def test_int(self):
        from .. import normalize_config
        config = {'botocore.metadata_service_num_attempts': '33',
                  'botocore.metadata_service_timeout': '25',
                  'botocore.profile': 'someprofile'}
        self.assertDictEqual(normalize_config(config), {
            'metadata_service_num_attempts': 33,
            'metadata_service_timeout': 25,
            'profile': 'someprofile',
        })
