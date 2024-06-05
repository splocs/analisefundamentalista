import streamlit as st
import pandas as pd
import investpy
from PIL import Image
from datetime import date
import plotly.express as px

# Configurando a largura da página
st.set_page_config(layout="wide")

# Função para formatar a data
def formatar_data(data):
    return data.strftime('%d-%m-%Y')

# Dicionário de tradução de nomes das colunas
traducao = {
    'Date': 'Data',
    'Open': 'Abertura',
    'High': 'Alta',
    'Low': 'Baixa',
    'Close': 'Fechamento',
    'Volume': 'Volume'
}

# Função para pegar os dados das ações
@st.cache
def pegar_dados_acoes():
    acoes = investpy.get_stocks_list(country='brazil')
    return acoes

# Definindo data de início e fim
DATA_INICIO = '01/01/2017'
DATA_FIM = date.today().strftime('%d/%m/%Y')

# Logo padrão (se não houver logo da empresa)
logo_path = "logo.png"
logo_padrao = Image.open(logo_path)

# Exibir o logo padrão no aplicativo Streamlit
st.image(logo_padrao, width=250)

# Exibir o logo padrão na sidebar
st.sidebar.image(logo_padrao, width=150)

st.title('Análise de ações')

# Criando a sidebar
st.sidebar.markdown('Escolha a ação')
n_dias = st.sidebar.slider('Quantidade de dias de previsão', 30, 365)

# Pegando os dados das ações
acoes = pegar_dados_acoes()

nome_acao_escolhida = st.sidebar.selectbox('Escolha uma ação:', acoes)

# Pegando os valores online
df_valores = investpy.get_stock_historical_data(stock=nome_acao_escolhida,
                                                country='brazil',
                                                from_date=DATA_INICIO,
                                                to_date=DATA_FIM)

st.subheader('Tabela de Valores - ' + nome_acao_escolhida)

# Renomeando as colunas usando o dicionário de tradução
df_valores = df_valores.rename(columns=traducao)

# Convertendo a coluna "Data" para o formato desejado
df_valores.reset_index(inplace=True)
df_valores['Data'] = df_valores['Data'].dt.strftime('%d-%m-%Y')
st.write(df_valores.tail(40))

# Exibir informações detalhadas da ação
st.subheader('Informações Detalhadas da Ação')

acao_info = investpy.get_stock_information(stock=nome_acao_escolhida, country='brazil')

st.write(pd.DataFrame(acao_info.items(), columns=["Descrição", "Valor"]))

# Exibir Indicadores Fundamentalistas
st.subheader('Indicadores Fundamentalistas')

indicadores = investpy.get_stock_company_profile(stock=nome_acao_escolhida, country='brazil')

st.write(pd.DataFrame(indicadores.items(), columns=["Indicador", "Valor"]))

# Dados do Balanço Patrimonial
st.subheader('Dados do Balanço Patrimonial')

balanco = investpy.get_stock_balance_sheet(stock=nome_acao_escolhida, country='brazil')

st.write(pd.DataFrame(balanco.items(), columns=["Descrição", "Valor"]))

# Seletor para alterar entre dados anuais e trimestrais
periodo_financeiro = st.radio("Selecionar período financeiro", ["Anual", "Trimestral"])

# Coletando e exibindo dados fundamentalistas adicionais
period = 'annual' if periodo_financeiro == "Anual" else 'quarterly'

# Função para exibir dados com tratamento de exceção
def exibir_dados(label, func, period):
    try:
        dados = func(period=period)
        if dados is not None and not dados.empty:
            st.write(f"**{label}:**")
            st.write(dados)
    except Exception as e:
        st.warning(f"{label} não disponível: {e}")

exibir_dados("Histórico de preços", lambda period: investpy.get_stock_historical_data(stock=nome_acao_escolhida,
                                                                                        country='brazil',
                                                                                        from_date='01/01/1990',
                                                                                        to_date=date.today().strftime('%d/%m/%Y')), period)
exibir_dados("Dividendos", lambda period: investpy.get_stock_dividends(stock=nome_acao_escolhida, country='brazil'), period)
exibir_dados("Splits de ações", lambda period: investpy.get_stock_splits(stock=nome_acao_escolhida, country='brazil'), period)
exibir_dados("Demonstração de resultados", lambda period: investpy.get_stock_financial_summary(stock=nome_acao_escolhida, country='brazil')[0], period)
exibir_dados("Fluxo de caixa", lambda period: investpy.get_stock_financial_summary(stock=nome_acao_escolhida, country='brazil')[1], period)


