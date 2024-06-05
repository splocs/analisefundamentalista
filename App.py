import yfinance as yf
import pandas as pd

# Função para buscar e exibir dados financeiros de uma ação
def get_stock_data(ticker):
    # Buscar os dados da ação
    stock = yf.Ticker(ticker)

    # Obter informações gerais
    info = stock.info
    
    # Obter histórico de preços
    history = stock.history(period="1y")
    min_52_weeks = history['Close'].min()
    max_52_weeks = history['Close'].max()
    last_quote_date = history.index[-1].strftime('%Y-%m-%d')
    last_quote = history['Close'][-1]

    # Criar dicionário com os dados desejados
    data = {
        "Papel": info['symbol'],
        "Cotação": last_quote,
        "Tipo": info.get('quoteType', 'N/A'),
        "Data últ cotação": last_quote_date,
        "Empresa": info.get('longName', 'N/A'),
        "Min 52 semanas": min_52_weeks,
        "Setor": info.get('sector', 'N/A'),
        "Max 52 semanas": max_52_weeks,
        "Subsetor": info.get('industry', 'N/A'),
        "Vol $ méd (2m)": info.get('averageDailyVolume10Day', 'N/A'),
        "Valor de mercado": info.get('marketCap', 'N/A'),
        "Últ balanço processado": info.get('lastFiscalYearEnd', 'N/A'),
        "Valor da firma": info.get('enterpriseValue', 'N/A'),
        "Nro. Ações": info.get('sharesOutstanding', 'N/A'),
        "P/L": info.get('trailingPE', 'N/A'),
        "LPA": info.get('trailingEps', 'N/A'),
        "P/VP": info.get('priceToBook', 'N/A'),
        "VPA": info.get('bookValue', 'N/A'),
        "P/EBIT": info.get('enterpriseToEbitda', 'N/A'),
        "Marg. Bruta": info.get('grossMargins', 'N/A'),
        "PSR": info.get('priceToSalesTrailing12Months', 'N/A'),
        "Marg. EBIT": info.get('ebitdaMargins', 'N/A'),
        "P/Ativos": info.get('priceToBook', 'N/A'),
        "Marg. Líquida": info.get('netMargins', 'N/A'),
        "P/Cap. Giro": 'N/A',  # Não disponível no Yahoo Finance
        "EBIT / Ativo": 'N/A',  # Não disponível no Yahoo Finance
        "P/Ativ Circ Liq": 'N/A',  # Não disponível no Yahoo Finance
        "ROIC": 'N/A',  # Não disponível no Yahoo Finance
        "Div. Yield": info.get('dividendYield', 'N/A'),
        "ROE": info.get('returnOnEquity', 'N/A'),
        "EV / EBITDA": info.get('enterpriseToEbitda', 'N/A'),
        "Liquidez Corr": info.get('currentRatio', 'N/A'),
        "EV / EBIT": 'N/A',  # Não disponível no Yahoo Finance
        "Div Br/ Patrim": 'N/A',  # Não disponível no Yahoo Finance
        "Cres. Rec (5a)": 'N/A',  # Não disponível no Yahoo Finance
        "Giro Ativos": info.get('totalRevenue', 'N/A') / info.get('totalAssets', 'N/A'),
        "Ativo": info.get('totalAssets', 'N/A'),
        "Dív. Bruta": info.get('totalDebt', 'N/A'),
        "Disponibilidades": info.get('cash', 'N/A'),
        "Dív. Líquida": info.get('totalDebt', 'N/A') - info.get('cash', 'N/A'),
        "Ativo Circulante": info.get('totalCurrentAssets', 'N/A'),
        "Patrim. Líq": info.get('totalStockholderEquity', 'N/A'),
    }

    # Criar DataFrame
    df = pd.DataFrame([data])

    # Exibir DataFrame
    print(df.to_string(index=False))

# Exemplo de uso
ticker = "AAPL"  # Substitua pelo ticker desejado
get_stock_data(ticker)

