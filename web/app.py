"""
Flask web application for POS image processing
Upload POS images and get complete cooking instructions
"""

import os
import json
from pathlib import Path
from datetime import datetime
from flask import Flask, request, render_template, jsonify, send_from_directory
from werkzeug.utils import secure_filename

import sys
sys.path.append(str(Path(__file__).parent.parent))

from pos_parser.image_processor import POSImageProcessor
from pos_parser.recipe_database import RecipeDatabase
from pos_parser.triage_engine import TriageEngine
from pos_parser.instruction_generator import InstructionGenerator


# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'kitchen-landscape-secret-key'
app.config['UPLOAD_FOLDER'] = Path(__file__).parent / 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}

# Create upload folder if it doesn't exist
app.config['UPLOAD_FOLDER'].mkdir(exist_ok=True)

# Initialize components
recipe_db = RecipeDatabase()
image_processor = POSImageProcessor()
triage_engine = TriageEngine(recipe_db)
instruction_generator = InstructionGenerator(recipe_db)


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_pos_image():
    """
    Upload POS image and process it
    Returns parsed order information
    """
    if 'pos_image' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['pos_image']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400

    try:
        # Save file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        filepath = app.config['UPLOAD_FOLDER'] / filename

        file.save(str(filepath))

        # Process image
        ticket = image_processor.process_image(str(filepath))

        # Add to triage engine
        triage_engine.add_ticket(ticket)

        # Generate instructions for all items
        instructions_list = []
        for item in ticket.items:
            # Find corresponding task
            for task in triage_engine.cooking_tasks:
                if (task.ticket_id == ticket.ticket_id and
                    task.dish_id == item.dish_name):
                    instructions = instruction_generator.generate_instructions(task)
                    if instructions:
                        instructions_list.append(
                            instruction_generator.export_instructions_to_dict(instructions)
                        )
                    break

        # Get triage report
        triage_report = triage_engine.get_triage_report()

        return jsonify({
            'success': True,
            'ticket': {
                'ticket_id': ticket.ticket_id,
                'table_number': ticket.table_number,
                'timestamp': ticket.timestamp.isoformat(),
                'server_name': ticket.server_name,
                'items': [
                    {
                        'dish_name': item.dish_name,
                        'quantity': item.quantity,
                        'modifiers': item.modifiers,
                        'course': item.course
                    }
                    for item in ticket.items
                ],
                'special_instructions': ticket.special_instructions
            },
            'instructions': instructions_list,
            'triage': {
                'total_active_tasks': triage_report['total_active_tasks'],
                'total_cook_time_minutes': triage_report['total_cook_time_minutes'],
                'bottleneck_stations': triage_report['bottleneck_stations']
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/triage-report')
def get_triage_report():
    """Get current triage report"""
    try:
        report = triage_engine.get_triage_report()

        # Format for JSON response
        formatted_report = {
            'total_active_tasks': report['total_active_tasks'],
            'total_cook_time_minutes': report['total_cook_time_minutes'],
            'bottleneck_stations': report['bottleneck_stations'],
            'station_workloads': {
                station: {
                    'station': workload.station,
                    'task_count': workload.task_count,
                    'total_cook_time': workload.total_cook_time,
                    'complexity_score': workload.complexity_score,
                    'tasks': [
                        {
                            'table': task.table_number,
                            'dish': task.dish_name,
                            'priority': task.priority_score
                        }
                        for task in workload.active_tasks
                    ]
                }
                for station, workload in report['station_workloads'].items()
            },
            'critical_tasks': [
                {
                    'table': task.table_number,
                    'dish': task.dish_name,
                    'priority': task.priority_score,
                    'cook_time': task.cook_time_minutes,
                    'station': task.station
                }
                for task in report['critical_tasks']
            ]
        }

        return jsonify(formatted_report)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/instructions/<dish_id>')
def get_dish_instructions(dish_id):
    """Get instructions for a specific dish"""
    try:
        recipe = recipe_db.get_recipe(dish_id)

        if not recipe:
            return jsonify({'error': 'Recipe not found'}), 404

        # Create a sample task for instruction generation
        from pos_parser.triage_engine import CookingTask
        from datetime import datetime

        task = CookingTask(
            ticket_id="SAMPLE",
            table_number="XX",
            dish_id=dish_id,
            dish_name=recipe.name,
            quantity=1,
            modifiers=[],
            station=recipe.station,
            cook_time_minutes=recipe.cook_time_minutes,
            difficulty=recipe.difficulty,
            course="entree",
            ticket_time=datetime.now()
        )

        instructions = instruction_generator.generate_instructions(task)

        if not instructions:
            return jsonify({'error': 'Could not generate instructions'}), 500

        return jsonify(
            instruction_generator.export_instructions_to_dict(instructions)
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/recipes')
def list_recipes():
    """List all available recipes"""
    try:
        recipes = recipe_db.get_all_recipes()

        recipe_list = [
            {
                'id': recipe.id,
                'name': recipe.name,
                'station': recipe.station,
                'cook_time': recipe.cook_time_minutes,
                'difficulty': recipe.difficulty
            }
            for recipe in recipes.values()
        ]

        return jsonify(recipe_list)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/reset-triage', methods=['POST'])
def reset_triage():
    """Reset triage engine (clear all tickets)"""
    global triage_engine
    triage_engine = TriageEngine(recipe_db)
    return jsonify({'success': True, 'message': 'Triage engine reset'})


@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'recipes_loaded': len(recipe_db.get_all_recipes()),
        'active_tasks': len(triage_engine.cooking_tasks)
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
