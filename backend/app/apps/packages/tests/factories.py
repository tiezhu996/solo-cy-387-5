"""测试共用的数据构造助手。"""
from app.apps.packages.models import Package
from app.constants.enums import PACKAGE_STATUS_REGISTERED, PACKAGE_STATUS_STORED


def create_registered(tracking_no='SF-REG', **kwargs):
    """创建一条「待入库」记录。"""
    defaults = {
        'company': '顺丰',
        'tenant_name': '测试租客',
        'tenant_phone': '13800000000',
        'building': '3栋',
        'room_no': '501',
        'status': PACKAGE_STATUS_REGISTERED,
    }
    defaults.update(kwargs)
    return Package.objects.create(tracking_no=tracking_no, **defaults)


def create_stored(tracking_no='SF-STORED', pickup_code='123456', **kwargs):
    """创建一条「待取件」记录并已生成取件凭证。"""
    from django.utils import timezone

    defaults = {
        'company': '顺丰',
        'tenant_name': '测试租客',
        'tenant_phone': '13800000000',
        'building': '3栋',
        'room_no': '501',
        'status': PACKAGE_STATUS_STORED,
        'pickup_code': pickup_code,
        'stored_at': timezone.now(),
    }
    defaults.update(kwargs)
    return Package.objects.create(tracking_no=tracking_no, **defaults)
