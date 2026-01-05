# Grouping Calculator - Darrin O'Brien

## Overview
This project groups together calculations into chains for easier reference after inputting calculations and understanding the chain that led to the answer. Currently, there is only a rule-based implementation on the `MU-NLPC/Calc-math_qa` dataset from Hugging Face. In the future, I plan on implementing a GUI for actual calculator inputs so that the grouping algorithms can organize calculations chains live. I also plan on introducing Graph Neural Networks as an exploratory area to understand how they work and how they perform relative to simple grouping rules.

## Features
- Extensive `MU-NLPC/Calc-math_qa` parsing into meaningful attributes
- Graph Construction from given processed `MU-NLPC/Calc-math_qa` data
- Rule-based logic evaluation for grouping together calculations and sorting them into their respective orders

## Project Structure
- \src: Contains modules for the service below
    - \logic: Contains the rule-based logic for grouping and sorting calculations
    - \parser: Contains the parser for the `MU-NLPC/Calc-math_qa` dataset and random shuffler on the data
    - \structures: Contains the node and adjacency list graph data structures
- \data: Placeholder folder for storing the processed `MU-NLPC/Calc-math_qa` data
- README.md: How to navigate and use the project
- requirements.txt: Libraries and versions used for this project

## Installation
1. Clone the repository: ```git clone _ ```
2. Create a virtual environment: 
    ```
    python -m venv .venv 
    source .venv/bin/activate # For Mac. For Windows, try .venv\Scripts\activate
    pip install -r requirements.txt
    ```
3. Running the progam on a randomly shuffled mix of `MU-NLPC/Calc-math_qa` calculations 58 and 59: python src/main.py

## Future Work
- More graph rules
- GUI implementation
- Graph Neural Networks (GNN's) add-on
- Adding automated tests