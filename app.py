from flask import Flask, jsonify, request, render_template, redirect, url_for
import db
import os
import mimetypes
from werkzeug.utils import secure_filename
from uuid import uuid4

# Register common audio MIME types for Windows environments
mimetypes.add_type('audio/mpeg', '.mp3')
mimetypes.add_type('audio/mp4', '.m4a')
mimetypes.add_type('audio/ogg', '.ogg')
mimetypes.add_type('audio/wav', '.wav')
mimetypes.add_type('audio/webm', '.webm')

app = Flask(__name__)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB maximum upload size
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['IMAGE_FOLDER'] = os.path.join(app.config['UPLOAD_FOLDER'], 'images')
app.config['AUDIO_FOLDER'] = os.path.join(app.config['UPLOAD_FOLDER'], 'audio')
app.config['CHARACTER_FOLDER'] = os.path.join(app.config['UPLOAD_FOLDER'], 'characters')

# Ensure upload directories exist
os.makedirs(app.config['IMAGE_FOLDER'], exist_ok=True)
os.makedirs(app.config['AUDIO_FOLDER'], exist_ok=True)
os.makedirs(app.config['CHARACTER_FOLDER'], exist_ok=True)

# Initialize database on startup
with app.app_context():
    db.init_db()

def save_uploaded_file(file, folder):
    """Helper to save uploaded files with a unique name."""
    if file:
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid4().hex}_{filename}"
        file_path = os.path.join(folder, unique_filename)
        file.save(file_path)
        return file_path.replace('\\', '/')
    return None

@app.route('/')
def root():
    """Redirect root to Adesha's page."""
    return redirect(url_for('adesha'))

@app.route('/adesha')
def adesha():
    """Renders Adesha's page."""
    return render_template('user_page.html', user='adesha')

@app.route('/levon')
def levon():
    """Renders Levon's page."""
    return render_template('user_page.html', user='levon')

@app.route('/api/envelopes/<recipient>', methods=['GET'])
def get_envelopes(recipient):
    """Retrieves all envelopes for a specific recipient."""
    try:
        envelopes = db.get_envelopes_by_recipient(recipient)
        return jsonify(envelopes), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/envelopes', methods=['POST'])
def create_envelope():
    """Creates a new envelope."""
    try:
        title = request.form.get('title')
        text_message = request.form.get('text_message')
        recipient = request.form.get('recipient')

        if not title or not text_message or not recipient:
            return jsonify({"error": "Title, message, and recipient are required"}), 400

        image_file = request.files.get('image')
        audio_file = request.files.get('audio')

        image_path = save_uploaded_file(image_file, app.config['IMAGE_FOLDER'])
        if image_path: image_path = '/' + image_path.lstrip('/')
        
        audio_path = save_uploaded_file(audio_file, app.config['AUDIO_FOLDER'])
        if audio_path: audio_path = '/' + audio_path.lstrip('/')

        envelope_id = db.create_envelope(title, text_message, recipient, image_path, audio_path)
        return jsonify({"id": envelope_id, "message": "Envelope created successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/envelopes/<int:envelope_id>', methods=['GET'])
def get_envelope(envelope_id):
    """Retrieves a specific envelope by ID."""
    try:
        envelope = db.get_envelope_by_id(envelope_id)
        if envelope:
            return jsonify(envelope), 200
        return jsonify({"error": "Envelope not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/envelopes/<int:envelope_id>', methods=['PUT'])
def update_envelope(envelope_id):
    """Updates an existing envelope."""
    try:
        title = request.form.get('title')
        text_message = request.form.get('text_message')
        recipient = request.form.get('recipient')

        current = db.get_envelope_by_id(envelope_id)
        if not current:
            return jsonify({"error": "Envelope not found"}), 404

        title = title or current['title']
        text_message = text_message or current['text_message']
        recipient = recipient or current['recipient']

        image_file = request.files.get('image')
        audio_file = request.files.get('audio')

        image_path = current['image_path']
        if image_file:
            image_path = save_uploaded_file(image_file, app.config['IMAGE_FOLDER'])
            if image_path: image_path = '/' + image_path.lstrip('/')

        audio_path = current['audio_path']
        if audio_file:
            audio_path = save_uploaded_file(audio_file, app.config['AUDIO_FOLDER'])
            if audio_path: audio_path = '/' + audio_path.lstrip('/')

        db.update_envelope(envelope_id, title, text_message, recipient, image_path, audio_path)
        return jsonify({"message": "Envelope updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/envelopes/<int:envelope_id>', methods=['DELETE'])
def delete_envelope(envelope_id):
    """Deletes an envelope."""
    try:
        db.delete_envelope(envelope_id)
        return jsonify({"message": "Envelope deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/characters/<path:image_path>', methods=['DELETE'])
def delete_character(image_path):
    """Deletes a character's position, and removes the image if it's user-uploaded."""
    try:
        recipient = request.args.get('recipient')
        if not recipient:
            return jsonify({"error": "Recipient is required"}), 400

        # Ensure image_path starts with / to match DB
        if not image_path.startswith('/'):
            image_path = '/' + image_path

        # If it's a user-uploaded character, delete the record and the file
        if db.is_user_character(recipient, image_path):
            db.remove_user_character(recipient, image_path)
            db.remove_character_position(recipient, image_path)

            # Convert URL path to filesystem path
            file_path = image_path.lstrip('/')
            if os.path.exists(file_path):
                os.remove(file_path)
        else:
            # It's a global character, just hide it for this user
            db.hide_character_position(recipient, image_path)

        return jsonify({"message": "Character deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/characters/<recipient>', methods=['GET'])
def get_characters(recipient):
    """Retrieves all characters (global + user-specific) and their saved positions."""
    try:
        import random
        # Global characters
        images_folder = 'static/assets/images'
        global_files = [f for f in os.listdir(images_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg'))]
        all_image_paths = [f'/static/assets/images/{f}' for f in global_files]

        # User-specific characters
        user_files = db.get_user_characters(recipient)
        all_image_paths.extend(user_files)

        saved_positions = db.get_all_character_positions(recipient)

        characters = []
        for image_path in all_image_paths:
            if image_path in saved_positions:
                pos = saved_positions[image_path]
                if pos.get('hidden'):
                    continue
                characters.append({
                    'image_path': image_path,
                    'top': pos['top'],
                    'left': pos['left']
                })
            else:
                # New image: Generate random safe position
                is_left = (len(characters) % 2 == 0)
                left_val = random.uniform(0, 20) if is_left else random.uniform(80, 95)
                top_val = random.uniform(5, 90)

                left_str = f"{left_val:.2f}%"
                top_str = f"{top_val:.2f}%"

                db.save_character_position(recipient, image_path, top_str, left_str)
                characters.append({
                    'image_path': image_path,
                    'top': top_str,
                    'left': left_str
                })

        return jsonify(characters), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/characters/upload', methods=['POST'])
def upload_character():
    """Uploads a new character image for a specific user."""
    try:
        recipient = request.form.get('recipient')
        image_file = request.files.get('image')

        if not recipient or not image_file:
            return jsonify({"error": "Recipient and image are required"}), 400

        image_path = save_uploaded_file(image_file, app.config['CHARACTER_FOLDER'])
        # save_uploaded_file returns path like 'static/uploads/characters/uuid_name.png'
        url_path = f'/{image_path}'

        db.add_user_character(recipient, url_path)

        # Generate random position for the new character
        import random
        is_left = (random.choice([True, False]))
        left_val = random.uniform(0, 20) if is_left else random.uniform(80, 95)
        top_val = random.uniform(5, 90)
        db.save_character_position(recipient, url_path, f"{top_val:.2f}%", f"{left_val:.2f}%")

        return jsonify({"message": "Character uploaded successfully", "image_path": url_path}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/characters/position', methods=['POST'])
def update_character_position():
    """Updates the position of a character."""
    try:
        data = request.json
        recipient = data.get('recipient')
        image_path = data.get('image_path')
        top = data.get('top')
        left = data.get('left')

        if not recipient or not image_path or not top or not left:
            return jsonify({"error": "recipient, image_path, top, and left are required"}), 400

        db.save_character_position(recipient, image_path, top, left)
        return jsonify({"message": "Position updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run('0.0.0.0', debug=True, port=5000)
