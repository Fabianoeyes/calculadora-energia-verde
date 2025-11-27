# calculadora-energia-verde
# Calculadora de Economia – Energia Verde

Aplicação Streamlit para simular rapidamente a economia financeira e o impacto
ambiental da adoção de energia verde, com opção de exportar um relatório em PDF.

## Pré-requisitos
- Python 3.9+
- Pip instalado

## Instalação
```bash
pip install -r requirements.txt
```

## Execução
Inicie o aplicativo localmente com o Streamlit:
```bash
streamlit run app.py
```
O servidor será iniciado em `http://localhost:8501` por padrão.

## Funcionalidades
- Entrada de dados no menu lateral (valor da conta, desconto, cobertura, parte
  variável, período, tarifa média e fator de emissão de CO₂).
- Cálculo automático de economia mensal, economia acumulada e nova conta
  estimada.
- Estimativa de CO₂ evitado e demais métricas energéticas.
- Geração de relatório em PDF com os valores simulados e logo da Prospera.

## Observações
- Os fatores de emissão são estimativos; para relatórios oficiais siga os
  fatores da distribuidora/região conforme metodologias como GHG Protocol.
- Inclua o arquivo `prospera_logo.png` na mesma pasta do `app.py` para exibir o
  logotipo no PDF.
app.py
+11
-3

