/**********************************************************/
/* CHANGES FROM THE SCRIPT MENTIONED BY PAUL LOGSTON      */
/* Demo program for:                                      */
/*    Board: SHIELD-EKG/EMG + Olimexino328                */
/*  Manufacture: OLIMEX                                   */
/*  COPYRIGHT (C) 2012                                    */
/*  Designed by:  Penko Todorov Bozhkov                   */
/*   Module Name:   Sketch                                */
/*   File   Name:   ShieldEkgEmgDemo.ino                  */
/*   Revision:  Rev.A                                     */
/*    -> Added is suppport for all Arduino boards.        */
/*       This code could be recompiled for all of them!   */
/*   Date: 19.12.2012                                     */
/*   Built with Arduino C/C++ Compiler, version: 1.0.3    */
/**********************************************************/
/**********************************************************
Purpose of this programme is to give you an easy way to 
connect Olimexino328 to ElectricGuru(TM), see:
https://www.olimex.com/Products/EEG/OpenEEG/EEG-SMT/resources/ElecGuru40.zip
where you'll be able to observe yours own EKG or EMG signal.
It is based on:
***********************************************************
* ModularEEG firmware for one-way transmission, v0.5.4-p2
* Copyright (c) 2002-2003, Joerg Hansmann, Jim Peters, Andreas Robinson
* License: GNU General Public License (GPL) v2
***********************************************************
For proper communication packet format given below have to be supported:
///////////////////////////////////////////////
////////// Packet Format Version 2 ////////////
///////////////////////////////////////////////
// 17-byte packets are transmitted from Olimexino328 at 256Hz,
// using 1 start bit, 8 data bits, 1 stop bit, no parity.

// Minimial Transmission Speed
// A sample is taken every 8ms (ie. 125 samples per second)
// 125 samples/s * sizeof(Olimexino328_packet) = 2,125 bytes per second
// 2125 bytes per second = 17,000 bits per second.
// 2.125 kBps (I think we can manage that :)
// 7,650 kB per hour ~ 7.5M MB per hour

struct Olimexino328_packet
{
  uint8_t	sync0;		// = 0xa5
  uint8_t	sync1;		// = 0x5a
  uint8_t	version;	// = 2 (packet version)
  uint8_t	count;		// packet counter. Increases by 1 each packet.
  uint16_t	data[6];	// 10-bit sample (= 0 - 1023) in big endian (Motorola) format.
  uint8_t	switches;	// State of PD5 to PD2, in bits 3 to 0.
};
*/
/**********************************************************/
#include <compat/deprecated.h>
#include <FlexiTimer2.h>
//http://www.arduino.cc/playground/Main/FlexiTimer2
#include <SD.h>

//~~~~~~~~~~
// Constants
//~~~~~~~~~~

// -------- Define Pins
#define LED1  6
#define CAL_SIG 9
#define SPEAKER 3
// change this to match your SD shield or module;
// Arduino Ethernet shield: pin 4
// Adafruit SD shields and modules: pin 10
// Sparkfun SD shield: pin 8
#define CHIPSELECT 4

// -------- Packet Constants
#define NUMCHANNELS 6
#define HEADERLEN 4
#define PACKETLEN (NUMCHANNELS * 2 + HEADERLEN + 1)

// -------- Transmission 
#define TIMER2VAL (1000/(SAMPFREQ))       // Set 125Hz sampling frequency
#define SAMPFREQ 125                      // ADC sampling rate
#define TXSPEED 115200                    // 57600 or 115200.

// --------- Global Variables
volatile unsigned char TXBuf[PACKETLEN];  // The transmission packet
volatile unsigned char TXIndex;           // Next byte to write in the transmission packet.
volatile unsigned char CurrentCh;         // Current channel being sampled.
volatile unsigned char counter = 0;	      // Additional divider used to generate CAL_SIG
volatile unsigned int ADC_Value = 0;	  // ADC current value
File dataFile;                            // File handle

boolean log_to_file = false;  // set to true to send data to SD card rather than serial port

//~~~~~~~~~~
// Functions
//~~~~~~~~~~

/****************************************************/
/*  Function name: Toggle_LED1                      */
/*  Parameters                                      */
/*    Input   :  No	                            */
/*    Output  :  No                                 */
/*    Action: Switches-over LED1.                   */
/****************************************************/
void Toggle_LED1(void){
 if (digitalRead(LED1) == HIGH) { 
   digitalWrite(LED1, LOW); 
 } else { 
   digitalWrite(LED1, HIGH); 
 }
}


/****************************************************/
/*  Function name: toggle_GAL_SIG                   */
/*  Parameters                                      */
/*    Input   :  No	                            */
/*    Output  :  No                                 */
/*    Action: Switches-over GAL_SIG.                */
/****************************************************/
void toggle_GAL_SIG(void){
 if (digitalRead(CAL_SIG) == HIGH) { 
   digitalWrite(CAL_SIG, LOW); 
 } else { 
   digitalWrite(CAL_SIG, HIGH); 
 }
}


/****************************************************/
/*  Function name: Timer2_Overflow_ISR              */
/*  Parameters                                      */
/*    Input   :  No	                            */
/*    Output  :  No                                 */
/*    Action: Determines ADC sampling frequency.    */
/****************************************************/
void Timer2_Overflow_ISR()
{ 
  //Read the 6 ADC inputs and store current values in Packet
  for (CurrentCh = 0; CurrentCh < 6; CurrentCh++) {
    ADC_Value = analogRead(CurrentCh);
    TXBuf[((2 * CurrentCh) + HEADERLEN)] = ((unsigned char)((ADC_Value & 0xFF00) >> 8)); // Write High Byte
    TXBuf[((2 * CurrentCh) + HEADERLEN + 1)] = ((unsigned char)(ADC_Value & 0x00FF));	// Write Low Byte
  }
 
  if (log_to_file) {
    dataFile = SD.open("datalog.txt", FILE_WRITE);
    // if the file is available, write to it:
    if (dataFile) {
      digitalWrite(LED1, HIGH);
      // Write packet to SD card
      for (TXIndex = 0 ; TXIndex < 17 ; TXIndex++) {
        dataFile.write(TXBuf[TXIndex]);
      }
      dataFile.close();
      digitalWrite(LED1, LOW);
    }  
    // if the file isn't open, pop up an error:
    else {
      Serial.println("error opening datalog.txt");
    }
  } else {
      digitalWrite(LED1, HIGH);
      // Send packet over serial
      for (TXIndex = 0 ; TXIndex < 17 ; TXIndex++) {
        Serial.write(TXBuf[TXIndex]);
      }
      dataFile.close();
      digitalWrite(LED1, LOW);
  }

  // Increment the packet counter
  TXBuf[3]++;	
  
  // Generate the CAL_SIGnal
  counter++;		// increment the divider counter
  if (counter == 12) {	// 250/12/2 = 10.4Hz -> Toggle frequency
    counter = 0;
    toggle_GAL_SIG();	// Generate CAL signal with frequ ~10Hz
  }
}


/****************************************************/
/*  Function name: reset_TXBuf                      */
/*  Parameters                                      */
/*    Input   :  No	                            */
/*    Output  :  No                                 */
/*    Action: Resets values in sample buffer.       */
/****************************************************/
void reset_TXBuf() {
 // Write packet header and footer
  TXBuf[0] = 0xa5;    // Sync 0
  TXBuf[1] = 0x5a;    // Sync 1
  TXBuf[2] = 2;       // Protocol version
  TXBuf[3] = 0;       // Packet counter
  TXBuf[4] = 0x02;    // CH1 High Byte
  TXBuf[5] = 0x00;    // CH1 Low Byte
  TXBuf[6] = 0x02;    // CH2 High Byte
  TXBuf[7] = 0x00;    // CH2 Low Byte
  TXBuf[8] = 0x02;    // CH3 High Byte
  TXBuf[9] = 0x00;    // CH3 Low Byte
  TXBuf[10] = 0x02;   // CH4 High Byte
  TXBuf[11] = 0x00;   // CH4 Low Byte
  TXBuf[12] = 0x02;   // CH5 High Byte
  TXBuf[13] = 0x00;   // CH5 Low Byte
  TXBuf[14] = 0x02;   // CH6 High Byte
  TXBuf[15] = 0x00;   // CH6 Low Byte 
  TXBuf[2 * NUMCHANNELS + HEADERLEN] =  0x01;	// Switches state
}


/****************************************************/
/*  Function name: write_reset_signal               */
/*  Parameters                                      */
/*    Input   :  No	                            */
/*    Output  :  No                                 */
/*    Action: Writes a reset signal to logger       */
/****************************************************/
void write_reset_signal() {

  reset_TXBuf();
  // Use switches byte to signal a reset.
  TXBuf[2 * NUMCHANNELS + HEADERLEN] =  0x02;	
  
  digitalWrite(LED1, HIGH);
  
  if (log_to_file) {
    dataFile = SD.open("datalog.txt", FILE_WRITE);
    // if the file is available, write to it:
    if (dataFile) {
      // write 3 seconds worth of packets as a reset signal.
      for (int i = 0; i < 3 * SAMPFREQ; i++) {
        digitalWrite(SPEAKER, HIGH);
        delay(TIMER2VAL / 2);
        for (TXIndex = 0 ; TXIndex < 17 ; TXIndex++) {
          dataFile.write(TXBuf[TXIndex]);
        }
        digitalWrite(SPEAKER, LOW);
        delay(TIMER2VAL / 2);
      }
      dataFile.close();
    }  
    // if the file isn't open, pop up an error:
    else {
      Serial.println("error opening datalog.txt");
    }
  } else {
    // write 3 seconds worth of packets as a reset signal.
    for (int i = 0; i < 3 * SAMPFREQ; i++) {
      digitalWrite(SPEAKER, HIGH);
      delay(TIMER2VAL / 2);
      for (TXIndex = 0 ; TXIndex < 17 ; TXIndex++) {
        Serial.write(TXBuf[TXIndex]);
      }
      digitalWrite(SPEAKER, LOW);
      delay(TIMER2VAL / 2);
    }
  }  
  
  digitalWrite(LED1, LOW);
}


/****************************************************/
/*  Function name: setup                            */
/*  Parameters                                      */
/*    Input   :  No	                            */
/*    Output  :  No                                 */
/*    Action: Initializes all peripherals           */
/****************************************************/
void setup() {
  // Setup LED1
  pinMode(5, OUTPUT);
  digitalWrite(5, LOW);
  pinMode(LED1, OUTPUT);  // Setup LED1 direction
  digitalWrite(LED1, LOW); // Setup LED1 state
  // Setup Speaker
  pinMode(0, OUTPUT);
  digitalWrite(0, LOW);
  pinMode(SPEAKER, OUTPUT);
  digitalWrite(SPEAKER, LOW);  
    // Setup calibration pin
  pinMode(CAL_SIG, OUTPUT);
  
  // Start serial port
  Serial.begin(TXSPEED);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for Leonardo only
  }
 
  if (log_to_file) {
    Serial.print("Initializing SD card...");
    // make sure that the default chip select pin is set to
    // output, even if you don't use it:
    pinMode(10, OUTPUT);
    
    // See if the card is present and can be initialized:
    if (!SD.begin(CHIPSELECT)) {
      Serial.println("card failed, or not present");
      // don't do anything more:
      return;
    }
    Serial.println("card initialized.");
  }

  // write a series of bytes that will act signal, to software 
  // consuming these bytes, that the arduino has been restarted.
  write_reset_signal();
  Serial.println("Reset signal logged.");

  noInterrupts();  // Disable all interrupts before initialization
 
  reset_TXBuf();
  // Timer2
  // Timer2 is used to setup the analag channels sampling frequency and packet update.
  // Whenever interrupt occures, the current read packet is sent to the PC
  // In addition the CAL_SIG is generated as well, so Timer1 is not required in this case!
  FlexiTimer2::set(TIMER2VAL, Timer2_Overflow_ISR);
  FlexiTimer2::start();
 
  // MCU sleep mode = idle.
  //outb(MCUCR,(inp(MCUCR) | (1<<SE)) & (~(1<<SM0) | ~(1<<SM1) | ~(1<<SM2)));
 
  interrupts();  // Enable all interrupts after initialization has been completed
}


/****************************************************/
/*  Function name: loop                             */
/*  Parameters                                      */
/*    Input   :  No	                            */
/*    Output  :  No                                 */
/*    Action: Puts MCU into sleep mode.             */
/****************************************************/
void loop() {
  __asm__ __volatile__ ("sleep");
}