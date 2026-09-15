from django.db import IntegrityError
from django.utils import timezone

from app.constants.enums import PACKAGE_STATUS_PICKED, PACKAGE_STATUS_REGISTERED, PACKAGE_STATUS_STORED
from app.constants.errors import (
    ERROR_MESSAGES,
    INVALID_PICKUP_CODE,
    PACKAGE_ALREADY_PICKED,
    PACKAGE_DUPLICATE,
    PACKAGE_NOT_FOUND,
    PACKAGE_STATUS_INVALID,
)
from app.utils.business_error import BusinessError
from app.utils.code import generate_pickup_code
from app.utils.logger import get_logger

from .models import Package

logger = get_logger('packages')


def register_package(data: dict) -> Package:
    """租客登记预计到达的快递（此时状态为待入库）。"""
    package = Package(
        tracking_no=data['trackingNo'],
        company=data.get('company', ''),
        tenant_name=data['tenantName'],
        tenant_phone=data['tenantPhone'],
        building=data.get('building', ''),
        room_no=data.get('roomNo', ''),
        status=PACKAGE_STATUS_REGISTERED,
    )
    try:
        package.save()
    except IntegrityError:
        logger.info('快递单号重复登记：%s', data['trackingNo'])
        raise BusinessError(ERROR_MESSAGES[PACKAGE_DUPLICATE], PACKAGE_DUPLICATE)
    logger.info('快递登记成功 id=%s no=%s', package.id, package.tracking_no)
    return package


def store_package(data: dict) -> Package:
    """物业按楼栋收件入库，并生成取件凭证。"""
    tracking_no = data['trackingNo'].strip()
    package = Package.objects.filter(tracking_no=tracking_no).first()
    if package is None:
        raise BusinessError(ERROR_MESSAGES[PACKAGE_NOT_FOUND], PACKAGE_NOT_FOUND, 404)
    if package.status == PACKAGE_STATUS_PICKED:
        raise BusinessError(ERROR_MESSAGES[PACKAGE_ALREADY_PICKED], PACKAGE_ALREADY_PICKED)

    package.building = data.get('building', '').strip() or package.building
    package.room_no = data.get('roomNo', '').strip() or package.room_no
    package.operator = data.get('operator', '').strip() or package.operator
    # 幂等：重复入库同一待取件包裹时沿用原凭证，避免覆盖
    if not package.pickup_code:
        package.pickup_code = _unique_pickup_code()
    package.status = PACKAGE_STATUS_STORED
    package.stored_at = timezone.now()
    package.save()
    logger.info('快递入库 id=%s no=%s 楼栋=%s 凭证=%s',
                package.id, package.tracking_no, package.building, package.pickup_code)
    return package


def pickup_package(tracking_no: str, pickup_code: str) -> Package:
    """取件：核对凭证并推进状态为已取件。"""
    package = Package.objects.filter(tracking_no=tracking_no).first()
    if package is None:
        raise BusinessError(ERROR_MESSAGES[PACKAGE_NOT_FOUND], PACKAGE_NOT_FOUND, 404)

    if package.status == PACKAGE_STATUS_PICKED:
        logger.info('重复取件 no=%s', tracking_no)
        raise BusinessError(ERROR_MESSAGES[PACKAGE_ALREADY_PICKED], PACKAGE_ALREADY_PICKED)
    if package.status != PACKAGE_STATUS_STORED or not package.pickup_code:
        raise BusinessError(ERROR_MESSAGES[PACKAGE_STATUS_INVALID], PACKAGE_STATUS_INVALID)
    if pickup_code.strip() != package.pickup_code:
        logger.info('凭证不符 no=%s input=%s', tracking_no, pickup_code)
        raise BusinessError(ERROR_MESSAGES[INVALID_PICKUP_CODE], INVALID_PICKUP_CODE)

    package.status = PACKAGE_STATUS_PICKED
    package.picked_at = timezone.now()
    package.save()
    logger.info('快递取件成功 id=%s no=%s', package.id, package.tracking_no)
    return package


def list_packages(state: str = ''):
    """按状态查询：默认全部，pending=待取件，registered=待入库，picked=已取件。"""
    queryset = Package.objects.all()
    alias = {
        'pending': PACKAGE_STATUS_STORED,
        'registered': PACKAGE_STATUS_REGISTERED,
        'picked': PACKAGE_STATUS_PICKED,
    }
    if state in alias:
        queryset = queryset.filter(status=alias[state])
    return queryset.order_by('-id')


def _unique_pickup_code() -> str:
    code = generate_pickup_code()
    while Package.objects.filter(pickup_code=code).exists():
        code = generate_pickup_code()
    return code
