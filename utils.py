"""
Utility functions for TerraformingMarsWebServer.
Extracted common patterns to reduce code duplication.
"""
import json
import os


def load_json_file(filepath, default=None):
    """
    Load JSON data from a file.
    
    Args:
        filepath: Path to the JSON file
        default: Default value to return if file doesn't exist
        
    Returns:
        Loaded JSON data or default value
    """
    if os.path.exists(filepath):
        with open(filepath, 'r') as file:
            return json.load(file)
    return default if default is not None else []


def save_json_file(filepath, data, indent=4):
    """
    Save data to a JSON file.
    
    Args:
        filepath: Path to the JSON file
        data: Data to save
        indent: Indentation level for formatting
    """
    with open(filepath, 'w') as file:
        json.dump(data, file, indent=indent)


def load_corps_data():
    """
    Load corps_left.json data.
    
    Returns:
        Dictionary with fearlessDraftOn and corpsLeft keys
    """
    return load_json_file("corps_left.json", {"fearlessDraftOn": False, "corpsLeft": 0})


def save_corps_data(corps_data):
    """
    Save corps_left.json data.
    
    Args:
        corps_data: Dictionary with corps data to save
    """
    save_json_file("corps_left.json", corps_data)


def update_corps_left(num_players):
    """
    Update corps_left count after a game is logged.
    
    Args:
        num_players: Number of players in the game
    """
    corps_data = load_corps_data()
    if corps_data.get("fearlessDraftOn", False):
        corps_data["corpsLeft"] = max(0, corps_data.get("corpsLeft", 0) - num_players)
        save_corps_data(corps_data)


def setup_plot_style(ax, fig, bg_color, tick_color, xlabel, ylabel, dates):
    """
    Apply common styling to matplotlib plots.
    
    Args:
        ax: Matplotlib axis object
        fig: Matplotlib figure object
        bg_color: Background color tuple (r, g, b, alpha)
        tick_color: Color for tick labels
        xlabel: Label for x-axis
        ylabel: Label for y-axis
        dates: List of dates for x-tick labels
    """
    fig.patch.set_facecolor(bg_color)
    ax.set_facecolor(bg_color)
    
    for spine in ax.spines.values():
        spine.set_edgecolor('white')
        spine.set_linewidth(1.5)
        spine.set_alpha(0.5)
    
    ax.tick_params(axis='both', which='both', colors=tick_color)
    ax.set_xticklabels(dates, rotation=45)
    ax.set_xlabel(xlabel, color=tick_color, alpha=0.7)
    ax.set_ylabel(ylabel, color=tick_color, alpha=0.7)
