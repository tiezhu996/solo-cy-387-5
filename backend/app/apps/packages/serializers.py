from rest_framework import serializers

from .models import Package


class PackageRegisterSerializer(serializers.Serializer):
    trackingNo = serializers.CharField(max_length=64, allow_blank=False)
    company = serializers.CharField(max_length=40, required=False, allow_blank=True)
    tenantName = serializers.CharField(max_length=40, allow_blank=False)
    tenantPhone = serializers.CharField(max_length=20, allow_blank=False)
    building = serializers.CharField(max_length=40, required=False, allow_blank=True)
    roomNo = serializers.CharField(max_length=20, required=False, allow_blank=True)

    def validate_trackingNo(self, value):
        return value.strip()

    def validate_tenantName(self, value):
        return value.strip()

    def validate_tenantPhone(self, value):
        return value.strip()


class PackageStoreSerializer(serializers.Serializer):
    trackingNo = serializers.CharField(max_length=64, allow_blank=False)
    building = serializers.CharField(max_length=40, allow_blank=False)
    roomNo = serializers.CharField(max_length=20, required=False, allow_blank=True)
    operator = serializers.CharField(max_length=40, required=False, allow_blank=True)


class PackagePickupSerializer(serializers.Serializer):
    trackingNo = serializers.CharField(max_length=64, required=False, allow_blank=True)
    pickupCode = serializers.CharField(max_length=16, required=False, allow_blank=True)

    def validate(self, attrs):
        if not (attrs.get('trackingNo') or '').strip() and not (attrs.get('pickupCode') or '').strip():
            raise serializers.ValidationError('请填写快递单号或取件凭证')
        return attrs


class PackageSerializer(serializers.ModelSerializer):
    trackingNo = serializers.CharField(source='tracking_no')
    tenantName = serializers.CharField(source='tenant_name')
    tenantPhone = serializers.CharField(source='tenant_phone')
    roomNo = serializers.CharField(source='room_no')
    pickupCode = serializers.CharField(source='pickup_code')
    registeredAt = serializers.DateTimeField(source='registered_at', format='%Y-%m-%d %H:%M')
    storedAt = serializers.DateTimeField(source='stored_at', format='%Y-%m-%d %H:%M')
    pickedAt = serializers.DateTimeField(source='picked_at', format='%Y-%m-%d %H:%M')

    class Meta:
        model = Package
        fields = [
            'id', 'trackingNo', 'company', 'tenantName', 'tenantPhone',
            'building', 'roomNo', 'status', 'pickupCode', 'operator',
            'registeredAt', 'storedAt', 'pickedAt',
        ]
