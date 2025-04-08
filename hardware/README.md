# ESP32 Sensor Data Logger

This project sets up an ESP32 as a web server to provide real-time sensor data (temperature, humidity, and alcohol concentration) and logs the data to a CSV file using a Python script.

## Features
- Reads temperature and humidity using a **DHT11** sensor.
- Reads alcohol concentration using an **MQ-3** gas sensor.
- Hosts a web server on ESP32 that provides sensor data in **JSON format**.
- A Python script fetches the data from ESP32 and logs it into a **CSV file** for further analysis.

---

## Hardware Requirements
- **ESP32** microcontroller
- **DHT11** or **DHT22** sensor (for temperature & humidity)
- **MQ-3** gas sensor (for alcohol detection)
- **WiFi connectivity** for ESP32

---

## Software Requirements
- Arduino IDE with ESP32 board support
- Python 3
- Required Python libraries: `requests`, `csv`, `time`

---

## ESP32 Code (esp_server.ino)
The ESP32 hosts a web server that responds with sensor data at `http://<ESP32-IP>/data` in JSON format.

### Libraries Used
- **WiFi.h** - For connecting ESP32 to WiFi
- **WebServer.h** - To create a simple HTTP server
- **DHT.h** - For interfacing with the DHT sensor

### Pin Configuration
| Component | ESP32 GPIO |
|-----------|-----------|
| DHT Sensor | GPIO 4 |
| MQ-3 Sensor | GPIO 34 |

### Setup Process
1. Connect the DHT11 and MQ-3 sensors to the specified GPIO pins.
2. Modify the `ssid` and `password` in the ESP32 code to match your WiFi network.
3. Upload the `esp_server.ino` sketch to your ESP32 using Arduino IDE.
4. Open the Serial Monitor to find the ESP32's IP address (printed after connection).
5. Use the printed IP address in the Python script (`esp_client.py`).
6. Access `http://<ESP32-IP>/data` in a browser to see real-time JSON data.

### JSON Response Example
```json
{
  "temperature": 25.4,
  "humidity": 60.3,
  "mq3_value": 75.6
}
```

---

## Python Data Logger (esp_client.py)
The Python script periodically requests sensor data from the ESP32 and saves it in a CSV file.

### Installation
Ensure you have Python installed, then install dependencies:
```bash
pip install requests
```

### CSV Logging Script
- Fetches data every **1 second** from the ESP32.
- Stores data in `sensor_data.csv` with columns: `Time`, `Temperature`, `Humidity`, and `MQ-3 Value`.

### Running the Script
1. Retrieve the ESP32 IP address from the Serial Monitor.
2. Modify `ESP32_IP` in `esp_client.py` to match your ESP32's IP.
3. Run the script:
   ```bash
   python esp_client.py
   ```
4. View the saved CSV file to analyze the recorded data.

---

## Testing
1. **Check ESP32 Web Server**
   - Open a web browser and go to `http://<ESP32-IP>/data`.
   - Ensure the response is in JSON format with valid sensor values.

2. **Run the Python Logger**
   - Start `esp_client.py` and confirm data is logged in `sensor_data.csv`.
   - Check console output for real-time data updates.

---


## License
This project is licensed under the MIT License.

