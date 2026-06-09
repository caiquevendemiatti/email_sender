import re
import pandas
from emails_controller.models import Colaborador, Contato
from django.db.utils import IntegrityError


def clean_email(raw):
    email = str(raw).strip().strip(';,').strip()
    if re.search(r'[;,]', email):
        return None, f'E-mail contém múltiplos endereços ou caractere inválido: "{raw}"'
    return email, None

class LoadData:
    def __init__(self):
        pass

    def load_email_list_by_vendor(self, vendor_name, filename):
        """
        This functions read an execel file with Fiels ['razao_social', 'nome_contato', 'email']
        :param vendor_name: Nome do Colaborador de acordo com o cadastrado no banco de dados
        :param filename: Caminho pora o arquivo excel contendo o arquivo a ser carregado
        :return:
        """
        try:
            colaborador = Colaborador.objects.get(nome=vendor_name)
        except Colaborador.DoesNotExist as err:
            print(f"Colaborador Não Cadastrado {vendor_name}")
            return

        contacts_df = pandas.read_excel(filename)
        index = pandas.Index(range(0, len(contacts_df), 1))
        contacts_df = contacts_df.set_index(index)

        for i in index:
            email, erro = clean_email(contacts_df['e-mail'][i])
            if erro:
                print(f"  Linha {i + 2}: {erro} — corrija na planilha e reimporte.")
                continue

            try:
                contact = Contato(
                    razao_social=str(contacts_df['razao_social'][i]).strip(),
                    contato=str(contacts_df['nome_contato'][i]).strip(),
                    e_mail=email,
                    colaborador_responsavel=colaborador
                )
                contact.save()
            except IntegrityError as err:
                print(f"Email já cadastrado - Erro {err}")
        pass

