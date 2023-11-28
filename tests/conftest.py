import os
import tempfile

import pytest
from flaskr import create_app
from flaskr.db import get_db, init_db

with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')

# O appfixture chamará a fábrica e passará test_configpara configurar a aplicação 
# e o banco de dados para teste em vez de usar sua configuração de desenvolvimento local.

    @pytest.fixture
    def app():
        # cria e abre um arquivo temporario, retornando o descritor do arquivo e seu caminho
        db_fd, db_path = tempfile.mkstemp()

        app = create_app({
            # informa ao flask que o aplicativo está em modo teste
            'TESTING': True,
            # database é substituido e aponta para esse caminho temporario
            # após definir o caminho as tbls do bd são criadas e os dados de testes são inseridos
            # após o teste o arquivo temporario é fechado e removido
            'DATABASE': db_path,
        })

        with app.app_context():
            init_db()
            get_db().executescript(_data_sql)

        yield app

        os.close(db_fd)
        os.unlink(db.path)

@pytest.fixture
# o client fixture chama o app.test_client() com o objeto de aplicação criado pelo appfixture
# os testes usarão o cliente sem executar o servidor para fazer as solicitações
def client(app):
    return app.test_client()

@pytest.fixture
# o runner é semelhante ao client
# o app.test_cli_runner() cria um executor que pode chamar os comandos click registrados no aplicativo 
def runner(app):
    return app.test_cli_runner()

# Pytest usa fixtures combinando seus nomes de funções com os nomes dos argumentos nas funções de teste. 
# Por exemplo, a test_hello função que você escreverá a seguir recebe um clientargumento. 
# Pytest combina isso com a clientfunção fixture, chama-a e passa o valor retornado para a função test.

# Para a maioria das visualizações, um usuário precisa estar logado. A maneira mais fácil de fazer isso nos 
# testes é fazer uma POSTsolicitação para a loginvisualização com o cliente. Em vez de escrever isso todas as vezes, 
# você pode escrever uma classe com métodos para fazer isso e usar um acessório para passá-la ao cliente em cada teste.

class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, username='test', password='test'):
        return self._client.post(
            '/auth/login',
            data={'username': username, 'password': password}
        )
    
    def logout(self):
        return self._client.get('/auth/logout')
    
@pytest.fixture
def auth(client):
    return AuthActions(client)

