from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('blog', __name__)


# o index mostrará todas as postagens, as mais recentes primeiro. 
# um JOIN é utilizado para que as informações do autor da user tabela estejam disponíveis

@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts)

# o formulario é exibido ou os dados postados são validades e a postagem é add ao bd ou um erro é mostrado
# o decorador login_required é usado nas views do blog 
# ou o ussuario está logado para visitar ou ele é redirecionado para a pg login

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))
    return render_template('blog/create.html')

# views update e delete vão buscar post by id e veriifcar se o autor == usuario logado
# para evitar duplicação de código, pode escrever um função para obet-la post e chama-la em cada view

def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    # abort() irá gerar uma exceção que retorna um cod de status http
    # 404 = não encontrado 404 = proibido 401 = não autorizado, mas vai redirecionar para pg de login em vez de retorna esse status
    if post is None:
        abort(404, f"Post id {id} doen't exist.")
    
    # o argumento de check_author é definido para que a função possa ser usada para obter o post sem verificar o autor
    # isso seria útil para uma visualização mostar uma postagem individual em uma pg, onde o suario não importa porque não está modificando a postagem
    if check_author and post['author_id'] != g.user['id']:
        abort(403)
    
    return post

# a função update recebe um argumento id em <int:id> Um URL real será parecido com /1/update
# o flsk irá pegar o 1, garantir que seja int e pass-lo como id argumento
@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))
    return render_template('blog/update.html', post=post)

# as views create e update são muito semelhantes, com a difrerença que a update view usa um post objeto 
# e faz uma consultar ao inves de insert
# Com uma refatoração inteligente, você poderia usar uma visualização e um modelo para ambas as ações, 
# mas para o tutorial é mais claro mantê-los separados.

# A visualização de exclusão não possui seu próprio modelo, o botão de exclusão faz parte update.htmle é 
# postado no /<id>/deleteURL. Como não há modelo, ele apenas tratará o POSTmétodo e depois redirecionará 
# para a indexvisualização.
@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))

