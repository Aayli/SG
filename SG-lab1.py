# https://www.g7smy.co.uk/2013/08/recording-sound-on-the-raspberry-pi/
# https://iotbytes.wordpress.com/connect-configure-and-test-usb-microphone-and-speaker-with-raspberry-pi/

import random
import time
import speech_recognition as sr
import RPi.GPIO as GPIO


BLUE_LED = 17
RED_LED = 27
YELLOW_LED = 22
GREEN_LED = 21
SERVO_PIN = 12


def recognize_speech_from_mic(recognizer, microphone):
    """Transcribe speech from recorded from `microphone`.

    Returns a dictionary with three keys:
    "success": a boolean indicating whether or not the API request was
               successful
    "error":   `None` if no error occured, otherwise a string containing
               an error message if the API could not be reached or
               speech was unrecognizable
    "transcription": `None` if speech could not be transcribed,
               otherwise a string containing the transcribed text
    """
    if not isinstance(recognizer, sr.Recognizer):
        raise TypeError("`recognizer` must be `Recognizer` instance")

    if not isinstance(microphone, sr.Microphone):
        raise TypeError("`microphone` must be `Microphone` instance")

    # adjust the recognizer sensitivity to ambient noise and record audio from the microphone
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    response = {
        "success": True,
        "error": None,
        "transcription": None
    }

    try:
        response["transcription"] = recognizer.recognize_google(
            audio, language="pl-PL")
    except sr.RequestError:
        response["success"] = False
        response["error"] = "API unavailable"
    except sr.UnknownValueError:
        response["error"] = "Unable to recognize speech"

    return response


def ask_until_success(recognizer, microphone):
    print('Podaj komende\n')
    response = recognize_speech_from_mic(recognizer, microphone)
    while response["error"]:
        print("ERROR: {}\n".format(response["error"]),
              "Nie rozpoznano. Proszę powtórz komende\n")
        response = recognize_speech_from_mic(recognizer, microphone)
    return response["transcription"]

def GPIO_setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(RED_LED, GPIO.OUT)
    GPIO.setup(BLUE_LED, GPIO.OUT)
    GPIO.setup(YELLOW_LED, GPIO.OUT)
    GPIO.setup(GREEN_LED, GPIO.OUT)
    GPIO.setup(SERVO_PIN, GPIO.OUT)

def execute_instruction(instruction):
    instruction = instruction.lower()
    words = instruction.split()
    switcher={
        'włącz':lambda:switch_on_led(words[1]),
        'wyłącz':lambda:switch_off_led(words[1]),
        'zamigaj':lambda:blink(words[1],words[3]),
        'rozświetl':lambda:light_up()
        }
    func=switcher.get(words[0],lambda :'Invalid')
    return func()

def switch_on_led(color):
    switcher={
    'czerwoną':lambda:GPIO.output(RED_LED, GPIO.HIGH),
    'niebieską':lambda:GPIO.output(BLUE_LED, GPIO.HIGH),
    'żółtą':lambda:GPIO.output(YELLOW_LED, GPIO.HIGH),
    'zieloną':lambda:GPIO.output(GREEN_LED, GPIO.HIGH),
    }
    func=switcher.get(color,lambda :'Invalid')
    return func

def switch_off_led(color):
    switcher={
    'czerwony':lambda:GPIO.output(RED_LED, GPIO.LOW),
    'niebieski':lambda:GPIO.output(BLUE_LED, GPIO.LOW),
    'żółty':lambda:GPIO.output(YELLOW_LED, GPIO.LOW),
    'zieloną':lambda:GPIO.output(GREEN_LED, GPIO.LOW),
    }
    func=switcher.get(color,lambda :'Invalid')
    return func

def blink(color, number=1):
    for i in range(number):
        switch_on_led(color)
        time.sleep(0.5)
        switch_off_led(color)
        time.sleep(0.5)

def set_servo(degree):
    filling = degree/180*5+5
    # motor = GPIO.PWM(SERVO_PIN, 50)
    # motor.start(filling)
    # time.sleep(1)
    # motor.stop()
    print("Ustawiono wypełnienie na {:.2f}%".format(filling))

def light_up():
    led = GPIO.PWM(GREEN_LED, 50)
    led.start(0)
    for bright in range(100):
        led.ChangeDutyCycle(bright)
        time.sleep(0.02)
    led.stop()

def light_down():
    led = GPIO.PWM(GREEN_LED, 50)
    led.start(0)
    for bright in range(100,0,-1):
        led.ChangeDutyCycle(bright)
        time.sleep(0.02)
    led.stop()



if __name__ == "__main__":
    API = ["włacz x diodę", "wyłącz x diodę", "zamigaj x diodą", "zamigaj x diodą x razy",
           "obróć silnik o x stopni", "exit"]

    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    start_msg = (
        "Jestem RasspberryPi, co mogę zrobić dla cb:\n"
        "{api}\n".format(api=', '.join(API))
    )
    print(start_msg)
    time.sleep(1)
    GPIO_setup()

    while True:
        instruction = ask_until_success(recognizer, microphone)
        print("Powiedziałeś: {}".format(instruction))
        execute_instruction(instruction)

        if instruction == 'exit':
            GPIO.cleanup()
            print("Bye bye!")
            break
