from flask import Blueprint, render_template, request, redirect, url_for
from models import db, Feedback

# Define Blueprint
routes_blueprint = Blueprint('routes', __name__)

@routes_blueprint.route('/')
def home():
    return render_template('index.html')

@routes_blueprint.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        username = request.form['username']
        feedback_text = request.form['feedback']

        new_feedback = Feedback(username=username, feedback=feedback_text)
        db.session.add(new_feedback)
        db.session.commit()

        return redirect(url_for('routes.home'))

    return render_template('feedback.html')
