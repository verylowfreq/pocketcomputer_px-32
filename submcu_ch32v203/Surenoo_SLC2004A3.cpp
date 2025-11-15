#include "Surenoo_SLC2004A3.h"

#include <cstdint>
#include <Arduino.h>

Surenoo_SLC2004A3::Surenoo_SLC2004A3(uint8_t rows, uint8_t cols, int pin_en, int pin_rs, int pin_d4, int pin_d5, int pin_d6, int pin_d7) :
  pin_en(pin_en), pin_rs(pin_rs), pin_d4(pin_d4), pin_d5(pin_d5), pin_d6(pin_d6), pin_d7(pin_d7), rows(rows), cols(cols) {
}

void Surenoo_SLC2004A3::begin() {
  pinMode(pin_en, OUTPUT);
  pinMode(pin_rs, OUTPUT);
  pinMode(pin_d4, OUTPUT);
  pinMode(pin_d5, OUTPUT);
  pinMode(pin_d6, OUTPUT);
  pinMode(pin_d7, OUTPUT);

  // Set 8-bit bus mode
  digitalWrite(pin_rs, LOW);
  sendHalfByte(0x03);
  delay(5);
  sendHalfByte(0x03);
  delay(1);
  sendHalfByte(0x03);
  delay(1);

  // Set 4-bit bus mode
  sendHalfByte(0x02);

  // Function set (N=1, F=0)
  sendCommand(0x28);
  // Display on (D=1, C=0, B=0)
  sendCommand(0x0c);
  // Clear
  sendCommand(0x01);
  delay(5);
  // Entry mode set (I/D=1, S=0)
  sendCommand(0x06);

  cursorRow = 0;
  cursorCol = 0;
}

void Surenoo_SLC2004A3::sendCommand(uint8_t command) {
  sendByte(command, true);
}

void Surenoo_SLC2004A3::sendData(uint8_t ch) {
  sendByte(ch, false);
}

void Surenoo_SLC2004A3::sendHalfByte(uint8_t halfByte) {
  digitalWrite(pin_en, HIGH);
  delayMicroseconds(50);
  digitalWrite(pin_d7, halfByte & 0x08 ? HIGH : LOW);
  digitalWrite(pin_d6, halfByte & 0x04 ? HIGH : LOW);
  digitalWrite(pin_d5, halfByte & 0x02 ? HIGH : LOW);
  digitalWrite(pin_d4, halfByte & 0x01 ? HIGH : LOW);
  delayMicroseconds(50);
  digitalWrite(pin_en, LOW);
  delayMicroseconds(50);
}

void Surenoo_SLC2004A3::sendByte(uint8_t b, bool is_command) {
  digitalWrite(pin_rs, is_command ? LOW : HIGH);

  sendHalfByte(b >> 4);
  sendHalfByte(b & 0x0f);
}

void Surenoo_SLC2004A3::clear(void) {
  sendCommand(0x01);
  delay(5);
}

void Surenoo_SLC2004A3::setCursor(uint8_t row, uint8_t col) {
  row = row % this->rows;
  col = col % this->cols;
  uint8_t addr = col;
  if (row == 1) { addr += 64; }
  else if (row == 2) { addr += 20; }
  else if (row == 3) { addr += 84; }
  sendCommand(0x80 + addr);
  delayMicroseconds(50);
}

void Surenoo_SLC2004A3::showUnderlineCursor(bool visible) {
  sendCommand(0x0C | (visible ? 0x02 : 0x00));
  delayMicroseconds(50);
}

void Surenoo_SLC2004A3::showBlockCursor(bool visible) {
  sendCommand(0x0C | (visible ? 0x01 : 0x00));
  delayMicroseconds(50);
}

size_t Surenoo_SLC2004A3::write(uint8_t ch) {
  // if (ch == '\r') {
  //   // Nop
  // } else if (ch == '\t') {
  //   write("  ");
  // } else if (ch == '\n') {
  //   cursorRow = (cursorRow + 1) % rows;
  //   cursorCol = 0;
  //   setCursor(cursorRow, cursorCol);
  // } else {
  //   sendData(ch);
  //   cursorCol = cursorCol + 1;
  //   if (cursorCol == cols) {
  //     // cursorRow = (cursorRow + 1) % rows;
  //     cursorCol = 0;
  //     setCursor(cursorRow, cursorCol);
  //   }
  // }
  sendData(ch);
  return 1;
}
