
from flask import Flask, render_template_string, request
import requests
import os

app = Flask(__name__)

API_KEY = os.environ.get("OPENWEATHER_API_KEY", "")

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Weather Prediction</title>
    <style>
        * { box-sizing: border-box; }
        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #141e30, #243b55);
            color: white;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .card {
            width: 100%;
            max-width: 480px;
            background: rgba(255,255,255,0.12);
            padding: 30px;
            border-radius: 22px;
            text-align: center;
            box-shadow: 0 10px 35px rgba(0,0,0,0.25);
        }
        h1 { font-size: 30px; }
        input, button {
            width: 100%;
            padding: 14px;
            margin-top: 12px;
            border: none;
            border-radius: 10px;
            font-size: 16px;
        }
        button {
            background: #38bdf8;
            color: #102033;
            font-weight: bold;
            cursor: pointer;
        }
        .result {
            margin-top: 22px;
            padding: 18px;
            background: rgba(0,0,0,0.18);
            border-radius: 14px;
        }
        .temp { font-size: 42px; font-weight: bold; }
        .error { color: #ffd1d1; }
        small { color: #dbeafe; }
    </style>
</head>
<body>
    <main class="card">
        <h1>🌦️ Weather Prediction</h1>
        <p>Check the current weather in your city.</p>
        <form method="POST">
            <input name="city" placeholder="Enter city name"
                   value="{{ city }}" required>
            <button type="submit">Check Weather</button>
        </form>

        {% if weather %}
        <div class="result">
            <h2>{{ weather.city }}</h2>
            <div class="temp">{{ weather.temp }}°C</div>
            <h3>{{ weather.description }}</h3>
            <p>Feels like: {{ weather.feels }}°C</p>
            <p>Humidity: {{ weather.humidity }}%</p>
            <p>Wind: {{ weather.wind }} m/s</p>
        </div>
        {% endif %}

        {% if error %}
        <p class="error">{{ error }}</p>
        {% endif %}

        <p><small>Weather data requires an OpenWeather API key.</small></p>
    </main>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    weather = None
    error = ""
    city = ""

    if request.method == "POST":
        city = request.form.get("city", "").strip()

        if not city:
            error = "Please enter a city name."
        elif not API_KEY:
            error = "Weather API key is not configured yet."
        else:
            try:
                response = requests.get(
                    "https://api.openweathermap.org/data/2.5/weather",
                    params={
                        "q": city,
                        "appid": API_KEY,
                        "units": "metric"
                    },
                    timeout=10
                )

                if response.status_code == 200:
                    data = response.json()
                    weather = {
                        "city": data["name"],
                        "temp": round(data["main"]["temp"]),
                        "feels": round(data["main"]["feels_like"]),
                        "humidity": data["main"]["humidity"],
                        "wind": data["wind"]["speed"],
                        "description": data["weather"][0]["description"].title()
                    }
                elif response.status_code == 404:
                    error = "City not found. Please check the spelling."
                else:
                    error = "Weather service error. Please try again."
            except requests.RequestException:
                error = "Unable to connect. Please try again later."

    return render_template_string(
        HTML, weather=weather, error=error, city=city
    )

if __name__ == "__main__":
    app.run(debug=True)
