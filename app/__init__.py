import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from apscheduler.schedulers.background import BackgroundScheduler

db = SQLAlchemy()
migrate = Migrate()
scheduler_instance = BackgroundScheduler()

def create_app(config_class=None):
    app = Flask(__name__)
    
    # Configure the app
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprint
    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)
    
    with app.app_context():
        # Import modules
        from app import models, printer, scheduler as task_scheduler

        # Create database tables if they don't exist
        db.create_all()

        # Start the background scheduler
        if not scheduler_instance.running:
            scheduler_instance.start()
            task_scheduler.initialize_scheduler(scheduler_instance)

    return app
