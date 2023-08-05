from rest_framework import serializers

__author__ = 'cenk'


class Serializer(serializers.Serializer):
    class Meta:
        abstract = True