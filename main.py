# Author: Heitor Foschiani de Souza
# Email: heitor.foschiani@outlook.com
# Phone-number: (11) 9 4825-3334

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(
        host='127.0.0.1',
        port=5001,
        debug=True,
    )