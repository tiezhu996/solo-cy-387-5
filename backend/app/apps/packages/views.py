from rest_framework.views import APIView

from app.utils.business_error import BusinessError
from app.constants.errors import ERROR_MESSAGES, PARAM_REQUIRED
from app.utils.response import success

from .serializers import (
    PackagePickupSerializer,
    PackageRegisterSerializer,
    PackageSerializer,
    PackageStoreSerializer,
)
from .services import list_packages, pickup_package, register_package, store_package


class PackageListCreateView(APIView):
    """GET 快递记录列表；POST 租客登记预计到达快递。"""

    def get(self, request):
        packages = list_packages(request.query_params.get('state', ''))
        return success(PackageSerializer(packages, many=True).data)

    def post(self, request):
        serializer = PackageRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        package = register_package(serializer.validated_data)
        return success(PackageSerializer(package).data, message='快递登记成功', code=201)


class PackageStoreView(APIView):
    """物业按楼栋收件入库并生成取件凭证。"""

    def post(self, request):
        serializer = PackageStoreSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        package = store_package(serializer.validated_data)
        return success(PackageSerializer(package).data, message=f'入库成功，取件凭证 {package.pickup_code}')


class PackagePickupView(APIView):
    """取件：核对单号与凭证，核验通过后推进为已取件。"""

    def post(self, request):
        serializer = PackagePickupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tracking_no = serializer.validated_data.get('trackingNo', '')
        pickup_code = serializer.validated_data.get('pickupCode', '')
        if not tracking_no or not pickup_code:
            raise BusinessError(ERROR_MESSAGES[PARAM_REQUIRED], PARAM_REQUIRED)
        package = pickup_package(tracking_no, pickup_code)
        return success(PackageSerializer(package).data, message='取件成功')
