import streamlit as st
from fpdf import FPDF

# ----------------- CONFIGURAÇÃO BÁSICA -----------------
st.set_page_config(
    page_title="Calculadora de Economia – Energia Verde",
    page_icon="⚡",
    layout="wide",
)

# Estilo simples para deixar mais bonito
st.markdown(
    """
    <style>
    .big-metric {
        font-size: 32px;
        font-weight: 700;
    }
    .section-title {
        font-size: 24px;
        font-weight: 700;
        margin-top: 1rem;
    }
    .subsection-title {
        font-size: 18px;
        font-weight: 600;
        margin-top: 0.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ----------------- FUNÇÕES AUXILIARES -----------------
def format_currency_br(valor: float) -> str:
    """Formata número em formato de moeda brasileira: R$ 1.234,56"""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def format_number_br(valor: float, decimals: int = 0) -> str:
    fmt = f"{{:,.{decimals}f}}"
    return fmt.format(valor).replace(",", "X").replace(".", ",").replace("X", ".")


def gerar_relatorio_pdf(dados: dict) -> bytes:
    """
    Gera um PDF em memória com o resumo da simulação.
    Usa apenas caracteres compatíveis com Latin-1 (sem emojis/CO₂ subscrito).
    """
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Logo Prospera (canto superior direito)
    try:
        # coordenadas em mm (padrão FPDF, página A4 ~ 210 x 297 mm)
        pdf.image("prospera_logo.png", x=165, y=8, w=30)
    except Exception:
        # se não encontrar o logo, continua sem quebrar
        pass

    # Título
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Calculadora de Economia - Energia Verde", ln=True)
    pdf.ln(2)

    # Subtítulo
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(
        0,
        6,
        "Resumo da economia financeira e do impacto ambiental estimado para este cliente.",
    )
    pdf.ln(4)

    # Dados principais
    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 8, "Resumo da simulacao", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 7, f"Conta atual: {dados['valor_conta']}", ln=True)
    pdf.cell(0, 7, f"Nova conta aproximada: {dados['nova_conta']}", ln=True)
    pdf.ln(2)
    pdf.cell(0, 7, f"Economia mensal estimada: {dados['economia_mensal']}", ln=True)
    pdf.cell(
        0,
        7,
        f"Economia em {dados['periodo_meses']} meses: {dados['economia_periodo']}",
        ln=True,
    )
    pdf.ln(6)

    # Parametros financeiros
    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 8, "Parametros financeiros", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(
        0,
        6,
        f"- Desconto aplicado: {dados['desconto']}%",
    )
    pdf.multi_cell(
        0,
        6,
        f"- Cobertura de energia verde: {dados['cobertura']}% da conta",
    )
    pdf.multi_cell(
        0,
        6,
        f"- Parte variavel considerada: {dados['parte_variavel']}% da conta",
    )
    pdf.ln(4)

    # Impacto ambiental
    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 8, "Impacto ambiental estimado", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(
        0,
        6,
        f"- Fator de emissao adotado: {dados['fator_co2']} kg CO2e/kWh",
    )
    pdf.multi_cell(
        0,
        6,
        f"- CO2 evitado em {dados['periodo_meses']} meses: {dados['co2_periodo_t']} t CO2e",
    )
    pdf.ln(6)

    # Observacao
    pdf.set_font("Arial", "I", 11)
    pdf.multi_cell(
        0,
        6,
        "Simulacao estimada. Para inventarios oficiais (GHG Protocol), "
        "use fatores de emissao oficiais da regiao e da fonte de energia do cliente.",
    )

    # Retorna bytes do PDF
    pdf_bytes = pdf.output(dest="S").encode("latin-1")
    return pdf_bytes


# ----------------- SIDEBAR – ENTRADAS -----------------
st.sidebar.title("📊 Dados do Cliente")

valor_conta = st.sidebar.number_input(
    "Valor atual da conta de luz (R$)",
    min_value=0.0,
    value=1500.0,
    step=50.0,
)

desconto_percent = st.sidebar.slider(
    "% de desconto na energia consumida",
    min_value=0,
    max_value=100,
    value=15,
    step=1,
)

cobertura_percent = st.sidebar.slider(
    "% da conta coberta pela energia verde",
    min_value=0,
    max_value=100,
    value=80,
    step=5,
)

periodo_meses = st.sidebar.number_input(
    "Período para simulação (meses)",
    min_value=1,
    max_value=60,
    value=12,
    step=1,
)

tarifa_media = st.sidebar.number_input(
    "Tarifa média (R$/kWh)",
    min_value=0.01,
    value=0.95,
    step=0.01,
)

st.sidebar.markdown(
    """
    _Preencha os dados e veja o resultado em tempo real na tela principal._
    """
)

# ----------------- PARÂMETROS DE CO2 (AVANÇADO) -----------------
with st.expander("🌱 Parâmetros de CO₂ (avançado)", expanded=False):
    st.markdown(
        """
        Aqui você define o **fator de emissão da energia da rede**.

        - Use um valor de **kg CO₂e por kWh** consumido da rede.
        - Para relatórios alinhados ao **GHG Protocol**, utilize o fator oficial
          da distribuidora/região (escopo 2, abordagem location-based ou market-based).
        """
    )

    fator_emissao_kg_kwh = st.number_input(
        "Fator de emissão da rede (kg CO₂e/kWh)",
        min_value=0.0,
        value=0.35,  # valor ilustrativo; ajuste conforme sua realidade/fornecedor
        step=0.01,
    )

# ----------------- CÁLCULOS -----------------
# Parte variável considerada (ex.: 80% da conta)
parte_variavel_percent = 80
valor_parte_variavel = valor_conta * (parte_variavel_percent / 100)

# Parte da conta coberta pela energia verde (em R$)
valor_coberto_verde = valor_parte_variavel * (cobertura_percent / 100)

# Economia mensal em R$ (desconto sobre a parte coberta pela energia verde)
economia_mensal = valor_coberto_verde * (desconto_percent / 100)

# Economia total no período
economia_total_periodo = economia_mensal * periodo_meses

# Nova conta aproximada
nova_conta = max(valor_conta - economia_mensal, 0)

# Consumo estimado (kWh/mês) da parte variável
if tarifa_media > 0:
    consumo_kwh_mes = valor_parte_variavel / tarifa_media
    kwh_economizados_mes = economia_mensal / tarifa_media
else:
    consumo_kwh_mes = 0.0
    kwh_economizados_mes = 0.0

# CO2 evitado (kg e toneladas)
co2_evitado_kg_mes = kwh_economizados_mes * fator_emissao_kg_kwh
co2_evitado_kg_periodo = co2_evitado_kg_mes * periodo_meses
co2_evitado_t_periodo = co2_evitado_kg_periodo / 1000


# ----------------- TÍTULO E RESUMO PRINCIPAL -----------------
st.title("⚡ Calculadora de Economia – Energia Verde")
st.write(
    "Ferramenta para o time comercial mostrar, em poucos segundos, "
    "a economia financeira e o impacto ambiental da energia verde."
)

st.markdown("---")

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("**Economia mensal estimada**")
    st.markdown(
        f"<div class='big-metric'>{format_currency_br(economia_mensal)}</div>",
        unsafe_allow_html=True,
    )
with col2:
    st.markdown(f"**Economia em {periodo_meses} meses**")
    st.markdown(
        f"<div class='big-metric'>{format_currency_br(economia_total_periodo)}</div>",
        unsafe_allow_html=True,
    )
with col3:
    st.markdown("**Nova conta aproximada**")
    st.markdown(
        f"<div class='big-metric'>{format_currency_br(nova_conta)}</div>",
        unsafe_allow_html=True,
    )

st.markdown("---")

# ----------------- DETALHAMENTO – RESUMO FINANCEIRO & IMPACTO -----------------
col_fin, col_amb = st.columns(2)

with col_fin:
    st.markdown("### 💰 Resumo financeiro")
    st.markdown(
        f"""
        - Valor atual da conta: **{format_currency_br(valor_conta)}**
        - Parte variável considerada ({parte_variavel_percent}%): **{format_currency_br(valor_parte_variavel)}**
        - Desconto aplicado: **{desconto_percent}%**
        - Cobertura de energia verde: **{cobertura_percent}% da conta**
        - Economia mensal estimada: **{format_currency_br(economia_mensal)}**
        - Economia em {periodo_meses} meses: **{format_currency_br(economia_total_periodo)}**
        - Nova conta aproximada: **{format_currency_br(nova_conta)}**
        """
    )

with col_amb:
    st.markdown("### 🌍 Impacto ambiental (estimado)")
    st.markdown(
        f"""
        - Consumo estimado (parte variável): **{format_number_br(consumo_kwh_mes, 0)} kWh/mês**
        - kWh economizados com energia verde: **{format_number_br(kwh_economizados_mes, 0)} kWh/mês**
        - Fator de emissão adotado: **{format_number_br(fator_emissao_kg_kwh, 2)} kg CO₂e/kWh**
        - CO₂ evitado por mês: **{format_number_br(co2_evitado_kg_mes, 1)} kg CO₂e**
        - CO₂ evitado em {periodo_meses} meses: **{format_number_br(co2_evitado_t_periodo, 2)} t CO₂e**
        """
    )

st.info(
    "⚠️ **Importante:** os fatores de emissão usados são aproximados. "
    "Para relatórios oficiais (ex.: inventário GHG Protocol), utilize fatores "
    "aprovados e ajustados à fonte de energia e à região do cliente."
)

# ----------------- RELATÓRIO EM PDF -----------------
st.markdown("---")
st.markdown("### 📄 Relatório em PDF")

st.write(
    "Clique no botão abaixo para gerar um **PDF com o resumo da simulação**, "
    "incluindo logo da Prospera. Você pode enviar esse PDF diretamente pelo WhatsApp."
)

dados_para_pdf = {
    "valor_conta": format_currency_br(valor_conta),
    "nova_conta": format_currency_br(nova_conta),
    "economia_mensal": format_currency_br(economia_mensal),
    "economia_periodo": format_currency_br(economia_total_periodo),
    "periodo_meses": periodo_meses,
    "desconto": desconto_percent,
    "cobertura": cobertura_percent,
    "parte_variavel": parte_variavel_percent,
    "fator_co2": format_number_br(fator_emissao_kg_kwh, 2),
    "co2_periodo_t": format_number_br(co2_evitado_t_periodo, 2),
}

if st.button("Gerar relatório em PDF"):
    pdf_bytes = gerar_relatorio_pdf(dados_para_pdf)

    st.download_button(
        label="⬇️ Baixar relatório (PDF)",
        data=pdf_bytes,
        file_name="relatorio_energia_verde_prospera.pdf",
        mime="application/pdf",
    )
