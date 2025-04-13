from flask import Flask, request, jsonify
from algorithm import main  # Import your algorithm from algorithm.py

app = Flask(__name__)

@app.route('/meal_plan', methods=['POST'])
def get_meal_plan():
    data = request.get_json()
    goal = data.get('goal')
    target_amount = data.get('target_amount')

    if not goal or not target_amount:
        return jsonify({"error": "Goal and target_amount are required."}), 400

    result = main(goal, target_amount)

    if isinstance(result, str):
        return jsonify({"error": result}), 500
    else:
        return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True) # debug=True for development. Remove it in production.