# WISPR
Here I have webscraped the winrates of DOTA 2 heroes played by the top .1% of DOTA 2 players and trained a deep learning model to predict the outcomes of general matches played in public matchmaking. 
Each match is a battle between a combination of 10 unique heroes seperated into 2 teams.
The model calculates an overall, synergy, and counter winrate for each 5-hero team.
I find the average, median, kurtosis, skewness, standard deviation, and variance for each of these 6 metrics. The match outcome is then predicted using the metrics each team has calculated.

*Synergy winrate is the average of winrates this hero has when played with the 4 other heroes on their team, individually.
*Counter winrate is the average of winrates this hero has when played against the 5 specific enemy heroes.

I webscraped all of my data from dota2portracker.com, where I used beutifulsoup to capture the overall winrates and the winrates for counter-pick/synergy scenarios.

The results folder contains images of the model's accuracy and loss against training and validation sets.
The metrics are average metrics after performing 10 sets of 50 epochs on training and validation sets. 
