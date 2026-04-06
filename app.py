from flask import Flask, request, redirect, session
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = "segredo_super_seguro"

ARQUIVO_DADOS = "dados.csv"
ARQUIVO_USUARIOS = "usuarios.csv"

# =========================
# 📥 CARREGAR DADOS
# =========================
def carregar_dados():
    caminho = os.path.join(os.path.dirname(__file__), ARQUIVO_DADOS)

    if os.path.exists(caminho):
        df = pd.read_csv(caminho, sep=";").fillna("")
    else:
        df = pd.DataFrame()

    if "usuario" not in df.columns:
        df["usuario"] = ""

    return df

# =========================
# 📥 USUÁRIOS
# =========================
def carregar_usuarios():
    caminho = os.path.join(os.path.dirname(__file__), ARQUIVO_USUARIOS)

    if os.path.exists(caminho):
        df = pd.read_csv(caminho, dtype=str)
        df = df.apply(lambda x: x.str.strip())
        return df

    return pd.DataFrame()

# =========================
# 🔐 LOGIN
# =========================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form.get("usuario", "").strip()
        senha = request.form.get("senha", "").strip()

        df = carregar_usuarios()

        user = df[(df["usuario"] == usuario) & (df["senha"] == senha)]

        if not user.empty:
            session["usuario"] = usuario
            session["tipo"] = user.iloc[0]["tipo"]
            return redirect("/")
        else:
            return "Usuário ou senha inválidos"

    return """
    <h2>Login</h2>
    <form method="POST">
        Usuário: <input name="usuario"><br><br>
        Senha: <input name="senha" type="password"><br><br>
        <button>Entrar</button>
    </form>
    """

# =========================
# LOGOUT
# =========================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

def usuario_logado():
    return "usuario" in session

# =========================
# TELA PRINCIPAL (FORMULÁRIO ORIGINAL)
# =========================
@app.route("/", methods=["GET"])
def home():
    if not usuario_logado():
        return redirect("/login")

    df = carregar_dados()

    if session["tipo"] != "admin":
        df = df[df["usuario"] == session["usuario"]]

    tabela = df.to_html(index=False) if not df.empty else "Sem registros"

    return f"""
    <h2>Bem-vindo, {session['usuario']} ({session['tipo']})</h2>
    <a href="/logout">Sair</a>

    <hr>

    <h2>DADOS PESSOAIS</h2>
    <form method="POST" action="/salvar">
        Nome: <input name="nome"><br>
        Sobrenome: <input name="sobrenome"><br>
        Email: <input name="email"><br>
        Telefone: <input name="telefone"><br>
        Celular: <input name="celular"><br>

        <h3>DOCUMENTOS</h3>
        Data Nascimento: <input name="data_nasc"><br>
        Nacionalidade: <input name="nacionalidade"><br>
        CPF: <input name="cpf"><br>
        RG: <input name="rg"><br>

        <br>
        <input type="checkbox" name="lgpd" required>
        Ao preencher esse formulário, declaro que autorizo a TUNIBRA a coletar e utilizar meus dados pessoais conforme a LGPD.

        <br><br>
        <button type="submit">Salvar</button>
    </form>

    <hr>

    <h2>Pesquisa</h2>
    <form method="GET">
        <input name="busca">
        <button>Buscar</button>
    </form>

    <h2>Registros</h2>
    {tabela}
    """

# =========================
# SALVAR
# =========================
@app.route("/salvar", methods=["POST"])
def salvar():
    if not usuario_logado():
        return redirect("/login")

    if not request.form.get("lgpd"):
        return "Aceite LGPD obrigatório"

    df = carregar_dados()

    novo = {
        "usuario": session["usuario"],
        "nome": request.form.get("nome"),
        "sobrenome": request.form.get("sobrenome"),
        "email": request.form.get("email"),
        "telefone": request.form.get("telefone"),
        "celular": request.form.get("celular"),
        "data_nasc": request.form.get("data_nasc"),
        "nacionalidade": request.form.get("nacionalidade"),
        "cpf": request.form.get("cpf"),
        "rg": request.form.get("rg"),
    }

    df = pd.concat([df, pd.DataFrame([novo])], ignore_index=True)

    caminho = os.path.join(os.path.dirname(__file__), ARQUIVO_DADOS)
    df.to_csv(caminho, sep=";", index=False)

    return redirect("/")

# =========================
# DEBUG
# =========================
@app.route("/debug")
def debug():
    return carregar_usuarios().to_html()

# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(debug=True)