from django.shortcuts import render
import pandas as pd
import json
import io
# Create your views here.
def render_painel(request):
    class setor:
        def __init__(self, nome):
            self.nome = nome
            self.n = 0
            self.horas = 0
            self.insat = []
            self.sat = []
            self.insat_l = []
            self.bemtreinados = []
            self.maltreinados = []
            self.faltantes = []
            self.sem_participação = []
            self.alta_participação = []
            self.alto_desempenho = []
            self.baixo_desempenho = []
            self.recentes = []
            self.antigos = []
            self.quer_liderar = []
            self.desalinhados = []
            self.despontuais =  []
        def get_bemtreinados(self, df):
            resultado = df[df['Horas de Capacitacção'] > self.horas*1.3 ].groupby('Setor')['Membro'].apply(list).to_dict()
            self.bemtreinados = resultado.get(self.nome, [])
        def get_maltreinados(self, df):
            resultado = df[df['Horas de Capacitacção'] < self.horas/1.3 ].groupby('Setor')['Membro'].apply(list).to_dict()
            self.maltreinados = resultado.get(self.nome, [])
    setores = {nome: setor(nome) for nome in ['RH','Comercial','Civil','Consultoria','Tecnologia','Total']}

    if request.method == 'POST' and request.FILES.get("planilha"):
        planilha = request.FILES.get("planilha")
        df = pd.read_excel(planilha, header=1)
        df = df.dropna(how='all')
        data = df.to_json(orient='records', force_ascii=False)

        n_setor = df['Setor'].value_counts()
        for nome, s in setores.items():
            s.n = n_setor.get(s.nome, 0) 
        setores['Total'].n = df.shape[0]
        print(setores['Total'].n)
            
        horas_setor = df.groupby('Setor')['Horas de Capacitacção'].mean()
        for nome, s in setores.items():
            s.horas = horas_setor.get(s.nome, 0)
        print(horas_setor)
        media_horas = df['Horas de Capacitacção'].mean()
        print(media_horas)

        insat = df[df['Satisfação Geral'] <= 2].groupby('Setor')['Membro'].apply(list).to_dict()
        for nome, s in setores.items():
            s.insat.extend(insat.get(s.nome, []))

        sat = df[df['Satisfação Geral'] >= 4].groupby('Setor')['Membro'].apply(list).to_dict()
        for nome, s in setores.items():
            s.sat.extend(sat.get(s.nome, []))

        insat_l = df[df['Satisfacao do membro com a Lideranca'] <= 2].groupby('Setor')['Membro'].apply(list).to_dict()
        for nome, s in setores.items():
            s.insat_l.extend(insat_l.get(s.nome, []))

        sem_participação = df[df['Participacao em Capacitacoes'] <= 5].groupby('Setor')['Membro'].apply(list).to_dict()
        for nome, s in setores.items():
            s.sem_participação.extend(sem_participação.get(s.nome, []))        
        
        alta_participação = df[df['Participacao em Capacitacoes'] >= 8].groupby('Setor')['Membro'].apply(list).to_dict()
        for nome, s in setores.items():
            s.alta_participação.extend(alta_participação.get(s.nome, []))     
  
        baixo_desempenho = df[df['Nota de Desempenho'] < 3].groupby('Setor')['Membro'].apply(list).to_dict()
        for nome, s in setores.items():
            s.baixo_desempenho.extend(baixo_desempenho.get(s.nome, []))         
        
        alto_desempenho = df[df['Nota de Desempenho'] > 3].groupby('Setor')['Membro'].apply(list).to_dict()
        for nome, s in setores.items():
            s.alto_desempenho.extend(alto_desempenho.get(s.nome, []))       

        recentes = df[df['Tempo na EJ (meses)'] < 6].groupby('Setor')['Membro'].apply(list).to_dict()
        for nome, s in setores.items():
            s.recentes.extend(recentes.get(s.nome, []))

        antigos = df[df['Tempo na EJ (meses)'] > 18].groupby('Setor')['Membro'].apply(list).to_dict()
        for nome, s in setores.items():
            s.antigos.extend(antigos.get(s.nome, []))

        quer_liderar = df[df['Interesse em Lideranca'] == 'Sim'].groupby('Setor')['Membro'].apply(list).to_dict()
        for nome, s in setores.items():
            s.quer_liderar.extend(quer_liderar.get(s.nome, []))

        desalinhados = df[df['Alinhamento Cultural'] <= 2].groupby('Setor')['Membro'].apply(list).to_dict()
        for nome, s in setores.items():
            s.desalinhados.extend(desalinhados)

        faltantes = df[df['Presenca em Reunioes (%)'] < 75].groupby('Setor')['Membro'].apply(list).to_dict()
        for nome, s in setores.items():
            s.faltantes.extend(faltantes.get(s.nome, []))

        despontuais = df[df['Entregas no Prazo (%)'] < 80].groupby('Setor')['Membro'].apply(list).to_dict()
        for nome, s in setores.items():
            s.despontuais.extend(despontuais.get(s.nome, []))

        for nome, s in setores.items():
            s.get_bemtreinados(df)
        for nome, s in setores.items():
            s.get_maltreinados(df)

        Turnover = []
        for nome, s in setores.items():
            if s.insat != [] and s.faltantes != []:
                em_todos = list(set(s.faltantes) & set(s.insat))
                Turnover.extend(em_todos)
        print("Turnover: ",Turnover)

        Desengajamento = []
        for nome, s in setores.items():
            if s.insat != [] and s.faltantes != []:
                em_todos = list(set(s.insat) - set(s.faltantes))
                Desengajamento.extend(em_todos)
        print("Desengajados: ", Desengajamento)

        Sobrecarga = []
        for nome, s in setores.items():
            if s.n <= 6 and s.alto_desempenho != []:
                    em_todos = list(set(s.alto_desempenho) - set(s.faltantes) - set(s.sat))
                    Sobrecarga.extend(em_todos)
        print("Sobrecarregados: ",Sobrecarga)

        Dependências = []
        for nome, s in setores.items():
            if s.alto_desempenho != [] and len(s.alto_desempenho) <= s.n/2 and s.antigos != []:
                em_todos = list(set(s.alto_desempenho) & set(s.antigos))
                Dependências.extend(em_todos)
        print("Membros dependência: ",Dependências)

        Subdesenvolvimento = []
        for nome, s in setores.items():
            if (len(s.quer_liderar) <= s.n/3 and s.nome != 'Total') or s.n < 6:
                em_todos = s.nome
                Subdesenvolvimento.append(em_todos)
        print("Setores em Subdesenvolvimento: ",Subdesenvolvimento)

        Cultural = []
        for nome, s in setores.items():
            if s.insat_l != [] and s.desalinhados != []:
                em_todos = list(set(s.insat_l) & set(s.desalinhados))
                Cultural.extend(em_todos)
        print("Membros em risco Cultural: ",Cultural)

        grupos_interesse = {
            'Turnover': Turnover,
            'Desengajamento': Desengajamento,
            'Sobrecarga': Sobrecarga,
            'Dependências': Dependências,
            'Subdesenvolvimento': Subdesenvolvimento,
            'Cultural': Cultural
        }

        request.session['dados'] = data
        request.session['grupos_interesse'] = grupos_interesse
        return render(request, 'painel.html', {'dados': data, 'grupos_interesse': grupos_interesse})
   
    return render(request, 'painel.html')


def buscar_membro(request):
    if request.POST.get('membros'):
        membro = request.POST.get('membros')
        data = request.session.get('dados')
        grupos_interesse = request.session.get('grupos_interesse')
        df = pd.DataFrame(pd.read_json(io.StringIO(data)))
        df = df.dropna(axis=1, how='all')
        print(df)
        serie = df[df['Membro'].astype(str) == str(membro)]
        print(serie)

        return render(request, 'painel.html', {
            'dados': data,
            'dados_membro': serie.iloc[0].dropna().to_dict if not serie.empty else None,
            'grupos_interesse': grupos_interesse
        })
    return render(request, 'painel.html')