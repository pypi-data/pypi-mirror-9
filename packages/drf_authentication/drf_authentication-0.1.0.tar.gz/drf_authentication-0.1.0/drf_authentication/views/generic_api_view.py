__author__ = 'cenk'

from rest_framework import generics


class GenericAPIView(generics.GenericAPIView):
    class Meta:
        abstract = True