from flask import Flask, request, jsonify
import pickle
import numpy as np

app = Flask(__name__)

# Modeli ve Scaler'ı yükle
scaler = pickle.load(open('scaler.pkl', 'rb'))
models = {}
targets = ['life_score', 'science_score', 'mining_score', 'success_score']

# Her hedef için model yükle
for target in targets:
    models[target] = pickle.load(open(f'{target}_model.pkl', 'rb'))

# API endpoint: tahmin yap
@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()

    # Input verisi
    input_data = [data[element] for element in data.keys()]
    
    # Verileri normalleştir
    input_scaled = scaler.transform([input_data])

    results = {}
    for target in targets:
        # Modeli kullanarak tahmin yap
        prediction = models[target].predict(input_scaled)[0]
        results[target] = prediction
    
    # Tahmin sonuçlarını JSON formatında döndür
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)