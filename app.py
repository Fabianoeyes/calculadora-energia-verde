import streamlit as st
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

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


def gerar_imagem_resumo(dados: dict) -> bytes:
    """
    Gera uma imagem em formato de card (900x1200),
    com logo da Prospera e resumo da simulação.
    Ideal para enviar pelo WhatsApp.
    """
    # Tamanho do card
    largura, altura = 900, 1200
    bg_color = (15, 23, 42)     # fundo escuro
    text_color = (255, 255, 255)
    accent_color = (56, 189, 248)
    secondary_color = (148, 163, 184)

    img = Image.new("RGB", (largura, altura), bg_color)
    draw = ImageDraw.Draw(img)

    # Fontes
    try:
        font_title = ImageFont.truetype("DejaVuSans-Bold.ttf", 48)
        font_sub = ImageFont.truetype("DejaVuSans-Bold.ttf", 30)
        font_body = ImageFont.truetype("DejaVuSans.ttf", 26)
    except Exception:
        font_title = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        font_body = ImageFont.load_default()

    # --- Logo Prospera (canto superior direito) ---
    try:
        logo = Image.open("prospera_logo.png").convert("RGBA")
        logo_width = 140
        ratio = logo_width / logo.width
        logo = logo.resize((logo_width, int(logo.height * ratio)), Image.LANCZOS)

        pos_logo = (largura - logo_width - 40, 40)  # margem 40 px
        img.paste(logo, pos_logo, logo)
    except Exception:
        # Se não achar o logo, segue sem quebrar
        pass

    # --- Título ---
    titulo = "Calculadora de Economia – Energia Verde"
    x_titulo, y_titulo = 40, 60
    draw.text((x_titulo, y_titulo), titulo, font=font_title, fill=accent_color)

    # --- Bloco principal ---
    y = 160
    draw.text(
        (40, y),
        f"Conta atual: {dados['valor_conta']}",
        font=font_sub,
        fill=text_color,
    )
    y += 40
    draw.text(
        (40, y),
        f"Nova conta aproximada: {dados['nova_conta']}",
        font=font_sub,
        fill=text_color,
    )
    y += 70

    draw.text(
        (40, y),
        f"Economia mensal estimada: {dados['economia_mensal']}",
        font=font_body,
        fill=text_color,
    )
    y += 35
    draw.text(
        (40, y),
        f"Economia em {dados['periodo_meses']} meses: {dados['economia_periodo']}",
        font=font_body,
        fill=text_color,
    )
    y += 60

    # --- Parâmetros financeiros ---
    draw.text(
        (40, y),
        "Parâmetros financeiros:",
        font=font_sub,
        fill=accent_color,
    )
    y += 40
    draw.text(
        (40, y),
        f"- Desconto aplicado: {dados['desconto']}%",
        font=font_body,
        fill=text_color,
    )
    y += 30
    draw.text(
        (40, y),
        f"- Cobertura energia verde: {dados['cobertura']}% da conta",
        font=font_body,
        fill=text_color,
    )
    y += 30
    draw.text(
        (40, y),
        f"- Parte variável considerada: {dados['parte_variavel']}% da conta",
        font=font_body,
        fill=text_color,
    )
    y += 60

    # --- Impacto ambiental ---
    draw.text(
        (40, y),
        "Impacto ambiental estimado:",
        font=font_sub,
        fill=accent_color,
    )
    y += 40
    draw.text(
        (40, y),
        f"- Fator de emissão: {dados['fator_co2']} kg CO₂e/kWh",
        font=font_body,
        fill=text_color,
    )
    y += 30
    draw.text(
        (40, y),
        f"- CO₂ evitado em {dados['periodo_meses']} meses:",
        font=font_body,
        fill=text_color,
    )
    y += 30
    draw.text(
        (60, y),
        f"{dados['co2_periodo_t']} t CO₂e",
        font=font_body,
        fill=accent_color,
    )

    # --- Rodapé ---
    rodape = (
        "Simulação estimada. Para inventários oficiais (GHG Protocol), "
        "use fatores de emissão da região do cliente."
    )
    y_rodape = altura - 90
    draw.text((40, y_rodape), rodape, font=font_body, fill=secondary_color)

    # Exporta para bytes
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer.getvalue()


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

# ----------------- COMPARTILHAR COM O CLIENTE (IMAGEM) -----------------
st.markdown("---")
st.markdown("### 📲 Compartilhar com o cliente")

st.write(
    "Clique no botão abaixo para gerar uma **imagem em PNG** com o resumo da simulação. "
    "Depois é só baixar e enviar pelo WhatsApp para o cliente."
)

dados_para_imagem = {
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

if st.button("Gerar imagem para WhatsApp"):
    img_bytes = gerar_imagem_resumo(dados_para_imagem)

    # prévia menor na tela, mas o arquivo continua em alta
    st.image(img_bytes, caption="Resumo da simulação", width=400)

    st.download_button(
        label="⬇️ Baixar imagem (PNG)",
        data=img_bytes,
        file_name="resumo_energia_verde.png",
        mime="image/png",
    )
