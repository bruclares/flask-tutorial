# Com o auth fixture, você pode chamar auth.login()um teste para fazer login como testusuário, 
# que foi inserido como parte dos dados de teste no appaparelho.
# A registervisualização deve ser renderizada com sucesso no GET. Com POST dados de formulário 
# válidos, ele deverá redirecionar para a URL de login e os dados do usuário deverão estar no banco de dados. 
# Dados inválidos devem exibir mensagens de erro.


import pytest
from flask import g, session
from flaskr.db import get_db


def test_register(client, app):
    # client.get()faz uma GETsolicitação e retorna o Responseobjeto retornado pelo Flask. 
    # Da mesma forma, client.post()faz uma POST solicitação, convertendo o datadict em dados do formulário.
    # para testar se a pg é renderizada com sucesso uma solicitação simples é feita e verificada para 200 ok
    # se falhasse o flask iria retornar 500 Internal Server Error code.
    assert client.get('/auth/register').status_code == 200
    response = client.post(
        '/auth/register', data={'username': 'a', 'password': 'a'}
    )
    # headersterá um Locationcabeçalho com a URL de login quando a visualização do 
    # registro redirecionar para a visualização de login.
    assert response.headers["Location"] == "/auth/login"

    with app.app_context():
        assert get_db().execute(
            "SELECT * FROM user WHERE username = 'a'",
        ).fetchone() is not None

# pytest.mark.parametrizediz ao Pytest para executar a mesma função de teste com argumentos diferentes. 
# Você o usa aqui para testar diferentes entradas inválidas e mensagens de erro sem escrever o mesmo código três vezes.
@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('', '', b'Username is required.'),
    ('a', '', b'Password is required.'),
    ('test', 'test', b'already registered'),
))
def test_register_validate_input(client, username, password, message):
    response = client.post(
        'auth/register',
        # datacontém o corpo da resposta como bytes. Se você espera que um determinado valor 
        # seja renderizado na página, verifique se ele está no formato data. Bytes devem ser comparados a bytes. 
        # Se você quiser comparar texto, use get_data(as_text=True) .
        data={'username': username, 'password': password}
    )
    assert message in response.data

# Os testes para a loginvisualização são muito semelhantes aos do register. 
# Em vez de testar os dados no banco de dados, sessionvocê deve user_idconfigurá-los após fazer login.
def test_login(client, auth):
    assert client.get('/auth/login').status_code == 200
    response = auth.login()
    assert response.headers["Location"] == "/"

    with client:
        client.get('/')
        assert session['user_id'] == 1
        assert g.user['username'] == 'test'

@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('a', 'test', b'Incorrect username.'),
    ('test', 'a', b'Incorrect password.'),
))
def test_login_validate_input(auth, username, password, message):
    response = auth.login(username, password)
    assert message in response.data

# Usar clientem um withbloco permite acessar variáveis ​​de contexto, como session após o retorno da resposta. 
# Normalmente, acessar sessionfora de uma solicitação geraria um erro 
# Testar logout é o oposto de login. session não deve conter user_id após o logout.
def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert 'user_id' not in session
