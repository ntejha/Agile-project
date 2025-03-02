from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    feedback = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"<Feedback {self.username}>"
