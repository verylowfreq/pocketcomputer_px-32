#pragma once

typedef enum
{
    KC_TAB = 0x00 | 0x00,
    KC_Q = 0x00 | 0x01,
    KC_W = 0x00 | 0x02,
    KC_E = 0x00 | 0x03,
    KC_R = 0x00 | 0x04,
    KC_T = 0x00 | 0x05,
    KC_Y = 0x00 | 0x06,
    KC_U = 0x00 | 0x07,
    KC_I = 0x00 | 0x08,
    KC_O = 0x00 | 0x09,
    KC_P = 0x00 | 0x0a,
    KC_MINUS = 0x00 | 0x0b,
    KC_BKSP = 0x00 | 0x0c,

    KC_SYM = 0x10 | 0x00,
    KC_A = 0x10 | 0x01,
    KC_S = 0x10 | 0x02,
    KC_D = 0x10 | 0x03,
    KC_F = 0x10 | 0x04,
    KC_G = 0x10 | 0x05,
    KC_H = 0x10 | 0x06,
    KC_J = 0x10 | 0x07,
    KC_K = 0x10 | 0x08,
    KC_L = 0x10 | 0x09,
    KC_COLON = 0x10 | 0x0a,
    KC_LBRC = 0x10 | 0x0b,
    KC_ENTER = 0x10 | 0x0c,

    KC_CAPS = 0x20 | 0x00,
    KC_Z = 0x20 | 0x01,
    KC_X = 0x20 | 0x02,
    KC_C = 0x20 | 0x03,
    KC_V = 0x20 | 0x04,
    KC_B = 0x20 | 0x05,
    KC_N = 0x20 | 0x06,
    KC_M = 0x20 | 0x07,
    KC_COMMA = 0x20 | 0x08,
    KC_PERIOD = 0x20 | 0x09,
    KC_SLASH = 0x20 | 0x0a,
    KC_SPACE = 0x20 | 0x0b,

    KC_NUM_0 = 0x30 | 0x00,
    KC_NUM_DOT = 0x30 | 0x01,
    KC_NUM_PM = 0x30 | 0x02,
    KC_NUM_PLUS = 0x30 | 0x03,
    KC_LEFT = 0x30 | 0x04,
    KC_UP = 0x30 | 0x05,
    KC_DOWN = 0x30 | 0x06,
    KC_RIGHT = 0x30 | 0x07,

    KC_NUM_1 = 0x40 | 0x00,
    KC_NUM_2 = 0x40 | 0x01,
    KC_NUM_3 = 0x40 | 0x02,
    KC_NUM_MINUS = 0x40 | 0x03,
    KC_NUM_4 = 0x40 | 0x04,
    KC_NUM_5 = 0x40 | 0x05,
    KC_NUM_6 = 0x40 | 0x06,
    KC_NUM_ASTRSK = 0x40 | 0x07,
    KC_NUM_7 = 0x40 | 0x08,
    KC_NUM_8 = 0x40 | 0x09,
    KC_NUM_9 = 0x40 | 0x0a,
    KC_NUM_SLASH = 0x40 | 0x0b,
} keycode_t;

typedef enum : char {
    KEY_SPECIAL_SYM = 0x01,
    KEY_SPECIAL_CAPS = 0x02,
    KEY_SPECIAL_PM = 0x03,
    KEY_SPECIAL_LEFT = 0x04,
    KEY_SPECIAL_UP = 0x05,
    KEY_SPECIAL_DOWN = 0x06,
    KEY_SPECIAL_RIGHT = 0x07,
    KEY_SPECIAL_LAST
} special_keys_t;

constexpr int KBD_ASCII_TABLE[] = {
    '\t', 'q','w','e','r','t','y','u','i','o','p','-','\b',
    0x01, 'a','s','d','f','g','h','j','k','l',':','[','\n',
    0x02, 'z','x','c','v','b','n','m',',','.','/',-1,' ',
    '0', '.', 0x03, '+', 0x04, 0x05, 0x06, 0x07,-1,-1,-1,-1,-1,
    '-','2','3','1','4','5','6','*','7','8','9','/',-1
};
constexpr size_t KBD_ASCII_TABLE_LENGTH = (sizeof(KBD_ASCII_TABLE) / sizeof(KBD_ASCII_TABLE[0]));

constexpr int KBD_SYM_ASCII_TABLE[] = {
    -1,  '!','"','#','$','%','&','\'','(',')','=','_', -1,
    -1,  '@','`','~','^', -1,'*', '+','{','}',';','[', -1,
    -1,   -1, -1, -1, -1, -1,'|', '?','<','>','\\',-1, -1,
    -1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,
    -1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1
};
constexpr size_t KBD_SYM_ASCII_TABLE_LENGTH = (sizeof(KBD_SYM_ASCII_TABLE) / sizeof(KBD_SYM_ASCII_TABLE[0]));



class KeyboardMatrix {
public:
    constexpr static int COLS = 13;
    constexpr static int ROWS = 5;
    constexpr static int DELAY_ROW_USEC = 50;

    const int* pin_cols;
    const int* pin_rows;

    uint32_t prev[ROWS];
    uint32_t state[ROWS];

    bool is_sym_enabled;
    bool is_caps_enabled;

    KeyboardMatrix(const int pin_cols[], const int pin_rows[]) : pin_cols(pin_cols), pin_rows(pin_rows) { }

    void begin();

    void select_row(uint8_t row);
    void unselect_row(uint8_t row);
    uint32_t read_row(uint8_t row);

    // キーの状態を読み取る
    void update();

    // 前回読み取り時から変更があるか？
    bool IsChanged();
    
    // 押されている文字・キーをひとつ取得する
    char ReadKeyASCII();

    // 指定のキーが押されているかを取得する
    bool IsKeyPressed(keycode_t key);
};
