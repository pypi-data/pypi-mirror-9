import copy

from django.contrib.auth import login
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from drf_authentication.app_settings import api_settings
from drf_authentication.serializers.drf_auth_user_serializer import DrfAuthUserSerializer
from drf_authentication.views.generic_api_view import GenericAPIView


__author__ = 'cenk'


class DrfAuthLogin(GenericAPIView):
    serializer_class = api_settings.LOGIN_SERIALIZER
    permission_classes = (AllowAny,)
    user_serializer_class = api_settings.USER_SERIALIZER


    def post(self, request, *args, **kwargs):
        self.serializer = self.get_serializer(data=self.request.DATA)
        request_data = copy.deepcopy(self.request.DATA)
        user_data = DrfAuthUserSerializer(data=request_data).initial_data
        if not self.serializer.is_valid():
            return self.get_error_response()
        self.user = self.serializer.validated_data['user']
        if not self.user:
            return Response(self.serializer.errors, status=status.HTTP_404_NOT_FOUND)
        login(request, self.user)
        return Response(user_data, status=status.HTTP_200_OK)

    def get_error_response(self):
        return Response(self.serializer.errors, status=status.HTTP_400_BAD_REQUEST)