from flask import Flask, request, redirect, session, url_for, Response
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = "segredo_super_seguro_v2"  # Necessário para sessão

ARQUIVO_DADOS = "dados.csv"
ARQUIVO_USUARIOS = "usuarios.csv"

# =========================
# 📥 CARREGAR DADOS
# =========================
def carregar_dados():
    caminho = os.path.join(os.path.dirname(__file__), ARQUIVO_DADOS)
    if os.path.exists(caminho):
        try:
            return pd.read_csv(caminho, sep=";").fillna("")
        except:
            return pd.DataFrame()
    return pd.DataFrame()

# =========================
# 📥 CARREGAR USUÁRIOS
# =========================
def carregar_usuarios():
    caminho = os.path.join(os.path.dirname(__file__), ARQUIVO_USUARIOS)
    if os.path.exists(caminho):
        return pd.read_csv(caminho)
    return pd.DataFrame()

# =========================
# 🔐 LOGIN
# =========================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form.get("usuario")
        senha = request.form.get("senha")

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
# 🔒 PROTEÇÃO
# =========================
def usuario_logado():
    return "usuario" in session

# =========================
# 🏠 TELA PRINCIPAL
# =========================
@app.route("/", methods=["GET", "POST"])
def formulario():
    if not usuario_logado():
        return redirect("/login")

    busca = request.args.get("busca", "")
    df = carregar_dados()

    # 🔐 FILTRO POR USUÁRIO
    if session["tipo"] != "admin":
        df = df[df["usuario"] == session["usuario"]]

    # 🔍 BUSCA
    if busca and not df.empty:
        df["nome_completo"] = df["nome"] + " " + df["sobrenome"]
        df = df[df["nome_completo"].str.contains(busca, case=False, na=False)]

    tabela = df.to_html(index=False)

    return f"""
    <h2>Bem-vindo, {session['usuario']} ({session['tipo']})</h2>
    <a href="/logout">Sair</a>

    <h3>Pesquisa</h3>
    <form method="GET">
        <input name="busca" placeholder="Pesquisar">
        <button>Buscar</button>
    </form>

    <br>

    {tabela}
    """

# =========================
# 💾 SALVAR DADOS
# =========================
@app.route("/salvar", methods=["POST"])
def salvar():
    if not usuario_logado():
        return redirect("/login")

    df = carregar_dados()

    novo = {
        "usuario": session["usuario"],  # 🔐 vincula ao usuário logado
        "nome": request.form.get("nome"),
        "sobrenome": request.form.get("sobrenome"),
        "email": request.form.get("email")
    }

    df = pd.concat([df, pd.DataFrame([novo])], ignore_index=True)
    df.to_csv(ARQUIVO_DADOS, sep=";", index=False)

    return redirect("/")
    
# =========================
# 📤 EXPORTAR CSV
# =========================
@app.route("/exportar")
def exportar():
    if not usuario_logado():
        return redirect("/login")

    df = carregar_dados()

    if session["tipo"] != "admin":
        df = df[df["usuario"] == session["usuario"]]

    csv = df.to_csv(index=False)

    return Response(
        csv,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=dados.csv"}
    )

# =========================
# 🚀 EXECUÇÃO LOCAL
# =========================
if __name__ == "__main__":
    app.run(debug=True)