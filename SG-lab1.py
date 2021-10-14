# with sr.AudioFile('hello.wav') as source1:
# 	audio1 = r.record(source1)
# u = r.recognize_google(audio1)
# print(u)


import random
import time
import speech_recognition as sr
import RPi.GPIO as GPIO


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


def ask_untill_success(recognizer, microphone):
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
    GPIO.setup(7, GPIO.OUT)
    GPIO.setup(8, GPIO.OUT)
    GPIO.setup(9, GPIO.OUT)
    GPIO.setup(0, GPIO.OUT)
    GPIO.setup(2, GPIO.OUT)
    GPIO.setup(3, GPIO.OUT)
    GPIO.setup(23, GPIO.OUT)
    motor = GPIO.PWM(23, 50)
    motor.start(7.5)
    match instruction:
        case 'Turn on first led':
            GPIO.output(8, GPIO.HIGH)
        case 'Turn on second led':
            GPIO.output(9, GPIO.HIGH)
        case 'Turn off first led':
            GPIO.output(8, GPIO.LOW)
        case 'Turn off second led':
            GPIO.output(9, GPIO.LOW)
        case 'Turn motor towards 0 degree':
            motor.ChangeDutyCycle(2.5)
        case 'Turn motor towards 90 degree':
            motor.ChangeDutyCycle(7.5)
        case 'Turn motor towards 180 degree':
            motor.ChangeDutyCycle(12.5)
        case 'Turn on':
            print("Which one?")
            match ask_untill_success():
                case 'First':
                    GPIO.output(8, GPIO.HIGH)
                case 'Second':
                    GPIO.output(9, GPIO.HIGH)
        case 'Turn off':
            print("Which one?")
            match ask_untill_success():
                case 'First':
                    GPIO.output(8, GPIO.LOW)
                case 'Second':
                    GPIO.output(9, GPIO.LOW)
        case _:
            print('Unknown instruction.\n')
    motor.stop()


if __name__ == "__main__":
    API = ["włacz x led", "wyłącz x led", "zamigaj x ledem x razy"
           "obróć silnik o x stopni", "exit"]

    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    start_msg = (
        "Hi I'm RasspberryPi, what can I do for you:\n"
        "{api}\n".format(api=', '.join(API))
    )
    print(start_msg)
    time.sleep(3)

    while True:
        instruction = ask_untill_success(recognizer, microphone)
        print("You said: {}".format(instruction["transcription"]))
        execute_instruction(instruction)

        if instruction["transcription"] == 'exit':
            print("Bye bye!")
            break
