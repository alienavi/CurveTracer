const int pwmOut[] = {5,6}; //PWM output will be to this pin.
#define X A0
#define Y A1
#define NV 3
const int sample = 50;

void garbage(){
    for(int i=1 ; i<9 ; i+=1){
      analogWrite(pwmOut[1],i*31);
      for(int j=0 ; j<10 ; j++){
        analogWrite(pwmOut[0],j);
        for(int k=0 ; k<4 ; k++){
            analogRead(X);
            analogRead(Y);     
        }
      }
    }  
}

void setup() {
    Serial.begin(115200);
  
    //Setting pwm freq as 62.5K
    int prescalerVal = 0x07;
    TCCR0B &= ~prescalerVal;
    prescalerVal = 1;
    TCCR0B |= prescalerVal;
    TCCR0B &= B11111000 | B00000001;
    //End
    //Setting pinModes  
    pinMode(pwmOut[0],OUTPUT);
    pinMode(pwmOut[1],OUTPUT);
    pinMode(X,INPUT);
    pinMode(Y,INPUT);
    //Setting analog reference 1.1V
    analogReference(INTERNAL);
    //Waiting fr analogReference to get stable
    garbage();
}

int x = 0,y = 0;
 
void loop() {
  //Wait for input
  analogWrite(NV,127);
  if(Serial.available() > 0){
      for(int i=1 ; i<9 ; i+=1){
        //Step 
        analogWrite(pwmOut[1],i*31);
        for(int j=255 ; j>=0 ; j--){
          //ramp
          analogWrite(pwmOut[0],j);
          for(int k=0 ; k<sample ; k++){
            x += analogRead(X);
            y += analogRead(Y);
            delay(5);  
          }
                    
          Serial.print(float(x/sample));
          Serial.print("\t");
          Serial.print(float(y/sample));  
          Serial.print("\t");
          x = 0;
          y = 0;   
          delay(5);  
        }
      }
      //Printing EOL to end
      Serial.println();
      //asm volatile("  jmp 0");
  }
}


