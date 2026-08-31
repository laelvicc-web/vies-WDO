import streamlit as st
import yfinance as yf

st.set_page_config(page_title="Checklist WDO Automação", layout="centered")

st.title("📊 Viés WDO — Automação Yahoo Finance")
st.caption("Atualização automática com variação limite de ±0.30%")

TICKERS = {
    "DXY (Índice Dólar)": "DX-Y.NYB",
    "Treasury 10 anos (US10Y)": "^TNX",
    "USD/JPY": "JPY=X",
    "VIX (Índice do Medo)": "^VIX",
    "Futuros S&P 500": "ES=F",
    "Petróleo WTI": "CL=F"
}

THRESHOLD = 0.30

@st.cache_data(ttl=60)
def carregar_dados():
    resultados = []
    pontos_alta = 0
    pontos_baixa = 0
    pontos_neutro = 0

    for nome, ticker in TICKERS.items():
        ativo = yf.Ticker(ticker)
        data = ativo.history(period="2d")
        
        if len(data) >= 2:
            preco_atual = data['Close'].iloc[-1]
            preco_anterior = data['Close'].iloc[-2]
            variacao = ((preco_atual - preco_anterior) / preco_anterior) * 100
            
            inverter_sinal = "S&P" in nome or "Petróleo" in nome
            
            if variacao > THRESHOLD:
                sinal = "ENFRAQUECE USD" if inverter_sinal else "FORTALECE USD"
                cor = "🔴" if inverter_sinal else "🟢"
            elif variacao < -THRESHOLD:
                sinal = "FORTALECE USD" if inverter_sinal else "ENFRAQUECE USD"
                cor = "🟢" if inverter_sinal else "🔴"
            else:
                sinal = "NEUTRO"
                cor = "⚪"

            if "FORTALECE" in sinal:
                pontos_alta += 1
            elif "ENFRAQUECE" in sinal:
                pontos_baixa += 1
            else:
                pontos_neutro += 1

            resultados.append({
                "Ativo": nome,
                "Preço": f"{preco_atual:.2f}",
                "Variação": f"{variacao:+.2f}%",
                "Sinal Dólar": f"{cor} {sinal}"
            })
            
    return resultados, pontos_alta, pontos_baixa, pontos_neutro

if st.button("🔄 Atualizar Dados Agora"):
    st.cache_data.clear()

with st.spinner("Puxando cotações do Yahoo Finance..."):
    dados, alta, baixa, neutro = carregar_dados()

st.divider()
st.subheader("Veredito do Mercado")
col1, col2, col3 = st.columns(3)
col1.metric("Fortalece Dólar", alta)
col2.metric("Enfraquece Dólar", baixa)
col3.metric("Neutros", neutro)

if alta > baixa and alta >= 3:
    st.success("🔥 **VIÉS DEFINIDO: ALTA NO DÓLAR (WDO)**")
elif baixa > alta and baixa >= 3:
    st.error("📉 **VIÉS DEFINIDO: BAIXA NO DÓLAR (WDO)**")
else:
    st.warning("⚠️ **MERCADO INDECISO / LATERAL (CAUTELA)**")

st.divider()
st.subheader("Detalhamento por Ativo")
st.table(dados)
