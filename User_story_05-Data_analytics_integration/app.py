from flask import Flask, render_template, jsonify
import random

app = Flask(__name__)

def generate_dummy_data():
    return {
        "donations": [random.randint(10, 100) for _ in range(12)],  # Monthly donation count
        "volunteers": [random.randint(5, 50) for _ in range(12)],  # Monthly volunteer count
        "registrations": [random.randint(20, 150) for _ in range(12)]  # Monthly registrations
    }

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/data")
def get_data():
    data = generate_dummy_data()
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)
