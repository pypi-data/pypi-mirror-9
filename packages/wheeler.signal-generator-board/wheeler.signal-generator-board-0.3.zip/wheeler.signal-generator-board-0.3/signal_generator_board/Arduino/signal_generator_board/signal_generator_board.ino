#include <SPI.h>
#include <Wire.h>
#include <EEPROM.h>
#include <BaseNode.h>
#include "Memory.h"

#include "SignalGeneratorBoard.h"

void setup() {
  SignalGeneratorBoard.begin();
}

void loop() {
  SignalGeneratorBoard.listen();
}
