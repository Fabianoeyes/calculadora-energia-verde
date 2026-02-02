import base64
import tempfile
from io import BytesIO

import streamlit as st
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFont

# ----------------- CONFIGURAÇÃO BÁSICA -----------------
st.set_page_config(
    page_title="Calculadora de Economia - Programa de Pontos & Desconto na Conta de Luz",
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
    .header-row {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: 1.5rem;
    }
    .header-title {
        font-size: 32px;
        font-weight: 700;
        line-height: 1.2;
        margin: 0;
    }
    .header-subtitle {
        font-size: 20px;
        font-weight: 600;
        line-height: 1.3;
        margin: 0;
    }
    .header-logo {
        height: 48px;
        margin-top: 2px;
    }
    @media (max-width: 768px) {
        .header-title {
            font-size: 28px;
        }
        .header-subtitle {
            font-size: 18px;
        }
        .header-logo {
            height: 42px;
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


def gerar_logo_soul_up() -> tuple[str, str]:
    largura, altura = 1200, 400
    fundo = (255, 255, 255)
    verde = (46, 174, 182)

    imagem = Image.new("RGB", (largura, altura), fundo)
    desenho = ImageDraw.Draw(imagem)

    fonte_principal = ImageFont.truetype("DejaVuSans-Bold.ttf", 180)
    fonte_icone = ImageFont.truetype("DejaVuSans-Bold.ttf", 90)

    texto = "soul"
    texto_largura, texto_altura = desenho.textbbox((0, 0), texto, font=fonte_principal)[
        2:
    ]
    texto_x = 40
    texto_y = (altura - texto_altura) // 2 - 10

    desenho.text((texto_x, texto_y), texto, fill=verde, font=fonte_principal)

    diametro = 160
    espacamento = 20
    inicio_x = texto_x + texto_largura + 40
    inicio_y = (altura - diametro) // 2

    for indice in range(3):
        x0 = inicio_x + indice * (diametro + espacamento)
        y0 = inicio_y
        x1 = x0 + diametro
        y1 = y0 + diametro
        desenho.ellipse([x0, y0, x1, y1], outline=verde, width=12)

    texto_up = "up"
    up_largura, up_altura = desenho.textbbox((0, 0), texto_up, font=fonte_icone)[2:]
    up_x = inicio_x + (diametro - up_largura) // 2
    up_y = inicio_y + (diametro - up_altura) // 2 - 5
    desenho.text((up_x, up_y), texto_up, fill=verde, font=fonte_icone)

    centro_folha_x = inicio_x + (diametro + espacamento) + diametro // 2
    centro_folha_y = inicio_y + diametro // 2
    folha_largura = 60
    folha_altura = 80

    desenho.polygon(
        [
            (centro_folha_x, centro_folha_y - folha_altura // 2),
            (centro_folha_x - folha_largura, centro_folha_y),
            (centro_folha_x, centro_folha_y + folha_altura // 2),
        ],
        outline=verde,
    )
    desenho.polygon(
        [
            (centro_folha_x, centro_folha_y - folha_altura // 2),
            (centro_folha_x + folha_largura, centro_folha_y),
            (centro_folha_x, centro_folha_y + folha_altura // 2),
        ],
        outline=verde,
    )
    desenho.line(
        [
            (centro_folha_x, centro_folha_y - folha_altura // 2),
            (centro_folha_x, centro_folha_y + folha_altura // 2),
        ],
        fill=verde,
        width=6,
    )

    centro_planeta_x = inicio_x + 2 * (diametro + espacamento) + diametro // 2
    centro_planeta_y = centro_folha_y
    raio_planeta = 45

    desenho.ellipse(
        [
            (centro_planeta_x - raio_planeta, centro_planeta_y - raio_planeta),
            (centro_planeta_x + raio_planeta, centro_planeta_y + raio_planeta),
        ],
        outline=verde,
        width=6,
    )
    for offset in (-18, 0, 18):
        desenho.arc(
            [
                centro_planeta_x - raio_planeta + offset,
                centro_planeta_y - raio_planeta,
                centro_planeta_x + raio_planeta + offset,
                centro_planeta_y + raio_planeta,
            ],
            start=90,
            end=270,
            fill=verde,
            width=4,
        )
    for offset in (-18, 0, 18):
        desenho.arc(
            [
                centro_planeta_x - raio_planeta,
                centro_planeta_y - raio_planeta + offset,
                centro_planeta_x + raio_planeta,
                centro_planeta_y + raio_planeta + offset,
            ],
            start=0,
            end=180,
            fill=verde,
            width=4,
        )

    buffer = BytesIO()
    imagem.save(buffer, format="PNG")
    dados_imagem = buffer.getvalue()
    logo_base64 = base64.b64encode(dados_imagem).decode("utf-8")

    arquivo_temporario = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    arquivo_temporario.write(dados_imagem)
    arquivo_temporario.close()

    return logo_base64, arquivo_temporario.name


def gerar_relatorio_pdf(dados: dict, logo_path: str) -> bytes:
    """
    Gera um PDF em memória com o resumo da simulação.
    Usa apenas caracteres compatíveis com Latin-1.
    """
    pdf = FPDF()
    # Mantém tudo em uma página para evitar que o rodapé seja empurrado
    # para uma segunda folha.
    pdf.set_auto_page_break(auto=False)
    pdf.add_page()

    # Logo Soul Up (canto superior direito)
    try:
        pdf.image(logo_path, x=155, y=8, w=40)
    except Exception:
        # Se não encontrar o logo, não quebra o PDF
        pass

    # Título
    pdf.set_font("Arial", "B", 16)
    pdf.cell(
        0,
        12,
        texto_pdf_safe(
            "Calculadora de Economia - Programa de Pontos & Desconto na Conta de Luz"
        ),
        ln=True,
    )

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
    bloco_titulo("Resumo da Simulação")
    linha_rotulo_valor("Valor da conta atual", dados["valor_conta"])
    linha_rotulo_valor(
        "Valor da nova conta da distribuidora", dados["nova_conta_distribuidora"]
    )
    linha_rotulo_valor("Valor da conta Soul Up", dados["conta_soul_up"])
    linha_rotulo_valor("Nova conta aproximada", dados["nova_conta"])
    linha_rotulo_valor("Economia mensal", dados["economia_mensal"])
    linha_rotulo_valor(
        f"Economia em {dados['periodo_meses']} meses", dados["economia_periodo"]
    )
    linha_rotulo_valor("Pontos Ecoa gerados/mês", dados["pontos_ecoa_mes"])
    linha_rotulo_valor(
        "Pontos adicionais necessários para 100% da conta",
        dados["pontos_faltantes_para_zerar"],
    )
    pdf.ln(4)

    # Parâmetros financeiros
    bloco_titulo("Parâmetros Financeiros")
    linha_rotulo_valor("Desconto aplicado", f"{dados['desconto']}%")
    linha_rotulo_valor(
        "Cobertura de energia verde", f"{dados['cobertura']}% da conta"
    )
    pdf.ln(4)

    # Impacto ambiental
    bloco_titulo("Impacto Ambiental Estimado")
    linha_rotulo_valor(
        "Fator de emissão adotado",
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
            "Simulação estimada. Metodologia: kWh economizados x fator de emissão "
            "(kg CO2e/kWh), convertendo para toneladas. Para inventários oficiais "
            "(GHG Protocol Escopo 2, abordagens location-based/market-based), "
            "use fatores aprovados da região e da fonte de energia do cliente."
        ),
    )

    # Rodapé
    pdf.set_y(-18)
    pdf.set_font("Arial", "I", 8)
    pdf.set_text_color(100)
    pdf.cell(
        0,
        8,
        texto_pdf_safe("By Tech Team Soul Up / Sales Team"),
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

percentual_distribuidora = 20
percentual_soul_up = 80
cobertura_percent = percentual_soul_up

periodo_meses = st.sidebar.number_input(
    "Período para simulação (meses)",
    min_value=1,
    max_value=60,
    value=12,
    step=1,
)

st.sidebar.markdown(
    """
    _Preencha os dados e veja o resultado em tempo real na tela principal._
    """
)
st.sidebar.markdown(
    f"**Distribuidora:** {percentual_distribuidora}% da conta  \n"
    f"**Conta Soul Up:** {percentual_soul_up}% da conta"
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
# Tarifa média fixa para estimativas internas (R$/kWh)
tarifa_media = 0.95

# Valores baseados na conta atual
valor_nova_conta_distribuidora = valor_conta * (percentual_distribuidora / 100)
valor_conta_soul_up = (
    valor_conta
    * (percentual_soul_up / 100)
    * (1 - desconto_percent / 100)
)

# Nova conta aproximada (distribuidora + Soul Up)
nova_conta = max(valor_nova_conta_distribuidora + valor_conta_soul_up, 0)

# Economia mensal em R$
economia_mensal = max(valor_conta - nova_conta, 0)

# Economia total no período
economia_total_periodo = economia_mensal * periodo_meses

# Pontos Ecoa (cada R$ 0,009 de economia mensal = 1 ponto)
valor_ponto_ecoa = 0.009
pontos_ecoa_mes = economia_mensal / valor_ponto_ecoa if valor_ponto_ecoa else 0
pontos_para_zerar_conta = valor_conta / valor_ponto_ecoa if valor_ponto_ecoa else 0
pontos_faltantes_para_zerar = max(pontos_para_zerar_conta - pontos_ecoa_mes, 0)

# Consumo estimado (kWh/mês) da parte variável
if tarifa_media > 0:
    consumo_kwh_mes = valor_conta / tarifa_media
    kwh_economizados_mes = economia_mensal / tarifa_media
else:
    consumo_kwh_mes = 0.0
    kwh_economizados_mes = 0.0

# CO2 evitado (kg e toneladas)
co2_evitado_kg_mes = kwh_economizados_mes * fator_emissao_kg_kwh
co2_evitado_kg_periodo = co2_evitado_kg_mes * periodo_meses
co2_evitado_t_periodo = co2_evitado_kg_periodo / 1000


# ----------------- TÍTULO E RESUMO PRINCIPAL -----------------
logo_base64, logo_path = gerar_logo_soul_up()
st.markdown(
    f"""
    <div class="header-row">
        <div class="header-text">
            <div class="header-title">⚡ Calculadora de Economia</div>
            <div class="header-subtitle">Programa de Pontos &amp; Desconto na Conta de Luz</div>
        </div>
        <img src="data:image/png;base64,{logo_base64}" class="header-logo" alt="Logo Soul Up" />
    </div>
    """,
    unsafe_allow_html=True,
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

col4, col5 = st.columns(2)
with col4:
    st.markdown("**Pontos Ecoa gerados/mês**")
    st.markdown(
        f"<div class='big-metric'>{format_number_br(pontos_ecoa_mes, 0)}</div>",
        unsafe_allow_html=True,
    )
with col5:
    st.markdown("**Pontos adicionais necessários para 100% da conta**")
    st.markdown(
        f"<div class='big-metric'>{format_number_br(pontos_faltantes_para_zerar, 0)}</div>",
        unsafe_allow_html=True,
    )

st.markdown("---")

# ----------------- DETALHAMENTO – RESUMO FINANCEIRO & IMPACTO -----------------
col_fin, col_amb = st.columns(2)

with col_fin:
    st.markdown("### 💰 Resumo da Simulação")
    st.markdown(
        f"""
        - Valor da conta atual: **{format_currency_br(valor_conta)}**
        - Valor da nova conta da distribuidora: **{format_currency_br(valor_nova_conta_distribuidora)}**
        - Valor da conta Soul Up: **{format_currency_br(valor_conta_soul_up)}**
        - Nova conta aproximada: **{format_currency_br(nova_conta)}**
        - Economia mensal estimada: **{format_currency_br(economia_mensal)}**
        - Economia em {periodo_meses} meses: **{format_currency_br(economia_total_periodo)}**
        - Pontos Ecoa gerados/mês: **{format_number_br(pontos_ecoa_mes, 0)} pontos**
        - Pontos adicionais necessários para 100% da conta: **{format_number_br(pontos_faltantes_para_zerar, 0)} pontos**
        """
    )

with col_amb:
    st.markdown("### 🌍 Impacto Ambiental Estimado")
    st.markdown(
        f"""
        - Consumo estimado: **{format_number_br(consumo_kwh_mes, 0)} kWh/mês**
        - kWh economizados com energia verde: **{format_number_br(kwh_economizados_mes, 0)} kWh/mês**
        - Fator de emissão adotado: **{format_number_br(fator_emissao_kg_kwh, 2)} kg CO₂e/kWh**
        - CO₂ evitado por mês: **{format_number_br(co2_evitado_kg_mes, 1)} kg CO₂e**
        - CO₂ evitado em {periodo_meses} meses: **{format_number_br(co2_evitado_t_periodo, 2)} t CO₂e**
        """
    )

st.info(
    "⚠️ **Importante:** metodologia de CO₂: kWh economizados × fator de emissão "
    "(kg CO₂e/kWh), convertido para toneladas, alinhado ao GHG Protocol para "
    "escopo 2 (location-based ou market-based). Use fatores oficiais da "
    "distribuidora/região para relatórios formais."
)

# ----------------- RELATÓRIO EM PDF -----------------
st.markdown("---")
st.markdown("### 📄 Relatório em PDF")

st.write(
    "Clique no botão abaixo para gerar um **PDF com o resumo da simulação**, "
    "incluindo logo da Soul Up. Você pode enviar esse PDF diretamente pelo WhatsApp."
)

dados_para_pdf = {
    "valor_conta": format_currency_br(valor_conta),
    "nova_conta_distribuidora": format_currency_br(valor_nova_conta_distribuidora),
    "conta_soul_up": format_currency_br(valor_conta_soul_up),
    "nova_conta": format_currency_br(nova_conta),
    "economia_mensal": format_currency_br(economia_mensal),
    "economia_periodo": format_currency_br(economia_total_periodo),
    "periodo_meses": periodo_meses,
    "desconto": desconto_percent,
    "cobertura": cobertura_percent,
    "pontos_ecoa_mes": format_number_br(pontos_ecoa_mes, 0),
    "pontos_faltantes_para_zerar": format_number_br(
        pontos_faltantes_para_zerar, 0
    ),
    "fator_co2": format_number_br(fator_emissao_kg_kwh, 2),
    "co2_periodo_t": format_number_br(co2_evitado_t_periodo, 2),
}

if st.button("Gerar relatório em PDF"):
    pdf_bytes = gerar_relatorio_pdf(dados_para_pdf, logo_path)

    st.download_button(
        label="⬇️ Baixar relatório (PDF)",
        data=pdf_bytes,
        file_name="relatorio_programa_pontos_soul_up.pdf",
        mime="application/pdf",
    )
