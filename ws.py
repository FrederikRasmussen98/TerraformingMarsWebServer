"""
TerraformingMarsWebServer - Flask application for tracking Terraforming Mars board game sessions
Season 3 Release: Jupiter-themed with enhanced features

Features:
- Multi-season support (Mars, Venus, Jupiter)
- Drag-and-drop player ranking (desktop + mobile)
- Awards and milestones tracking
- Role-based access control
- Map history tracking with CSV
- Performance statistics and plotting
- Admin features (fearless draft management)
"""

from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash, send_from_directory
import json
import os
import csv
import matplotlib.pyplot as plt
import io
import base64
import numpy as np
from flask_bcrypt import Bcrypt
from flask_wtf import FlaskForm
from werkzeug.utils import secure_filename

from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length

from utils import load_json_file, save_json_file, load_corps_data, save_corps_data, update_corps_left, setup_plot_style

# ===== Flask Application Configuration =====
app = Flask(__name__)
app.secret_key = 'your_secret_key_change_this_in_production'
bcrypt = Bcrypt(app)

# ===== File & Folder Configuration =====
DATA_FILE = "results.json"
USER_SETTINGS_FILE = "user_settings.json"
UPLOAD_FOLDER = "static/music"
ALLOWED_EXTENSIONS = {'mp3'}
IMAGE_UPLOAD_FOLDER = "static/images"
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['IMAGE_UPLOAD_FOLDER'] = IMAGE_UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(IMAGE_UPLOAD_FOLDER, exist_ok=True)

# Function to parse PLAYER_CREDENTIALS.txt file
def load_credentials_and_roles():
    """Parse PLAYER_CREDENTIALS.txt and extract credentials and roles"""
    credentials = {}
    roles = {}
    
    credentials_file = 'PLAYER_CREDENTIALS.txt'
    if os.path.exists(credentials_file):
        try:
            with open(credentials_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                current_username = None
                current_password = None
                
                for line in lines:
                    line = line.strip()
                    
                    if line.startswith('Username:'):
                        current_username = line.replace('Username:', '').strip()
                    elif line.startswith('Password:'):
                        current_password = line.replace('Password:', '').strip()
                        if current_username:
                            credentials[current_username] = current_password
                    elif line.startswith('Role:'):
                        current_role = line.replace('Role:', '').strip()
                        if current_username:
                            roles[current_username] = current_role
        except Exception as e:
            print(f"Error parsing credentials file: {e}")
    
    return credentials, roles

# Load credentials and roles from file
PLAYER_CREDENTIALS, PLAYER_ROLES = load_credentials_and_roles()

# Hash passwords on first load
users = {username: bcrypt.generate_password_hash(password).decode('utf-8') 
         for username, password in PLAYER_CREDENTIALS.items()}

# Load data
results = load_json_file(DATA_FILE, [])

# ===== Routes - Page Views =====

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate_plot', methods=['GET'])
def generate_plot():
    # Get the players from query parameters
    selected_players = request.args.getlist('players')
    
    # Parse season safely
    season_param = request.args.get('season', '1')
    try:
        season = int(season_param)
    except ValueError:
        season = 1  # default to season 1 if invalid

    # Load game data
    game_data = load_json_file('results.json', [])

    # Filter by season
    game_data = [entry for entry in game_data if entry.get('season', 1) == season]

    # Extract unique players and dates
    players = set(player for entry in game_data for player in entry['players'])
    dates = sorted(set(entry['date'] for entry in game_data))

    # Filter players if specified
    if selected_players:
        players = [player for player in players if player in selected_players]

    # Initialize dictionaries
    player_scores = {player: [0]*len(dates) for player in players}
    player_game_points = {player: [0]*len(dates) for player in players}
    player_game_scores = {player: [None]*len(dates) for player in players}
    player_wins = {player: 0 for player in players}
    player_points = {player: 0 for player in players}
    player_games = {player: 0 for player in players}
    player_milestones = {player: 0 for player in players}
    player_award_firsts = {player: 0 for player in players}
    player_award_seconds = {player: 0 for player in players}

    date_index_map = {date: idx for idx, date in enumerate(dates)}

    # Populate scores and stats
    for entry in game_data:
        date_idx = date_index_map[entry['date']]
        num_players = len(entry['players'])
        for idx, player in enumerate(entry['players']):
            if player not in players:
                continue
            score = int(entry['points'][idx])
            player_scores[player][date_idx] = score
            game_score = entry.get('game_scores', [None]*num_players)[idx]
            player_game_scores[player][date_idx] = game_score
            if score == num_players:
                player_wins[player] += 1
            player_games[player] += 1
        
        # Count milestones for this game
        if 'milestones' in entry:
            for milestone in entry['milestones']:
                winner = milestone.get('winner')
                if winner in players:
                    player_milestones[winner] += 1
        
        # Count awards for this game
        if 'awards' in entry:
            for award in entry['awards']:
                first_winner = award.get('first')
                if first_winner and first_winner in players:
                    player_award_firsts[first_winner] += 1
                second_winner = award.get('second')
                if second_winner and second_winner in players:
                    player_award_seconds[second_winner] += 1

    # Accumulate scores and determine current winner
    currentWinner = ""
    currentWinnerScore = 0
    for player in player_scores:
        player_game_points[player] = list(player_scores[player])
        if player_game_points[player][-1] > currentWinnerScore:
            currentWinner = player
            currentWinnerScore = player_game_points[player][-1]
        for i in range(1, len(player_scores[player])):
            player_scores[player][i] += player_scores[player][i-1]
        player_points[player] = player_scores[player][-1]

    # Player stats
    player_stats = {}
    for player in players:
        game_scores = player_game_scores[player]
        filtered_points = [x for x in player_game_points[player] if x != 0]
        player_stats[player] = {
            'mean_points': np.mean(filtered_points) if filtered_points else 0,
            'std_points': np.std(filtered_points) if len(filtered_points) > 1 else 0,
            'max_game_score': max([score for score in game_scores if score is not None], default=0),
            'min_game_score': min([score for score in game_scores if score is not None], default=0),
            'total_games': player_games[player],
            'total_wins': player_wins[player],
            'total_points': player_points[player],
            'milestones': player_milestones[player],
            'award_firsts': player_award_firsts[player],
            'award_seconds': player_award_seconds[player],
        }

    # Define colors per season
    if season == 1:  # Mars colors
        bg_color = (139/255, 69/255, 19/255, 0.4)  # Mars-like
        player_colors = {
            "Frederik": "green",
            "Best": "blue",
            "Magnus": "gold",
            "Raschke": "black",
            "Alstrup": "red",
            "MicrobeMorten": "gray"
        }
        tick_color = 'white'
    elif season == 2:  # Mars colors:  # Venus colors
        bg_color = (255/255, 245/255, 230/255, 0.4)  # soft Venus-like
        player_colors = {
            "Frederik": "green",
            "Best": "blue",
            "Magnus": "gold",
            "Raschke": "black",
            "Alstrup": "red",
            "MicrobeMorten": "gray"
        }
        tick_color = 'black'
        
    elif season == 3:  # Jupiter colors
        bg_color = (13/255, 27/255, 42/255, 0.6)  # Deep space blue
        tick_color = 'white'
        
        player_colors = {
            "Frederik": "green",
            "Best": "blue",
            "Magnus": "gold",
            "Raschke": "black",
            "Alstrup": "red",
            "MicrobeMorten": "gray"
        }


    # Plot 1: Accumulated Scores
    fig, ax = plt.subplots(figsize=(10, 5), dpi=220)
    setup_plot_style(ax, fig, bg_color, tick_color, 'Date', 'Accumulated Score', dates)

    

    for player, scores in player_scores.items():
        ax.step(dates, scores, marker='o', label=player, color=player_colors.get(player, 'gray'), alpha=0.7, where='post')

    legend = ax.legend()
    for text in legend.get_texts():
        text.set_color('white')
    plt.tight_layout()
    legend.get_frame().set_edgecolor('none')
    legend.get_frame().set_facecolor('none')

    img_stream = io.BytesIO()
    fig.savefig(img_stream, format='png')
    img_stream.seek(0)
    img_base64 = base64.b64encode(img_stream.read()).decode('utf-8')

    # Plot 2: Game Points
    fig2, ax2 = plt.subplots(figsize=(10, 5), dpi=220)
    setup_plot_style(ax2, fig2, bg_color, tick_color, 'Date', 'Points', dates)

    for player, scores in player_game_points.items():
        ax2.plot(dates, scores, marker='o', label=player, color=player_colors.get(player, 'gray'), alpha=0.7)

    plt.tight_layout()

    img_stream2 = io.BytesIO()
    fig2.savefig(img_stream2, format='png')
    img_stream2.seek(0)
    img_base64_2 = base64.b64encode(img_stream2.read()).decode('utf-8')

    # Prepare stats
    stats = {
        'Total Wins': player_wins,
        'Total Points': player_points,
        'Player Stats': player_stats,
        'Current Winner': currentWinner
    }

    return jsonify({
        'plot_url': img_base64,
        'plot2_url': img_base64_2,
        'stats': stats
    })


@app.route('/plots', methods=['GET'])
def show_plots():
    # Extract the list of unique players
    players = set(player for entry in results for player in entry['players'])

    # Pass the players to the template
    return render_template('plots.html', players=players)
@app.route('/log', methods=['POST'])
def log_result():
    try:
        data = request.form
        print("Received form data:", data)  # Debug print

        players = data.getlist("player")
        num_players = len(players)

        points = data.getlist("points")[:num_players]
        game_scores = data.getlist("game_score")[:num_players]
        game_scores = [int(score) if score is not None and score != '' else None for score in game_scores]
        
        # Get milestones data
        milestone_names = data.getlist("milestone_name")
        milestone_winners = data.getlist("milestone_winner")
        milestones = []
        for i in range(len(milestone_names)):
            if milestone_names[i] and milestone_winners[i]:
                milestones.append({
                    "name": milestone_names[i],
                    "winner": milestone_winners[i]
                })
        
        # Get awards data
        award_names = data.getlist("award_name")
        award_first_counts = data.getlist("award_first_count")
        award_second_counts = data.getlist("award_second_count")
        award_firsts = data.getlist("award_first")
        award_seconds = data.getlist("award_second")
        
        awards = []
        first_idx = 0
        second_idx = 0
        
        for i in range(len(award_names)):
            if not award_names[i]:
                continue
                
            award_entry = {
                "name": award_names[i],
                "first": []
            }
            
            # Get first place winners
            first_count = int(award_first_counts[i]) if i < len(award_first_counts) else 1
            for _ in range(first_count):
                if first_idx < len(award_firsts) and award_firsts[first_idx]:
                    award_entry["first"].append(award_firsts[first_idx])
                first_idx += 1
            
            # Get second place winners
            second_count = int(award_second_counts[i]) if i < len(award_second_counts) else 0
            if second_count > 0:
                award_entry["second"] = []
                for _ in range(second_count):
                    if second_idx < len(award_seconds) and award_seconds[second_idx]:
                        award_entry["second"].append(award_seconds[second_idx])
                    second_idx += 1
            
            # Simplify format if only one winner
            if len(award_entry["first"]) == 1:
                award_entry["first"] = award_entry["first"][0]
            if "second" in award_entry and len(award_entry["second"]) == 1:
                award_entry["second"] = award_entry["second"][0]
            
            awards.append(award_entry)

        season_value = data.get("season")
        if not season_value:
            return jsonify({"success": False, "message": "Season is missing."}), 400

        season = int(season_value)

        new_result = {
            "date": data.get("date"),
            "game": data.get("game"),
            "season": season,
            "players": players,
            "points": points,
            "game_scores": game_scores,
            "milestones": milestones,
            "awards": awards
        }

        results.append(new_result)
        save_json_file(DATA_FILE, results)

        # Update corps_left
        update_corps_left(num_players)

        return jsonify({"success": True, "message": "Result saved!"}), 200

    except Exception as e:
        print("Error while saving result:", e)
        return jsonify({"success": False, "message": "Failed to save result"}), 500
@app.route('/get_corps_status')
def get_corps_status():
    data = load_corps_data()
    return jsonify(data)
@app.route("/adjust_corps", methods=["POST"])
def adjust_corps():
    try:
        data = request.json
        corps_data = load_corps_data()
        if not corps_data.get("fearlessDraftOn"):
            corps_data["fearlessDraftOn"] = True
        
        corps_data["corpsLeft"] = max(0, int(data.get("corpsLeft", corps_data.get("corpsLeft", 0))))
        save_corps_data(corps_data)

        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/get_results', methods=['GET'])
def get_results():
    try:
        results = load_json_file('results.json', [])
        print("Results loaded successfully:", results)  # Log the results
        return jsonify(results)
    except Exception as e:
        print("Error loading results:", str(e))  # Log any error
        return jsonify({"error": "Failed to load results"}), 500

@app.route('/update_results', methods=['POST'])
def update_results():
    updated_results = request.json
    save_json_file('results.json', updated_results)
    return jsonify({"status": "success"})

@app.route('/update_season', methods=['POST'])
def update_season():
    season = int(request.form['season'])
    players = rank_players(season)
    return jsonify(players=players)

def rank_players(season):
    # Sort the players based on their points
    players = player_data[season]
    sorted_players = sorted(players, key=lambda x: x['points'], reverse=True)

    # Assign ranks
    for i, player in enumerate(sorted_players):
        player['rank'] = i + 1

    return sorted_players
@app.route('/manage_results')
def manage_results():
    return render_template('manage_results.html')

@app.route('/houseRules')
def houseRules():
    return render_template('houseRules.html')


@app.route('/wheelOfNames')
def wheelOfNames():
    return render_template('wheelOfNames.html')  # Replace with your Hall of Fame page HTML

# === Authentication Routes ===

@app.route('/api/check_login', methods=['GET'])
def check_login():
    if 'username' in session:
        return jsonify({'logged_in': True, 'username': session['username']})
    return jsonify({'logged_in': False})

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if username in users and bcrypt.check_password_hash(users[username], password):
        session['username'] = username
        session['role'] = PLAYER_ROLES.get(username, 'user')
        return jsonify({'success': True, 'username': username, 'role': session['role']})
    return jsonify({'success': False, 'message': 'Invalid username or password'})

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.pop('username', None)
    return jsonify({'success': True})

@app.route('/settings')
def settings():
    if 'username' not in session:
        return redirect(url_for('home'))
    role = session.get('role', 'user')
    return render_template('settings.html', username=session['username'], role=role, is_admin=role=='admin')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_image_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS

@app.route('/api/upload_music', methods=['POST'])
def upload_music():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    if 'music' not in request.files:
        return jsonify({'success': False, 'message': 'No file uploaded'}), 400
    
    file = request.files['music']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        username = session['username']
        filename = f"{username}Win.mp3"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return jsonify({'success': True, 'message': 'Music uploaded successfully'})
    
    return jsonify({'success': False, 'message': 'Invalid file type'}), 400

@app.route('/api/get_winner_image', methods=['GET'])
def get_winner_image():
    """Get the selected winner image path for a specific player (public endpoint)"""
    player = request.args.get('player')
    if not player:
        return jsonify({'success': False, 'message': 'Player parameter required'}), 400
    
    user_settings = load_json_file(USER_SETTINGS_FILE, {})
    selected_image = user_settings.get(player, {}).get('winner_image')
    
    if selected_image:
        # Check which extension exists
        image_dir = app.config['IMAGE_UPLOAD_FOLDER']
        for ext in ['.png', '.jpg', '.jpeg']:
            filepath = os.path.join(image_dir, selected_image + ext)
            if os.path.exists(filepath):
                image_path = f"/static/images/{selected_image}{ext}"
                return jsonify({'success': True, 'image_path': image_path})
        # If file not found, fall back to default
        image_path = f"/static/images/{player}.png"
    else:
        image_path = f"/static/images/{player}.png"
    
    return jsonify({'success': True, 'image_path': image_path})

@app.route('/api/get_winner_images', methods=['GET'])
def get_winner_images():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    username = session['username']
    
    # Get user settings
    user_settings = load_json_file(USER_SETTINGS_FILE, {})
    current_image = user_settings.get(username, {}).get('winner_image', username)
    
    # List available images in slots (3 max)
    images = []
    image_dir = app.config['IMAGE_UPLOAD_FOLDER']
    
    # Check slots 1-3
    for slot in range(1, 4):
        slot_name = f"{username}_slot{slot}"
        # Check for .png, .jpg, .jpeg
        for ext in ['.png', '.jpg', '.jpeg']:
            filepath = os.path.join(image_dir, slot_name + ext)
            if os.path.exists(filepath):
                images.append({
                    'name': slot_name,
                    'filename': slot_name + ext,
                    'slot': slot,
                    'display_name': f'Image {slot}'
                })
                break
    
    # Add default image if exists
    default_img = f"{username}.png"
    if os.path.exists(os.path.join(image_dir, default_img)):
        images.insert(0, {
            'name': username,
            'filename': default_img,
            'slot': 0,
            'display_name': 'Default'
        })
    
    return jsonify({'images': images, 'current': current_image})

@app.route('/api/upload_winner_image', methods=['POST'])
def upload_winner_image():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    if 'image' not in request.files:
        return jsonify({'success': False, 'message': 'No file uploaded'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'}), 400
    
    if file and allowed_image_file(file.filename):
        username = session['username']
        image_dir = app.config['IMAGE_UPLOAD_FOLDER']
        
        # Find first available slot (1-3)
        available_slot = None
        for slot in range(1, 4):
            slot_name = f"{username}_slot{slot}"
            # Check if slot is empty
            slot_exists = False
            for ext in ['.png', '.jpg', '.jpeg']:
                if os.path.exists(os.path.join(image_dir, slot_name + ext)):
                    slot_exists = True
                    break
            if not slot_exists:
                available_slot = slot
                break
        
        if available_slot is None:
            return jsonify({'success': False, 'message': 'Maximum 3 images allowed. Delete one first.'}), 400
        
        # Get file extension and save to slot
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{username}_slot{available_slot}.{ext}"
        filepath = os.path.join(image_dir, filename)
        file.save(filepath)
        
        # Auto-select the newly uploaded image
        user_settings = load_json_file(USER_SETTINGS_FILE, {})
        if username not in user_settings:
            user_settings[username] = {}
        image_name = filename.rsplit('.', 1)[0]  # Remove extension for name
        user_settings[username]['winner_image'] = image_name
        save_json_file(USER_SETTINGS_FILE, user_settings)
        
        return jsonify({'success': True, 'message': f'Image uploaded to slot {available_slot}', 'filename': filename, 'slot': available_slot})
    
    return jsonify({'success': False, 'message': 'Invalid file type. Use PNG, JPG, or JPEG'}), 400

@app.route('/api/save_winner_image', methods=['POST'])
def save_winner_image():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    data = request.get_json()
    image_name = data.get('image')
    username = session['username']
    
    # Load and update settings
    user_settings = load_json_file(USER_SETTINGS_FILE, {})
    if username not in user_settings:
        user_settings[username] = {}
    user_settings[username]['winner_image'] = image_name
    save_json_file(USER_SETTINGS_FILE, user_settings)
    
    return jsonify({'success': True, 'message': 'Winner image saved'})

@app.route('/api/delete_winner_image', methods=['POST'])
def delete_winner_image():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    data = request.get_json()
    image_name = data.get('image_name')
    
    if not image_name:
        return jsonify({'success': False, 'message': 'Image name required'}), 400
    
    username = session['username']
    
    # Don't allow deleting default image
    if image_name == username:
        return jsonify({'success': False, 'message': 'Cannot delete default image'}), 400
    
    image_dir = app.config['IMAGE_UPLOAD_FOLDER']
    
    # Try to find and delete the file
    deleted = False
    for ext in ['.png', '.jpg', '.jpeg']:
        filepath = os.path.join(image_dir, image_name + ext)
        if os.path.exists(filepath):
            os.remove(filepath)
            deleted = True
            break
    
    if not deleted:
        return jsonify({'success': False, 'message': 'Image not found'}), 404
    
    # If the deleted image was selected, revert to default
    user_settings = load_json_file(USER_SETTINGS_FILE, {})
    if username in user_settings and user_settings[username].get('winner_image') == image_name:
        user_settings[username]['winner_image'] = username
        save_json_file(USER_SETTINGS_FILE, user_settings)
    
    return jsonify({'success': True, 'message': 'Image deleted successfully'})



@app.route('/result.json')
def serve_json():
    return send_from_directory('.', 'results.json')  # Serve result.json from the root folder

# === FEARLESS DRAFT ADMIN ROUTES ===

@app.route('/api/get_fearless_draft', methods=['GET'])
def get_fearless_draft():
    """Get current fearless draft settings (admin only)"""
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    role = session.get('role', 'user')
    if role != 'admin':
        return jsonify({'success': False, 'message': 'Admin access required'}), 403
    
    try:
        corps_data = load_corps_data()
        return jsonify({
            'success': True,
            'fearlessDraftOn': corps_data.get('fearlessDraftOn', False),
            'corpsLeft': corps_data.get('corpsLeft', 0)
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/update_fearless_draft', methods=['POST'])
def update_fearless_draft():
    """Update fearless draft settings (admin only)"""
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    role = session.get('role', 'user')
    if role != 'admin':
        return jsonify({'success': False, 'message': 'Admin access required'}), 403
    
    try:
        data = request.get_json()
        fearless_on = data.get('fearlessDraftOn', False)
        corps_left = int(data.get('corpsLeft', 0))
        
        # Validate corps_left
        if corps_left < 0 or corps_left > 100:
            return jsonify({'success': False, 'message': 'Corporations left must be between 0 and 100'}), 400
        
        # Load and update corps data
        corps_data = load_corps_data()
        corps_data['fearlessDraftOn'] = fearless_on
        corps_data['corpsLeft'] = corps_left
        save_corps_data(corps_data)
        
        return jsonify({
            'success': True,
            'message': 'Fearless draft settings updated',
            'fearlessDraftOn': fearless_on,
            'corpsLeft': corps_left
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ===== Map Tracking Functions & API Endpoints =====

def get_last_map():
    """Get the last played map from CSV file"""
    import csv
    map_history_file = 'map_history.csv'
    if not os.path.exists(map_history_file):
        return None
    
    try:
        with open(map_history_file, 'r', encoding='utf-8', newline='') as f:
            # Read all lines and get the last data entry
            lines = f.readlines()
            # Skip header and get last non-empty line
            data_lines = [line for line in lines[1:] if line.strip()]
            if data_lines:
                last_line = data_lines[-1].strip()
                # Parse CSV with proper handling of spaces and special characters
                reader = csv.reader([last_line])
                row = next(reader)
                if len(row) >= 2:
                    return row[1].strip()  # map_name is second column
    except Exception as e:
        print(f"Error reading map history: {e}")
    
    return None

def update_map_history(map_name):
    """Add a new map entry to the CSV file"""
    import csv
    from datetime import datetime
    map_history_file = 'map_history.csv'
    
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # Check if file exists and get size BEFORE opening
        file_exists = os.path.exists(map_history_file)
        file_is_empty = not file_exists or os.path.getsize(map_history_file) == 0 if file_exists else True
        
        with open(map_history_file, 'a', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            # Write header if file is new or empty
            if file_is_empty:
                writer.writerow(['timestamp', 'map_name'])
            writer.writerow([timestamp, map_name])
        return True
    except Exception as e:
        print(f"Error updating map history: {e}")
        import traceback
        traceback.print_exc()
        return False

@app.route('/api/get_last_map', methods=['GET'])
def api_get_last_map():
    """API endpoint to get the last played map"""
    try:
        last_map = get_last_map()
        return jsonify({
            'success': True,
            'lastMap': last_map
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/update_map_history', methods=['POST'])
def api_update_map_history():
    """API endpoint to update the last played map"""
    try:
        data = request.get_json()
        map_name = data.get('mapName', '').strip()
        
        if not map_name:
            return jsonify({'success': False, 'message': 'Map name is required'}), 400
        
        if update_map_history(map_name):
            return jsonify({
                'success': True,
                'message': f'Map history updated: {map_name}'
            })
        else:
            return jsonify({'success': False, 'message': 'Failed to update map history'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port = 5000, host = '0.0.0.0')

