# https://www.g7smy.co.uk/2013/08/recording-sound-on-the-raspberry-pi/
# https://iotbytes.wordpress.com/connect-configure-and-test-usb-microphone-and-speaker-with-raspberry-pi/

import random
import time
import speech_recognition as sr
import RPi.GPIO as GPIO


BLUE_LED = 17
RED_LED = 27
YELLOW_LED = 22


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
    print('Tell command\n')
    response = recognize_speech_from_mic(recognizer, microphone)
    while response["error"]:
        print("ERROR: {}\n".format(response["error"]),
              "Pelease tell your command again.\n")
        response = recognize_speech_from_mic(recognizer, microphone)
    return response["transcription"]


def execute_instruction(instruction):
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(RED_LED,GPIO.OUT)
    switcher={
        'włącz':lambda:GPIO.output(RED_LED,GPIO.HIGH),
        'wyłącz':lambda:GPIO.output(RED_LED,GPIO.LOW)
        }
    func=switcher.get(instruction,lambda :'Invalid')
    return func()
#     motor = GPIO.PWM(23, 50)
#     motor.start(7.5)
#     match instruction:
#         case 'Włącz 1 led':
#             GPIO.setup(RED_LED,GPIO.OUT)
#             GPIO.output(RED_LED,GPIO.HIGH)
#             time.sleep(1)
#             GPIO.output(RED_LED,GPIO.LOW)
#             GPIO.setup(RED_LED,GPIO.IN)
#         case 'Turn on second led':
#             GPIO.output(9, GPIO.HIGH)
#         case 'Turn off first led':
#             GPIO.output(8, GPIO.LOW)
#         case 'Turn off second led':
#             GPIO.output(9, GPIO.LOW)
#         case 'Turn motor towards 0 degree':
#             motor.ChangeDutyCycle(2.5)
#         case 'Turn motor towards 90 degree':
#             motor.ChangeDutyCycle(7.5)
#         case 'Turn motor towards 180 degree':
#             motor.ChangeDutyCycle(12.5)
#         case 'Turn on':
#             print("Which one?")
#             match ask_until_success():
#                 case 'First':
#                     GPIO.output(8, GPIO.HIGH)
#                 case 'Second':
#                     GPIO.output(9, GPIO.HIGH)
#         case 'Turn off':
#             print("Which one?")
#             match ask_until_success():
#                 case 'First':
#                     GPIO.output(8, GPIO.LOW)
#                 case 'Second':
#                     GPIO.output(9, GPIO.LOW)
#         case _:
#             print('Unknown instruction.\n')
#     motor.stop()


if __name__ == "__main__":
    API = ["włacz x led", "wyłącz x led", "zamigaj x ledem", "zamigaj x ledem x razy",
           "obróć silnik o x stopni", "exit"]

    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    start_msg = (
        "Jestem RasspberryPi, co mogę zrobić dla cb:\n"
        "{api}\n".format(api=', '.join(API))
    )
    print(start_msg)
    time.sleep(3)

    while True:
        instruction = ask_until_success(recognizer, microphone)
        print("Powiedziałeś: {}".format(instruction))
        execute_instruction(instruction)

        if instruction == 'exit':
            GPIO.cleanup()
            print("Bye bye!")
            break
