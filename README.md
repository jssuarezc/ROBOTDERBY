# ROBOT DERBY

This project idea uses an old repo that navigates a robot through a maze using Q-algorithm to find a way out. In this case, 
3 agents or "participants# will be using different learning strategies to find a way out of this maze. Within each iteration, 
the maze changes. This system aims to conneck this backend file into a Web Frontend using Javascript to make it interactive, 
like watching a live horse race. Ideally, an implementation with an SVM modell will be done to evaluate performance signals 
and categorize them based on efficiency.


# Overview

## Setup

1. Create venv
2. Install requirements by running `pip install -r requirements.txt`
3. Follow the env file example to create the variables to be used


## Race participants



**Kweebie:**
- Learns from each (state,value) pair
- Improves over time and repetitions
- Sensitive to epsilon(exploration), alpha(learning rate) and gamma(penalty)

**Randy:**
- Always fast to reach the goal
- Ignores path structure
- While initially fast, it gets stuck in loops quite often

**John:**
- "Wanderer"
- Slightly biased towards new obstacles

## TO DO NEXT
1. Work on the API endpoints
2. Frontend implementation
3. SVM training and classification
