from flask import Flask, request, jsonify
import pickle
import numpy as np

app = Flask(__name__)

# Model ve Scaler yükle
scaler = pickle.load(open('scaler.pkl', 'rb'))
models = {}
targets = ['life_score', 'science_score', 'mining_score', 'success_score']

# Element isimleri
elements = ['He', 'Ne', 'Cl', 'Mg', 'Ti', 'Fe', 'Ag', 'Ni', 'Si', 'Cu', 'Mn', 'Pt', 'U', 'Al', 'Ar', 'N', 'Zn', 'P', 'H', 'Ca', 'C', 'Cr', 'S', 'Li', 'Na', 'V']

# Modelleri yükle
for target in targets:
    models[target] = pickle.load(open(f'{target}_model.pkl', 'rb'))

import pandas as pd

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()

    input_data = [data[element] for element in elements]

    average_density = np.mean(input_data)
    sum_density = np.sum(input_data)
    H_to_C_ratio = input_data[elements.index('H')] / (input_data[elements.index('C')] + 1e-6)
    life_related_sum = sum([data[el] for el in ['H', 'C', 'N', 'P', 'S']])
    metal_sum = sum([data[el] for el in ['Fe', 'Ni', 'Cu', 'Mn', 'Zn', 'Ag', 'Pt', 'Ti']])

    full_input = input_data + [average_density, sum_density, H_to_C_ratio, life_related_sum, metal_sum]

    # Özellik isimlerini ayarlıyoruz
    feature_names = elements + ['average_density', 'sum_density', 'H_to_C_ratio', 'life_related_sum', 'metal_sum']
    input_df = pd.DataFrame([full_input], columns=feature_names)

    input_scaled = scaler.transform(input_df)

    results = {}
    for target in targets:
        prediction = models[target].predict(input_scaled)[0]
        results[target] = float(prediction)

    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
