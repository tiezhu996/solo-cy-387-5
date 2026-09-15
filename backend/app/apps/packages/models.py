from django.db import models

from app.constants.enums import PACKAGE_STATUS, PACKAGE_STATUS_REGISTERED


class Package(models.Model):
    """快递代收单：登记 -> 入库（生成凭证）-> 取件。"""

    tracking_no = models.CharField('快递单号', max_length=64, unique=True, db_index=True)
    company = models.CharField('快递公司', max_length=40, blank=True, default='')
    tenant_name = models.CharField('租客姓名', max_length=40)
    tenant_phone = models.CharField('租客手机号', max_length=20)
    building = models.CharField('楼栋', max_length=40, blank=True, default='')
    room_no = models.CharField('房号', max_length=20, blank=True, default='')

    status = models.CharField(
        '状态',
        max_length=10,
        choices=[(s, s) for s in PACKAGE_STATUS],
        default=PACKAGE_STATUS_REGISTERED,
    )
    pickup_code = models.CharField('取件凭证', max_length=16, blank=True, default='', db_index=True)
    operator = models.CharField('入库经办人', max_length=40, blank=True, default='')

    registered_at = models.DateTimeField('登记时间', auto_now_add=True)
    stored_at = models.DateTimeField('入库时间', null=True, blank=True)
    picked_at = models.DateTimeField('取件时间', null=True, blank=True)

    class Meta:
        ordering = ['-id']
        verbose_name = '快递代收单'
