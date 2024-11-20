#include <WiFi.h>
#include <WebServer.h>

// Configuración de la red Wi-Fi
const char* ssid = "iPhone de Isai";      // Reemplaza con el nombre de tu red Wi-Fi
const char* password = "tamalito26";  // Reemplaza con la contraseña de tu red Wi-Fi

const int plumaPin = 17;
WebServer server(80);

const char* http_username = "ESP32";   // Cambia esto por el nombre de usuario deseado
const char* http_password = "Tamalito26"; // Cambia esto por la contraseña deseada

// Función para manejar la activación de la pluma
void handleActivatePluma() {
  if (!server.authenticate(http_username, http_password)) {
    return server.requestAuthentication();
  }
  digitalWrite(plumaPin, HIGH);
  delay(1000);
  digitalWrite(plumaPin, LOW);
  server.send(200, "text/plain", "Pluma activada");
}

void setup() {
  pinMode(plumaPin, OUTPUT);
  digitalWrite(plumaPin, LOW);

  Serial.begin(115200);
  
  // Conectar al Wi-Fi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("\nConectado a Wi-Fi");

  // Mostrar la IP asignada por el router
  Serial.print("IP asignada: ");
  Serial.println(WiFi.localIP());  // Imprime la IP local de la ESP32

  // Configurar la ruta para activar la pluma
  server.on("/activar_pluma", handleActivatePluma);

  server.begin();
  Serial.println("Servidor web iniciado");
}


void loop() {
  server.handleClient();
}
