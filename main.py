from flask import Flask, request, jsonify
import skfuzzy as fuzz
from skfuzzy import control as ctrl
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Input variables
distance = ctrl.Antecedent(universe=(0, 100), label='distance')
speed = ctrl.Antecedent(universe=(0, 60), label='speed')
traffic_light = ctrl.Antecedent(universe=(0, 1), label='traffic_light')  # 0: Red, 1: Green

# Output variable
acceleration = ctrl.Consequent(universe=(0, 20), label='acceleration')

# Membership functions
distance['near'] = fuzz.trimf(distance.universe, [0, 0, 50])
distance['medium'] = fuzz.trimf(distance.universe, [10, 50, 90])
distance['far'] = fuzz.trimf(distance.universe, [50, 100, 100])

speed['slow'] = fuzz.trimf(speed.universe, [0, 0, 30])
speed['moderate'] = fuzz.trimf(speed.universe, [10, 30, 50])
speed['fast'] = fuzz.trimf(speed.universe, [30, 60, 60])

traffic_light['red'] = fuzz.trimf(traffic_light.universe, [0, 0, 0.5])
traffic_light['green'] = fuzz.trimf(traffic_light.universe, [0.5, 1, 1])

acceleration['decelerate'] = fuzz.trimf(acceleration.universe, [0, 0, 10])
acceleration['maintain'] = fuzz.trimf(acceleration.universe, [5, 10, 15])
acceleration['accelerate'] = fuzz.trimf(acceleration.universe, [10, 20, 20])

# Rule base
rule1 = ctrl.Rule(antecedent=(distance['near'] & speed['slow'] & traffic_light['red']), consequent=acceleration['decelerate'])
rule2 = ctrl.Rule(antecedent=(distance['medium'] & speed['moderate'] & traffic_light['green']), consequent=acceleration['maintain'])
rule3 = ctrl.Rule(antecedent=(distance['far'] & speed['fast'] & traffic_light['green']), consequent=acceleration['accelerate'])

# Control system
fuzzySystem = ctrl.ControlSystem(rules=[rule1, rule2, rule3])
fuzzySystemSimulation = ctrl.ControlSystemSimulation(fuzzySystem)

# Counter for requests
request_counter = 0

@app.route('/')
def root():
    global request_counter
    return f"Chahid Ahmadi\nNumber of Requests: {request_counter}"

@app.route('/api', methods=['POST'])
def recommend_acceleration():
    global request_counter
    request_counter += 1

    data = request.get_json()

    if 'distance' not in data or 'speed' not in data or 'traffic_light' not in data:
        return jsonify({'status': 'denied', 'error': 'Invalid input. Please provide distance, speed, and traffic_light.'}), 400

    fuzzySystemSimulation.input['distance'] = int(data['distance'])
    fuzzySystemSimulation.input['speed'] = int(data['speed'])
    fuzzySystemSimulation.input['traffic_light'] = float(data['traffic_light'])
    fuzzySystemSimulation.compute()

    result = fuzzySystemSimulation.output['acceleration']

    return jsonify({'status': 'success', 'recommended_acceleration': result})

if __name__ == '__main__':
    app.run(debug=True)
