#pragma once

#include <cstdint>
#include <Print.h>

class Surenoo_SLC2004A3 : public Print {
public:
  const int pin_en;
  const int pin_rs;
  const int pin_d4;
  const int pin_d5;
  const int pin_d6;
  const int pin_d7;

  const uint8_t rows;
  const uint8_t cols;

  uint8_t cursorRow;
  uint8_t cursorCol;

  Surenoo_SLC2004A3(uint8_t rows, uint8_t cols, int pin_en, int pin_rs, int pin_d4, int pin_d5, int pin_d6, int pin_d7);

  void begin();
  void clear(void);
  void setCursor(uint8_t row, uint8_t col);
  void showUnderlineCursor(bool visible);
  void showBlockCursor(bool visible);
  virtual size_t write(uint8_t ch) override;

  void sendCommand(uint8_t command);
  void sendData(uint8_t ch);
  void sendHalfByte(uint8_t halfByte);
  void sendByte(uint8_t b, bool is_command);
};
