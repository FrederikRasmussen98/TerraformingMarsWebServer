import matplotlib.pyplot as plt

# Create a dummy plot for testing
plt.figure(figsize=(6, 4))
plt.plot([1, 2, 3, 4], [10, 20, 25, 30], label='Scores')
plt.title('Game Scores')
plt.legend()
plt.savefig('static/images/plot.png')
plt.close()

# Generate another plot for total points
plt.figure(figsize=(6, 4))
plt.plot([1, 2, 3, 4], [15, 35, 50, 70], label='Total Points')
plt.title('Total Points')
plt.legend()
plt.savefig('static/images/total_points.png')
plt.close()
