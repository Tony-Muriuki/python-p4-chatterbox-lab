from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'GET':
        msg_arr = Message.query.order_by(Message.created_at.asc()).all()
        # Ensure each message is converted to a dictionary
        msg_dict = [message.to_dict() for message in msg_arr]
        
        response = make_response(
            jsonify(msg_dict),
            200
        )
        return response

    elif request.method == 'POST':
        # Extract 'body' and 'username' from request data
        data = request.get_json()
        body = data.get('body')
        username = data.get('username')

        if not body or not username:
            return make_response(jsonify({'error': 'Missing body or username'}), 400)
        
        # Create a new Message instance
        new_message = Message(body=body, username=username)
        
        # Add and commit the new message to the database
        db.session.add(new_message)
        db.session.commit()
        
        # Return the newly created message as JSON
        response = make_response(
            jsonify(new_message.to_dict()),
            201  # HTTP status code for created resource
        )
        return response

@app.route('/messages/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def messages_by_id(id):
    if request.method == 'GET':
        message = Message.query.filter_by(id=id).first()
        if message is None:
            return make_response(jsonify({'error': 'Message not found'}), 404)
        
        # Convert the message to a dictionary and return as JSON
        response = make_response(
            jsonify(message.to_dict()),
            200
        )
        return response

    elif request.method == 'PATCH':
        message = Message.query.filter_by(id=id).first()
        if message is None:
            return make_response(jsonify({'error': 'Message not found'}), 404)

        # Extract the updated 'body' from the request data
        data = request.get_json()
        new_body = data.get('body')

        if not new_body:
            return make_response(jsonify({'error': 'No body provided for update'}), 400)

        # Update the message body
        message.body = new_body
        db.session.commit()

        # Return the updated message as JSON
        response = make_response(
            jsonify(message.to_dict()),
            200
        )
        return response

    elif request.method == 'DELETE':
        message = Message.query.filter_by(id=id).first()
        if message is None:
            return make_response(jsonify({'error': 'Message not found'}), 404)

        # Delete the message from the database
        db.session.delete(message)
        db.session.commit()

        # Return a success message or empty response
        return make_response(jsonify({'message': 'Message deleted'}), 200)

if __name__ == '__main__':
    app.run (port=5555)
