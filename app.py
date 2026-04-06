# ==============================
# IMPORTAÇÕES
# ==============================

from flask import Flask, request, redirect, Response
import pandas as pd
import os
from datetime import datetime  # Para registrar data do consentimento


# ==============================
# CONFIGURAÇÃO DA APLICAÇÃO
# ==============================

app = Flask(__name__)

# Nome do arquivo CSV (nosso "banco de dados")
ARQUIVO = "dados.csv"


# ==============================
# FUNÇÃO: CARREGAR DADOS
# ==============================
def carregar_dados():
    caminho = os.path.join(os.path.dirname(__file__), ARQUIVO)

    if os.path.exists(caminho):
        try:
            return pd.read_csv(caminho, sep=';').fillna("")
        except:
            return pd.DataFrame()
    else:
        return pd.DataFrame()


# ==============================
# FUNÇÃO: FORMATAR NOME
# ==============================
def formatar_nome(nome):
    return " ".join([p.capitalize() for p in nome.split()])


# ==============================
# ROTA PRINCIPAL (FORMULÁRIO)
# ==============================
@app.route('/')
def formulario():

    busca = request.args.get("busca", "")
    df = carregar_dados()

    # ==========================
    # FILTRO DE BUSCA
    # ==========================
    if busca and not df.empty:
        df['nome_completo'] = df['nome'] + ' ' + df['sobrenome']
        df = df[df['nome_completo'].str.contains(busca, case=False, na=False)]

    # ==========================
    # ORGANIZAÇÃO DAS COLUNAS
    # ==========================
    if not df.empty:
        colunas = list(df.columns)
        nova_ordem = ['nome', 'sobrenome'] + [c for c in colunas if c not in ['nome', 'sobrenome']]
        df = df[nova_ordem]

    tabela_html = df.to_html(index=False) if not df.empty else ""

    # ==========================
    # HTML DA PÁGINA
    # ==========================
    return f"""
<!DOCTYPE html>
<html>
<head>
<title>Cadastro com LGPD</title>

<style>
body {{ font-family: Arial; background:#f4f4f4; }}
.container {{ display:flex; }}
.left {{ width:50%; padding:20px; }}
.right {{ width:50%; padding:20px; overflow:auto; }}

.section {{
    background:#1f3a5f;
    color:white;
    padding:8px;
    margin-top:20px;
    font-weight:bold;
}}

table {{
    width:100%;
    border-collapse: collapse;
    background:white;
}}

td, th {{
    border:1px solid #ccc;
    padding:6px;
    font-size:12px;
}}

th {{
    background:#1f3a5f;
    color:white;
}}

input {{
    width:95%;
    padding:5px;
}}

button {{
    background:#1f3a5f;
    color:white;
    padding:8px;
    border:none;
    margin-top:5px;
    cursor:pointer;
}}

</style>
</head>

<body>

<div class="container">

<!-- FORMULÁRIO -->
<div class="left">

<form action="/salvar" method="post">

<div class="section">DADOS PESSOAIS</div>
<table>
<tr><td>Nome*</td><td><input name="nome" required></td></tr>
<tr><td>Sobrenome*</td><td><input name="sobrenome" required></td></tr>
<tr><td>Email*</td><td><input name="email" required></td></tr>
</table>

<!-- ==========================
     LGPD
========================== -->
<div class="section">LGPD</div>
<table>
<tr>
<td colspan="2">
<label>
<input type="checkbox" name="lgpd" required>
Declaro que li e concordo com o uso dos meus dados para fins de cadastro conforme a LGPD.
</label>
</td>
</tr>
</table>

<button type="submit">Salvar</button>

</form>
</div>


<!-- LISTAGEM -->
<div class="right">
<h2>Pesquisa</h2>

<form method="get">
<input type="text" name="busca" placeholder="Pesquisar por nome completo" value="{busca}">
<button type="submit">Buscar</button>
<a href="/exportar?busca={busca}">
<button type="button">Exportar CSV</button>
</a>
</form>

{tabela_html}

</div>

</div>

</body>
</html>
"""


# ==============================
# ROTA: SALVAR DADOS
# ==============================
@app.route('/salvar', methods=['POST'])
def salvar():

    dados = request.form.to_dict(flat=False)

    # ==========================
    # VALIDAÇÃO LGPD
    # ==========================
    if 'lgpd' not in dados:
        return "Você precisa aceitar os termos da LGPD"

    # ==========================
    # FORMATAR NOME
    # ==========================
    if 'nome' in dados:
        dados['nome'] = formatar_nome(dados['nome'][0])

    if 'sobrenome' in dados:
        dados['sobrenome'] = formatar_nome(dados['sobrenome'][0])

    # ==========================
    # REGISTRO LGPD
    # ==========================
    dados['lgpd'] = "SIM"
    dados['data_consentimento'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ==========================
    # NORMALIZA DADOS
    # ==========================
    dados = {k: v[0] if isinstance(v, list) else v for k, v in dados.items()}

    caminho = os.path.join(os.path.dirname(__file__), ARQUIVO)

    df = pd.DataFrame([dados])

    if os.path.exists(caminho):
        df.to_csv(caminho, mode='a', header=False, index=False, sep=';')
    else:
        df.to_csv(caminho, index=False, sep=';')

    return redirect('/')


# ==============================
# ROTA: EXPORTAR CSV
# ==============================
@app.route('/exportar')
def exportar():

    busca = request.args.get("busca", "")
    df = carregar_dados()

    if busca and not df.empty:
        df['nome_completo'] = df['nome'] + ' ' + df['sobrenome']
        df = df[df['nome_completo'].str.contains(busca, case=False, na=False)]

    if df.empty:
        return "Sem dados para exportar"

    csv = df.to_csv(index=False, sep=';')

    return Response(
        csv,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=dados_exportados.csv"}
    )


# ==============================
# INICIAR SERVIDOR
# ==============================
if __name__ == '__main__':
    app.run(debug=True)