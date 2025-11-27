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
    .header-text {
        display: flex;
        flex-direction: column;
        gap: 0.2rem;
    }
    .header-title {
        font-size: 32px;
        font-weight: 700;
        line-height: 1.2;
        margin: 0;
    }
    .header-subtitle {
        font-size: 15px;
        line-height: 1.4;
        margin: 0;
    }
    @media (max-width: 768px) {
        .header-title {
            font-size: 28px;
        }
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


def texto_pdf_safe(texto: str) -> str:
    """
    Remove caracteres que não são suportados pelo encoding Latin-1 do FPDF.
    Evita FPDFUnicodeEncodingException.
    """
    return texto.encode("latin-1", "ignore").decode("latin-1")


def gerar_relatorio_pdf(dados: dict) -> bytes:
    """
    Gera um PDF em memória com o resumo da simulação.
    Usa apenas caracteres compatíveis com Latin-1.
    """
    pdf = FPDF()
    # Mantém tudo em uma página para evitar que o rodapé seja empurrado
    # para uma segunda folha.
    pdf.set_auto_page_break(auto=False)
    pdf.add_page()

    # Logo Prospera (canto superior direito)
    try:
        pdf.image("prospera_logo.png", x=170, y=10, w=25)
    except Exception:
        # Se não encontrar o logo, não quebra o PDF
        pass

    # Título
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 12, texto_pdf_safe("Calculadora de Economia - Energia Verde"), ln=True)

    # Subtítulo
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(
        pdf.epw,
        6,
        texto_pdf_safe(
            "Resumo da economia financeira e do impacto ambiental estimado para este cliente."
        ),
    )
    pdf.ln(4)

    def bloco_titulo(texto: str):
        pdf.set_font("Arial", "B", 13)
        pdf.cell(0, 8, texto_pdf_safe(texto), ln=True)
        pdf.set_line_width(0.2)
        pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
        pdf.ln(3)

    def linha_rotulo_valor(rotulo: str, valor: str):
        pdf.set_font("Arial", "", 12)
        pdf.cell(70, 8, texto_pdf_safe(rotulo), ln=0)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, texto_pdf_safe(valor), ln=1)

    # Resumo da simulação
    bloco_titulo("Resumo da simulacao")
    linha_rotulo_valor("Conta atual", dados["valor_conta"])
    linha_rotulo_valor("Nova conta aproximada", dados["nova_conta"])
    linha_rotulo_valor("Economia mensal", dados["economia_mensal"])
    linha_rotulo_valor(
        f"Economia em {dados['periodo_meses']} meses", dados["economia_periodo"]
    )
    linha_rotulo_valor("Pontos Ecoa gerados/mês", dados["pontos_ecoa_mes"])
    linha_rotulo_valor(
        "Pontos para zerar a conta", dados["pontos_para_zerar_conta"]
    )
    linha_rotulo_valor(
        "Pontos adicionais necessários", dados["pontos_faltantes_para_zerar"]
    )
    pdf.ln(4)

    # Parâmetros financeiros
    bloco_titulo("Parametros financeiros")
    linha_rotulo_valor("Desconto aplicado", f"{dados['desconto']}%")
    linha_rotulo_valor(
        "Cobertura energia verde", f"{dados['cobertura']}% da conta"
    )
    linha_rotulo_valor(
        "Parte variavel considerada", f"{dados['parte_variavel']}% da conta"
    )
    pdf.ln(4)

    # Impacto ambiental
    bloco_titulo("Impacto ambiental estimado")
    linha_rotulo_valor(
        "Fator de emissao adotado",
        f"{dados['fator_co2']} kg CO2e/kWh",
    )
    linha_rotulo_valor(
        f"CO2 evitado em {dados['periodo_meses']} meses",
        f"{dados['co2_periodo_t']} t CO2e",
    )
    pdf.ln(6)

    # Observação
    pdf.set_font("Arial", "I", 10)
    pdf.multi_cell(
        pdf.epw,
        5.5,
        texto_pdf_safe(
            "Simulacao estimada. Metodologia: kWh economizados x fator de emissao "
            "(kg CO2e/kWh), convertendo para toneladas. Para inventarios oficiais "
            "(GHG Protocol Escopo 2, abordagens location-based/market-based), "
            "use fatores aprovados da regiao e da fonte de energia do cliente."
        ),
    )

    # Rodapé
    pdf.set_y(-18)
    pdf.set_font("Arial", "I", 8)
    pdf.set_text_color(100)
    pdf.cell(
        0,
        8,
        texto_pdf_safe("By Tech Team Prospera / Sales Team"),
        ln=True,
        align="C",
    )

    # Retorna bytes do PDF
    pdf_bytes = pdf.output(dest="S")
    return bytes(pdf_bytes)


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

# ----------------- PARÂMETROS DE CO₂ (AVANÇADO) -----------------
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
# Parte variável considerada (100% da conta) para aplicar o desconto corretamente
parte_variavel_percent = 100
valor_parte_variavel = valor_conta * (parte_variavel_percent / 100)

# Parte da conta coberta pela energia verde (em R$)
valor_coberto_verde = valor_conta * (cobertura_percent / 100)

# Economia mensal em R$ (desconto sobre a parte coberta pela energia verde)
economia_mensal = valor_coberto_verde * (desconto_percent / 100)

# Economia total no período
economia_total_periodo = economia_mensal * periodo_meses

# Nova conta aproximada
nova_conta = max(valor_conta - economia_mensal, 0)

# Pontos Ecoa (cada R$ 0,03 de economia mensal = 1 ponto)
valor_ponto_ecoa = 0.03
pontos_ecoa_mes = economia_mensal / valor_ponto_ecoa if valor_ponto_ecoa else 0
pontos_para_zerar_conta = valor_conta / valor_ponto_ecoa if valor_ponto_ecoa else 0
pontos_faltantes_para_zerar = max(pontos_para_zerar_conta - pontos_ecoa_mes, 0)

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
header_col1, header_col2 = st.columns([5, 1])

with header_col1:
    st.markdown(
        """
        <div class="header-text">
            <div class="header-title">⚡ Calculadora de Economia – Energia Verde</div>
            <div class="header-subtitle">
                Ferramenta para o time comercial mostrar, em poucos segundos,
                a economia financeira e o impacto ambiental da energia verde.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with header_col2:
    st.image("prospera_logo.png", width=120)

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

col4, col5, col6 = st.columns(3)
with col4:
    st.markdown("**Pontos Ecoa gerados/mês**")
    st.markdown(
        f"<div class='big-metric'>{format_number_br(pontos_ecoa_mes, 0)}</div>",
        unsafe_allow_html=True,
    )
with col5:
    st.markdown("**Pontos necessários para zerar a conta**")
    st.markdown(
        f"<div class='big-metric'>{format_number_br(pontos_para_zerar_conta, 0)}</div>",
        unsafe_allow_html=True,
    )
with col6:
    st.markdown("**Pontos adicionais para zerar**")
    st.markdown(
        f"<div class='big-metric'>{format_number_br(pontos_faltantes_para_zerar, 0)}</div>",
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
        - Pontos Ecoa gerados/mês: **{format_number_br(pontos_ecoa_mes, 0)} pontos**
        - Pontos necessários para zerar a conta: **{format_number_br(pontos_para_zerar_conta, 0)} pontos**
        - Pontos adicionais para zerar: **{format_number_br(pontos_faltantes_para_zerar, 0)} pontos**
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
    "⚠️ **Importante:** metodologia de CO₂: kWh economizados x fator de emissão "
    "(kg CO₂e/kWh), convertido para toneladas, alinhado ao GHG Protocol para "
    "escopo 2 (location-based ou market-based). Use fatores oficiais da "
    "distribuidora/região para relatórios formais."
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
    "pontos_ecoa_mes": format_number_br(pontos_ecoa_mes, 0),
    "pontos_para_zerar_conta": format_number_br(pontos_para_zerar_conta, 0),
    "pontos_faltantes_para_zerar": format_number_br(
        pontos_faltantes_para_zerar, 0
    ),
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
