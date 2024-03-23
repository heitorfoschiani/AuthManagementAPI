# API Authentication Management
A secure Flask API that requires user authentication and manages access

## About The Project
This project leverages Flask, Flask-RESTX, and Flask-JWT-Extended functionality to deliver an object-oriented Python solution that effectively manages user sessions and endpoint access permissions. It provides a robust foundation for any other Flask API project, offering, in addition to strong access control, database table creation on project initialization, a straightforward structure for PostgreSQL connections, and log storage for all endpoint requests. With decorators already developed for these features, integrating them into any other endpoint developed from this foundation is streamlined and efficient.

## Key Features
- **User Authentication:** Implements secure session management using JSON Web Tokens (JWT), ensuring safe user authentication processes.
- **Access Control:** Manage access control by the user privileges.
- **PostgreSQL Integratio:** Manages data through a PostgreSQL connection, offering a reliable and scalable database solution.
- **Log Storage:** Maintains comprehensive logs of all API requests.

## Getting Started
To get your project up and running with API Authentication Management, follow these simple steps.

### Prerequisites
Ensure you have the following installed:
- Python 3.10 or higher
- PostgreSQL

### Installation
1. Clone the repository:
```bash
git clone https://github.com/yourusername/APIAuthenticationManagement.git
```

2. Install the required packages (It is recommended that it be carried out within a virtual environment):
```bash
pip install -r requirements.txt
```

## Start PostgreSQL database
- Create a database called "AuthenticationManagement" or, if you want to connect with another database, you might change the variable "dbname" on "APIAuthenticationManagement -> app -> database -> connection.py"

# Star Project
1. Run at prompt:
```bash
flask run