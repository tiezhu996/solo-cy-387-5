"""取件：正常取件、错误凭证、无效单号、取件后重复操作。"""
from rest_framework.test import APITestCase

from app.apps.packages.models import Package
from app.apps.packages.tests.factories import create_registered, create_stored


class PickupTests(APITestCase):
    url = '/api/packages/pickup/'

    def test_normal_pickup(self):
        create_stored('SF3001', '246810')

        resp = self.client.post(self.url, {'trackingNo': 'SF3001', 'pickupCode': '246810'}, format='json')

        self.assertEqual(resp.status_code, 200)
        data = resp.json()['data']
        self.assertEqual(data['status'], '已取件')
        self.assertIsNotNone(data['pickedAt'])
        package = Package.objects.get(tracking_no='SF3001')
        self.assertEqual(package.status, '已取件')
        self.assertIsNotNone(package.picked_at)

    def test_wrong_pickup_code(self):
        create_stored('SF3002', '246810')

        resp = self.client.post(self.url, {'trackingNo': 'SF3002', 'pickupCode': '000000'}, format='json')
        body = resp.json()

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(body['code'], 'INVALID_PICKUP_CODE')
        # 凭证错误不得改变状态或写入取件时间
        package = Package.objects.get(tracking_no='SF3002')
        self.assertEqual(package.status, '待取件')
        self.assertIsNone(package.picked_at)

    def test_unknown_tracking_no(self):
        resp = self.client.post(self.url, {'trackingNo': 'NOPE', 'pickupCode': '246810'}, format='json')
        body = resp.json()
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(body['code'], 'PACKAGE_NOT_FOUND')

    def test_duplicate_pickup_after_picked(self):
        create_stored('SF3003', '246810')
        first = self.client.post(self.url, {'trackingNo': 'SF3003', 'pickupCode': '246810'}, format='json')
        self.assertEqual(first.status_code, 200)
        first_picked_at = Package.objects.get(tracking_no='SF3003').picked_at

        second = self.client.post(self.url, {'trackingNo': 'SF3003', 'pickupCode': '246810'}, format='json')
        body = second.json()

        self.assertEqual(second.status_code, 400)
        self.assertEqual(body['code'], 'PACKAGE_ALREADY_PICKED')
        package = Package.objects.get(tracking_no='SF3003')
        self.assertEqual(package.status, '已取件')
        # 重复取件不得改写取件时间
        self.assertEqual(package.picked_at, first_picked_at)

    def test_pickup_before_stored_rejected(self):
        create_registered('SF3004')
        resp = self.client.post(self.url, {'trackingNo': 'SF3004', 'pickupCode': '123456'}, format='json')
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json()['code'], 'PACKAGE_STATUS_INVALID')

    def test_missing_credentials_rejected(self):
        resp = self.client.post(self.url, {}, format='json')
        self.assertEqual(resp.status_code, 400)
        self.assertFalse(resp.json()['success'])
