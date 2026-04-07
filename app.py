from flask import Flask, request, redirect, Response
import pandas as pd
import os
from datetime import datetime  # Para registrar data do consentimento

app = Flask(__name__)

ARQUIVO = "dados.csv"

def carregar_dados():
    caminho = os.path.join(os.path.dirname(__file__), ARQUIVO)
    if os.path.exists(caminho):
        try:
            return pd.read_csv(caminho, sep=';').fillna("")
        except:
            return pd.DataFrame()
    else:
        return pd.DataFrame()

def formatar_nome(nome):
    return " ".join([p.capitalize() for p in nome.split()])


@app.route('/')
def formulario():

    busca = request.args.get("busca", "")

    df = carregar_dados()

    # 🔎 Busca por nome completo
    if busca and not df.empty:
        df['nome_completo'] = df['nome'] + ' ' + df['sobrenome']
        df = df[df['nome_completo'].str.contains(busca, case=False, na=False)]

    # 🔄 Ordenar colunas
    if not df.empty:
        colunas = list(df.columns)
        nova_ordem = ['nome', 'sobrenome'] + [c for c in colunas if c not in ['nome', 'sobrenome']]
        df = df[nova_ordem]

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
    text-align:left;
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
    margin:0;
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
.clear-btn {{ background:#6c757d; }}
.export-btn {{ background:#17a2b8; }}

.search-box {{
    margin-bottom:20px;
}}
</style>
</head>

<body>

<div class="container">

<div class="left">

<form action="/salvar" method="post">

<div class="section">DADOS PESSOAIS</div>
<table>
<tr><td>Primeiro Nome*</td><td><input name="nome" required></td></tr>
<tr><td>Sobrenome*</td><td><input name="sobrenome" required></td></tr>
<tr><td>Email*</td><td><input name="email" required></td></tr>
<tr><td>Telefone</td><td><input name="telefone"></td></tr>
<tr><td>Celular</td><td><input name="celular"></td></tr>
</table>

<div class="section">DOCUMENTOS</div>
<table>
<tr><td>Data Nascimento*</td><td><input type="date" name="data_nasc"></td></tr>
<tr><td>Nacionalidade*</td><td><input name="nacionalidade"></td></tr>
<tr><td>2ª Nacionalidade</td><td><input name="nacionalidade2"></td></tr>
<tr><td>Passaporte*</td><td><input name="passaporte"></td></tr>
<tr><td>Validade Passaporte</td><td><input type="date" name="validade_passaporte"></td></tr>
<tr><td>2º Passaporte</td><td><input name="passaporte2"></td></tr>
<tr><td>Validade 2º Passaporte</td><td><input type="date" name="validade_passaporte2"></td></tr>
<tr><td>CPF*</td><td><input name="cpf"></td></tr>
<tr><td>RG*</td><td><input name="rg"></td></tr>
<tr><td>RNE</td><td><input name="rne"></td></tr>
<tr><td>Validade RNE</td><td><input type="date" name="validade_rne"></td></tr>
<tr><td>Estado Civil*</td><td><input name="estado_civil"></td></tr>
</table>

<div class="section">ENDEREÇO</div>
<table>
<tr><td>Endereço*</td><td><input name="endereco"></td></tr>
<tr><td>Complemento</td><td><input name="complemento"></td></tr>
<tr><td>Bairro*</td><td><input name="bairro"></td></tr>
<tr><td>Cidade*</td><td><input name="cidade"></td></tr>
<tr><td>Estado*</td><td><input name="estado"></td></tr>
<tr><td>CEP*</td><td><input name="cep"></td></tr>
</table>

<div class="section">DADOS DA EMPRESA</div>
<table>
<tr><td>Empresa*</td><td><input name="empresa"></td></tr>
<tr><td>Cargo*</td><td><input name="cargo"></td></tr>
<tr><td>Departamento</td><td><input name="departamento"></td></tr>
<tr><td>Centro de Custo</td><td><input name="centro_custo"></td></tr>
</table>

<div class="section">PREFERÊNCIAS</div>
<table>
<tr><td>Assento</td><td><input name="assento"></td></tr>
<tr>
<td>Fumante</td>
<td>
<select name="fumante">
<option>Não</option>
<option>Sim</option>
</select>
</td>
</tr>
</table>

<div class="section">CARTÃO DE MILHAGENS</div>

<table id="milhagem_table">
<tr>
<th>Cia Aérea</th>
<th>Número</th>
<th>Validade</th>
<th>Categoria</th>
<th>Ação</th>
</tr>

<tr>
<td><input name="cia_aerea[]"></td>
<td><input name="numero_milhagem[]"></td>
<td><input type="date" name="validade_milhagem[]"></td>
<td><input name="categoria_milhagem[]"></td>
<td><button type="button" class="delete-btn" onclick="removerLinha(this)">🗑</button></td>
</tr>
</table>

<button type="button" class="add-btn" onclick="addLinha()">+ Adicionar</button>

<!-- LGPD -->
<div style="margin-top:20px;">
    <label for="lgpd" style="font-size:12px; line-height:1.4; display:block;">
        <input type="checkbox" name="lgpd" id="lgpd" required style="margin-right:6px;">
        *Ao preencher esse formulário, declaro que autorizo a TUNIBRA a coletar e utilizar meus dados pessoais exclusivamente para fins de emissão de documentos e serviços relacionados à minha viagem, conforme a LGPD (Lei nº 13.709/2018).
    </label>
</div>

<button type="submit">Salvar</button>

</form>
</div>

<div class="right">
<h2>Pesquisa</h2>

<form method="get" class="search-box">
<input type="text" id="busca" name="busca" placeholder="Pesquisar por nome completo" value="{busca}">
<button type="submit">Buscar</button>
<button type="button" class="clear-btn" onclick="limparBusca()">Limpar</button>

<a href="/exportar?busca={busca}">
<button type="button" class="export-btn">Exportar CSV</button>
</a>

</form>

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
    <td><input name="categoria_milhagem[]"></td>
    <td><button type="button" class="delete-btn" onclick="removerLinha(this)">🗑</button></td>
    `;
}}

function removerLinha(botao) {{
    let row = botao.parentNode.parentNode;
    let table = document.getElementById("milhagem_table");

    if (table.rows.length > 2) {{
        row.remove();
    }} else {{
        alert("É necessário manter pelo menos uma linha.");
    }}
}}

function limparBusca() {{
    document.getElementById("busca").value = "";
    window.location.href = "/";
}}
</script>

</body>
</html>
"""

# ==============================
# 🔥 ROTA QUE FALTAVA (ADICIONADA)
# ==============================
@app.route('/salvar', methods=['GET', 'POST'])
def salvar():

    if request.method == 'GET':
        return redirect('/')

    dados = request.form.to_dict(flat=False)

    if 'lgpd' not in dados:
        return "É obrigatório aceitar a LGPD"

    dados['nome'] = formatar_nome(dados.get('nome', [''])[0])
    dados['sobrenome'] = formatar_nome(dados.get('sobrenome', [''])[0])

    milhagens = []
    for i in range(len(dados.get('cia_aerea[]', []))):
        linha = f"{dados['cia_aerea[]'][i]} | {dados['numero_milhagem[]'][i]} | {dados['validade_milhagem[]'][i]} | {dados['categoria_milhagem[]'][i]}"
        milhagens.append(linha)

    dados['milhagens'] = " || ".join(milhagens)

    dados.pop('cia_aerea[]', None)
    dados.pop('numero_milhagem[]', None)
    dados.pop('validade_milhagem[]', None)
    dados.pop('categoria_milhagem[]', None)

    dados['lgpd'] = "SIM"
    dados['data_consentimento'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    dados = {k: v[0] if isinstance(v, list) else v for k, v in dados.items()}

    print("SALVANDO DADOS:", dados) #  

    caminho = os.path.join(os.path.dirname(__file__), ARQUIVO)
    df = pd.DataFrame([dados])

    if os.path.exists(caminho):
        df.to_csv(caminho, mode='a', header=False, index=False, sep=';')
    else:
        df.to_csv(caminho, index=False, sep=';')

    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)