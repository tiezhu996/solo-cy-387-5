"""物业按楼栋收件入库并生成取件凭证。"""
from rest_framework.test import APITestCase

from app.apps.packages.models import Package
from app.apps.packages.tests.factories import create_registered
from app.constants.enums import PACKAGE_STATUS_STORED


class StorePackageTests(APITestCase):
    url = '/api/packages/store/'

    def test_store_generates_pickup_code(self):
        create_registered('SF2001')

        resp = self.client.post(self.url, {
            'trackingNo': 'SF2001', 'building': '3栋', 'roomNo': '501', 'operator': '王物业',
        }, format='json')

        self.assertEqual(resp.status_code, 200)
        data = resp.json()['data']
        self.assertEqual(data['status'], PACKAGE_STATUS_STORED)
        self.assertRegex(data['pickupCode'], r'^\d{6}$')
        self.assertEqual(data['operator'], '王物业')
        self.assertIsNotNone(data['storedAt'])
        # 凭证回写数据库，供后续取件核对
        self.assertEqual(Package.objects.get(tracking_no='SF2001').pickup_code, data['pickupCode'])

    def test_store_unknown_tracking_no(self):
        resp = self.client.post(self.url, {'trackingNo': 'NOPE', 'building': '1栋'}, format='json')
        body = resp.json()
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(body['code'], 'PACKAGE_NOT_FOUND')

    def test_store_is_idempotent_and_keeps_code(self):
        create_registered('SF2002')

        first = self.client.post(self.url, {'trackingNo': 'SF2002', 'building': '3栋'}, format='json').json()['data']
        second = self.client.post(self.url, {'trackingNo': 'SF2002', 'building': '3栋'}, format='json').json()['data']

        self.assertEqual(first['pickupCode'], second['pickupCode'])
        self.assertEqual(Package.objects.count(), 1)
