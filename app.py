import streamlit as st
import base64
from pathlib import Path
from fpdf import FPDF

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
    .letterhead {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 0.5rem 0 0.75rem;
        border-bottom: 2px solid #e6e6e6;
        margin-bottom: 1rem;
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
        height: 52px;
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
            height: 44px;
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


def carregar_logo() -> tuple[str, str]:
    logo_path = Path(__file__).with_name("Logo_Soul_Up_Azul.jpg.jpeg")
    try:
        with logo_path.open("rb") as arquivo_logo:
            logo_base64 = base64.b64encode(arquivo_logo.read()).decode("utf-8")
    except FileNotFoundError:
        return "", ""

    return logo_base64, str(logo_path)


def gerar_relatorio_pdf(dados: dict, logo_path: str) -> bytes:
    """
    Gera um PDF em memória com o resumo da simulação.
    Usa apenas caracteres compatíveis com Latin-1.
    """
    pdf = FPDF()
    # Mantém tudo em uma página para evitar que o rodapé seja empurrado
    # para uma segunda folha.
    pdf.set_auto_page_break(auto=False)
    pdf.set_margins(left=15, top=28, right=15)
    pdf.add_page()

    # Logo (cabeçalho)
    if logo_path:
        try:
            logo_width = 60
            logo_x = (pdf.w - logo_width) / 2
            pdf.image(logo_path, x=logo_x, y=8, w=logo_width)
        except Exception:
            pass

    pdf.ln(22)
    pdf.set_line_width(0.4)
    pdf.set_draw_color(200)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
    pdf.ln(6)

    # Título
    pdf.set_font("Arial", "B", 16)
    pdf.multi_cell(
        pdf.epw,
        8,
        texto_pdf_safe(
            "Calculadora de Economia - Programa de Pontos & Desconto na Conta de Luz"
        ),
    )
    pdf.ln(2)

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
        label_width = 110
        value_width = pdf.w - pdf.l_margin - pdf.r_margin - label_width
        x_inicial = pdf.get_x()
        y_inicial = pdf.get_y()

        pdf.set_font("Arial", "", 12)
        pdf.multi_cell(label_width, 7, texto_pdf_safe(rotulo))
        y_apos_rotulo = pdf.get_y()

        pdf.set_xy(x_inicial + label_width, y_inicial)
        pdf.set_font("Arial", "B", 12)
        pdf.multi_cell(value_width, 7, texto_pdf_safe(valor), align="R")
        y_apos_valor = pdf.get_y()

        pdf.set_xy(x_inicial, max(y_apos_rotulo, y_apos_valor))

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

# --- (restante do app permanece igual) ---
