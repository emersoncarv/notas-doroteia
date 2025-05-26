import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from warnings import filterwarnings
filterwarnings('ignore')

st.set_page_config(page_title='Projeção de Notas Trimestrais', layout='wide')
st.title('Projeção de Notas Trimestrais')

# Função para calcular a média do trimestre
def calcular_media_trimestre(p1, p2, trimestral):
    return ((p1 + p2) / 2 + trimestral) / 2

# Função para calcular a nota necessária na prova trimestral para alcançar média 7.0
def calcular_nota_necessaria(p1, p2):
    return 2 * 7.0 - (p1 + p2) / 2

disciplinas = sorted([
    "Matemática", 
    "Língua Portuguesa", 
    "Literatura",
    "Arte",
    "Biologia",
    "Educação Física",
    "Filosofia",
    "Física",
    "Formação Humano-Cristã",
    "Geografia",
    "História",
    "Língua Inglesa",
    "Química",
    "Redação",
    "Sociologia",
    "Vida e Carreira"
    ])
trimestres = ["T1", "T2", "T3"]

if 'notas' not in st.session_state:
    # Criação inicial da tabela de notas
    notas = pd.DataFrame(
        {
            'Disciplina': pd.Series(dtype='str'),
            'Trimestre': pd.Series(dtype='str'),
            'P1': pd.Series(dtype='float64'),
            'P2': pd.Series(dtype='float64'),
            'Trimestral': pd.Series(dtype='float64'),
            'Média Trimestre': pd.Series(dtype='float64'),
            'Nota Necessária para 7.0': pd.Series(dtype='float64')
        }
    )
    st.session_state['notas'] = notas
else:
    # busca as notas armazenadas em memória
    notas = st.session_state['notas']

# barra lateral
with st.sidebar:
    upload_file = st.file_uploader('Selecione seu arquivo de notas', type=['csv'], accept_multiple_files=False)
    import_button = st.button('Importar')

    if import_button:
        import_notas = pd.read_csv(upload_file, sep=',', encoding='utf-8')
        import_notas.drop_duplicates(inplace=True)
        
        # Preencher o session_state com os valores do CSV
        for _, row in import_notas.iterrows():
            disciplina = row["Disciplina"]
            trimestre = row["Trimestre"]
            
            st.session_state[f"{disciplina}|{trimestre}|P1"] = row["P1"]
            st.session_state[f"{disciplina}|{trimestre}|P2"] = row["P2"]
            st.session_state[f"{disciplina}|{trimestre}|Trim"] = row["Trimestral"]
        notas = import_notas.copy()
        del import_notas
        st.info('Arquivo importado com sucesso.')

    st.divider()

    st.download_button(
        label='Exportar arquivo de notas',
        data=notas.to_csv(index=False).encode('utf-8'),
        file_name='notas.csv',
        mime='text/csv',
        # disabled=(notas.shape[0]==0)
    )

# interface principal
tabs = st.tabs(disciplinas)
for i, tab in enumerate(tabs):
    with tab:
        cols = st.columns(len(trimestres))
        for j, col in enumerate(cols):
            with col:
                st.subheader(f"{disciplinas[i]} - {trimestres[j]}")

                object_key = f"{disciplinas[i]}|{trimestres[j]}|"
                p1 = st.number_input(f"Nota P1", format="%.1f", min_value=0.0, max_value=10.0, step=0.1, key=object_key + "P1")
                p2 = st.number_input(f"Nota P2", format="%.1f", min_value=0.0, max_value=10.0, step=0.1, key=object_key + "P2")
                trimestral = st.number_input(f"Nota Trimestral", format="%.1f", min_value=0.0, max_value=10.0, step=0.1, key=object_key + "Trim")

                p1 = round(p1, 1)
                p2 = round(p2, 1)
                trimestral = round(trimestral, 1)

                if p1 == 0 or p2 == 0:
                    media_trimestre = nota_necessaria = 0
                elif trimestral == 0:
                    nota_necessaria = round( calcular_nota_necessaria(p1, p2) , 1)
                    media_trimestre = 0
                    st.write(f'Nota Necessária para 7.0: **{nota_necessaria}**')
                else:
                    media_trimestre = round( calcular_media_trimestre(p1, p2, trimestral), 1)
                    nota_necessaria = round( calcular_nota_necessaria(p1, p2) , 1)
                    st.write(f'Média trimestral: **{media_trimestre}**')

                if media_trimestre > 0 or nota_necessaria > 0:
                    nova_linha = pd.DataFrame({
                        "Disciplina": [disciplinas[i]],
                        "Trimestre": [trimestres[j]],
                        "P1": [p1],
                        "P2": [p2],
                        "Trimestral": [trimestral],
                        "Média Trimestre": [media_trimestre],
                        "Nota Necessária para 7.0": [nota_necessaria]
                    })

                    notas = pd.concat([notas, nova_linha], ignore_index=True)

notas.drop_duplicates(inplace=True)
notas.sort_values(by=['Disciplina', 'Trimestre'], inplace=True)

st.divider()

with st.expander('Gráficos: Trimestres'):
    tabs_graficos = st.tabs(trimestres)
    for i, tab in enumerate(tabs_graficos):
        with tab:
            chart_data = notas[notas['Trimestre'] == trimestres[i]]
            
            fig = px.bar(
                chart_data,
                x='Disciplina', 
                y=['P1', 'P2', 'Trimestral', 'Média Trimestre'], 
                range_y=[0, 10],
                #title='Notas por Disciplina',
                barmode='group',
                labels={
                    'value':'Nota',
                    'variable': 'Avaliação'
                },
                #color_discrete_sequence=['lightblue', 'blue', 'magenta', 'red'],
                text_auto=True,
            )
            #linha de referência para a nota de aprovação
            fig.add_hline(y=7.0)
            st.plotly_chart(fig, key='Chart1|' + trimestres[i])


with st.expander('Notas Detalhadas'):
    st.dataframe(notas, hide_index=True)


# # Cálculo da média final por disciplina
# medias_finais = notas[notas['Média Trimestre'] > 0].groupby("Disciplina")["Média Trimestre"].mean().reset_index()
# medias_finais.columns = ["Disciplina", "Média Final"]



