import streamlit as st
from fpdf import FPDF
from datetime import datetime

# =========================
# CONFIG STREAMLIT
# =========================
st.set_page_config(page_title="Calculadora Energia Verde", page_icon="⚡", layout="wide")

# =========================
# FUNÇÕES AUXILIARES
# =========================
def texto_pdf_safe(texto: str) -> str:
    return texto.encode("latin-1", "ignore").decode("latin-1")

def gerar_relatorio_pdf(dados: dict) -> bytes:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Logo Prospera
    try:
        pdf.image("prospera_logo.png", x=160, y=8, w=35)
    except:
        pass

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, texto_pdf_safe("Calculadora de Economia - Energia Verde"), ln=True)

    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(0, 8, texto_pdf_safe(
        "Relatório gerado automaticamente com base nos dados informados."
    ))

    pdf.ln(4)

    # Dados principais
    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 8, texto_pdf_safe("Resumo financeiro"), ln=True)

    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 7, texto_pdf_safe(f"Conta atual: {dados['valor_conta']}"), ln=True)
    pdf.cell(0, 7, texto_pdf_safe(f"Nova conta aproximada: {dados['nova_conta']}"), ln=True)
    pdf.cell(0, 7, texto_pdf_safe(f"Economia mensal: {dados['economia_mensal']}"), ln=True)
    pdf.cell(0, 7, texto_pdf_safe(
        f"Economia em {dados['periodo_meses']} meses: {dados['economia_periodo']}"
    ), ln=True)

    pdf.ln(4)

    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 8, texto_pdf_safe("Parâmetros financeiros"), ln=True)

    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 7, texto_pdf_safe(f"Desconto aplicado: {dados['desconto']}%"))
    pdf.multi_cell(0, 7, texto_pdf_safe(
        f"Cobertura energia verde: {dados['cobertura']}% da conta"
    ))
    pdf.multi_cell(0, 7, texto_pdf_safe(
        f"Parte variável considerada: {dados['parte_variavel']}% da conta"
    ))

    pdf.ln(4)

    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 8, texto_pdf_safe("Impacto ambiental estimado"), ln=True)

    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 7, texto_pdf_safe(
        f"Fator de emissão (GHG Protocol): {dados['fator_co2']} kg CO2e/kWh"
    ))
    pdf.multi_cell(0, 7, texto_pdf_safe(
        f"CO2 evitado em {dados['periodo_meses']} meses: {dados['co2_periodo_t']} t CO2e"
    ))

    pdf.ln(6)

    pdf.set_font("Arial", "I", 10)
    pdf.multi_cell(0, 6, texto_pdf_safe(
        "Simulação estimada. Para inventários oficiais (GHG Protocol), "
        "utilize fatores de emissão homologados pela distribuidora local."
    ))

    return pdf.output(dest="S").encode("latin-1")


# =========================
# SIDEBAR INPUTS
# =========================
st.sidebar.header("📊 Dados do Cliente")

valor_conta = st.sidebar.number_input("Valor atual da conta (R$)", value=1500.0, step=50.0)
desconto = st.sidebar.slider("% de desconto na energia consumida", 0, 50, 15)
cobertura = st.sidebar.slider("% da conta coberta pela energia verde", 0, 100, 80)
periodo = st.sidebar.number_input("Período da simulação (meses)", value=12)
tarifa_media = st.sidebar.number_input("Tarifa média (R$/kWh)", value=0.95)

parte_variavel = 80
fator_emissao = 0.35  # GHG Protocol

# =========================
# CÁLCULOS
# =========================
parte_variavel_valor = valor_conta * (parte_variavel / 100)
economia_mensal = parte_variavel_valor * (desconto / 100) * (cobertura / 100)
nova_conta = valor_conta - economia_mensal
economia_total = economia_mensal * periodo

kwh_mensal = parte_variavel_valor / tarifa_media
kwh_economizados = kwh_mensal * (cobertura / 100)
co2_mensal = kwh_economizados * fator_emissao
co2_periodo_t = (co2_mensal * periodo) / 1000

# =========================
# RESULTADO
# =========================
st.title("⚡ Calculadora de Economia - Energia Verde")

st.markdown(f"""
### 💰 Resumo financeiro
- Conta atual: **R$ {valor_conta:,.2f}**
- Nova conta aproximada: **R$ {nova_conta:,.2f}**
- Economia mensal estimada: **R$ {economia_mensal:,.2f}**
- Economia em {periodo} meses: **R$ {economia_total:,.2f}**

### 🌱 Impacto ambiental (GHG Protocol)
- Fator de emissão: {fator_emissao} kg CO2e/kWh  
- CO2 evitado em {periodo} meses: **{co2_periodo_t:.2f} t CO2e**
""")

st.info("Simulação estimada conforme diretrizes do GHG Protocol.")

# =========================
# BOTÃO GERAR PDF
# =========================
st.markdown("## 📄 Relatório em PDF")

dados_pdf = {
    "valor_conta": f"R$ {valor_conta:,.2f}",
    "nova_conta": f"R$ {nova_conta:,.2f}",
    "economia_mensal": f"R$ {economia_mensal:,.2f}",
    "economia_periodo": f"R$ {economia_total:,.2f}",
    "periodo_meses": int(periodo),
    "desconto": desconto,
    "cobertura": cobertura,
    "parte_variavel": parte_variavel,
    "fator_co2": fator_emissao,
    "co2_periodo_t": f"{co2_periodo_t:.2f}",
}

if st.button("✅ Gerar relatório em PDF"):
    pdf_bytes = gerar_relatorio_pdf(dados_pdf)
    st.download_button(
        "📥 Baixar PDF",
        data=pdf_bytes,
        file_name="relatorio_energia_verde_prospera.pdf",
        mime="application/pdf"
    )
