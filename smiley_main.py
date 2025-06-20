import eel
import Notify.SeLink
import Chat_YTube.main_agent

def start():
    # Initialize the eel app with the directory where your web files are located
    eel.init("web")  


    # Start the eel application, and it will open the browser automatically
    eel.start("index.html", mode="chrome", host='localhost', block=True)

start()