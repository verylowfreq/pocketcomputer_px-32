#include <Arduino.h>
#include "KeyboardMatrix.h"

void KeyboardMatrix::begin() {
    for (int i = 0; i < COLS; i++) {
        pinMode(pin_cols[i], INPUT_PULLUP);
    }
    for (int i = 0; i < ROWS; i++) {
        pinMode(pin_rows[i], OUTPUT);
        digitalWrite(pin_rows[i], HIGH);
    }
    memset(prev, 0x00, sizeof(prev));
    memset(state, 0x00, sizeof(state));
    is_sym_enabled = false;
    is_caps_enabled = false;
}

void KeyboardMatrix::select_row(uint8_t row) {
    digitalWrite(pin_rows[row], LOW);
}

void KeyboardMatrix::unselect_row(uint8_t row) {
    digitalWrite(pin_rows[row], HIGH);
}

uint32_t KeyboardMatrix::read_row(uint8_t row) {
    uint32_t result = 0;

    select_row(row);
    delayMicroseconds(DELAY_ROW_USEC);
    for (int i = 0; i < COLS; i++) {
        bool pressed = digitalRead(pin_cols[i]) == LOW;
        if (pressed) {
            result |= 0x01 << i;
        }
    }

    unselect_row(row);

    return result;
}

void KeyboardMatrix::update() {
    memcpy(prev, state, sizeof(state));
    for (int i = 0; i < ROWS; i++) {
        state[i] = read_row(i);
    }
}

bool KeyboardMatrix::IsChanged() {
    return memcmp(prev, state, sizeof(state)) != 0;
}

char KeyboardMatrix::ReadKeyASCII() {
    for (int row = 0; row < ROWS; row++) {
        for (int col = 0; col < COLS; col++) {
            uint32_t testbit = 0x01 << col;
            bool is_pressed_now = state[row] & testbit;
            bool is_pressed_prev = prev[row] & testbit;

            if (state[row] & (0x01 << col)) {
                int index = 13 * row + col;
                char ch = KBD_ASCII_TABLE[index];

                if (ch == KEY_SPECIAL_SYM && !is_pressed_prev) {
                    is_sym_enabled = !is_sym_enabled;
                    is_caps_enabled = false;
                    ch = 0;

                } else if (ch == KEY_SPECIAL_CAPS && !is_pressed_prev) {
                    is_caps_enabled = !is_caps_enabled;
                    is_sym_enabled = false;
                    ch = 0;

                } else {
                    if (is_sym_enabled) {
                        ch = KBD_SYM_ASCII_TABLE[index];
                        if (ch == -1) {
                            ch = KBD_ASCII_TABLE[index];
                        }
                    } else if (is_caps_enabled) {
                        if ('a' <= ch && ch <= 'z') {
                            ch = ch - 0x20;
                        }
                    }
                }

                if (ch == -1) {
                    return 0;
                } else {
                    return ch;
                }
            }
        }
    }
    return 0x00;
}

bool KeyboardMatrix::IsKeyPressed(keycode_t keycode) {
    int row = keycode >> 4;
    int col = keycode & 0x0f;
    uint32_t testbit = 0x01 << col;
    return state[row] & testbit;
}
