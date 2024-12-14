from flask import Flask, render_template, request, redirect, url_for, session
import os
import json

app = Flask(__name__)

# Chave secreta para a sessão
app.secret_key = os.urandom(24)

# Classe Cliente
class Cliente:
    def __init__(self, nome, email):
        self.nome = nome
        self.email = email

    def atualizar_email(self, novo_email):
        self.email = novo_email
        print("E-mail atualizado com sucesso")

    def exibir_dados(self):
        print(f"Nome: {self.nome} E-mail: {self.email}")

# Função para carregar os usuários
def carregar_usuarios():
    try:
        with open('usuarios.json', 'r') as f:
            data = json.load(f)
            # Convertendo os dados do JSON para instâncias de Cliente
            return [Cliente(usuario['nome'], usuario['email']) for usuario in data]
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# Função para salvar os usuários
def salvar_usuarios(usuarios):
    # Convertendo as instâncias de Cliente de volta para o formato de dicionário
    usuarios_data = [{'nome': usuario.nome, 'email': usuario.email} for usuario in usuarios]
    with open('usuarios.json', 'w') as f:
        json.dump(usuarios_data, f, indent=4)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Verifica se as credenciais estão corretas
        if email == 'gerente_rogerio@itau.com' and password == 'adm123':
            # Se o login for bem-sucedido, cria uma sessão e redireciona
            session['logged_in'] = True
            return redirect(url_for('area_restrita'))
        else:
            # Se as credenciais estiverem erradas, exibe uma mensagem de erro
            return redirect(url_for('index', erro=1))

    return render_template('index.html', erro=request.args.get('erro'))

@app.route('/area-restrita', methods=['GET', 'POST'])
def area_restrita():
    # Verifica se o gerente está logado
    if not session.get('logged_in'):
        return redirect(url_for('index'))

    # Carrega os dados dos usuários
    usuarios = carregar_usuarios()

    # Se o formulário for enviado para atualizar o e-mail de um usuário
    if request.method == 'POST' and 'usuario' in request.form and 'novoEmail' in request.form:
        usuario_selecionado = request.form['usuario']
        novo_email = request.form['novoEmail']

        # Encontra o cliente selecionado e atualiza o e-mail
        cliente_encontrado = False
        for cliente in usuarios:
            if cliente.nome == usuario_selecionado:
                cliente.atualizar_email(novo_email)  # Atualiza o e-mail usando o método da classe Cliente
                cliente_encontrado = True
                break

        if not cliente_encontrado:
            return redirect(url_for('area_restrita', msg="Usuário não encontrado."))

        # Salva as alterações de volta no arquivo JSON
        salvar_usuarios(usuarios)

        return redirect(url_for('area_restrita', msg="E-mail atualizado com sucesso!"))

    # Se o formulário foi enviado para adicionar um novo usuário
    if request.method == 'POST' and 'novoNome' in request.form and 'novoEmail' in request.form:
        novo_nome = request.form['novoNome']
        novo_email = request.form['novoEmail']

        # Cria um novo cliente e adiciona à lista
        novo_cliente = Cliente(novo_nome, novo_email)
        usuarios.append(novo_cliente)

        # Salva os usuários atualizados
        salvar_usuarios(usuarios)

        return redirect(url_for('area_restrita', msg="Usuário adicionado com sucesso!"))

    return render_template('area_restrita.html', usuarios=usuarios, msg=request.args.get('msg'))

@app.route('/remover-usuario', methods=['POST'])
def remover_usuario():
    # Verifica se o gerente está logado
    if not session.get('logged_in'):
        return redirect(url_for('index'))

    # Carrega os dados dos usuários
    usuarios = carregar_usuarios()

    # Obtém o índice do usuário a ser removido
    index = int(request.form['index'])

    # Verifica se o índice é válido
    if 0 <= index < len(usuarios):
        # Remove o usuário pelo índice
        usuarios.pop(index)

        # Salva os dados atualizados de volta no arquivo JSON
        salvar_usuarios(usuarios)

        # Redireciona de volta para a área restrita com a mensagem de sucesso
        return redirect(url_for('area_restrita', msg="Usuário removido com sucesso!"))
    else:
        # Caso o índice não seja válido
        return redirect(url_for('area_restrita', msg="Erro ao remover o usuário."))

@app.route('/logout', methods=['POST'])
def logout():
    # Destrói a sessão e redireciona para a página inicial
    session.pop('logged_in', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
