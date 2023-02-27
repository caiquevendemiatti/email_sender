from django.shortcuts import render
from django.views.generic.base import TemplateView
from rest_framework.generics import GenericAPIView, UpdateAPIView
from rest_framework.mixins import UpdateModelMixin, CreateModelMixin
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.renderers import TemplateHTMLRenderer


from .models import Contato
from .serializers import ContatoSerializer
#
class CancelarInscrição(UpdateAPIView):

    authentication_classes = []  # disables authentication
    permission_classes = []  # disables permission
    serializer_class = ContatoSerializer  # Instantiate the Serializer
    queryset = Contato.objects.all()

    def update(self, request, *args, **kwargs):
        data_to_change = {'excluido': True}
        try:
            instance = Contato.objects.get(e_mail=request.data.get('e_mail'))

            serializer = self.serializer_class(instance=instance, data=data_to_change, partial=True)
            if serializer.is_valid():
                self.perform_update(serializer)
                return Response(f'Inscrição excluída com sucesso', status=status.HTTP_200_OK)

        except Contato.DoesNotExist:
            return Response(f'E-mail não cadastrado - Verifique o endereço digitado',
                            status=status.HTTP_202_ACCEPTED)


class CancelarInscricaoPage(TemplateView):
    template_name = 'unsubscribe.html'