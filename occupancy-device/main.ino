#include <WiFi.h>
#include <HTTPClient.h>

const char* device_id = "f8d6c431-32a8-4374-8e1e-f7703deee370";

const char* ssid = "XXXXXX";
const char* password = "XXXXXX";

const char* serverUrl = "http://localhost:8080/api/occupancy";

#define PIR_PIN 13

unsigned long lastPostTime = 0;
const long postInterval = 10000;

void setup() {
  Serial.begin(115200);
  
  pinMode(PIR_PIN, INPUT);
  
  connectToWiFi();
}

void loop() {
  int occupancyStatus = digitalRead(PIR_PIN);
  
  if (millis() - lastPostTime > postInterval) {
    sendOccupancyData(occupancyStatus);
    lastPostTime = millis();
  }
}

void connectToWiFi() {
  Serial.print("Connecting to WiFi...");
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  
  Serial.println("\nConnected to WiFi!");
}

void sendOccupancyData(int occupancyStatus) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    
    String postData = "occupancy=" + String(occupancyStatus) + "&id=" + device_id;
    
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/x-www-form-urlencoded");
    
    int httpResponseCode = http.POST(postData);
    
    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println("Server Response: " + response);
    } else {
      Serial.println("Error in sending POST request.");
    }
    
    http.end();
  } else {
    Serial.println("WiFi Disconnected, cannot send data.");
  }
}
