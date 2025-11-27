import streamlit as st
import math
from fpdf import FPDF

# --------------------------
# Configuração da página
# --------------------------
st.set_page_config(
    page_title="Calculadora de Economia – Energia Verde",
    page_icon="⚡",
    layout="centered"
)

# --------------------------
# Título / Cabeçalho
# --------------------------
st.markdown(
    """
    <h1 style="text-align:center; margin-bottom:0;">⚡ Calculadora de Economia – Energia Verde</h1>
    <p style="text-align:center; font-size:16px; color:#555;">
        Ferramenta para o time comercial mostrar, em poucos segundos, 
        a economia financeira e o impacto ambiental da energia verde.
    </p>
    <hr>
    """,
    unsafe_allow_html=True
)

# --------------------------
# Sidebar – parâmetros de entrada
# --------------------------
st.sidebar.header("📥 Dados do Cliente")

valor_conta = st.sidebar.number_input(
    "Valor atual da conta de luz (R$)",
    min_value=0.0,
    value=1500.0,
    step=50.0,
    format="%.2f",
    help="Informe o valor TOTAL médio da fatura de energia do cliente."
)

desconto_percent = st.sidebar.slider(
    "% de desconto na energia consumida",
    min_value=0,
    max_value=30,
    value=15,
    step=1,
    help="Por padrão 15%, mas pode ajustar conforme a proposta comercial."
)

cobertura_percent = st.sidebar.slider(
    "% da conta coberta pela energia verde",
    min_value=0,
    max_value=100,
    value=80,
    step=5,
    help="Normalmente usamos 80% porque ~20% é custo fixo da distribuidora."
)

periodo_meses = st.sidebar.number_input(
    "Período para simulação (meses)",
    min_value=1,
    value=12,
    step=1
)

tarifa_media = st.sidebar.number_input(
    "Tarifa média (R$/kWh)",
    min_value=0.10,
    value=0.95,
    step=0.05,
    format="%.2f",
    help="Estimativa do valor médio do kWh na região do cliente."
)

st.sidebar.markdown("---")
st.sidebar.caption("Preencha os dados e veja o resultado em tempo real na tela principal.")

# --------------------------
# Parâmetros de CO₂ (ajustáveis)
# --------------------------
with st.expander("🌱 Parâmetros de CO₂ (avançado)"):
    st.write(
        "Aqui usamos fatores médios de emissão para ilustrar o impacto ambiental. "
        "Esses valores podem ser ajustados conforme estudos ou inventários (ex.: GHG Protocol)."
    )
    fator_convencional = st.number_input(
        "Fator de emissão da energia convencional (kg CO₂e / kWh)",
        min_value=0.0,
        value=0.40,  # Exemplo genérico
        step=0.05
    )
    fator_energia_verde = st.number_input(
        "Fator de emissão da energia verde (kg CO₂e / kWh)",
        min_value=0.0,
        value=0.05,  # Exemplo genérico
        step=0.01
    )

# --------------------------
# Cálculos principais
# --------------------------

# Parte variável da conta (80% do total)
parte_variavel = valor_conta * 0.8

# Economia mensal em R$
economia_mensal = parte_variavel * (desconto_percent / 100) * (cobertura_percent / 100)

# Nova conta estimada
nova_conta = valor_conta - economia_mensal

# Economia total no período
economia_periodo = economia_mensal * periodo_meses

# Estimativa de consumo em kWh (parte variável / tarifa média)
if tarifa_media > 0:
    kwh_consumidos = parte_variavel / tarifa_media
else:
    kwh_consumidos = 0.0

# kWh economizados (considerando desconto e cobertura)
kwh_economizados = kwh_consumidos * (desconto_percent / 100) * (cobertura_percent / 100)

# CO₂ evitado (comparando energia convencional vs verde)
co2_convencional_kg = kwh_economizados * fator_convencional
co2_verde_kg = kwh_economizados * fator_energia_verde
co2_evitar_kg = max(co2_convencional_kg - co2_verde_kg, 0)
co2_evitar_t = co2_evitar_kg / 1000  # toneladas

# --------------------------
# Layout de resultados
# --------------------------

col1, col2, col3 = st.columns(3)

def formata_reais(valor: float) -> str:
    texto = f"R$ {valor:,.2f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")

with col1:
    st.metric(
        "Economia mensal estimada",
        formata_reais(economia_mensal),
    )

with col2:
    st.metric(
        f"Economia em {periodo_meses} meses",
        formata_reais(economia_periodo),
    )

with col3:
    st.metric(
        "Nova conta aproximada",
        formata_reais(nova_conta),
    )

st.markdown("---")

col4, col5 = st.columns(2)

with col4:
    st.subheader("💰 Resumo financeiro")
    st.write(
        f"- Valor atual da conta: **{formata_reais(valor_conta)}**\n"
        f"- Parte variável considerada (80%): **{formata_reais(parte_variavel)}**\n"
        f"- Desconto aplicado: **{desconto_percent}%**\n"
        f"- Cobertura de energia verde: **{cobertura_percent}% da conta**\n"
        f"- Economia mensal estimada: **{formata_reais(economia_mensal)}**\n"
        f"- Economia em **{periodo_meses} meses**: **{formata_reais(economia_periodo)}**\n"
        f"- Nova conta aproximada: **{formata_reais(nova_conta)}**"
    )

with col5:
    st.subheader("🌎 Impacto ambiental (estimado)")
    st.write(
        f"- Consumo estimado (parte variável): **{kwh_consumidos:,.0f} kWh/mês**\n"
        f"- kWh economizados com energia verde: **{kwh_economizados:,.0f} kWh/mês**\n"
        f"- CO₂ evitado por mês: **{co2_evitar_kg:,.1f} kg CO₂e**\n"
        f"- CO₂ evitado em {periodo_meses} meses: **{co2_evitar_t * periodo_meses:,.2f} t CO₂e**"
    )

st.info(
    "🔍 **Observação:** os fatores de emissão usados são aproximados. "
    "Para relatórios oficiais (ex.: inventário GHG Protocol), use fatores aprovados "
    "e ajustados à fonte de energia e à região do cliente."
)

st.markdown("---")

# --------------------------
# Geração de relatório em PDF
# --------------------------

def gerar_pdf(
    valor_conta,
    desconto_percent,
    cobertura_percent,
    periodo_meses,
    tarifa_media,
    economia_mensal,
    economia_periodo,
    nova_conta,
    kwh_consumidos,
    kwh_economizados,
    co2_evitar_t,
):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Relatorio - Calculadora de Energia Verde", ln=True)

    pdf.set_font("Helvetica", "", 12)
    pdf.ln(5)
    pdf.multi_cell(
        0, 7,
        "Este relatorio apresenta a estimativa de economia financeira e impacto "
        "ambiental relacionados à contratacao de energia verde."
    )

    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "Dados informados", ln=True)

    pdf.set_font("Helvetica", "", 12)
    pdf.multi_cell(
        0, 7,
        f"• Valor atual da conta: R$ {valor_conta:,.2f}\n"
        f"• Desconto na energia consumida: {desconto_percent}%\n"
        f"• Cobertura de energia verde: {cobertura_percent}% da conta\n"
        f"• Periodo considerado: {periodo_meses} meses\n"
        f"• Tarifa media estimada: R$ {tarifa_media:.2f} / kWh\n"
    )

    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "Resultados financeiros", ln=True)

    pdf.set_font("Helvetica", "", 12)
    pdf.multi_cell(
        0, 7,
        f"• Economia mensal estimada: R$ {economia_mensal:,.2f}\n"
        f"• Economia acumulada em {periodo_meses} meses: R$ {economia_periodo:,.2f}\n"
        f"• Nova conta aproximada: R$ {nova_conta:,.2f}\n"
    )

    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "Impacto ambiental estimado", ln=True)

    pdf.set_font("Helvetica", "", 12)
    pdf.multi_cell(
        0, 7,
        f"• Consumo estimado (parte variavel): {kwh_consumidos:,.0f} kWh/mês\n"
        f"• kWh economizados com energia verde: {kwh_economizados:,.0f} kWh/mês\n"
        f"• CO2 evitado em {periodo_meses} meses: {co2_evitar_t * periodo_meses:,.2f} t CO2e\n"
        "\n"
        "Importante: estes valores sao estimativas com base em fatores medios de emissao. "
        "Para relatorios corporativos oficiais (ex.: GHG Protocol), e recomendado usar "
        "fatores de emissao atualizados e validados para a regiao e a fonte de energia."
    )

    return pdf.output(dest="S").encode("latin-1")


st.subheader("📄 Relatório em PDF")

st.write(
    "Clique no botão abaixo para baixar um relatório em PDF com o resumo da economia "
    "financeira e do impacto ambiental estimado para este cliente."
)

pdf_bytes = gerar_pdf(
    valor_conta,
    desconto_percent,
    cobertura_percent,
    periodo_meses,
    tarifa_media,
    economia_mensal,
    economia_periodo,
    nova_conta,
    kwh_consumidos,
    kwh_economizados,
    co2_evitar_t,
)

st.download_button(
    label="📥 Baixar relatório em PDF",
    data=pdf_bytes,
    file_name="relatorio_energia_verde.pdf",
    mime="application/pdf",
)
