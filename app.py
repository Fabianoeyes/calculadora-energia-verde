import streamlit as st
import math

st.set_page_config(page_title="Calculadora de Economia – Energia Verde", page_icon="⚡")

st.title("⚡ Calculadora de Economia – Energia Verde")
st.write(
    "Use esta calculadora para mostrar ao cliente quanto ele pode economizar "
    "ao contratar a **energia verde** da sua empresa."
)

st.markdown("### 1️⃣ Preencha os dados do cliente")

valor_conta = st.number_input(
    "Valor atual da conta de luz (R$)",
    min_value=0.0,
    value=1000.0,
    step=50.0,
    format="%.2f",
)

desconto_percent = st.number_input(
    "% de desconto na energia consumida",
    min_value=0.0,
    max_value=100.0,
    value=15.0,
    step=1.0,
    help="Por padrão usamos 15%, mas você pode ajustar conforme a proposta."
)

cobertura_percent = st.number_input(
    "% da conta coberta pela energia verde",
    min_value=0.0,
    max_value=100.0,
    value=80.0,
    step=5.0,
    help="Por padrão 80%, pois 20% é parte fixa da distribuidora."
)

periodo_meses = st.slider(
    "Período de análise (meses)",
    min_value=1,
    max_value=60,
    value=12,
)

st.markdown("---")
st.markdown("### 2️⃣ Resultados da simulação")

desconto = desconto_percent / 100.0
cobertura = cobertura_percent / 100.0

valor_elegivel = valor_conta * cobertura
economia_mensal = valor_elegivel * desconto
nova_conta = valor_conta - economia_mensal
economia_total = economia_mensal * periodo_meses

meses_para_uma_conta = None
if economia_mensal > 0:
    meses_para_uma_conta = math.ceil(valor_conta / economia_mensal)

col1, col2 = st.columns(2)

def format_real(v):
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

with col1:
    st.metric("Economia mensal estimada", format_real(economia_mensal))
    st.metric("Economia total no período", format_real(economia_total))

with col2:
    st.metric("Conta atual (sem energia verde)", format_real(valor_conta))
    st.metric("Nova conta estimada com energia verde", format_real(nova_conta))

st.markdown("---")
st.markdown("### 3️⃣ Frase pronta para o vendedor usar com o cliente")

resumo = (
    f"Com a nossa energia verde, considerando **{desconto_percent:.0f}% de desconto** "
    f"sobre **{cobertura_percent:.0f}% da sua conta de luz**, "
    f"você passa de **{format_real(valor_conta)}** para aproximadamente "
    f"**{format_real(nova_conta)}** por mês.\n\n"
    f"Isso representa uma **economia mensal de {format_real(economia_mensal)}**, "
    f"ou **{format_real(economia_total)} em {periodo_meses} meses**."
)

if meses_para_uma_conta:
    resumo += (
        f"\n\nEm cerca de **{meses_para_uma_conta} meses**, você terá economizado o "
        f"equivalente a **1 conta inteira** do valor atual."
    )

st.write(resumo)

st.markdown("---")
st.caption(
    "Dica: você pode rodar esta calculadora no notebook ou celular e ajustar os números "
    "ao vivo na frente do cliente."
)
