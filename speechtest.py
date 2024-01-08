import pyttsx3

def text_to_speech(text):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    
    # Set the voice using its ID (Zira in this case)
    engine.setProperty('voice', voices[0].id)

    # Other properties
    engine.setProperty('rate', 150)
    engine.setProperty('volume', 0.9)

    engine.say(text)
    engine.runAndWait()

if __name__ == "__main__":
    input_text = input("Enter the text to convert to speech: ")
    text_to_speech(input_text)
