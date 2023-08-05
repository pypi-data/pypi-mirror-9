from rest_framework import status
from rest_framework.response import Response

from drf_authentication.serializers.serializer import Serializer
from drf_authentication import utils


__author__ = 'cenk'

UserModel = utils.get_user_model()


class DrfAuthLoginSerializer(Serializer):
    def validate(self, attrs):
        from drf_authentication.authentication import authenticate

        attrs = super(DrfAuthLoginSerializer, self).validate(self.initial_data)
        try:
            username = attrs.get(UserModel.USERNAME_FIELD)
            password = attrs.get('password')
        except:
            return Response(self.serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        credentials = {UserModel.USERNAME_FIELD: username, 'password': password}
        user = authenticate(**credentials)
        attrs['user'] = user
        return attrs