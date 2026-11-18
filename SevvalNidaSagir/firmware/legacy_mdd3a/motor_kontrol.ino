// RAPTOR - Motor kontrol: enkoder + PI hiz kontrolu + odometri
// Donanim: ESP32 + Cytron MDD3A + 2x JGB37-520 enkoderli motor
// Arduino IDE, ESP32 core 3.x (LEDC API: ledcAttach / ledcWrite)
// Kutuphane: Library Manager'dan "ESP32Encoder" (Kevin Harrington)
//
// TEST: Tekerler havadayken baslayin (araci bir kutunun ustune koyun).
// Serial Monitor: 115200 baud, satir sonu "Newline".
//   "0.3 0"   -> 0.3 m/s ileri
//   "0 1.0"   -> yerinde 1 rad/s sola donus
//   "0 0"     -> dur
// Elle test ederken WATCHDOG_MS = 0 yapin, yoksa tek komut 300 ms sonra durur.

#include <ESP32Encoder.h>

// ================= PINLER =================
const int ENC_SOL_A = 32, ENC_SOL_B = 33;   // sol enkoder sari/yesil
const int ENC_SAG_A = 25, ENC_SAG_B = 26;   // sag enkoder sari/yesil
const int MDD_M1A = 23, MDD_M1B = 19;       // MDD3A kanal 1 -> sol motor
const int MDD_M2A = 18, MDD_M2B = 27;       // MDD3A kanal 2 -> sag motor
// GPIO 21/22 IMU (I2C) icin bos birakildi.

// ================= ARAC PARAMETRELERI (kalibrasyonla duzelt) =================
const float SAYIM_PER_TUR = 1320.0;   // teker turu basina sayim
const float TEKER_CAP     = 0.085;    // m
const float TEKER_ARALIGI = 0.20;     // m (L)
// Ileri komutta iki teker de ileri donmuyorsa MOTOR_YON'u,
// ileri giderken olculen hiz negatifse ENC_YON'u degistir.
const int SOL_ENC_YON = 1,   SAG_ENC_YON = -1;
const int SOL_MOTOR_YON = 1, SAG_MOTOR_YON = -1;

// ================= KONTROL PARAMETRELERI (ayarlanacak) =================
const uint32_t DONGU_MS    = 20;      // 50 Hz kontrol dongusu
const float V_MAX          = 1.2;     // m/s, teker basina hiz siniri
const float IVME_MAX       = 1.0;     // m/s^2, hiz rampasi
const float KFF            = 0.75;    // feedforward: PWM / (m/s)
const float KP             = 0.6;
const float KI             = 3.0;
const float MIN_PWM        = 0.08;    // olu bolge: motorun donmeye basladigi PWM
const float HIZ_FILTRE     = 0.5;     // 0..1, olculen hiz icin alcak geciren filtre
const uint32_t WATCHDOG_MS = 300;     // bu surede komut gelmezse dur (0 = kapali)
const bool PLOT_MODU       = false;   // true: Serial Plotter icin hedef/olculen hiz

// ================= PWM =================
const int PWM_FREKANS    = 20000;     // 20 kHz: motor otmez, MDD3A'nin siniri
const int PWM_COZUNURLUK = 10;        // 0..1023
const int PWM_MAX        = (1 << PWM_COZUNURLUK) - 1;

const float METRE_PER_SAYIM = PI * TEKER_CAP / SAYIM_PER_TUR;

struct Teker {
  ESP32Encoder enc;
  int encYon, motorYon, pinA, pinB;
  int64_t oncekiSayim = 0;
  float hedef = 0;      // rampadan gecmis hedef hiz (m/s)
  float olculen = 0;    // filtrelenmis olculen hiz (m/s)
  float integral = 0;
  float yol = 0;        // bu dongude gidilen yol (m)
};

Teker sol, sag;
float komutV = 0, komutW = 0;     // Pi'den gelen hedef (m/s, rad/s)
uint32_t sonKomut = 0, sonDongu = 0;
float x = 0, y = 0, theta = 0;
char satir[64];
int satirLen = 0;

// ---------- Motoru sur: u = -1..1 ----------
void motorYaz(Teker &t, float u) {
  u *= t.motorYon;
  int duty = (int)(fabsf(u) * PWM_MAX);
  if (duty == 0)      { ledcWrite(t.pinA, 0);    ledcWrite(t.pinB, 0); }
  else if (u > 0)     { ledcWrite(t.pinA, duty); ledcWrite(t.pinB, 0); }
  else                { ledcWrite(t.pinA, 0);    ledcWrite(t.pinB, duty); }
}

// ---------- Enkoderden hiz olc ----------
void olc(Teker &t, float dt) {
  int64_t sayim = t.enc.getCount();
  long fark = t.encYon * (long)(sayim - t.oncekiSayim);
  t.oncekiSayim = sayim;
  t.yol = fark * METRE_PER_SAYIM;
  float v = t.yol / dt;
  t.olculen = HIZ_FILTRE * v + (1.0f - HIZ_FILTRE) * t.olculen;
}

// ---------- PI + feedforward: PWM dondurur ----------
float kontrol(Teker &t, float istenen, float dt) {
  // Rampa: hedef hiz en fazla IVME_MAX ile degisir
  float fark = istenen - t.hedef;
  float maxFark = IVME_MAX * dt;
  if (fark >  maxFark) fark =  maxFark;
  if (fark < -maxFark) fark = -maxFark;
  t.hedef += fark;

  // Durma: hedef sifirsa motoru birak, integrali temizle
  if (fabsf(t.hedef) < 0.005f && fabsf(istenen) < 0.005f) {
    t.hedef = 0; t.integral = 0;
    return 0;
  }

  float e = t.hedef - t.olculen;
  float ff = KFF * t.hedef + (t.hedef > 0 ? MIN_PWM : -MIN_PWM);
  float yeniIntegral = t.integral + e * dt;
  float u = ff + KP * e + KI * yeniIntegral;

  // Anti-windup: cikis doyumdaysa integrali buyutme
  if (u > 1.0f)       u = 1.0f;
  else if (u < -1.0f) u = -1.0f;
  else                t.integral = yeniIntegral;
  return u;
}

// ---------- Seri porttan "v w" komutu oku ----------
void komutOku() {
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n' || c == '\r') {
      if (satirLen > 0) {
        satir[satirLen] = 0;
        char *son;
        float v = strtof(satir, &son);
        float w = strtof(son, nullptr);
        komutV = v; komutW = w;
        sonKomut = millis();
        satirLen = 0;
      }
    } else if (satirLen < (int)sizeof(satir) - 1) {
      satir[satirLen++] = c;
    }
  }
}

void tekerKur(Teker &t, int encA, int encB, int encYon, int pinA, int pinB, int motorYon) {
  t.enc.attachFullQuad(encA, encB);
  t.enc.clearCount();
  t.encYon = encYon; t.motorYon = motorYon;
  t.pinA = pinA; t.pinB = pinB;
  ledcAttach(pinA, PWM_FREKANS, PWM_COZUNURLUK);
  ledcAttach(pinB, PWM_FREKANS, PWM_COZUNURLUK);
  motorYaz(t, 0);
}

void setup() {
  Serial.begin(115200);
  ESP32Encoder::useInternalWeakPullResistors = puType::up;
  tekerKur(sol, ENC_SOL_A, ENC_SOL_B, SOL_ENC_YON, MDD_M1A, MDD_M1B, SOL_MOTOR_YON);
  tekerKur(sag, ENC_SAG_A, ENC_SAG_B, SAG_ENC_YON, MDD_M2A, MDD_M2B, SAG_MOTOR_YON);
  sonDongu = millis();
}

void loop() {
  komutOku();

  uint32_t simdi = millis();
  if (simdi - sonDongu < DONGU_MS) return;
  float dt = (simdi - sonDongu) / 1000.0f;
  sonDongu = simdi;

  // 1) Olc
  olc(sol, dt);
  olc(sag, dt);

  // 2) Watchdog: komut kesildiyse hemen dur
  bool guvenli = (WATCHDOG_MS == 0) || (simdi - sonKomut <= WATCHDOG_MS && sonKomut != 0);
  if (!guvenli) {
    komutV = 0; komutW = 0;
    sol.hedef = sag.hedef = 0;
    sol.integral = sag.integral = 0;
  }

  // 3) (v, w) -> teker hizlari, oran korunarak sinirla
  float vSol = komutV - komutW * TEKER_ARALIGI / 2.0f;
  float vSag = komutV + komutW * TEKER_ARALIGI / 2.0f;
  float m = max(fabsf(vSol), fabsf(vSag));
  if (m > V_MAX) { vSol *= V_MAX / m; vSag *= V_MAX / m; }

  // 4) Kontrol ve motorlari sur
  motorYaz(sol, guvenli ? kontrol(sol, vSol, dt) : 0);
  motorYaz(sag, guvenli ? kontrol(sag, vSag, dt) : 0);

  // 5) Odometri
  float ds  = (sag.yol + sol.yol) / 2.0f;
  float dth = (sag.yol - sol.yol) / TEKER_ARALIGI;
  x += ds * cosf(theta + dth / 2.0f);
  y += ds * sinf(theta + dth / 2.0f);
  theta += dth;
  float vOlc = (sag.olculen + sol.olculen) / 2.0f;
  float wOlc = (sag.olculen - sol.olculen) / TEKER_ARALIGI;

  // 6) Cikti
  if (PLOT_MODU) {
    Serial.printf("hedefSol:%.3f,olcSol:%.3f,hedefSag:%.3f,olcSag:%.3f\n",
                  sol.hedef, sol.olculen, sag.hedef, sag.olculen);
  } else {
    // O,zaman_ms,x,y,theta,v,w  -> Raspberry Pi bu satiri okuyacak
    Serial.printf("O,%lu,%.4f,%.4f,%.4f,%.3f,%.3f\n",
                  (unsigned long)simdi, x, y, theta, vOlc, wOlc);
  }
}
