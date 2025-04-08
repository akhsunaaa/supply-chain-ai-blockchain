#include <WiFi.h>
#include <WebServer.h>
#include <DHT.h>

#define DHT_PIN 4       // GPIO where DHT sensor is connected
#define DHT_TYPE DHT11  // Change to DHT22 if using DHT22
#define MQ3_PIN 34      // MQ-3 sensor on ADC
#define BAUD_RATE 115200

const char* ssid = "Nothing";
const char* password = "12345678";

WebServer server(80);
DHT dht(DHT_PIN, DHT_TYPE);

void handleData() {
    float temperature = dht.readTemperature();
    float humidity = dht.readHumidity();
    float mq3_value = (analogRead(MQ3_PIN) / 40.96); // Convert ADC value (0-4095) to percentage

    if (isnan(temperature) || isnan(humidity)) {
        server.send(500, "text/plain", "ERROR: Failed to read from DHT sensor!");
        return;
    }

    String json = "{";
    json += "\"temperature\":" + String(temperature) + ",";
    json += "\"humidity\":" + String(humidity) + ",";
    json += "\"mq3_value\":" + String(mq3_value);
    json += "}";

    server.send(200, "application/json", json);  // Send JSON data
    Serial.println("Sent: " + json);
}

void setup() {
    Serial.begin(BAUD_RATE);
    dht.begin();
    
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        Serial.print(".");
    }

    Serial.println("\nConnected! IP Address:");
    Serial.println(WiFi.localIP());

    server.on("/data", handleData);
    server.begin();
}

void loop() {
    server.handleClient();
    delay(1000);  // Send data every second
}
