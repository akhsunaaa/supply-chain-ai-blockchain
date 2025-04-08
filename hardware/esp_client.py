import requests
import csv
import time

ESP32_IP = "http://192.168.189.163/data"  # Change to your ESP32 IP
FILENAME = r"C:\Users\danis\OneDrive\Documents\MIT WS\Projects\SCM\sensor_data.csv"

# Create CSV file and add headers
with open(FILENAME, "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Time", "Temperature (°C)", "Humidity (%)", "MQ-3 Value"])

print("Collecting sensor data...")

while True:
    try:
        response = requests.get(ESP32_IP, timeout=2)  # Get data from ESP32
        data = response.json()  # Parse JSON
        
        # Get sensor values
        temperature = data["temperature"]
        humidity = data["humidity"]
        mq3_value = data["mq3_value"]
        timestamp = time.strftime("%H:%M:%S")  # Current time

        # Save to CSV
        with open(FILENAME, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([timestamp, temperature, humidity, mq3_value])

        print(f"{timestamp} | Temp: {temperature}°C | Humidity: {humidity}% | MQ-3: {mq3_value}")

        time.sleep(30)  # Fetch data every second

    except requests.exceptions.RequestException as e:
        print("Error:", e)
        time.sleep(2)  # Retry after 2s
