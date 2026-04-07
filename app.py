from flask import Flask, request, redirect, Response
import pandas as pd
import os
from datetime import datetime

app = Flask(__name__)

ARQUIVO = "dados.csv"

# ==============================
# CARREGAR DADOS
# ==============================
def carregar_dados():
    caminho = os.path.join(os.path.dirname(__file__), ARQUIVO)
    if os.path.exists(caminho):
        try:
            return pd.read_csv(caminho, sep=';').fillna("")
        except:
            return pd.DataFrame()
    return pd.DataFrame()

# ==============================
# FORMATAR NOME
# ==============================
def formatar_nome(nome):
    return " ".join([p.capitalize() for p in nome.split()])


# ==============================
# TELA PRINCIPAL
# ==============================
@app.route('/')
def formulario():

    busca = request.args.get("busca", "")
    df = carregar_dados()

    if busca and not df.empty:
        df['nome_completo'] = df['nome'] + ' ' + df['sobrenome']
        df = df[df['nome_completo'].str.contains(busca, case=False, na=False)]

    tabela_html = df.to_html(index=False) if not df.empty else ""

    return f"""
<!DOCTYPE html>
<html>
<head>
<title>Cadastro</title>

<style>
body {{ font-family: Arial; background:#f4f4f4; }}
.container {{ display:flex; }}
.left {{ width:50%; padding:20px; }}
.right {{ width:50%; padding:20px; }}

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

input[type="text"],
input[type="date"],
input[type="email"],
select {{
    width:95%;
    padding:5px;
}}

input[type="checkbox"] {{
    width:auto;
}}

button {{
    background:#1f3a5f;
    color:white;
    padding:8px;
    border:none;
    margin-top:5px;
    cursor:pointer;
}}

.add-btn {{ background:#28a745; }}
.delete-btn {{ background:#dc3545; }}

</style>
</head>

<body>

<div class="container">

<div class="left">

<form action="/salvar" method="post">

<div class="section">DADOS PESSOAIS</div>
<table>
<tr><td>Nome*</td><td><input name="nome" required></td></tr>
<tr><td>Sobrenome*</td><td><input name="sobrenome" required></td></tr>
<tr><td>Email*</td><td><input name="email" required></td></tr>
</table>

<div class="section">ENDEREÇO</div>
<table>
<tr><td>CEP</td><td><input name="cep" id="cep" onblur="buscarCEP()"></td></tr>
<tr><td>Endereço</td><td><input name="endereco" id="endereco"></td></tr>
<tr><td>Bairro</td><td><input name="bairro" id="bairro"></td></tr>
<tr><td>Cidade</td><td><input name="cidade" id="cidade"></td></tr>
<tr><td>Estado</td><td><input name="estado" id="estado"></td></tr>
</table>

<div class="section">MILHAGENS</div>
<table id="milhagem_table">
<tr>
<th>Cia</th><th>Número</th><th>Validade</th><th>Ação</th>
</tr>

<tr>
<td><input name="cia_aerea[]"></td>
<td><input name="numero_milhagem[]"></td>
<td><input type="date" name="validade_milhagem[]"></td>
<td><button type="button" onclick="removerLinha(this)">X</button></td>
</tr>
</table>

<button type="button" class="add-btn" onclick="addLinha()">+ Adicionar</button>

<!-- LGPD -->
<div style="margin-top:20px;">
    <label style="font-size:12px;">
        <input type="checkbox" name="lgpd" required style="margin-right:5px;">
        *Ao preencher esse formulário, declaro que autorizo a TUNIBRA a coletar e utilizar meus dados pessoais conforme a LGPD.
    </label>
</div>

<button type="submit">Salvar</button>

</form>
</div>

<div class="right">
<h2>Registros</h2>
{tabela_html}
</div>

</div>

<script>
function addLinha() {{
    let table = document.getElementById("milhagem_table");
    let row = table.insertRow();

    row.innerHTML = `
    <td><input name="cia_aerea[]"></td>
    <td><input name="numero_milhagem[]"></td>
    <td><input type="date" name="validade_milhagem[]"></td>
    <td><button type="button" onclick="removerLinha(this)">X</button></td>
    `;
}}

function removerLinha(btn) {{
    btn.parentNode.parentNode.remove();
}}

function buscarCEP() {{
    let cep = document.getElementById("cep").value.replace(/\\D/g, '');

    if (cep.length !== 8) return;

    fetch(`https://viacep.com.br/ws/${{cep}}/json/`)
    .then(res => res.json())
    .then(data => {{
        if (!data.erro) {{
            document.getElementById("endereco").value = data.logradouro;
            document.getElementById("bairro").value = data.bairro;
            document.getElementById("cidade").value = data.localidade;
            document.getElementById("estado").value = data.uf;
        }}
    }});
}}
</script>

</body>
</html>
"""


# ==============================
# 🔥 ROTA CORRIGIDA
# ==============================
@app.route('/salvar', methods=['GET', 'POST'])
def salvar():

    # 🔒 evita erro 404 ao acessar direto
    if request.method == 'GET':
        return redirect('/')

    dados = request.form.to_dict(flat=False)

    if 'lgpd' not in dados:
        return "Aceite a LGPD"

    dados['nome'] = formatar_nome(dados.get('nome', [''])[0])
    dados['sobrenome'] = formatar_nome(dados.get('sobrenome', [''])[0])

    milhagens = []
    for i in range(len(dados.get('cia_aerea[]', []))):
        linha = f"{dados['cia_aerea[]'][i]} | {dados['numero_milhagem[]'][i]}"
        milhagens.append(linha)

    dados['milhagens'] = " || ".join(milhagens)

    dados.pop('cia_aerea[]', None)
    dados.pop('numero_milhagem[]', None)
    dados.pop('validade_milhagem[]', None)

    dados['lgpd'] = "SIM"
    dados['data_consentimento'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    dados = {k: v[0] if isinstance(v, list) else v for k, v in dados.items()}

    caminho = os.path.join(os.path.dirname(__file__), ARQUIVO)
    df = pd.DataFrame([dados])

    if os.path.exists(caminho):
        df.to_csv(caminho, mode='a', header=False, index=False, sep=';')
    else:
        df.to_csv(caminho, index=False, sep=';')

    return redirect('/')


# ==============================
# EXPORTAR
# ==============================
@app.route('/exportar')
def exportar():

    df = carregar_dados()

    csv = df.to_csv(index=False, sep=';')

    return Response(
        csv,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=dados.csv"}
    )


if __name__ == '__main__':
    app.run(debug=True)