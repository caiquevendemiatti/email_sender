from django.shortcuts import render
from django.views.generic.base import TemplateView
from rest_framework.generics import GenericAPIView, UpdateAPIView
from rest_framework.mixins import UpdateModelMixin, CreateModelMixin
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.renderers import TemplateHTMLRenderer



from .models import Contato, Colaborador
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


class PremioMgaPage(TemplateView):
    template_name = 'premio_mga_server.html'

    def get(self, *args, **kwargs):
        vendor_id = self.request.GET['id']
        colaborador = Colaborador.objects.get(id=vendor_id)
        link_wa = link_wa = f'https://wa.me/55{colaborador.ddd}{colaborador.whatsapp}'
        format_phone = f'({colaborador.ddd}) {colaborador.whatsapp[0:5]}-{colaborador.whatsapp[5:]}'

        add_content = {'vendor_name': colaborador.nome,
                           'vendor_email': colaborador.e_mail,
                           'link_wa': link_wa,
                           'phone_number': format_phone,
                           'link_cancel_inscr': 'http://marketing.hidrotube.com.br/cancelar_inscricao'}

        return render(self.request, self.template_name, add_content)



