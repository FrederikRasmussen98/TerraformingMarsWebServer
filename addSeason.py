import json

# Load JSON data
with open('results.json', 'r') as f:
    data = json.load(f)

# Add 'season' key with value '1' to each entry
for entry in data:
    entry['season'] = 1

# Save back to file (overwrite or change filename as needed)
with open('game_results_updated.json', 'w') as f:
    json.dump(data, f, indent=4)

print("Season added to all entries.")
