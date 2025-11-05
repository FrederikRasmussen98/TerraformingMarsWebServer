from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash, send_from_directory
import json
import os
import matplotlib.pyplot as plt
import io
import base64
import numpy as np
from flask_bcrypt import Bcrypt
from flask_wtf import FlaskForm

from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length

app = Flask(__name__)
DATA_FILE = "results.json"


# Load data
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as file:
        results = json.load(file)
else:
    results = []

@app.route('/')
def home():
    return render_template('index.html')
    


app.secret_key = 'your_secret_key'
bcrypt = Bcrypt(app)

# Mock user database
users = {'frederik': bcrypt.generate_password_hash('password123').decode('utf-8')}

# Login Form
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=6, max=20)])
    submit = SubmitField('Login')

@app.context_processor
def inject_login_form():
    # Make the login form available to all templates
    return {'login_form': LoginForm()}

@app.route('/login', methods=['POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        if username in users and bcrypt.check_password_hash(users[username], password):
            session['username'] = username
            flash('Login successful!', 'success')
        else:
            flash('Invalid username or password.', 'danger')
    return redirect(request.referrer or url_for('home'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect(request.referrer or url_for('home'))


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
    with open('results.json', 'r') as file:
        game_data = json.load(file)

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


    # Plot 1: Accumulated Scores
    fig, ax = plt.subplots(figsize=(10, 5), dpi=220)
    fig.patch.set_facecolor(bg_color)
    ax.set_facecolor(bg_color)
    for spine in ax.spines.values():
        spine.set_edgecolor('white')
        spine.set_linewidth(1.5)
        spine.set_alpha(0.5)
    ax.tick_params(axis='both', which='both', colors=tick_color)
    ax.set_xticklabels(dates, rotation=45)
    ax.set_xlabel('Date', color=tick_color, alpha=0.7)
    ax.set_ylabel('Accumulated Score', color=tick_color, alpha=0.7)

    

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
    fig2.patch.set_facecolor(bg_color)
    ax2.set_facecolor(bg_color)
    for spine in ax2.spines.values():
        spine.set_edgecolor('white')
        spine.set_linewidth(1.5)
        spine.set_alpha(0.5)
    ax2.tick_params(axis='both', which='both', colors=tick_color)
    ax2.set_xticklabels(dates, rotation=45)
    ax2.set_xlabel('Date', color=tick_color, alpha=0.7)
    ax2.set_ylabel('Points', color=tick_color, alpha=0.7)

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

        season_value = data.get("season")
        if not season_value:
            return jsonify({"message": "Season is missing."}), 400

        season = int(season_value)

        new_result = {
            "date": data.get("date"),
            "game": data.get("game"),
            "season": season,
            "players": players,
            "points": points,
            "game_scores": game_scores,
        }

        results.append(new_result)
        with open(DATA_FILE, "w") as file:
            json.dump(results, file, indent=4)

        # ======= NEW: update corps_left =======
        if os.path.exists("corps_left.json"):
            with open("corps_left.json", "r") as f:
                corps_data = json.load(f)
            if corps_data.get("fearlessDraftOn", False):
                corps_data["corpsLeft"] = max(0, corps_data.get("corpsLeft", 0) - num_players)
                with open("corps_left.json", "w") as f:
                    json.dump(corps_data, f, indent=4)
        # =======================================

        return jsonify({"message": "Result saved!"}), 200

    except Exception as e:
        print("Error while saving result:", e)
        return jsonify({"message": "Failed to save result"}), 500
@app.route('/get_corps_status')
def get_corps_status():
    if os.path.exists("corps_left.json"):
        with open("corps_left.json", "r") as f:
            data = json.load(f)
    else:
        data = {"fearlessDraftOn": False, "corpsLeft": 0}
    return jsonify(data)
@app.route("/adjust_corps", methods=["POST"])
def adjust_corps():
    try:
        data = request.json
        if os.path.exists("corps_left.json"):
            with open("corps_left.json", "r") as f:
                corps_data = json.load(f)
        else:
            corps_data = {"fearlessDraftOn": True, "corpsLeft": 0}

        corps_data["corpsLeft"] = max(0, int(data.get("corpsLeft", corps_data.get("corpsLeft", 0))))

        with open("corps_left.json", "w") as f:
            json.dump(corps_data, f, indent=4)

        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/get_results', methods=['GET'])
def get_results():
    try:
        with open('results.json', 'r') as f:
            results = json.load(f)
        print("Results loaded successfully:", results)  # Log the results
        return jsonify(results)
    except Exception as e:
        print("Error loading results:", str(e))  # Log any error
        return jsonify({"error": "Failed to load results"}), 500

@app.route('/update_results', methods=['POST'])
def update_results():
    updated_results = request.json
    with open('results.json', 'w') as f:
        json.dump(updated_results, f, indent=4)
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




@app.route('/result.json')
def serve_json():
    return send_from_directory('.', 'results.json')  # Serve result.json from the root folder

if __name__ == "__main__":
    app.run(debug=True, port = 5000, host = '0.0.0.0')
