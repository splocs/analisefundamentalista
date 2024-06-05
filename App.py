import yfinance as yf
import streamlit as st

# Funções para calcular indicadores financeiros
def calculate_var_ll(data):
    return data['Net Income'].pct_change(periods=3).mean()

def calculate_p_l(data):
    return data['Close'].iloc[-1] / data['Earnings']

def calculate_pfcp_pft(data):
    return data['Short Term Debt'].iloc[-1] / data['Total Debt'].iloc[-1]

def calculate_ls(data):
    return data['Current Assets'].iloc[-1] / data['Current Liabilities'].iloc[-1]

def calculate_at(data):
    return data['Total Assets'].iloc[-1]

def calculate_lc(data):
    return data['Current Assets'].iloc[-1] / data['Current Liabilities'].iloc[-1]

def calculate_p_vpa(data):
    return data['Close'].iloc[-1] / data['Book Value'].iloc[-1]

def calculate_lpa(data):
    return data['Net Income'].iloc[-1] / data['Shares Outstanding'].iloc[-1]

def calculate_roa(data):
    return data['Net Income'].iloc[-1] / data['Total Assets'].iloc[-1]

# Função principal do Streamlit
def main():
    st.title('Indicadores Financeiros')

    ticker = st.text_input('Digite o ticker da ação:', 'AAPL')

    if ticker:
        data = yf.Ticker(ticker).history(period='5y')
        financials = yf.Ticker(ticker).financials
        balance_sheet = yf.Ticker(ticker).balance_sheet

        indicators = {
            'Variação da Média Trienal do Lucro Líquido (VarLL)': calculate_var_ll(financials),
            'Índice Preço Lucro Médio (P/L)': calculate_p_l(data),
            'Índice Dívida Financeira de Curto Prazo / Dívida Financeira Total (PFCP/PFT)': calculate_pfcp_pft(balance_sheet),
            'Liquidez Seca (LS)': calculate_ls(balance_sheet),
            'Ativo Total (AT)': calculate_at(balance_sheet),
            'Liquidez Corrente (LC)': calculate_lc(balance_sheet),
            'Índice Preço Valor Patrimonial por Ação (P/VPA)': calculate_p_vpa(balance_sheet),
            'Lucro por Ação (LPA)': calculate_lpa(financials),
            'Return on Assets (ROA)': calculate_roa(balance_sheet)
        }

        st.write('Indicadores Calculados:')
        for name, value in indicators.items():
            st.write(f'{name}: {value}')

if __name__ == "__main__":
    main()

