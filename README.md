# TerraformingMarsWebServer

A web server for tracking Terraforming Mars board game sessions with seasonal records, drag-and-drop player rankings, awards/milestones tracking, and detailed game statistics.

## Features

### Core Features
- **Season 3 Support**: Jupiter-themed season with dynamic styling and color schemes
- **Drag-and-Drop Ranking**: Intuitive ranking system for both desktop (drag) and mobile (long-press) devices
- **Player Management**: Support for up to 6 players with role-based access control
- **Game Logging**: 
  - Manual score entry with numpad support on mobile devices
  - Awards and milestones tracking with winners
  - Game history with detailed statistics
- **Spin the Wheel**: 
  - Spin the Names for random player selection
  - Spin the Moons for map/location selection
  - Spin the Map with CSV-based map history tracking
  - Excludes last-played options from available choices

### Analytics & Statistics
- **Comprehensive Statistics**: Win counts, point averages, performance trends
- **Hall of Fame**: Track seasonal winners and achievements
- **Results Plotting**: Visual representation of player performance over time
- **Data Export**: Backup and restore game results

### Administration
- **Role-Based Access Control**: Admin and user roles with specific permissions
- **Fearless Draft Admin**: Special admin feature for house rule tracking
- **Settings Management**: User preferences for music, images, and display options
- **Responsive Design**: Optimized for desktop, tablet, and mobile devices

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd TerraformingMarsWebServer
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure credentials:
   - Edit `PLAYER_CREDENTIALS.txt` with player usernames, passwords, and roles
   - First player listed should have role: `admin`

5. Run the web server:
   ```bash
   python ws.py
   ```
   - Access at `http://localhost:5000`

## Usage

### Recording Game Results
1. Login with player credentials
2. Select the season and number of players
3. Use drag-and-drop (desktop) or click-to-place (all devices) to rank players
4. Enter game scores with award/milestone winners
5. Submit to save the game result

### Map Tracking (Spin the Map)
- Navigate to "Spin the Map" wheel
- Spin to select a random map
- After confirming a map was used, click "Mark as last played map"
- Last played map is excluded from future spins (CSV-tracked)
- Map history stored in `map_history.csv`

### Admin Features
- **Fearless Draft**: Toggle and manage corporation count via Settings
- **User Management**: Roles defined in `PLAYER_CREDENTIALS.txt`

## Project Structure

```
├── ws.py                    # Main Flask application & API endpoints
├── utils.py                 # Helper functions for data processing
├── requirements.txt         # Python dependencies
├── PLAYER_CREDENTIALS.txt   # Player authentication & roles
├── map_history.csv          # CSV tracking of played maps
├── results.json             # Game results storage
├── user_settings.json       # User preferences
│
├── templates/               # HTML templates
│   ├── index.html          # Main game logging form (1777 lines)
│   ├── base.html           # Base template with navigation
│   ├── results.html        # Results display page
│   ├── plots.html          # Performance statistics & charts
│   ├── hallOfFame.html     # Season winners & achievements
│   ├── wheelOfNames.html   # Spin the Wheel features
│   ├── settings.html       # User & admin settings
│   ├── houseRules.html     # Custom game rules
│   ├── manage_results.html # Results management
│   ├── navbar.html         # Navigation component
│   └── navbar.html         # Navigation component
│
├── static/                  # Static assets
│   ├── main.js             # JavaScript functionality
│   ├── css/
│   │   └── style.css       # Responsive styling
│   ├── images/             # Game images & assets
│   └── music/              # Sound effects
│
├── backup/                  # Automatic backups of game results
└── venv/                    # Python virtual environment
```

## Technical Details

### Backend Stack
- **Framework**: Flask with Bcrypt authentication
- **Data Storage**: JSON files with CSV tracking for map history
- **Authentication**: Session-based with role-based access control
- **Plotting**: Matplotlib for performance visualizations

### Frontend Stack
- **HTML5**: Semantic markup with responsive design
- **CSS**: Grid/Flexbox layouts with season-themed variables
- **JavaScript**: 
  - Drag & Drop API for player ranking
  - Touch events (500ms long-press) for mobile
  - Fetch API for async communication
  - Canvas-based wheel spinner

### Database
- `results.json`: Game entries with players, scores, awards, milestones, season
- `user_settings.json`: User preferences (music enabled, images enabled)
- `map_history.csv`: Map tracking with timestamp and name
- `PLAYER_CREDENTIALS.txt`: UTF-8 encoded player authentication

## API Endpoints

### Authentication
- `POST /api/login` - User login
- `POST /api/logout` - User logout
- `GET /api/check_login` - Check login status

### Game Data
- `POST /api/save_results` - Save game results
- `GET /api/get_results` - Retrieve game history
- `POST /api/save_plot` - Generate and save performance plot

### Admin Features
- `GET /api/get_fearless_draft` - Get fearless draft settings (admin only)
- `POST /api/update_fearless_draft` - Update fearless draft settings (admin only)

### Map Tracking
- `GET /api/get_last_map` - Get last played map from history
- `POST /api/update_map_history` - Record played map to CSV

## Gameplay

### Players
- Login with personal credentials
- View personal and team statistics
- Participate in game logging and award tracking

### Game Session
1. Select season (Mars/Venus/Jupiter)
2. Add players to the session
3. Rank players using drag-and-drop or click-to-place
4. Enter manual game scores
5. Assign awards and milestones
6. Submit game result
7. View immediate statistics update

### House Rules
- Fearless Draft: Configure corporation pool size
- Custom rules displayed on dedicated page

## Configuration

### Player Credentials (PLAYER_CREDENTIALS.txt)
```
Username: Frederik
Password: password123
Role: admin

Username: Player2
Password: pass456
Role: user
```

### Season Themes
- **Mars**: Red theme with Mars imagery
- **Venus**: Yellow/golden theme
- **Jupiter**: Blue/purple theme with Jupiter colors

## Development

### Running Tests
```bash
python -m pytest  # If test suite exists
```

### Creating Backups
```bash
python backup_results.py
```

### Code Structure
- Modular Flask blueprints organization
- Utility functions for data operations
- Template inheritance for consistent UI
- CSS custom properties for theming

## License

Specify your license here (e.g., MIT, GPL-3.0)

## Contributing

To contribute to this project:
1. Create a feature branch
2. Make your changes
3. Test thoroughly on desktop and mobile
4. Submit a pull request with detailed description

## Support

For issues or feature requests, please open an issue on GitHub.

## Changelog

### Version 3.0 (Season 3 Release)
- ✅ Full Season 3 Jupiter theme with dynamic styling
- ✅ Enhanced drag-and-drop ranking (desktop + mobile touch)
- ✅ Click-to-place alternative for all placement zones
- ✅ Milestones and awards with winner tracking
- ✅ Support for up to 6 players
- ✅ Role-based access control with admin features
- ✅ CSV-based map history tracking for Spin the Map
- ✅ Fearless draft admin feature
- ✅ Performance plots and statistics
- ✅ Responsive mobile design with numpad support
- ✅ Audio feedback with "Woo" sound effect
- ✅ Session management and data persistence

### Previous Versions
- Season 1 & 2: Initial release with basic game logging

