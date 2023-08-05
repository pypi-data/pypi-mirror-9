from rest_framework import serializers

__author__ = 'cenk'


class ModelSerializer(serializers.ModelSerializer):
    class Meta:
        abstract = True