from flask import Blueprint, request, jsonify

api = Blueprint('api', __name__)


@api.route('/track_event/', methods=['POST'])
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
    user_id = request.args.get('user_id')
    event_type = request.args.get('event_type')
    timestamp = request.args.get('timestamp')
    data = request.json.get('data')
    source = request.args.get('source')

    # Here you would process the incoming data
    # For now, we will just return the received data
    event = {
        "user_id": user_id,
        "event_type": event_type,
        "timestamp": timestamp,
        "data": data,
        "source": source
    }
    return jsonify({"status": "success", "event": event}), 200
