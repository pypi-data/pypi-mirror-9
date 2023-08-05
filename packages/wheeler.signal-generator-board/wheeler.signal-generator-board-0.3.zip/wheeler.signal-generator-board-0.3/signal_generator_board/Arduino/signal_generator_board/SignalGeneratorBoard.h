#ifndef _SIGNAL_GENERATOR_BOARD_H_
#define _SIGNAL_GENERATOR_BOARD_H_

#include <BaseNode.h>
#include "Config.h"

#if ___HARDWARE_MINOR_VERSION___ > 1
  #define SOFT_SPI // SPI pins are reserved for in system programming
#endif

#ifdef SOFT_SPI
inline void shiftOutFast(uint8_t dataPin, uint8_t clockPin, uint8_t bitOrder,
                         uint8_t val) {
  uint8_t cnt;
  uint8_t bitData, bitNotData;
  uint8_t bitClock, bitNotClock;
  volatile uint8_t *outData;
  volatile uint8_t *outClock;

  outData = portOutputRegister(digitalPinToPort(dataPin));
  outClock = portOutputRegister(digitalPinToPort(clockPin));
  bitData = digitalPinToBitMask(dataPin);
  bitClock = digitalPinToBitMask(clockPin);

  bitNotClock = bitClock;
  bitNotClock ^= 0x0ff;

  bitNotData = bitData;
  bitNotData ^= 0x0ff;

  cnt = 8;
  if (bitOrder == LSBFIRST) {
    do {
      if ( val & 1 ) {
        *outData |= bitData;
      } else {
        *outData &= bitNotData;
      }

      *outClock |= bitClock;
      *outClock &= bitNotClock;
      val >>= 1;
      cnt--;
    } while( cnt != 0 );
  } else {
    do {
      if ( val & 128 ) {
        *outData |= bitData;
      } else {
        *outData &= bitNotData;
      }

      *outClock |= bitClock;
      *outClock &= bitNotClock;
      val <<= 1;
      cnt--;
    } while( cnt != 0 );
  }
}
#endif // SOFT_SPI

class SignalGeneratorClass : public BaseNode {
public:
  struct ConfigSettings {
    Version version;
    uint8_t pot[6];
    float hf_amplitude_correction;
    float max_voltage_rms;
  };

  static const uint8_t CMD_GET_WAVEFORM_VOLTAGE =           0xA7;
  static const uint8_t CMD_SET_WAVEFORM_VOLTAGE =           0xA8;
  static const uint8_t CMD_GET_WAVEFORM_FREQUENCY =         0xA9;
  static const uint8_t CMD_SET_WAVEFORM_FREQUENCY =         0xAA;
  static const uint8_t CMD_GET_POT_VALUE =                  0xB7;
  static const uint8_t CMD_SET_POT_VALUE =                  0xB8;
  static const uint8_t CMD_MEASURE_VOUT_PK_PK =             0xB9;

  static const int LTC6903_SS_PIN = 2;
  static const int AD5206_SS_PIN = 3;
  static const int FREQ_RANGE_PIN = 4;
#ifdef SOFT_SPI
  static const int S_SCK_PIN = 5;
  static const int S_MOSI_PIN = 6;
#endif // SOFT_SPI
  static const float F_MIN = 100.0;
  static const float F_MAX = 10e3;
  static const float R_MAX = 100e3;
  static const float C1 = 47e-9;
  static const float C2 = 6.8e-9;
  static const float LOG_F_STEP;
  static const char R1_INDEX[] PROGMEM;
  static const char R2_INDEX[] PROGMEM;
  static const char R4_INDEX[] PROGMEM;
  static const char R5_INDEX[] PROGMEM;

  void begin();
  bool process_serial_input();
  void process_wire_command();
  Version config_version();
  void set_pot(byte address, byte level, bool save_to_eeprom=false, bool display_msg=true);
  void set_waveform_frequency(float freq);
  uint8_t set_waveform_voltage(float vrms);
  void set_i2c_address(uint8_t address);
  void set_hf_amplitude_correction(float correction);
  float vout_pk_pk();

protected:
#if ___HARDWARE_MINOR_VERSION___ > 1
  bool supports_isp() { return true; }
#endif
  void dump_config();
  void load_config(bool use_defaults=false);
  void save_config();
  ConfigSettings config_settings_;

private:
  float waveform_frequency_;
  float waveform_voltage_;
  uint8_t pot_[6];
};

extern SignalGeneratorClass SignalGeneratorBoard;

#endif // _SIGNAL_GENERATOR_BOARD_H_
