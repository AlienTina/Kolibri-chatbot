from playwright.sync_api import Playwright, sync_playwright, expect
import curses
import sys
import time
import datetime

 
import speech_recognition as sr
import pyttsx3

# Initialize the recognizer
r = sr.Recognizer()
 
# Function to convert text to
# speech
def SpeakText(command):
     
    # Initialize the engine
    engine = pyttsx3.init()
    voice = engine.getProperty('voices')
    engine.setProperty('voice', voice[1].id)
    engine.say(command)
    engine.runAndWait()
     

def run(stdscr):
    if len(sys.argv) > 1:
        chara_id = sys.argv[1]
    else:
        chara_id = "e02BniVFfEPog7-Q9SkzrrshVYOnHWaZgrPIn6ftTjs"
    browser = playwright.firefox.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    page.goto('https://beta.character.ai/chat?char='+chara_id)
    page.get_by_role("button", name="Accept").click()
    
    
    for index, name in enumerate(sr.Microphone.list_microphone_names()):
        stdscr.addstr(f'{index}, {name}' + '\n')
    stdscr.addstr('Please enter device number of your microphone: ')
    stdscr.refresh()
    curses.echo()
    device = int(stdscr.getstr().decode())
    stdscr.clear()
    stdscr.refresh()

    while True:
        stdscr.refresh()
        stdscr.addstr("> ")
        stdscr.refresh()
        #curses.echo()
        now = datetime.datetime.now()
        time_str = "[{:%H:%M}]".format(now)
        message = ""
        gotAudio = False
        while not gotAudio:
            with sr.Microphone(device_index=device) as source2:
                
                # wait for a second to let the recognizer
                # adjust the energy threshold based on
                # the surrounding noise level
                r.adjust_for_ambient_noise(source2, duration=0.2)

                #listens for the user's input
                audio2 = r.listen(source2)

                # Using google to recognize audio
                try:
                    MyText = r.recognize_google(audio2)
                    MyText = MyText.lower()
                    gotAudio = True
                except:
                    gotAudio = False
                    stdscr.addstr('\n Sorry, didnt quite get that. \n> ')
                    stdscr.refresh()
                    continue

                stdscr.addstr(MyText + '\n')
                stdscr.refresh()
                #SpeakText(MyText)
                message = MyText
            
        #message = stdscr.getstr().decode()
        page.get_by_placeholder("Type a message").fill(message)
        page.get_by_placeholder("Type a message").press("Enter")
        chara = page.query_selector('div.chattitle.p-0.pe-1.m-0')
        chara_name = chara.inner_text()
        page.wait_for_selector('.swiper-button-next').is_visible()
        div = page.query_selector('div.msg.char-msg')
        output_text = div.inner_text()
        stdscr.clear()
        stdscr.refresh()
        stdscr.addstr('> ' + message + '\n')
        stdscr.addstr(time_str+ chara_name + ' ✉\n' + output_text + '\n \n')
        stdscr.refresh()
        SpeakText(output_text)
        #if stdscr.getch() == 27:
        #    break

    context.close()
    browser.close()

if __name__ == '__main__':
    with sync_playwright() as playwright:
        curses.wrapper(run)