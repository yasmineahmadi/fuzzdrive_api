from flask import Flask, request, jsonify
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

app = Flask(__name__)

# Define fuzzy logic system
distance = ctrl.Antecedent(np.arange(0, 101, 1), 'distance')
speed = ctrl.Antecedent(np.arange(0, 61, 1), 'speed')
acceleration = ctrl.Consequent(np.arange(0, 21, 1), 'acceleration')

# ... (Define membership functions, rules, and control system as in the previous code)
@app.route('/')
def welcome():
    return "hello"
@app.route('/api', methods=['POST'])
def fuzzy_controller():
    try:
        data = request.get_json()
        distance_value = data['distance']
        speed_value = data['speed']

        acceleration_sim = ctrl.ControlSystemSimulation(acceleration_ctrl)
        acceleration_sim.input['distance'] = distance_value
        acceleration_sim.input['speed'] = speed_value

        # Compute acceleration
        acceleration_sim.compute()

        # Return the result
        result = {'recommendedAcceleration': acceleration_sim.output['acceleration']}
        return jsonify(result)

    except Exception as e:
        print(e)
        return jsonify({'error': 'Internal Server Error'}), 500

if __name__ == '__main__':
    app.run(port=5000)
