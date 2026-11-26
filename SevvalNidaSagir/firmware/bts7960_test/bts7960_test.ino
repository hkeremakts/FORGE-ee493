// RAPTOR - BTS7960 + JGB37-520 ilk test (ESP32 DevKit V1, Arduino IDE)
// ESP32 core 3.x (LEDC API: ledcAttach / ledcWrite)
// Kutuphane: Library Manager'dan "ESP32Encoder" (Kevin Harrington)
//
// Seri Monitor: 115200 baud, satir sonu "Newline".
// Komutlar (yuzde, -100..100; ilk testte en fazla MAKS_YUZDE):
//   L 30   -> sol motor %30 ileri      L -30 -> sol motor %30 geri
//   R 30   -> sag motor %30            B 30  -> ikisi birden %30
//   S      -> dur                       Z     -> enkoder sayaclarini sifirla
// Guvenlik: son komuttan ZAMAN_ASIMI_MS sonra motorlar kendiliginden durur.
//
// Baglanti (her surucu icin):
//   RPWM, LPWM -> asagidaki GPIO'lar
//   R_EN + L_EN birlestir -> ESP32 3V3     VCC -> ESP32 3V3     GND -> ESP32 GND
//   B+ / B-  -> 12 V kaynak (sigortadan sonra)   M+ / M- -> motor kirmizi / beyaz
// Enkoder: mavi -> 3V3 (5V DEGIL), siyah -> GND, sari -> A, yesil -> B

#include <ESP32Encoder.h>

// ---- Pinler ----
const int SOL_RPWM = 23, SOL_LPWM = 19;
const int SAG_RPWM = 18, SAG_LPWM = 27;
const int SOL_A = 32, SOL_B = 33;
const int SAG_A = 25, SAG_B = 26;

// ---- Ayarlar ----
const int PWM_FREKANS = 20000;          // 20 kHz: duyulmaz, BTS7960 en fazla 25 kHz
const int PWM_BIT = 10;                 // 0..1023
const int MAKS_YUZDE = 60;              // ilk testte guvenlik siniri
const uint32_t ZAMAN_ASIMI_MS = 5000;   // komut gelmezse 5 sn sonra dur
const float SAYIM_PER_TUR = 836.0;      // 11 darbe x 4 kenar x 19 disli (elle 10 tur cevirip dogrula)
const uint32_t RAMPA_MS = 10;           // her 10 ms'de %1 artir/azalt (0 -> %60: 0,6 sn)
const uint32_t YAZDIR_MS = 200;

struct Motor {
  const char* ad;
  int rpwm, lpwm;
  ESP32Encoder enc;
  int hedef = 0;          // %
  int simdiki = 0;        // % (rampali)
  int64_t oncekiSayim = 0;
  Motor(const char* a, int r, int l) : ad(a), rpwm(r), lpwm(l) {}
};

Motor sol("SOL", SOL_RPWM, SOL_LPWM);
Motor sag("SAG", SAG_RPWM, SAG_LPWM);

uint32_t sonKomut = 0, sonRampa = 0, sonYazdir = 0;

void pwmYaz(Motor& m, int yuzde) {
  int duty = abs(yuzde) * ((1 << PWM_BIT) - 1) / 100;
  if (yuzde > 0)      { ledcWrite(m.lpwm, 0);    ledcWrite(m.rpwm, duty); }
  else if (yuzde < 0) { ledcWrite(m.rpwm, 0);    ledcWrite(m.lpwm, duty); }
  else                { ledcWrite(m.rpwm, 0);    ledcWrite(m.lpwm, 0); }
}

void rampa(Motor& m) {
  if (m.simdiki < m.hedef) m.simdiki++;
  else if (m.simdiki > m.hedef) m.simdiki--;
  pwmYaz(m, m.simdiki);
}

void hedefKoy(Motor& m, int yuzde) {
  m.hedef = constrain(yuzde, -MAKS_YUZDE, MAKS_YUZDE);
}

void komutOku() {
  if (!Serial.available()) return;
  String s = Serial.readStringUntil('\n');
  s.trim();
  if (s.length() == 0) return;
  char c = toupper(s.charAt(0));
  int deger = s.substring(1).toInt();
  sonKomut = millis();
  switch (c) {
    case 'L': hedefKoy(sol, deger); break;
    case 'R': hedefKoy(sag, deger); break;
    case 'B': hedefKoy(sol, deger); hedefKoy(sag, deger); break;
    case 'S': hedefKoy(sol, 0); hedefKoy(sag, 0); break;
    case 'Z': sol.enc.clearCount(); sag.enc.clearCount();
              sol.oncekiSayim = 0; sag.oncekiSayim = 0; break;
    default:  Serial.println("Komutlar: L <yuzde>, R <yuzde>, B <yuzde>, S, Z"); return;
  }
  Serial.printf(">> hedef SOL %d%%  SAG %d%%\n", sol.hedef, sag.hedef);
}

void yazdir(Motor& m, float dt) {
  int64_t sayim = m.enc.getCount();
  float tur = (sayim - m.oncekiSayim) / SAYIM_PER_TUR;
  m.oncekiSayim = sayim;
  float rpm = tur / dt * 60.0;
  Serial.printf("%s pwm %4d%%  sayim %8lld  teker %7.1f rpm | ", m.ad, m.simdiki, (long long)sayim, rpm);
}

void setup() {
  Serial.begin(115200);
  Serial.setTimeout(20);
  const int pwmPinleri[] = {SOL_RPWM, SOL_LPWM, SAG_RPWM, SAG_LPWM};
  for (int p : pwmPinleri) {
    ledcAttach(p, PWM_FREKANS, PWM_BIT);
    ledcWrite(p, 0);
  }
  ESP32Encoder::useInternalWeakPullResistors = puType::up;
  sol.enc.attachFullQuad(SOL_A, SOL_B);
  sag.enc.attachFullQuad(SAG_A, SAG_B);
  sol.enc.clearCount();
  sag.enc.clearCount();
  delay(300);
  Serial.println("\nRAPTOR BTS7960 testi hazir. Ornek: L 20  (sol motor %20)");
}

void loop() {
  uint32_t t = millis();
  komutOku();

  if ((sol.hedef || sag.hedef) && t - sonKomut > ZAMAN_ASIMI_MS) {
    hedefKoy(sol, 0); hedefKoy(sag, 0);
    Serial.println(">> zaman asimi: duruyorum");
  }
  if (t - sonRampa >= RAMPA_MS) {
    sonRampa = t;
    rampa(sol);
    rampa(sag);
  }
  if (t - sonYazdir >= YAZDIR_MS) {
    float dt = (t - sonYazdir) / 1000.0;
    sonYazdir = t;
    yazdir(sol, dt);
    yazdir(sag, dt);
    Serial.println();
  }
}
