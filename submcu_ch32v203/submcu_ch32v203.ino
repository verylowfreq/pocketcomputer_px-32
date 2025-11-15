#include <ch32v20x.h>
#include <Wire.h>
#include "Surenoo_SLC2004A3.h"
#include "KeyboardMatrix.h"

constexpr int PIN_ROWS[5] = {PB14,PB15,PA8,PA9,PA10};
constexpr int PIN_COLS[13] = {PA1,PA2,PA3,PA4,PA5,PA6,PA7,PB0,PB1,PB10,PB11,PB12,PB13};

constexpr int PIN_CLCD_EN = PA12;
constexpr int PIN_CLCD_RS = PA11;
constexpr int PIN_CLCD_DATA[4] = {PB5,PB4,PB3,PA15};

constexpr int PIN_SCL = 0;
constexpr int PIN_SDA = 0;

#define SLAVE_ADDRESS 0x2e

Surenoo_SLC2004A3 CLCD(4, 20, PIN_CLCD_EN, PIN_CLCD_RS, PIN_CLCD_DATA[0], PIN_CLCD_DATA[1], PIN_CLCD_DATA[2], PIN_CLCD_DATA[3]);
KeyboardMatrix Keyboard(PIN_COLS, PIN_ROWS);

typedef enum {
  CMD_NOP,
  CMD_CLCD_DATA,
  CMD_CLCD_CMD,
  CMD_CLCD_BKL,
  CMD_KBD_READ_HID,
  CMD_KBD_READ_ASCII,
  CMD_SLEEP
} command_t;

uint8_t requested_data_type;

constexpr uint8_t WIRE_DATA_LENGTH = 8;
uint8_t wire_data[WIRE_DATA_LENGTH];
uint8_t wire_data_cursor;

void receiveEvent(int num_of_Bytes) {
  while (num_of_Bytes) {
    uint8_t data = Wire.read();
    num_of_Bytes -= 1;
    if (data == CMD_NOP) {
      // Nop
      Wire.read();
    
    } else if (data == CMD_CLCD_DATA) {
      if (!num_of_Bytes) break;
      uint8_t databyte = Wire.read();
      CLCD.sendData(databyte);

    } else if (data == CMD_CLCD_CMD) {
      if (!num_of_Bytes) break;
      uint8_t cmdbyte = Wire.read();
      CLCD.sendCommand(cmdbyte);

    } else if (data == CMD_CLCD_BKL) {
      if (!num_of_Bytes) break;
      uint8_t bklstate = Wire.read();
      (void)bklstate;

    } else if (data == CMD_KBD_READ_HID) {
      requested_data_type = CMD_KBD_READ_HID;
      wire_data_cursor = 0;

    } else if (data == CMD_KBD_READ_ASCII) {
      requested_data_type = CMD_KBD_READ_ASCII;
      wire_data_cursor = 0;

    } else if (data == CMD_SLEEP) {
      enter_sleep();
    }
  }
}

void requestEvent() {
  Wire.write(wire_data[wire_data_cursor]);
  wire_data_cursor = (wire_data_cursor + 1) % WIRE_DATA_LENGTH;
}


void enter_sleep() {
  // I2CのSCLピンに割り込みを設定して、STOPモードに入る

  Wire.end();


  RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOB, ENABLE);
  RCC_APB2PeriphClockCmd(RCC_APB2Periph_AFIO, ENABLE);
  RCC_APB1PeriphClockCmd(RCC_APB1Periph_PWR, ENABLE);
  NVIC_PriorityGroupConfig(NVIC_PriorityGroup_1);

  GPIO_InitTypeDef GPIO_InitStructure = {};
  GPIO_InitStructure.GPIO_Pin = GPIO_Pin_9;
  GPIO_InitStructure.GPIO_Mode = GPIO_Mode_IPU;
  GPIO_InitStructure.GPIO_Speed = GPIO_Speed_50MHz;
  GPIO_Init(GPIOB, &GPIO_InitStructure);

  /* GPIO PB9 ----> EXTI_Line0 */
  EXTI_InitTypeDef EXTI_InitStructure = {};
  GPIO_EXTILineConfig(GPIO_PortSourceGPIOB, GPIO_PinSource9);
  EXTI_InitStructure.EXTI_Line = EXTI_Line9;
  EXTI_InitStructure.EXTI_Mode = EXTI_Mode_Interrupt;
  EXTI_InitStructure.EXTI_Trigger = EXTI_Trigger_Falling;
  EXTI_InitStructure.EXTI_LineCmd = ENABLE;
  EXTI_Init(&EXTI_InitStructure);

  NVIC_InitTypeDef NVIC_InitStructure = {};
  NVIC_InitStructure.NVIC_IRQChannel = EXTI9_5_IRQn;
  NVIC_InitStructure.NVIC_IRQChannelPreemptionPriority = 1;
  NVIC_InitStructure.NVIC_IRQChannelSubPriority = 1;
  NVIC_InitStructure.NVIC_IRQChannelCmd = ENABLE;
  NVIC_Init(&NVIC_InitStructure);

  PWR_EnterSTOPMode(PWR_Regulator_LowPower, PWR_STOPEntry_WFI);

  // STOPモードから復帰したら、ここから再開する

  SystemInit();

  clcd_init();
  wire_init();
  keyboard_init();
}



void clcd_init() {
  CLCD.begin();
  CLCD.clear();
}

void clcd_print_banner() {
  CLCD.clear();
  CLCD.setCursor(0, 0);
  CLCD.print("PX-32 SubMCU");
  CLCD.setCursor(1, 0);
  CLCD.print("Build:");
  CLCD.setCursor(2, 0);
  CLCD.print(" " __TIME__);
  CLCD.setCursor(3, 0);
  CLCD.print(" " __DATE__);
}

void wire_init() {
  Wire.setSCL(PB8);
  Wire.setSDA(PB9);
  Wire.begin(SLAVE_ADDRESS);
  Wire.onReceive(receiveEvent);
  Wire.onRequest(requestEvent);
}

void keyboard_init() {
  Keyboard.begin();
}

void setup() {
  // Wait for power stable
  delay(100);

  clcd_init();
  wire_init();
  keyboard_init();

  // clcd_print_banner();
}

void loop() {
  static unsigned long timer = 0;
  static int counter = 0;

  Keyboard.update();
  {
    char ch = Keyboard.ReadKeyASCII();
    wire_data[0] = ch;
  }

  delay(20);
}
