from flask import Flask, jsonify, request
import redis
from prometheus_flask_exporter import PrometheusMetrics
from flask import Flask, send_from_directory, render_template
from flask_restful import Resource, Api
from package.patient import Patients, Patient
from package.doctor import Doctors, Doctor
from package.appointment import Appointments, Appointment
from package.common import Common
from package.medication import Medication, Medications
from package.department import Departments, Department
from package.nurse import Nurse, Nurses
from package.room import Room, Rooms
from package.procedure import Procedure, Procedures 
from package.prescribes import Prescribes, Prescribe
from package.undergoes import Undergoess, Undergoes
from datetime import datetime
import json
import os
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Counter, Histogram, Gauge
import time
from dotenv import load_dotenv

app = Flask(__name__, static_url_path='')
api = Api(app)

# Initialize Prometheus metrics
metrics = PrometheusMetrics(app)
metrics.info('app_info', 'Hospital Management System', version='1.0.0')

# Custom metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP Requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency', ['method', 'endpoint'])
ACTIVE_USERS = Gauge('active_users', 'Number of active users')
DB_CONNECTIONS = Gauge('database_connections', 'Active database connections')
REDIS_CONNECTIONS = Gauge('redis_connections', 'Active Redis connections')

# Load environment variables
load_dotenv()


redis_client = None
try:
    redis_host = os.getenv('REDIS_HOST', 'localhost')
    redis_port = int(os.getenv('REDIS_PORT', 6379))
    redis_password = os.getenv('REDIS_PASSWORD', None)
    
    redis_client = redis.Redis(
        host=redis_host,
        port=redis_port,
        password=redis_password,
        decode_responses=True,  # Converts responses to strings
        socket_connect_timeout=5  # Timeout for connection
    )
    # Test the connection
    redis_client.ping()
    print("✅ Connected to Redis successfully")
except redis.exceptions.ConnectionError as e:
    print(f"❌ Could not connect to Redis: {e}")
    redis_client = None  # App will still run, but without caching

@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    # Record request metrics
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.endpoint,
        status=response.status_code
    ).inc()
    
    # Record latency
    if hasattr(request, 'start_time'):
        REQUEST_LATENCY.labels(
            method=request.method,
            endpoint=request.endpoint
        ).observe(time.time() - request.start_time)
    
    return response


# ===== 3. Example: Modify an Existing API to Use Redis Caching =====
# Let's modify the Patients GET endpoint (in package/patient.py) as an example.
# You would apply similar logic to other resources.

# First, you need to add caching logic to your Patients resource class.
# Here's a generic cache decorator you can use:

def cache_response(timeout=300):  # 5 minutes default timeout
    """Decorator to cache Flask-RESTful GET responses in Redis."""
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            # Skip caching if Redis is not available
            if not redis_client:
                return func(self, *args, **kwargs)
            
            # Create a unique cache key based on the request
            cache_key = f"cache:{self.__class__.__name__}:{func.__name__}:{str(kwargs)}"
            
            # Try to get cached result
            cached_result = redis_client.get(cache_key)
            if cached_result:
                print(f"Cache HIT for {cache_key}")
                # You would return the appropriate Flask-RESTful response
                # This is a simplified example
                return jsonify(eval(cached_result))
            
            # If not cached, execute the function
            print(f"Cache MISS for {cache_key}")
            result = func(self, *args, **kwargs)
            
            # Cache the result (simplified - you need to extract data from result)
            # In practice, you would serialize the result data appropriately
            if hasattr(result, 'data'):
                redis_client.setex(cache_key, timeout, str(result.data))
            
            return result
        return wrapper
    return decorator


# Add API resources first
api.add_resource(Patients, '/patient')
api.add_resource(Patient, '/patient/<int:id>')
api.add_resource(Doctors, '/doctor')
api.add_resource(Doctor, '/doctor/<int:id>')
api.add_resource(Appointments, '/appointment')
api.add_resource(Appointment, '/appointment/<int:id>')
api.add_resource(Common, '/common')
api.add_resource(Medications, '/medication')
api.add_resource(Medication, '/medication/<int:code>')
api.add_resource(Departments, '/department')
api.add_resource(Department, '/department/<int:department_id>')
api.add_resource(Nurses, '/nurse')
api.add_resource(Nurse, '/nurse/<int:id>')
api.add_resource(Rooms, '/room')
api.add_resource(Room, '/room/<int:room_no>')
api.add_resource(Procedures, '/procedure')
api.add_resource(Procedure, '/procedure/<int:code>')
api.add_resource(Prescribes, '/prescribes')
api.add_resource(Undergoess, '/undergoes')

# Routes

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                          'favicon.ico',mimetype='image/vnd.microsoft.icon')

@app.route('/')
def index():
    return app.send_static_file('index.html')


@app.route('/health')
def health_check():
    health_status = {
        "status": "healthy",
        "service": "Hospital Management System API",
        "timestamp": datetime.now().isoformat(),
        "metrics": {
            "prometheus_endpoint": "/metrics"
        }
    }

    # Database check
    try:
        from package.model import conn
        conn.execute('SELECT 1')
        health_status["database"] = "connected"
        DB_CONNECTIONS.set(1)
    except Exception as e:
        health_status["database"] = "disconnected"
        DB_CONNECTIONS.set(0)
        health_status["database_error"] = str(e)

    # Redis check
    if redis_client:
        try:
            redis_client.ping()
            health_status["redis"] = "connected"
            REDIS_CONNECTIONS.set(1)
        except Exception as e:
            health_status["redis"] = "disconnected"
            REDIS_CONNECTIONS.set(0)
            health_status["redis_error"] = str(e)
    else:
        health_status["redis"] = "disabled"

    return jsonify(health_status), 200


@app.route('/metrics')
def metrics_endpoint():
    """Expose Prometheus metrics"""
    from prometheus_client import generate_latest
    return generate_latest(), 200, {'Content-Type': 'text/plain'}

# Add a simple test endpoint
@app.route('/api/test')
def test_api():
    return {"message": "API is working", "status": "success"}, 200

if __name__ == '__main__':
    host = os.getenv('APP_HOST', '0.0.0.0')
    port = int(os.getenv('APP_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    print(f"Starting app with Redis: {'Enabled' if redis_client else 'Disabled'}")
    print(f"Prometheus metrics available at: http://{host}:{port}/metrics")
    
    app.run(debug=debug, host=host, port=port)