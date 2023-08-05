from django.shortcuts import get_object_or_404

from uuidfield.fields import StringUUID

from rest_framework import generics, status
from rest_framework.response import Response

from mobile_framework import get_device_model
from mobile_framework.device.serializers import DeviceSerializer
from mobile_framework.version.serializers import AppVersionSerializer

Device = get_device_model()


class CreateDevice(generics.ListCreateAPIView):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer


class RetrieveUpdateDevice(generics.RetrieveUpdateAPIView):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    lookup_field = 'uuid'