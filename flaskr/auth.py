import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

# url_prefix é anexado em todos os URLs do BP
bp = Blueprint('auth', __name__, url_prefix='/auth')

# associa a url à função de visualização. Qdo o flask recebe uma solictação
# /auth/register, ele chamará a registervisualização e usará o valor de retorno como resposta.
@bp.route('/register', methods=('GET', 'POST'))
                                                
def register():
    # se o usuário enviar o form será POST e começa a validar a entrada
    if request.method == 'POST':
        # mapeamento de chaves e valores
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        # valida para que usuário e senha não estejam vazios
        error = None
    
        if not username:
            error = 'Nome do usuário é requerido.'
        elif not password:
            error = 'Senha requerida.'

        # se a validação for bem-sucedida vai inserir os dados no BD
        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    # a senha não será armazenda diretamente no BD e sim no hash
                    (username, generate_password_hash(password)),
                )
                # BD é chamado para salvar as alterações
                db.commit()
            except db.InterruptedError:
                error = f"O usuário {username} já está registrado."
            else:
                # após armazenar o usuario ele é redeirecionado para a pg de login.
                # url_for() gera url para visualização de login com base em seu nome
                return redirect(url_for("auth.login"))
        # armazena mensagens que podem ser recuperadas ao renderizar o template  
        flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        # aqui o usuario é consultado primeiro e armazenado em uma variável para uso posterior
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        # retorna uma linha de consulta, se não retorna nenhum resultado, será none
        # depois o fetcha11() é utilizado para restorna uma lista de todos os resultados
        ).fetchone()

        if user is None:
            error = 'Nome de usuário incorreto.'
        # faz o hash da senha enviada que é comparada com o hash ja armazenado
        elif not check_password_hash(user['password'], password):
            error = 'Senha incorreta.'

        if error is None:
        # armazena dados entre solicitações que são armazenados em um cookie enviado ao navegador
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))
        # quando dá erro ele para tudo e manda uma mensagem para o template que requisitou, neste caso é o login
        flash(error)

    return render_template('auth/login.html')

# registra uma função que é executada antes da função de visualizaçõa, independente da url solicitada
@bp.before_app_request
# carregar usuario logado
# verifica se um usuaroi está armazenado na session, obtem os dados no BD e armazena em g.user
# g é um objeto que armazena dados de sessão e dados de conexão com banco enquanto durar a duração da solicitação
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        # retorna a primeira linha da query passada
        ).fetchone()

# sair - remove id do usuário da session
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# para criar / editar / excluir postagens precisa de usuario logado 
# este decorador verifica isso a cada visualização
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        
        return view(**kwargs)
    
    return wrapped_view

""" Endpoints e URLs 
A url_for()função gera a URL para uma visualização com base em um nome e argumentos. O nome associado a uma visualização também é chamado de endpoint e, por padrão, é igual ao nome da função de visualização.

Por exemplo, a hello()visualização que foi adicionada à fábrica de aplicativos anteriormente no tutorial tem o nome 'hello'e pode ser vinculada a url_for('hello'). Se fosse necessário um argumento, que você verá mais tarde, ele estaria vinculado ao uso de .url_for('hello', who='World')

Ao usar um blueprint, o nome do blueprint é anexado ao nome da função, portanto, o ponto final da loginfunção que você escreveu acima é 'auth.login'porque você a adicionou ao 'auth' blueprint.
 """

