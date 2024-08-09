from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

api = Blueprint('api', __name__)


@api.route('/track_event/', methods=['POST'])
@jwt_required()
def track_event():
    """
    Endpoint for tracking user events
    ---
    parameters:
      - name: user_id
        in: query
        type: string
        required: true
      - name: event_type
        in: query
        type: string
        required: true
      - name: timestamp
        in: query
        type: string
        required: true
      - name: data
        in: body
        type: object
        required: true
      - name: source
        in: query
        type: string
        required: true
    responses:
      200:
        description: Event tracked successfully
    """
    user_id = get_jwt_identity()
    event_type = request.args.get('event_type')
    timestamp = request.args.get('timestamp')
    data = request.json.get('data')
    source = request.args.get('source')

    # Здесь вы можете обработать входящие данные
    event = {
        "user_id": user_id,
        "event_type": event_type,
        "timestamp": timestamp,
        "data": data,
        "source": source
    }
    return jsonify({"status": "success", "event": event}), 200
