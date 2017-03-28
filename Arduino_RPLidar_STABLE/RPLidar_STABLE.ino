#include <RPLidar.h>
#include <SPI.h>
#include <SD.h>
#include <Wire.h>
#include "RTClib.h"

//-----------------------------LIDAR CONSTANT DEFINES
#define RPLIDAR_MIN_QUALITY 10
#define RPLIDAR_MIN_DISTANCE 6500

//-----------------------------SD I/O CONSTANT DEFINES
#define LOG_INTERVAL  1000 // mills between entries (reduce to take more/faster data)
// how many milliseconds before writing the logged data permanently to disk
// set it to the LOG_INTERVAL to write each time (safest)
// set it to 10*LOG_INTERVAL to write all data every 10 datareads, you could lose up to 
// the last 10 reads if power is lost but it uses less power and is much faster!
#define SYNC_INTERVAL 1000 // mills between calls to flush() - to write data to the card
uint32_t syncTime = 0; // time of last sync()
#define ECHO_TO_SERIAL   1 // echo data to serial port
#define WAIT_TO_START    0 // Wait for serial input in setup()
#define aref_voltage 3.3         // we tie 3.3V to ARef and measure it with a multimeter!
#define bandgap_voltage 1.1     

//LIDAR VARIABLES
RPLidar lidar;

//SD I/O VARIABLES
Sd2Card card;
SdVolume volume;
SdFile root;
File datafile; 

//PIN CONSTANTS
#define RPLIDAR_MOTOR 9 // The PWM pin for control the speed of RPLIDAR's motor.
#define CHIP_SELECT 53
#define BUTTON_PRESS_NEXT 30 // 0 for on, 1 for off
#define BUTTON_PRESS_RUN 32
#define BUTTON_PRESS_PREV 34
#define RED_PIN  2
#define GREEN_PIN 3
#define BLUE_PIN 4

//DATA FILES VARIABLES (file names have to be 8.3 format)
int file_counter = 0;
char* data_file_names[] = {"1M1MPHT1.CSV", "1M1MPHT2.CSV", "1M1MPHT3.CSV","1M1MPHT4.CSV", "1M3MPHT5.CSV",
                          "1M2MPHT1.CSV", "1M2MPHT2.CSV", "1M2MPHT3.CSV","1M2MPHT4.CSV", "1M2MPHT5.CSV",
                          "1M3MPHT1.CSV", "1M3MPHT2.CSV", "1M3MPHT3.CSV","1M3MPHT4.CSV", "1M3MPHT5.CSV",
                          "1M4MPHT1.CSV", "1M4MPHT2.CSV", "1M4MPHT3.CSV","1M4MPHT4.CSV", "1M4MPHT5.CSV",
                          "1M5MPHT1.CSV", "1M5MPHT2.CSV", "1M5MPHT3.CSV","1M5MPHT4.CSV", "1M5MPHT5.CSV"};                        
long int trial_time_intervals[] = {26843, 13421, 8947, 6710, 5368}; //time (ms) it takes to complete 12m in 1-5 mph

//TIMING VARIABLES
bool trial_running = false;
bool test_running = true;
unsigned long last_timestamp = 0;
unsigned long current_time = 0;
int file_changer = 0;
/**************************SD CARD FNS**************************/
void initSDCard(){
  if (!SD.begin(CHIP_SELECT)) {
     Serial.println("Card failed, or not present");
  }
  else{
    Serial.println("SD card initialized.");
  }
  Wire.begin();  
  analogReference(EXTERNAL); 
}

bool initFile(){
  if(file_counter > sizeof(data_file_names))
    return false;

  Serial.print("Init File: ");
  Serial.print(data_file_names[file_counter]);
  Serial.println();
  
  datafile = SD.open(data_file_names[file_counter], FILE_WRITE);
  
  if(datafile){
    Serial.println("FILE SUCCESSFULLY OPENED");
    return true;
  }else{
    Serial.println("COULD NOT INIT FILE");
    return false;
  }

}

void writeToSD(float t, float d, float a, float q){
  datafile.print(t); datafile.print(","); datafile.print(d); datafile.print(","); datafile.print(a); datafile.print(","); datafile.print(q); datafile.print("\n"); 
  //research is needed to find out how often should we use flush()
  datafile.flush();
}
/**************************   END   **************************/


void scanLidar(int timestamp){
  if (IS_OK(lidar.waitPoint())) {
    float distance = lidar.getCurrentPoint().distance;
    float quality = lidar.getCurrentPoint().quality;
    if(!(quality < RPLIDAR_MIN_QUALITY || distance > RPLIDAR_MIN_DISTANCE)){
      //Timestamp (ms), distance (mm), angle (degrees), quality (0-60~)
      writeToSD(timestamp, distance, lidar.getCurrentPoint().angle, quality);
    }
  } else {
    rplidar_response_device_info_t info;
    if (IS_OK(lidar.getDeviceInfo(info, 100))) {
       lidar.startScan();
       delay(1000);
    }
    
  }
}

void setColor(int red, int green, int blue)
{
  #ifdef COMMON_ANODE
  red = 255 - red;
  green = 255 - green;
  blue = 255 - blue;
  #endif
  analogWrite(RED_PIN, red);
  analogWrite(GREEN_PIN, green);
  analogWrite(BLUE_PIN, blue);
}

void setup() {
  // bind the RPLIDAR driver to the arduino hardware serial
  lidar.begin(Serial2);
  Serial.begin(115200);
  
  // set pin modes
  pinMode(RPLIDAR_MOTOR, OUTPUT);
  pinMode(CHIP_SELECT,OUTPUT);
  
  pinMode(BUTTON_PRESS_RUN, INPUT_PULLUP);
  pinMode(BUTTON_PRESS_NEXT, INPUT_PULLUP);
  pinMode(BUTTON_PRESS_PREV, INPUT_PULLUP);

  pinMode(RED_PIN, OUTPUT);
  pinMode(GREEN_PIN, OUTPUT);
  pinMode(BLUE_PIN, OUTPUT);
  
  initSDCard();
  
}

void loop() {
  if(!test_running)
    return;
    
  if(trial_running){
    
    current_time = millis();
    scanLidar(current_time - last_timestamp);
    if(current_time - last_timestamp > trial_time_intervals[file_counter%5]){
      trial_running = false;
      analogWrite(RPLIDAR_MOTOR, 0);
      Serial.println("***SCAN ENDED***\n\n");
      datafile.close();
    }
  }
  else{
    //wait for button to be pressed
    
    if(digitalRead(BUTTON_PRESS_PREV) == 0 && file_counter > 0){

      file_counter --;
      Serial.print("PREV: FileCounter: ");
      Serial.print(file_counter);
      Serial.println();
      setColor(255,0,0); //red if prev
      delay(2000);
      setColor(0,0,0);
    }
    if(digitalRead(BUTTON_PRESS_NEXT) == 0){

      file_counter ++;
      Serial.print("NEXT: FileCounter: ");
      Serial.print(file_counter);
      Serial.println();
      setColor(0,255,0); //green if next
      delay(2000);
      setColor(0,0,0);
    }
    if(digitalRead(BUTTON_PRESS_RUN) == 0){
    
      Serial.print("RUN: FileCounter: ");
      Serial.print(file_counter);
      Serial.println();
      
      trial_running = true;
      test_running = initFile();
      
      for(int i = 255; i >= 0; i-=25){
        setColor(0, i, 255);
        delay(200);
      }

      setColor(255,0,0);//ready
      delay(1000);
      setColor(0,0,255);//set
      analogWrite(RPLIDAR_MOTOR, 255);
      delay(2000);
      setColor(255,255,0);//go
      delay(1000);
     
      Serial.println("***SCAN STARTED***");
      last_timestamp = millis();
      
    }
  } 
}
