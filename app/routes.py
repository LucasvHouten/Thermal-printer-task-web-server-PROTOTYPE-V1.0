from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from datetime import datetime
from app import db
from app.models import Task
from app.scheduler import schedule_task_print
from app.printer import printer_manager

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Main page showing tasks"""
    tasks = Task.query.order_by(Task.print_datetime).all()
    return render_template('index.html', tasks=tasks)

@bp.route('/tasks/add', methods=['GET', 'POST'])
def add_task():
    """Add a new task"""
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        print_date = request.form.get('print_date')
        print_time = request.form.get('print_time')
        reminder_minutes = request.form.get('reminder_minutes')

        if not title or not print_date or not print_time:
            return jsonify({'success': False, 'error': 'Missing required fields'})

        # Parse date and time
        try:
            print_datetime_str = f"{print_date} {print_time}"
            print_datetime = datetime.strptime(print_datetime_str, '%Y-%m-%d %H:%M')
        except ValueError:
            return jsonify({'success': False, 'error': 'Invalid date or time format'})

        # Handle reminder minutes
        reminder_minutes_int = None
        if reminder_minutes and reminder_minutes.isdigit():
            reminder_minutes_int = int(reminder_minutes)

        # Create new task
        task = Task(
            title=title,
            description=description,
            print_datetime=print_datetime,
            reminder_minutes=reminder_minutes_int,
            is_printed=False,
            is_reminder_printed=False
        )

        db.session.add(task)
        db.session.commit()

        return redirect(url_for('main.index'))

    return render_template('add_task.html')

@bp.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a task"""
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({'success': True})

@bp.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """Get a specific task"""
    task = Task.query.get_or_404(task_id)
    return jsonify(task.to_dict())

@bp.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """Update a task"""
    task = Task.query.get_or_404(task_id)
    data = request.json
    
    if 'title' in data:
        task.title = data['title']
    if 'description' in data:
        task.description = data['description']
    if 'print_datetime' in data:
        try:
            task.print_datetime = datetime.strptime(data['print_datetime'], '%Y-%m-%d %H:%M')
        except ValueError:
            return jsonify({'success': False, 'error': 'Invalid date format'})
    if 'reminder_minutes' in data:
        task.reminder_minutes = data['reminder_minutes']
    
    db.session.commit()
    return jsonify({'success': True, 'task': task.to_dict()})

@bp.route('/tasks/<int:task_id>/print', methods=['POST'])
def print_task(task_id):
    """Print a task immediately"""
    if schedule_task_print(task_id):
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': 'Failed to print task'})

@bp.route('/printer/status', methods=['GET'])
def printer_status():
    """Get the status of the printer"""
    is_connected = printer_manager.is_connected
    return jsonify({
        'connected': is_connected
    })

@bp.route('/printer/connect', methods=['POST'])
def connect_printer():
    """Connect to the printer"""
    success = printer_manager.connect()
    return jsonify({'success': success})
