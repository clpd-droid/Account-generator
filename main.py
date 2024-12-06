#    .--.                    
#    |   :                   
#    |   | .-. .,-. .--. .-. 
#    |   ;(.-' |   )`--.(   )
#    '--'  `--'|`-' `--' `-' 
#              |             
#              '             
# Created by depso and by the help of the lord

from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys

from random import choice as randchoice, randint, randrange
from time import sleep
from colorama import Fore

import requests
import string
import os

###### Config
To_Create_Count = 5
Request_Limit_Wait_Minutes = 50

# Browser config
MacOS = False # (REQUIRED)
Headless = False
Use_Proxy = False
Proxy = "http://1.1.1.1/"

# Fun-Capture config
NOPECHA_KEY = "-------"
Use_Nopecha = False
Allow_Manual_Completion = True
Capture_Timeout_Minutes = 4

# Account details
Random_Password = True
Fixed_Password = "depsoisgreat"

Use_Username_Base = False
Username_Base = "ilovedepso_"

# Website buttons
Accept_All = "//button[contains(text(),'Accept All')]"
Signup_Button = '//*[@id="signup-button"]'
General_Error = "//div[@id='GeneralErrorText']"

Username_Box = '//*[@id="signup-username"]'
Password_Box = '//*[@id="signup-password"]'
Details_Error = "//p[@id='signup-usernameInputValidation']"

Male_Gender = "//button[@id='MaleButton']"
Female_Gender = "//button[@id='FemaleButton']"

Month_Dropdown = '//*[@id="MonthDropdown"]'
Day_Dropdown = '//*[@id="DayDropdown"]'
Year_Dropdown = '//*[@id="YearDropdown"]'

Arkose_iFrame = "arkose-iframe"
Enforcement_Frame = '[data-e2e="enforcement-frame"]'
Game_Core_Frame = "game-core-frame"
Verify_Button = '//*[@data-theme="home.verifyButton"]'
Method_Title = '//*[contains(@class, "sc-1io4bok-0") and contains(@class, "text")]'

Profile_Options = "//button[@id='popover-link']"
Follow_User = "//a[contains(text(),'Follow') and @role='menuitem']"

# Data lists
Adjectives = open('extra/adjectives.txt',"r").readlines()
Nouns = open('extra/nouns.txt',"r").readlines()

Browser = None

def RandomString(Min, Max):
    Characters = string.ascii_letters + string.digits
    return ''.join(randchoice(Characters) for _ in range(randint(Min, Max)))

def MakePassword():
    if Random_Password:
        return RandomString(10, 20)
    else:
        return Fixed_Password

def MakeUsername():
    if Use_Username_Base:
        # Generate an ending to stop conflicting usernames
        Max = 20 - len(Username_Base)
        Ending = RandomString(5, Max)

        return f"{Username_Base}{Ending}"

    # Compile a some-what realistic username
    Adjective = randchoice(Adjectives)
    Noun = randchoice(Nouns)
    Number = ""

    # Capitalization
    if randint(1,2) == 2:
        Adjective = Adjective.capitalize()
    if randint(1,2) == 2:
        Noun = Noun.capitalize()
    if randint(1,2) == 2:
        Number = str(randrange(68))

    # Word order
    Type = randint(1,3)
    if Type == 1:
        Username = Adjective + Number + Noun 
    if Type == 2:
        Username = Adjective + Noun + Number
    if Type == 3:
        Username = Noun + Adjective + Number
    if Type == 4:
        Username = Adjective + "_" + Noun + Number

    return str(Username).replace("\n","").replace("\r","")

def FlushConsole():
    Is_Windows = os.name == 'nt'
    os.system('cls' if Is_Windows else 'clear')

def ResetDriver(driver):
    driver.delete_all_cookies()
    #driver.quit()
 
def ClickButton(driver, Xpath, Move=False):
    try:
        Button = WebDriverWait(driver, 40).until(
            EC.presence_of_element_located((By.XPATH, Xpath))
        )
    except:
        Button = driver.find_element(By.XPATH, Xpath)

    if Move:
        Actions = ActionChains(driver)
        Actions.move_to_element(Button)
        Actions.click().perform()
        Actions.reset_actions()
    else:
        Button.click()

    return Button

def SelectDropdown(driver, Xpath, Min, Max):
    Index = randint(Min, Max)
    Ending = "/option[{0}]"
    Option_Xpath = f"{Xpath}{Ending.format(Index)}"

    Dropdown = driver.find_element("xpath", Xpath)
    Dropdown.click()

    ClickButton(driver, Option_Xpath)

def SetBirthDay(driver):
    SelectDropdown(driver, Month_Dropdown, 1, 12)
    SelectDropdown(driver, Day_Dropdown, 1, 20)
    SelectDropdown(driver, Year_Dropdown, 24, 37)

def CreateDriver():    
    parameters = {
        "source": "Object.defineProperty(navigator, 'webdriver', { get: () => undefined })"
    }

    # Add browser options
    options = Options()

    if Headless:
        options.add_argument("--headless")
    
    if Use_Proxy:
        options.add_argument(f"--proxy-server={Proxy}")

    # Install nopecha extention
    Extention_Path = "extra/ext.crx"
    if Use_Nopecha:
        with open(Extention_Path, 'wb+') as f:
            request = requests.get('https://nopecha.com/f/ext.crx')
            f.write(request.content)

        options.add_extension(Extention_Path)

    # Addional options
    #options.add_argument("user-agent=")
    options.add_argument("log-level=3")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_argument('--incognito')
    options.add_argument('--no-sandbox') 
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Edge(options=options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", parameters)

    # Set Nopecha key
    if Use_Nopecha:
        SetNopechaKey(driver, NOPECHA_KEY)

    return driver

def CheckDriver(driver):
    if not driver:
        driver = CreateDriver()
    
    return driver

def SetNopechaKey(driver, Key):
    driver.get(f"https://nopecha.com/setup#{Key}")
    sleep(1)
    driver.get(f"https://nopecha.com/setup#{Key}")

def ColoredPrint(Color, Text, End="\n"):
    print(f"{Color}{Text}{Fore.RESET}", end=End)

def Error(Text, End=None):
    ColoredPrint(Fore.LIGHTRED_EX, f"Error: {Fore.LIGHTCYAN_EX}{Text}", End)

def Info(Text, End=None):
    ColoredPrint(Fore.LIGHTYELLOW_EX, Text, End)
    
def Success(Text, End=None):
    ColoredPrint(Fore.GREEN, Text, End)

def PrintUserAndPass(Username, Password, Gender):
    print(f"Username: {Fore.GREEN}{Username}{Fore.RESET} Password: {Fore.RED}{Password}{Fore.RESET} Gender: {Fore.MAGENTA}{Gender}{Fore.RESET}")

def ConsoleExample():
    for i in range(1, 50):
        PrintUserAndPass(MakeUsername(), MakePassword(), "Male")

def Timeout(Seconds):
    Remaining = Seconds

    while Remaining > 0:
        Mins, Secs = divmod(Remaining, 60)

        Info(f"Time Remaining: {Mins:f}:{Secs:f}", end="\r")
        
        Remaining -= 1
        sleep(1)

def RequestLimitWait():
    Seconds = Request_Limit_Wait_Minutes / 60

    Error("Rate Limit!")
    Timeout(Seconds)

def LogDetails(Username, Password, Cookie):
    with open("accounts.txt", "a+") as f:
        f.write(f"{Username} : {Password}\n")

    with open("cookies.txt", "a+") as f:
        f.write(f"{Cookie}\n")

def SolveCapture(driver):
    # Select correct iframe
    Arkose = driver.find_element(By.ID, Arkose_iFrame)
    driver.switch_to.frame(Arkose)
    Enforcement = driver.find_element(By.CSS_SELECTOR, Enforcement_Frame)
    driver.switch_to.frame(Enforcement)
    Game_Core = driver.find_element(By.ID, Game_Core_Frame)
    driver.switch_to.frame(Game_Core)
    
    ClickButton(driver, Verify_Button)
    sleep(1)

    Method = driver.find_element(By.XPATH, Method_Title).text
    Info(f"Capture method: {Method}")

    # Solve methods
    if "Pick any square" in Method:
        Square = driver.find_element(By.CSS_SELECTOR, f'[aria-label="Image {randint(1,6)} of 6."]')
        Square.click()
    else:
        Error("Unknown capture method!")
        return True
    
    #key-frame-image
    
    driver.switch_to.default_content()
    sleep(5)
    #WebDriverWait(driver, 60).until_not(EC.presence_of_element_located((By.ID, Arkose_iFrame)))

    return False

def CaptureCheck(driver):
    Minutes = Capture_Timeout_Minutes
    Seconds = 60 * Minutes

    # Attempt automatic solve
    try:
        Failed = SolveCapture(driver)

        if not Failed:
            Info("Capture solved!")
            return True
    except Exception as e:
        #Error(e)
        pass

    # Prompt user to solve capture if enabled
    if Allow_Manual_Completion:
        Info(f"Waiting for manual capture competion! ({Minutes}) minutes maxium!")

        Completed = WaitForCreation(driver, Seconds)
        if Completed:
            return True

    # Capture solve failed
    Error("Program will now sleep")
    Timeout(Seconds)

    return False

def SelectGender(driver):
    Gender = randint(1,3)
    Gender_Name = "No gender"

    if Gender == 1: # Male
        ClickButton(driver, Male_Gender)
        Gender_Name = "Male"
    elif Gender == 2: # Female
        ClickButton(driver, Female_Gender)
        Gender_Name = "Female"

    return Gender_Name

def EnterValue(driver, Xpath, Text, Clear=False):
    TextBox = ClickButton(driver, Xpath)

    if Clear:
        ClearValue(TextBox)
    
    TextBox.send_keys(Text)

def ClearValue(Element):
    Control = Keys.CONTROL

    # COMMAND instead of CONTROL for Mac
    if MacOS:
        Control = Keys.COMMAND

    Element.send_keys(Control + "a") 
    Element.send_keys(Keys.BACKSPACE)

def EnterUsername(driver):
    Username = MakeUsername()

    EnterValue(driver, Username_Box, Username, True)

    return Username

def EnterPassword(driver):
    Password = MakePassword()

    EnterValue(driver, Password_Box, Password, True)

    return Password

def Username_Birthday_Loop(driver):
    while True:
        Username = EnterUsername(driver)

        sleep(2)
        Error_Message = driver.find_element(By.XPATH, Details_Error).text

        # Check birthday
        if "birthday" in Error_Message.lower():
            SetBirthDay(driver)
            continue
        
        # Error check
        if len(Error_Message) < 3:
            return Username
        
def WaitForUrl(driver, Timeout, Url):
    try:
        WebDriverWait(driver, Timeout).until(
            EC.url_contains(Url)
        )
        return True
    except TimeoutException:
        return False

def CheckForError(driver):
    try:
        Message = driver.find_element(By.XPATH, General_Error)
        if "An unknown error occurred" in Message.text:
            return True
    except:
        pass

    return False

def FollowDepso(driver):
    Profile_Url = "https://www.roblox.com/users/1223447/profile"
    driver.get(Profile_Url)

    #ClickButton(driver, Accept_All, True)

    ClickButton(driver, Profile_Options)
    sleep(1)
    ClickButton(driver, Follow_User)

    sleep(5)
    CaptureCheck(driver)

def ProblemCheck(driver):
    # Capture test
    if not Use_Nopecha:
        Capture_Success = CaptureCheck(driver)
        if not Capture_Success:
            return False
        
    # Apon request limit
    Has_Error = CheckForError(driver)
    if Has_Error:
        RequestLimitWait()
        return False
        
    return True

def WaitForCreation(driver, Timeout):
    Success_Url = "www.roblox.com/home"
    Created = WaitForUrl(driver, Timeout, Success_Url)

    return Created

def GenerateAccount():
    # Initilase web driver
    driver = Browser
    ResetDriver(driver)

    # Goto signup page
    driver.get("https://www.roblox.com")

    # Accept all cookes (without your consent muhahaha... or not)
    ClickButton(driver, Accept_All, True)
    
    # Set birthday
    SetBirthDay(driver)

    # Username and birthday entry
    Username = Username_Birthday_Loop(driver)

    # Password entry
    Password = EnterPassword(driver)

    # Select gender
    Gender = SelectGender(driver)

    # Request signup
    ClickButton(driver, Signup_Button)

    # Wait for successful creation
    Created = WaitForCreation(driver, 5)
    
    if not Created:
        Info("Creation timeout.. Checking for problems")

        Resolved = ProblemCheck(driver)

        if not Resolved:
            Error("Account creation failed! Capture/rate-limit error!")
            ResetDriver(driver)
            return
        
        Created = WaitForCreation(driver, 60)
        if not Created:
            Error("Account creation failed! Exceeded timeout")
            return

    # Success!
    PrintUserAndPass(Username, Password, Gender)

    # Append account creation details to file
    Cookie = driver.get_cookie(".ROBLOSECURITY")["value"]
    LogDetails(Username, Password, Cookie)

    #FollowDepso(driver)

    return Username, Password, Cookie

if __name__ == "__main__":
    FlushConsole()
    Info("Depso's Roblox account generator")

    #ConsoleExample()
    #exit(1)

    # Creation loop
    for i in range(1, To_Create_Count):
        try:
            Browser = CheckDriver(Browser)
            GenerateAccount()
        except Exception as e:
            Browser = None
            Error(e)

    Info("Job finished! Press enter to exit...")
    input()
    
    exit(1)
