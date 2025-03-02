from flask import Flask
from config import Config
from models import db
from routes import routes_blueprint

app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
db.init_app(app)

# Register the blueprint
app.register_blueprint(routes_blueprint)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create tables in the database
    app.run(debug=True)
