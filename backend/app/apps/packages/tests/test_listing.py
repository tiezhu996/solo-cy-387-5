"""待取件 / 待入库 / 已取件记录查询。"""
from rest_framework.test import APITestCase

from app.apps.packages.tests.factories import create_registered, create_stored


class PackageListTests(APITestCase):
    url = '/api/packages/'

    def test_filter_by_state(self):
        create_registered('R1')
        create_stored('S1', pickup_code='111111')
        picked = create_stored('P1', pickup_code='222222')
        picked.status = '已取件'
        picked.save()

        self.assertEqual(len(self.client.get(self.url, {'state': 'registered'}).json()['data']), 1)
        pending = self.client.get(self.url, {'state': 'pending'}).json()['data']
        picked_list = self.client.get(self.url, {'state': 'picked'}).json()['data']
        self.assertEqual([p['trackingNo'] for p in pending], ['S1'])
        self.assertEqual([p['trackingNo'] for p in picked_list], ['P1'])

    def test_list_all(self):
        create_registered('R1')
        create_stored('S1')
        data = self.client.get(self.url).json()['data']
        self.assertEqual(len(data), 2)
        # 默认按 id 倒序
        self.assertEqual([p['trackingNo'] for p in data], ['S1', 'R1'])

    def test_empty_state_returns_empty_list(self):
        self.assertEqual(self.client.get(self.url, {'state': 'picked'}).json()['data'], [])
