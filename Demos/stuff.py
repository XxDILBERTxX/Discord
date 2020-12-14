def button_press(channel):
    if ledstats() == 'Off':
        print("LED on - motion")
        GPIO.output(led1, GPIO.HIGH)       
    else:
        print("LED off")
        GPIO.output(led1, GPIO.LOW)
    time.sleep(0.3)
GPIO.add_event_detect(button1,GPIO.RISING,callback=button_press)