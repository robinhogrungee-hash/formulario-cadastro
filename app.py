from flask import Flask, request, redirect, session, Response
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
        try:
            df = pd.read_csv(caminho, sep=";").fillna("")
        except:
            df = pd.DataFrame()
    else:
        df = pd.DataFrame()

    colunas_obrigatorias = ["usuario", "nome", "sobrenome", "email"]

    for col in colunas_obrigatorias:
        if col not in df.columns:
            df[col] = ""

    return df

# =========================
# 📥 CARREGAR USUÁRIOS
# =========================
def carregar_usuarios():
    caminho = os.path.join(os.path.dirname(__file__), ARQUIVO_USUARIOS)

    if os.path.exists(caminho):
        df = pd.read_csv(caminho, dtype=str)

        df["usuario"] = df["usuario"].str.strip()
        df["senha"] = df["senha"].str.strip()
        df["tipo"] = df["tipo"].str.strip()

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
        <button type="submit">Entrar</button>
    </form>
    """

# =========================
# 🚪 LOGOUT
# =========================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# =========================
# 🔒 VERIFICA LOGIN
# =========================
def usuario_logado():
    return "usuario" in session

# =========================
# 🏠 TELA PRINCIPAL
# =========================
@app.route("/", methods=["GET"])
def formulario():
    if not usuario_logado():
        return redirect("/login")

    busca = request.args.get("busca", "").strip()
    df = carregar_dados()

    if not df.empty and session["tipo"] != "admin":
        df = df[df["usuario"] == session["usuario"]]

    if busca and not df.empty:
        df["nome_completo"] = df["nome"] + " " + df["sobrenome"]
        df = df[df["nome_completo"].str.contains(busca, case=False, na=False)]

    tabela = df.to_html(index=False) if not df.empty else "<p>Sem registros</p>"

    return f"""
    <h2>Bem-vindo, {session['usuario']} ({session['tipo']})</h2>
    <a href="/logout">Sair</a>

    <hr>

    <h3>📋 Cadastro</h3>
    <form method="POST" action="/salvar">
        Nome: <input name="nome" required><br><br>
        Sobrenome: <input name="sobrenome" required><br><br>
        Email: <input name="email" required><br><br>

        <br>
        <input type="checkbox" name="lgpd" required>
        <label>
        Ao preencher esse formulário, declaro que autorizo a TUNIBRA a coletar e utilizar meus dados pessoais exclusivamente para fins de emissão de documentos e serviços relacionados à minha viagem, conforme a LGPD (Lei nº 13.709/2018).
        </label>

        <br><br>
        <button type="submit">Salvar</button>
    </form>

    <hr>

    <h3>🔍 Pesquisa</h3>
    <form method="GET">
        <input name="busca" placeholder="Pesquisar por nome">
        <button>Buscar</button>
    </form>

    <br>

    <h3>📊 Registros</h3>
    {tabela}
    """

# =========================
# 💾 SALVAR DADOS
# =========================
@app.route("/salvar", methods=["POST"])
def salvar():
    if not usuario_logado():
        return redirect("/login")

    # 🔒 VALIDA LGPD
    if not request.form.get("lgpd"):
        return "Você precisa aceitar os termos da LGPD"

    df = carregar_dados()

    novo = {
        "usuario": session["usuario"],
        "nome": request.form.get("nome"),
        "sobrenome": request.form.get("sobrenome"),
        "email": request.form.get("email")
    }

    df = pd.concat([df, pd.DataFrame([novo])], ignore_index=True)

    caminho = os.path.join(os.path.dirname(__file__), ARQUIVO_DADOS)
    df.to_csv(caminho, sep=";", index=False)

    return redirect("/")

# =========================
# 📤 EXPORTAR CSV
# =========================
@app.route("/exportar")
def exportar():
    if not usuario_logado():
        return redirect("/login")

    df = carregar_dados()

    if not df.empty and session["tipo"] != "admin":
        df = df[df["usuario"] == session["usuario"]]

    csv = df.to_csv(index=False)

    return Response(
        csv,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=dados.csv"}
    )

# =========================
# 🔍 DEBUG
# =========================
@app.route("/debug")
def debug():
    df = carregar_usuarios()
    return df.to_html()

# =========================
# 🚀 EXECUÇÃO
# =========================
if __name__ == "__main__":
    app.run(debug=True)