from flask import Flask, request, jsonify
import skfuzzy as fuzz
from skfuzzy import control as ctrl
from flask_cors import CORS
from typing import Dict, Any, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

class FuzzyAccelerationController:
    def __init__(self):
        """Initialize the fuzzy logic control system."""
        self.request_counter = 0
        self.fuzzy_system = self._setup_fuzzy_system()
        
    def _setup_fuzzy_system(self) -> ctrl.ControlSystemSimulation:
        """Configure the fuzzy logic variables and rules."""
        # Input variables
        distance = ctrl.Antecedent(universe=(0, 100), label='distance')
        speed = ctrl.Antecedent(universe=(0, 60), label='speed')
        traffic_light = ctrl.Antecedent(universe=(0, 1), label='traffic_light')  # 0: Red, 1: Green

        # Output variable
        acceleration = ctrl.Consequent(universe=(0, 20), label='acceleration')

        # Membership functions
        distance.automf(3, names=['near', 'medium', 'far'])
        speed.automf(3, names=['slow', 'moderate', 'fast'])
        
        traffic_light['red'] = fuzz.trimf(traffic_light.universe, [0, 0, 0.5])
        traffic_light['green'] = fuzz.trimf(traffic_light.universe, [0.5, 1, 1])

        acceleration['decelerate'] = fuzz.trimf(acceleration.universe, [0, 0, 10])
        acceleration['maintain'] = fuzz.trimf(acceleration.universe, [5, 10, 15])
        acceleration['accelerate'] = fuzz.trimf(acceleration.universe, [10, 20, 20])

        # Rule base - expanded for better coverage
        rules = [
            ctrl.Rule(distance['near'] & speed['slow'] & traffic_light['red'], acceleration['decelerate']),
            ctrl.Rule(distance['near'] & speed['moderate'] & traffic_light['red'], acceleration['decelerate']),
            ctrl.Rule(distance['medium'] & speed['moderate'] & traffic_light['green'], acceleration['maintain']),
            ctrl.Rule(distance['far'] & speed['fast'] & traffic_light['green'], acceleration['accelerate']),
            ctrl.Rule(distance['far'] & speed['moderate'] & traffic_light['green'], acceleration['maintain']),
            ctrl.Rule(distance['medium'] & speed['slow'] & traffic_light['green'], acceleration['maintain']),
            ctrl.Rule(distance['near'] & speed['fast'] & traffic_light['red'], acceleration['decelerate']),
            ctrl.Rule(distance['far'] & speed['slow'] & traffic_light['green'], acceleration['accelerate'])
        ]

        control_system = ctrl.ControlSystem(rules)
        return ctrl.ControlSystemSimulation(control_system)

    def get_recommendation(self, input_data: Dict[str, float]) -> Tuple[Dict[str, Any], int]:
        """Process input data and return acceleration recommendation."""
        self.request_counter += 1
        logger.info(f"Processing request #{self.request_counter}")

        try:
            # Validate input
            if not all(key in input_data for key in ['distance', 'speed', 'traffic_light']):
                return {'status': 'error', 'message': 'Missing required parameters'}, 400

            # Convert and validate values
            distance_val = float(input_data['distance'])
            speed_val = float(input_data['speed'])
            traffic_val = float(input_data['traffic_light'])

            if not (0 <= distance_val <= 100):
                return {'status': 'error', 'message': 'Distance must be between 0-100'}, 400
            if not (0 <= speed_val <= 60):
                return {'status': 'error', 'message': 'Speed must be between 0-60'}, 400
            if traffic_val not in (0, 1):
                return {'status': 'error', 'message': 'Traffic light must be 0 (red) or 1 (green)'}, 400

            # Compute fuzzy logic
            self.fuzzy_system.input['distance'] = distance_val
            self.fuzzy_system.input['speed'] = speed_val
            self.fuzzy_system.input['traffic_light'] = traffic_val
            self.fuzzy_system.compute()

            result = round(float(self.fuzzy_system.output['acceleration']), 2)
            
            return {
                'status': 'success',
                'recommended_acceleration': result,
                'request_count': self.request_counter
            }, 200

        except ValueError as e:
            logger.error(f"Value error: {str(e)}")
            return {'status': 'error', 'message': 'Invalid input values'}, 400
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return {'status': 'error', 'message': 'Internal server error'}, 500

# Initialize controller
controller = FuzzyAccelerationController()

@app.route('/')
def root():
    """Root endpoint showing basic information."""
    return f"Fuzzy Logic Acceleration Controller\nNumber of Requests: {controller.request_counter}"

@app.route('/api', methods=['POST'])
def recommend_acceleration():
    """API endpoint for acceleration recommendations."""
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': 'No JSON data provided'}), 400
    
    response, status_code = controller.get_recommendation(data)
    return jsonify(response), status_code

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
