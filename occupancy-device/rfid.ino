#include <Adafruit_Fingerprint.h>
#include <SPI.h>
#include <MFRC522.h>
#include <WiFi.h>         // Include Wi-Fi library
#include <HTTPClient.h>   // Include HTTP library

#define SS_PIN 15
#define RST_PIN 16

#if (defined(__AVR__) || defined(ESP8266)) && !defined(__AVR_ATmega2560__)
SoftwareSerial mySerial(2, 3);
#else
#define mySerial Serial1
#endif

Adafruit_Fingerprint finger = Adafruit_Fingerprint(&mySerial);
MFRC522 rfid(SS_PIN, RST_PIN);
MFRC522::MIFARE_Key key;

byte nuidPICC[4];
bool in = true;

// Wi-Fi credentials
const char* ssid = "geo";
const char* password = "1234567809";
const char* serverURL = "http://localhost:3003//api/v1/occupancy";  // Replace with your server URL

void setup() {
  Serial.begin(115200);
  while (!Serial) ;
  delay(100);

  Serial.println("\n\nInitializing...");
  
  // Fingerprint setup
  finger.begin(57600);
  delay(5);
  if (finger.verifyPassword()) {
    Serial.println("Found fingerprint sensor!");
  } else {
    Serial.println("Fingerprint sensor not found :(");
    while (1) { delay(1); }
  }

  pinMode(5, OUTPUT); // GREEN
  pinMode(10, OUTPUT); // RED

  // RFID setup
  SPI.begin();
  rfid.PCD_Init();

  // Initialize key for RFID
  for (byte i = 0; i < 6; i++) {
    key.keyByte[i] = 0xFF;
  }

  // Wi-Fi setup
  WiFi.begin(ssid, password);
  Serial.print("Connecting to Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("\nConnected to Wi-Fi!");
}

void loop() {
  getFingerprintID();
  delay(50);

  // Check for RFID card presence
  if (!rfid.PICC_IsNewCardPresent() || !rfid.PICC_ReadCardSerial()) {
    return;
  }

  Serial.println("RFID card detected");
  String rfidData = readRFID();
  sendToServer("RFID", rfidData);

  // Toggle LEDs
  toggleLEDs();
}

// Helper function to read RFID data
String readRFID() {
  String uid = "";
  for (byte i = 0; i < rfid.uid.size; i++) {
    uid += String(rfid.uid.uidByte[i], HEX);
  }
  rfid.PICC_HaltA(); // Halt the card
  rfid.PCD_StopCrypto1(); // Stop encryption
  return uid;
}

// Helper function to toggle LEDs
void toggleLEDs() {
  digitalWrite(5, !in);
  digitalWrite(10, in);
  in = !in;
}

// Helper function to send data to server
void sendToServer(String type, String data) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    String url = serverURL + "?occupancy=" + data + "&id=" + data;
    http.begin(url);
    http.addHeader("Content-Type", "application/json");

    String payload = "{}"; // Empty payload for query parameters

    int httpResponseCode = http.POST(payload);

    if (httpResponseCode > 0) {
      Serial.println("Data sent to server successfully");
    } else {
      Serial.print("Error sending data: ");
      Serial.println(httpResponseCode);
    }
    http.end();
  } else {
    Serial.println("Wi-Fi not connected!");
  }
}

// Fingerprint functions
uint8_t getFingerprintID() {
  uint8_t p = finger.getImage();
  if (p != FINGERPRINT_OK) return -1;

  p = finger.image2Tz();
  if (p != FINGERPRINT_OK) return -1;

  p = finger.fingerSearch();
  if (p == FINGERPRINT_OK) {
    Serial.println("Fingerprint match found!");
    String fingerprintData = String(finger.fingerID);
    sendToServer("Fingerprint", fingerprintData);
    toggleLEDs();
    return finger.fingerID;
  } else {
    Serial.println("No match found");
    return -1;
  }
}
