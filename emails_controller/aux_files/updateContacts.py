import pandas as pd

from ..models import Contato, Colaborador


class UpdateContacts:
    def __init__(self):
        self.load_contats_list()
        self.process_info()

    def load_contats_list(self):
        self.df = pd.read_excel('emails_controller/aux_files/Lista_Contatos.xlsx')
        #self.df = pd.read_excel('C:/Users/caiqu/Documents/Hidrotube/email_sender/emails_controller/aux_files/Lista_Contatos.xlsx')

    def process_info(self):

        for index, row in self.df.iterrows():
            print(f'Atualizando: {row["Razao_Social"]}')
            contato = Contato.objects.get(id=row['id'])
            colaborador = Colaborador.objects.get(nome=row['Colaborador'])
            pesquisa = True if row['Pesquisa'] == 1 else False

            contato.update(
                colaborador=colaborador,
                pesquisa=pesquisa
            )
