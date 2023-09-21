# Author: Heitor Foschiani de Souza
# Email: heitor.foschiani@outlook.com
# Number: (11) 9 4825-3334

# Importing python files from the project
from app import create_app

# Starting app
app = create_app()

# Running app
if __name__ == '__main__':
    app.run(
        host='127.0.0.1',
        port=5001,
        debug=True,
    )