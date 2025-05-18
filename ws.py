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
    # Get the players from the query parameters (passed via the URL)
    selected_players = request.args.getlist('players')
    season = int(request.args.get('season', 1))  # Default to season 1 if not provided

    # Load the results from the JSON file
    with open('results.json', 'r') as file:
        game_data = json.load(file)
    game_data = [entry for entry in game_data if entry.get('season', 1) == season]
    print("SEASON")
    print(season)
    # Extract all unique players and dates
    players = set(player for entry in game_data for player in entry['players'])
    dates = sorted(set(entry['date'] for entry in game_data))
    
    # If specific players are selected, filter the data
    if selected_players:
        players = [player for player in players if player in selected_players]

    
    # Initialize player scores dictionary with 0 for each player on each date
    player_scores = {player: [0] * len(dates) for player in players}
    player_game_points = {player: [0] * len(dates) for player in players}
    player_game_scores = {player: [None] * len(dates) for player in players}
    # Initialize player wins dictionary to track the number of wins
    player_wins = {player: 0 for player in players}
    player_points = {player: 0 for player in players}
    # Initialize player game count dictionary
    player_games = {player: 0 for player in players}
    
    # Map each date to its index in the dates list
    date_index_map = {date: idx for idx, date in enumerate(dates)}
    
    # Populate player scores and count total wins and total games played
    for entry in game_data:
        date_idx = date_index_map[entry['date']]
        num_players = len(entry['players'])
        for idx, player in enumerate(entry['players']):
            if player not in players:  # Skip if player is not in selected list
                continue
            score = int(entry['points'][idx])  # Convert score to integer
            player_scores[player][date_idx] = score
            game_score = entry.get('game_scores', [None] * num_players)[idx]  # Use None if no game_score exists
        
            # Store the game score for the player on that date
            player_game_scores[player][date_idx] = game_score
            # Check if the player has won (score equals number of players)
            if score == num_players:
                player_wins[player] += 1
            
            
            # Count the number of games this player has played
            player_games[player] += 1
    
    currentWinner = ""
    currentWinnerScore = 0
    # Accumulate scores over time for each player
    for player in player_scores:
        # Create a copy of the original scores
        player_game_points[player] = list(player_scores[player])
        
        # Update winner info based on final game score
        if player_game_points[player][-1] > currentWinnerScore:
            currentWinner = player
            currentWinnerScore = player_game_points[player][-1]
        
        # Accumulate scores over time
        for i in range(1, len(player_scores[player])):
            player_scores[player][i] += player_scores[player][i - 1]
        
        # Get final accumulated score
        player_points[player] = player_scores[player][-1]
    print("WINNER:")
    print(currentWinner)
    # Calculate player statistics
    player_stats = {}
    for player in players:
        scores = player_scores[player]
        # Get the game scores for the player (game_scores)
        game_scores = player_game_scores[player]
        #print(scores)
        #print(np.mean(scores))
        print()
        print(player)
        print(player_wins[player])
        
        player_stats[player] = {
            'mean_points': np.mean([x for x in player_game_points[player] if x != 0]) if player_game_points[player] else 0,
            'std_points': np.std([x for x in player_game_points[player] if x != 0]) if len([x for x in player_game_points[player]  if x != 0]) > 1 else 0,
            # For game scores (new)
            'max_game_score': max([score for score in game_scores if score is not None], default=0),
            'min_game_score': min([score for score in game_scores if score is not None], default=0),
            'total_games': player_games[player],  # Total games played by the player
            'total_wins': player_wins[player],
            'total_points': player_points[player],
        }
       

    # Define player colors
    player_colors = {
        "Frederik": "green",
        "Best": "blue",
        "Magnus": "gold",
        "Raschke": "black",
        "Alstrup": "red",
        "MicrobeMorten": "gray"
    }

    # Generate the plot
    fig, ax = plt.subplots(figsize=(10, 5), dpi=220)

    # Set background color to Mars-like brown with more transparency (alpha=0.5)
    fig.patch.set_facecolor((139/255, 69/255, 19/255, 0.4))  # Reduce opacity to 50%
    ax.set_facecolor((139/255, 69/255, 19/255, 0.4))  # Reduce opacity to 50%

    # Set the spines (axes borders) to white and transparent (alpha=0.5)
    for spine in ax.spines.values():
        spine.set_edgecolor('white')
        spine.set_linewidth(1.5)  # Optional: adjust spine thickness
        spine.set_alpha(0.5)  # Set spine transparency

    # Set the ticks (axis marks) to white
    ax.tick_params(axis='both', which='both', colors='white')
    # Rotate x-axis labels by 45 degrees
    ax.set_xticklabels(dates, rotation=45)

    # Set the labels for axes to white with more transparency
    ax.set_xlabel('Date', color='white', alpha=0.7)
    ax.set_ylabel('Accumulated Score', color='white', alpha=0.7)

    # Plot each player's scores with color mapping and more transparency (alpha=0.5)
    for player, scores in player_scores.items():
        ax.step(dates, scores, marker='o', label=player, color=player_colors.get(player, 'gray'), alpha=0.7, where ='post')  # Set alpha to 0.5 for more transparency

    # Set title and make it white with more transparency
    # ax.set_title('Accumulated Game Scores Over Time', color='white', alpha=0.7)

    # Adjust the legend and make its background transparent
    legend = ax.legend()
    for text in legend.get_texts():
        text.set_color('white')  # Set legend text color to white
    
    # Adjust the layout to prevent clipping of text
    plt.tight_layout()
    # Make legend background transparent
    legend.get_frame().set_edgecolor('none')  # Removes the border
    legend.get_frame().set_facecolor('none')  # Makes the background transparent

    # Save the plot to a BytesIO object
    img_stream = io.BytesIO()
    fig.savefig(img_stream, format='png')
    img_stream.seek(0)

    # Encode the image as base64
    img_base64 = base64.b64encode(img_stream.read()).decode('utf-8')




    # Example statistics
    stats = {
        'Total Wins': player_wins,  # Add total wins for each player
        'Total Points': player_points,
        'Player Stats': player_stats,  # Include player-specific stats
        'Current Winner': currentWinner
    }
    
 # === Plot 2 (New Plot) ===
    fig2, ax2 = plt.subplots(figsize=(10, 5), dpi=220)
    
      # Set background color to Mars-like brown with more transparency (alpha=0.5)
    fig2.patch.set_facecolor((139/255, 69/255, 19/255, 0.4))  # Reduce opacity to 50%
    ax2.set_facecolor((139/255, 69/255, 19/255, 0.4))  # Reduce opacity to 50%



    # Set the spines (axes borders) to white and transparent (alpha=0.5)
    for spine in ax2.spines.values():
        spine.set_edgecolor('white')
        spine.set_linewidth(1.5)  # Optional: adjust spine thickness
        spine.set_alpha(0.5)  # Set spine transparency
    # Set the ticks (axis marks) to white
    ax2.tick_params(axis='both', which='both', colors='white')
    # Rotate x-axis labels by 45 degrees
    ax2.set_xticklabels(dates, rotation=45)
    
    ax2.set_xlabel('Date', color='white', alpha=0.7)
    ax2.set_ylabel('Points', color='white', alpha=0.7)
    
    
    for player, scores in player_game_points.items():
        ax2.plot(dates, scores, marker='o', label=player, color=player_colors.get(player, 'gray'), alpha=0.7)  # Set alpha to 0.5 for more transparency


    # Adjust the legend and make its background transparent
    legend2 = ax2.legend()
    for text in legend2.get_texts():
        text.set_color('white')  # Set legend text color to white
        
    # Adjust the layout to prevent clipping of text
    plt.tight_layout()
    # Make legend background transparent
    legend2.get_frame().set_edgecolor('none')  # Removes the border
    legend2.get_frame().set_facecolor('none')  # Makes the background transparent

    img_stream2 = io.BytesIO()
    fig2.savefig(img_stream2, format='png')
    img_stream2.seek(0)
    img_base64_2 = base64.b64encode(img_stream2.read()).decode('utf-8')

    # Return the plot and statistics as a JSON response
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
    data = request.form
    num_players = int(data.get("max_players"))
    players = data.getlist("player")[:num_players]
    points = data.getlist("points")[:num_players]
    game_scores = data.getlist("game_score")[:num_players]

    # Convert game_scores to None if empty
    game_scores = [int(score) if score else None for score in game_scores]

    # Extract season value
    season = int(data.get("season"))

    new_result = {
        "date": data.get("date"),
        "game": data.get("game"),
        "season": season,  # Add the season to the result
        "players": players,
        "points": points,
        "game_scores": game_scores,
    }

    results.append(new_result)
    with open(DATA_FILE, "w") as file:
        json.dump(results, file, indent=4)
    
    return jsonify({"message": "Result saved!"}), 200


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
