// RAPTOR - Enkoder okuma ve odometri testi (ESP32, Arduino IDE)
// Gerekli kutuphane: Library Manager'dan "ESP32Encoder" (Kevin Harrington)
// Enkoder beslemesi: mavi kablo 3.3V, siyah kablo GND
// Sinyal: sari/yesil kablolar asagidaki pinlere
// Not: GPIO 34-39'da dahili pull-up yok, enkoder icin kullanma.

#include <ESP32Encoder.h>

// ---- Pinler ----
const int SOL_A = 32, SOL_B = 33;
const int SAG_A = 25, SAG_B = 26;

// ---- Kalibrasyonla duzeltilecek sayilar ----
const float SAYIM_PER_TUR  = 1320.0;  // 11 darbe x 4 kenar x 30 disli (elle 10 tur cevirip olc)
const float TEKER_CAP      = 0.085;   // metre (5 m duz surusle duzelt)
const float TEKER_ARALIGI  = 0.20;    // metre, L (10 tur yerinde donusle duzelt)

// Sag motor ayna gibi monte edildigi icin ileri giderken ters doner.
// Arac ileri giderken iki hiz da pozitif cikmiyorsa ilgili isareti degistir.
const int SOL_YON = 1;
const int SAG_YON = -1;

const uint32_t DONGU_MS = 20;  // 50 Hz

ESP32Encoder solEnc, sagEnc;
int64_t solOnceki = 0, sagOnceki = 0;
float x = 0, y = 0, theta = 0;
uint32_t sonZaman = 0;
const float METRE_PER_SAYIM = PI * TEKER_CAP / SAYIM_PER_TUR;

void setup() {
  Serial.begin(115200);
  ESP32Encoder::useInternalWeakPullResistors = puType::up;
  solEnc.attachFullQuad(SOL_A, SOL_B);  // A ve B'nin tum kenarlari: x4 cozunurluk
  sagEnc.attachFullQuad(SAG_A, SAG_B);
  solEnc.clearCount();
  sagEnc.clearCount();
  sonZaman = millis();
}

void loop() {
  uint32_t simdi = millis();
  if (simdi - sonZaman < DONGU_MS) return;
  float dt = (simdi - sonZaman) / 1000.0;
  sonZaman = simdi;

  // 1) Sayaclari oku
  int64_t sol = solEnc.getCount();
  int64_t sag = sagEnc.getCount();
  long dSol = SOL_YON * (long)(sol - solOnceki);
  long dSag = SAG_YON * (long)(sag - sagOnceki);
  solOnceki = sol;
  sagOnceki = sag;

  // 2) Sayimdan mesafe ve hiza
  float dL = dSol * METRE_PER_SAYIM;   // sol tekerin bu dongudeki yolu (m)
  float dR = dSag * METRE_PER_SAYIM;
  float vL = dL / dt;                  // m/s  -> PID bunu kullanacak
  float vR = dR / dt;

  // 3) Odometri
  float ds  = (dR + dL) / 2.0;
  float dth = (dR - dL) / TEKER_ARALIGI;
  x += ds * cos(theta + dth / 2.0);
  y += ds * sin(theta + dth / 2.0);
  theta += dth;

  // 4) Seri porta yaz: sayimSol, sayimSag, vSol, vSag, x, y, theta(derece)
  Serial.printf("%ld,%ld,%.3f,%.3f,%.3f,%.3f,%.1f\n",
                (long)sol, (long)sag, vL, vR, x, y, theta * 180.0 / PI);
}
