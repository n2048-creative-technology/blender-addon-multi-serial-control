void setup() {
    Serial.begin(115200);
}

void loop() {
    if (Serial.available()) {
        String data = Serial.readStringUntil('\n');  // Read until newline
        int firstDelim = data.indexOf('|');
        int secondDelim = data.indexOf('|', firstDelim + 1);

        if (firstDelim != -1 && secondDelim != -1) {
            String objName = data.substring(0, firstDelim);
            String prop = data.substring(firstDelim + 1, secondDelim);
            float value = data.substring(secondDelim + 1).toFloat();

            Serial.print("🔹 Received: ");
            Serial.print(objName);
            Serial.print(" | ");
            Serial.print(prop);
            Serial.print(" | ");
            Serial.println(value);
        }
    }
}
