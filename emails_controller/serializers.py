from rest_framework import serializers
from .models import Contato


class ContatoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Contato
        fields = ['e_mail']

    def update(self, instance, validated_data):
        instance.excluido = True
        instance.save()
        return instance