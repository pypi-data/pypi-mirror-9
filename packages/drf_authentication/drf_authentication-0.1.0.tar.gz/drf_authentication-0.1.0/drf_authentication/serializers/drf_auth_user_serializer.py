from .model_serializer import ModelSerializer

from drf_authentication import utils


__author__ = 'cenk'

UserModel = utils.get_user_model()


class DrfAuthUserSerializer(ModelSerializer):
    class Meta:
        model = UserModel
        fields = (UserModel.USERNAME_FIELD, "password")