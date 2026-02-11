from flask_cors import CORS
from werkzeug.security import generate_password_hash
from app import db
from app import create_app
# from app.Routes.Login_Routes2 import login_user
from app.Models import *

app = create_app()

if __name__ == "__main__":
    print("Lancement de l'application Flask...")
    app.run(debug=True)
