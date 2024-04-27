# API Authentication Management
[![NPM](https://img.shields.io/npm/l/react)](https://github.com/heitorfoschiani/APIAuthenticationManagement/blob/main/LICENSE)

A secure Flask API that requires user authentication and manages access.

## About The Project
This project leverages Flask, Flask-RESTX, and Flask-JWT-Extended functionality to deliver an object-oriented Python solution that effectively manages user sessions and endpoint access permissions. It provides a robust foundation for any other Flask API project, offering, in addition to strong access control, database table creation on project initialization, a straightforward structure for PostgreSQL connections, and log storage for all endpoint requests. With decorators already developed for these features, integrating them into any other endpoint developed from this foundation is streamlined and efficient.

## Key Features
- **User Authentication:** Implements secure session management using JSON Web Tokens (JWT), ensuring safe user authentication processes;
- **Access Control:** Manage access control by the user privileges;
- **Security on acccess information:** Encrypts passwords in database storage and forces a rotation of the JWT token used to request endpoints;
- **PostgreSQL Integration:** Manages data through a PostgreSQL connection, offering a reliable and scalable database solution;
- **Log Storage:** Maintains comprehensive logs of all API requests.

## Getting Started
To get your project up and running with API Authentication Management, follow these simple steps.

### Prerequisites
Ensure you have the following installed:
- Python 3.10 or higher;
- PostgreSQL.

### Installation
1. Clone the repository:
    ```bash
    git clone https://github.com/heitorfoschiani/APIAuthenticationManagement.git
    ```

2. Install the required packages (It is recommended that it be carried out within a virtual environment):
    ```bash
    pip install -r requirements.txt
    ```

### Configure PostgreSQL database
1. To set up your PostgreSQL connection, first create a .env file and input your PostgreSQL connection details into it, as below. 
    ```
    DBHOST=localhost
    DBPORT=5432
    DBUSER=postgres
    DBPASSWORD=your_password123
    ```

2. Then, go to the "APIAuthenticationManagement -> app -> database -> credential.env", and update the "CREDENTIALS_FILE_PATH" variable with the path to the .env file you've saved on your computer.

3. Create a database called "AuthenticationManagement" on your postgres sever or, if you want to connect with another database, you can change the variable "DBNAME" in "APIAuthenticationManagement -> app -> database -> credential.env"

### Initialize the app
1. Run at prompt:
    ```bash
    flask run
    ```

### Test the application
1. Verify the prompt output:
    ```bash
    * Running on all addresses (0.0.0.0)
    * Running on http://127.0.0.1:5001
    ```

2. Confirm that tables were created in the database.

3. Access the swagger documentation at http://127.0.0.1:5001/auth-management

4. Create the first user in the application by making a request:
    ```
    import requests
    
    response = requests.post(
        f"http://127.0.0.1:5001/auth-management/user",
        headers = {
            "Content-type": "application/json"
        },
        json = {
          "full_name": "Bruce Wayne",
          "email": "bruce.wayne@outlook.com",
          "phone": "11912345678",
          "username": "batman",
          "password": "ImBatman",
        },
    )
    ```

## Starting a new project on top of this
1. Make sure you have knowledge about Flask and Flask-RESTX;

2. Create a new blueprint folder on "APIAuthenticationManagement -> app -> api -> blueprints";

3. Following the existing bluepirint structure "auth_management", create the same folders and files:
    ```
    your_blueprint/
    |
    ├── database/
    |    ├── tables/
    |    |    ├── your_table1.py
    |    |    ├── your_table2.py
    |    |
    |    ├── __init__.py
    |
    ├── namespaces/
    |    ├── your_namespace1/
    |    |    ├── __init__.py
    |    |    ├── models.py
    |    |    ├── parse.py
    |    |    ├── resources.py
    |    |
    |    ├── your_namespace2/
    |    |    ├── __init__.py
    |    |    ├── models.py
    |    |    ├── parse.py
    |    |    ├── resources.py
    |
    |── __init__.py
    |── register.py
    ```

4. Use your knowlege aboud Flask-RESTX and this project construction to create a new feature for your API

## Contact
For any questions, please contact-me: heitor.foschiani@outlook.com