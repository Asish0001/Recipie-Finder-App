from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import json
import os
import requests

app = Flask(__name__)
DATA_FILE = 'data.json'
app.secret_key = 'recipeFinder'
SPOONACULAR_API_KEY = '97f32d06b94d4eefbcac1904c40fda76'

@app.route('/')
def home():
    ingredients = session.get('ingredients', []) #if none, return empty list
    return render_template('index.html', ingredients=ingredients)

@app.route('/add')
def add_ingredients():
    return render_template('add.html')

@app.route('/find', methods=['POST'])
def find_recipes():
    user_input = request.form['ingredients'] #get ingredients from form
    user_ingredients = [item.strip().lower() for item in user_input.split(',') if item.strip()] #clean + split
    session['ingredients'] = user_ingredients #store ingredients in session

    #prepare API request
    api_url = 'https://api.spoonacular.com/recipes/findByIngredients'
    params = {
        'ingredients' : ','.join(user_ingredients),
        'number' : 5, 
        'apiKey' : SPOONACULAR_API_KEY
    }
    #debug
    print("Sending API request with params:", params)



    #Make the API request
    response = requests.get(api_url, params=params)
    #debugs
    print("API status code:", response.status_code)
    print("Raw response:", response.text)

    if response.status_code == 200:
        basic_results = response.json()
        print("Parsed JSON:", basic_results) #debug
        recipes = []

        for item in basic_results:
            recipe_id = item['id']
            detail_url = f'https://api.spoonacular.com/recipes/{recipe_id}/information'
            detail_params = {'apiKey' : SPOONACULAR_API_KEY}
            detail_resp = requests.get(detail_url, params=detail_params)

            if detail_resp.status_code == 200:
                data = detail_resp.json()
                recipes.append({
                    'title' : data['title'],
                    'image' : data['image'],
                    'instructions' : data.get('instructions', 'No instructions available.'),
                    'readyInMinutes' : data.get('readyInMinutes', '?'),
                    'servings' : data.get('servings', '?'),
                    'missedIngredients': [i['name'] for i in item['missedIngredients']]
                })
        #return results to a new templatea
        return render_template('results.html', recipes = recipes)
    else:
        print("Failed to fetch recipes:", response.status_code)
        return "API request failed.", 500 #debug
 
if __name__ == '__main__':
    app.run(debug=True)

