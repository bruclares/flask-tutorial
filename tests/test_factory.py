from flaskr import create_app


def test_config():
    assert not create_app().testing
    assert create_app({'TESTING': True}).testing

# Você adicionou a hellorota como exemplo ao escrever a fábrica no início do tutorial. 
# Ele retorna “Hello, World!”, então o teste verifica se os dados de resposta correspondem.
def test_hello(client):
    reponse = client.get('/hello')
    assert reponse.data == b'Hello, Word!'

