from rest_framework import generics, status
from rest_framework.response import Response

from mobile_framework.device.models import Device
from mobile_framework.device.serializers import DeviceSerializer
from mobile_framework.version.serializers import AppVersionSerializer


class AppVersionMixin(object):
    """ Allows AppVersion processing for both Create and Update views. """
    def _process_request(self, request, obj=None, *args, **kwargs):
        data = request.DATA
        try:
            try:
                version_serializer = AppVersionSerializer(data=data['app'])
                device_data = data['device']
            except KeyError as e:
                return Response({'detail': 'KeyError: {}'.format(e)}, status=status.HTTP_400_BAD_REQUEST)

            # Create the version first.
            if version_serializer.is_valid():
                version = version_serializer.save()
                device_data['app_version'] = version.pk
                device_data['build'] = version.app_store_build 
                device_serializer = self.serializer_class(obj, data=device_data)

                # Create the device
                if device_serializer.is_valid():
                    device_serializer.save()
                    return device_serializer.data
                else:
                    return Response({'detail': device_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'detail': version_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': e}, status=status.HTTP_400_BAD_REQUEST)


class CreateDevice(AppVersionMixin, generics.ListCreateAPIView):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer

    def post(self, request, *args, **kwargs):
        """
        Creates a new Device.

        Accepted:
            - json
            - formdata
            - multipart
        Request Structure:
        ```
        {
            "app": {
                "version": <the app's version>,
                "app_store_build": <the app's build>
            },
            "device": {
                "uuid": <the Device's UUID>,
                "device": <the Device's name>,
                "os": <the Device's OS name>,
                "os_version": <the Device's OS Version>,
                "screen": <the Device's screen size (ie. 600x960)>
            }
        }
        ```

        Status Codes:
            - 201 : Created successfully
            - 400 : Bad Request
        Response Structure:
            - Serialized version of the device object
        """
        retval = self._process_request(request, *args, **kwargs)
        if not isinstance(retval, Response):
            return Response(retval, status=status.HTTP_201_CREATED)
        return retval


class RetrieveUpdateDevice(AppVersionMixin, generics.RetrieveUpdateAPIView):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    lookup_field = 'uuid'

    def put(self, request, *args, **kwargs):
        """
        Creates a new Device.

        Accepted:
            - json
            - formdata
            - multipart
        Request Structure:
        ```
        {
            "app": {
                "version": <the app's version>,
                "app_store_build": <the app's build>
            },
            "device": {
                "uuid": <the Device's UUID>,
                "device": <the Device's name>,
                "os": <the Device's OS name>,
                "os_version": <the Device's OS Version>,
                "screen": <the Device's screen size (ie. 600x960)>
            }
        }
        ```

        Status Codes:
            - 200 : Updated successfully
            - 400 : Bad Request
        Response Structure:
            - Serialized version of the device object
        """
        obj = self.get_object()
        retval = self._process_request(request, obj, *args, **kwargs)
        if not isinstance(retval, Response):
            return Response(retval, status=status.HTTP_200_OK)
        return retval