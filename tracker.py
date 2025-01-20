from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tracking_advanced.db'  # Replace with PostgreSQL for production
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Models
class Target(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    device_id = db.Column(db.String(100), unique=True, nullable=False)

class LocationLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    target_id = db.Column(db.Integer, db.ForeignKey('target.id'), nullable=False)
    latitude = db.Column(db.String(50), nullable=True)
    longitude = db.Column(db.String(50), nullable=True)
    accuracy = db.Column(db.String(50), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Initialize Database
@app.before_first_request
def create_tables():
    db.create_all()

# Add new target
@app.route('/add_target', methods=['POST'])
def add_target():
    try:
        data = request.json
        new_target = Target(name=data['name'], device_id=data['device_id'])
        db.session.add(new_target)
        db.session.commit()
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Track location
@app.route('/track', methods=['POST'])
def track():
    try:
        data = request.json
        target = Target.query.filter_by(device_id=data['device_id']).first()
        if not target:
            return jsonify({"status": "error", "message": "Target not found"}), 404

        new_log = LocationLog(
            target_id=target.id,
            latitude=data['latitude'],
            longitude=data['longitude'],
            accuracy=data['accuracy']
        )
        db.session.add(new_log)
        db.session.commit()
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Get location history for a target
@app.route('/history/<int:target_id>', methods=['GET'])
def get_history(target_id):
    try:
        logs = LocationLog.query.filter_by(target_id=target_id).all()
        results = [
            {
                "latitude": log.latitude,
                "longitude": log.longitude,
                "accuracy": log.accuracy,
                "timestamp": log.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            }
            for log in logs
        ]
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# List all targets
@app.route('/targets', methods=['GET'])
def list_targets():
    try:
        targets = Target.query.all()
        results = [{"id": t.id, "name": t.name, "device_id": t.device_id} for t in targets]
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    create_tables()
    app.run(host='0.0.0.0', port=5000)
