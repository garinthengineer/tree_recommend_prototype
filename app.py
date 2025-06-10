from flask import Flask, render_template_string, request, url_for
import os

app = Flask(__name__)

# Вопросы и соответствующие бинарные признаки
questions = [
    ("Страдные?", "Страдные_да"),
    ("Есть ли тематика 'Сверхъестественное и ужасы'?", "Тематика_общая_Сверхъестественное и ужасы"),
    ("Есть ли тематика 'Фэнтези/Магия'?", "Тематика_фэнтези_Магия"),
    ("Это детектив?", "Жанр_Детектив"),
    ("Есть ли приключения и сокровища?", "Тематика_общая_Приключения и сокровища"),
    ("Есть ли тематика 'Искусство/Театр'?", "Тематика_искусство_Театр")
]

# Простая логика дерева решений на основе графа

def classify(flags):
    import pandas as pd
    df = pd.read_csv("static/комбинации классов.csv")

    # Только те признаки, которые пришли с фронтенда
    input_features = list(flags.keys())
    print(input_features)

    for _, row in df.iterrows():
        row_values = row[input_features]

        match = True
        for col in input_features:
            expected = row[col]
            user_value = flags[col]

            if pd.isna(expected):
                if user_value is not None:
                    match = False
                    break
            else:
                if user_value is None or float(user_value) != expected:
                    match = False
                    break

        if match:
            return row["class"]

    return "Не удалось определить класс"

@app.route('/', methods=['GET', 'POST'])
def index():
    selected = {}
    result = None
    if request.method == 'POST':
        for q, key in questions:
            selected_val = request.form.get(key)
            if selected_val == '1':
                selected[key] = 1.0
            elif selected_val == '0':
                selected[key] = 0.0
            else:
                selected[key] = None
            result = classify(selected)

    return render_template_string('''
<!doctype html>
<html lang="ru">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <title>Рекомендатель квестов</title>
    <style>
      .half-screen {
        height: 100vh;
      }
    </style>
  </head>
  <body>
    <div class="container-fluid">
      <div class="row">
        <div class="col-md-6 d-flex align-items-center justify-content-center half-screen">
          <div>
            <h2 class="mb-4 text-center">Ответьте на вопросы</h2>
            <form method="POST">
              {% for text, key in questions %}
                <div class="mb-3">
                  <label for="{{ key }}" class="form-label">{{ text }}</label>
                  <select class="form-select" name="{{ key }}" id="{{ key }}">
                    <option value="unset" selected>Не задано</option>
                    <option value="1">Да</option>
                    <option value="0">Нет</option>
                  </select>
                </div>
              {% endfor %}
              <button type="submit" class="btn btn-primary mt-3">Получить рекомендацию</button>
            </form>
            {% if result %}
              <div class="alert alert-success mt-4" role="alert">
                Рекомендованный класс: <strong>{{ result }}</strong>
              </div>
            {% endif %}
          </div>
        </div>
        <div class="col-md-6 d-flex align-items-center justify-content-center half-screen">
          <img src="{{ url_for('static', filename='Tree.png') }}" class="img-fluid" alt="Дерево решений">
        </div>
      </div>
    </div>
  </body>
</html>
''', questions=questions, result=result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
