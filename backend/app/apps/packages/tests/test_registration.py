"""租客登记快递。"""
from rest_framework.test import APITestCase

from app.apps.packages.models import Package
from app.constants.enums import PACKAGE_STATUS_REGISTERED


class RegisterPackageTests(APITestCase):
    url = '/api/packages/'

    def test_register_success(self):
        resp = self.client.post(self.url, {
            'trackingNo': 'SF1001', 'company': '顺丰',
            'tenantName': '陈晨', 'tenantPhone': '13800001111',
            'building': '3栋', 'roomNo': '501',
        }, format='json')

        self.assertEqual(resp.status_code, 201)
        body = resp.json()
        self.assertTrue(body['success'])
        self.assertEqual(body['message'], '快递登记成功')
        data = body['data']
        self.assertEqual(data['trackingNo'], 'SF1001')
        self.assertEqual(data['status'], PACKAGE_STATUS_REGISTERED)
        self.assertEqual(data['pickupCode'], '')
        self.assertEqual(Package.objects.count(), 1)

    def test_duplicate_tracking_no_rejected(self):
        payload = {'trackingNo': 'SF1001', 'tenantName': '陈晨', 'tenantPhone': '13800001111'}
        self.client.post(self.url, payload, format='json')

        resp = self.client.post(self.url, payload, format='json')
        body = resp.json()

        self.assertEqual(resp.status_code, 400)
        self.assertFalse(body['success'])
        self.assertEqual(body['code'], 'PACKAGE_DUPLICATE')
        self.assertEqual(Package.objects.count(), 1)

    def test_missing_required_fields_rejected(self):
        resp = self.client.post(self.url, {'trackingNo': 'SF1002'}, format='json')
        self.assertEqual(resp.status_code, 400)
        self.assertFalse(resp.json()['success'])
        self.assertEqual(Package.objects.count(), 0)
