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
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.keys import Keys

from random import choice as randchoice, randint, randrange
from time import sleep
from colorama import Fore

from modules import Usernames
from modules import Webhooks

import requests
import os
import yaml

# Load configuation file
with open('config.yml', 'r') as f:
    Config = yaml.safe_load(f)

# Unpack Config
Core = Config["Core"]
Browser = Config["Browser"]
Capture = Config["Capture"]
Accounts = Config["Accounts"]
Webhook = Config["Webhook"]

Webhooks.LoadConfig(Webhook)

# Website buttons
Accept_All = '//button[contains(@class, "btn-cta-lg") and contains(@class, "cookie-btn")]'
Cookie_Banner = '//*[@id="cookie-banner-wrapper"]'
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

BrowserClient = None

def MakePassword():
    Random_Password = Accounts["Random_Password"]
    Fixed_Password = Accounts["Fixed_Password"]

    if Random_Password:
        return Usernames.RandomString(10, 20)
    else:
        return Fixed_Password

def MakeUsername():
    Use_Username_Base = Accounts["Use_Username_Base"]
    Username_Base = Accounts["Username_Base"]
    Username = None

    while True:
        # Generate username string
        if Use_Username_Base:
            Username = Usernames.MakeRandomUsername(Username_Base)
        else:
            Username = Usernames.MakeWordedUsername()

        # Check if username is approved by Roblox
        if Usernames.UsernameAllowed(Username):
            break

    return Username

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

    ClickButton(driver, Xpath)
    ClickButton(driver, Option_Xpath)

def SetBirthDay(driver):
    SelectDropdown(driver, Month_Dropdown, 1, 12)
    SelectDropdown(driver, Day_Dropdown, 1, 20)
    SelectDropdown(driver, Year_Dropdown, 24, 37)

def CreateOptions():
    Headless = Browser["Headless"]
    Use_Proxy = Browser["Use_Proxy"]
    Proxy_Address = Browser["Proxy"]
    Use_Nopecha = Capture["Use_Nopecha"]

    # Add browser options
    options = Options()

    if Headless:
        options.add_argument("--headless")
    
    if Use_Proxy:
        options.add_argument(f"--proxy-server={Proxy_Address}")

    # Install nopecha extention
    Extention_Path = "extra/ext.crx"
    if Use_Nopecha:
        with open(Extention_Path, 'wb+') as f:
            request = requests.get('https://nopecha.com/f/ext.crx')
            f.write(request.content)

        options.add_extension(Extention_Path)

    # Addional options
    options.add_argument("log-level=3")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_argument('--incognito')
    options.add_argument('--no-sandbox') 
    options.add_argument('--disable-dev-shm-usage')

def CreateDriver():    
    Options = CreateOptions()
    NOPECHA_KEY = Capture["NOPECHA_KEY"]
    Use_Nopecha = Capture["Use_Nopecha"]

    Parameters = {
        "source": "Object.defineProperty(navigator, 'webdriver', { get: () => undefined })"
    }

    # Create driver instance
    driver = webdriver.Edge(options = Options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", Parameters)

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

def ColoredPrint(Text="", Color=Fore.WHITE, End="\n"):
    print(f"{Color}{Text}{Fore.RESET}", end=End)

def ColoredPrints(Seperator, Lines):
    for Line in Lines:
        ColoredPrint(*Line, End=Seperator)
    print()

def Error(Text, End=None):
    ColoredPrint(f"Error: {Fore.LIGHTCYAN_EX}{Text}", Fore.LIGHTRED_EX, End)

def Info(Text, End=None):
    ColoredPrint(Text, Fore.LIGHTYELLOW_EX, End)
    
def Success(Text, End=None):
    ColoredPrint(Text, Fore.GREEN, End)

def PrintUserAndPass(Username, Password, Gender):
    ColoredPrints(" ", [
        ("Username:", Fore.WHITE),
        (Username, Fore.GREEN),
        ("Password:", Fore.WHITE),
        (Password, Fore.RED),
        ("Gender:", Fore.WHITE),
        (Gender, Fore.MAGENTA)
    ])

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
    Wait_Minutes = Core["Request_Limit_Wait_Minutes"]
    Seconds = Wait_Minutes / 60

    Error("Rate Limit!")
    Timeout(Seconds)

def LogDetails(Username, Password, Cookie):
    Accounts_File = Accounts["Accounts_File"]
    Cookies_File = Accounts["Cookies_File"]
    Use_Webhooks = Webhooks["Use_Webhooks"]

    # Send webhook request
    if Use_Webhooks:
        Webhooks.SendWebhook({
            "Username": "Bozo",
            "Password": "Bozo zozo"
        })

    # Write password and username for the generated account
    with open(Accounts_File, "a+") as f:
        f.write(f"{Username} : {Password}\n")

    # Write cookie for the generated account
    with open(Cookies_File, "a+") as f:
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

    # Get capture method name
    Method = driver.find_element(By.XPATH, Method_Title).text
    Info(f"Capture method: {Method}")

    # Solve methods
    if "Pick any square" in Method:
        #Square = driver.find_element(By.CSS_SELECTOR, f'[aria-label="Image {randint(1,6)} of 6."]')
        #Square.click()
        ClickButton(driver, f"//*[@aria-label='Image {randint(1,6)} of 6.']")
    else:
        Error("Unknown capture method!")
        return True
    
    #key-frame-image
    
    driver.switch_to.default_content()
    sleep(5)
    #WebDriverWait(driver, 60).until_not(EC.presence_of_element_located((By.ID, Arkose_iFrame)))

    return False

def CaptureCheck(driver):
    Manual = Capture["Allow_Manual_Completion"]
    Minutes = Capture["Capture_Timeout_Minutes"]
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
    if Manual:
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
    Gender_Name = "None"

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
    MacOS = Core["MacOS"]
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

def FollowUser(driver, UserId):
    Profile_Url = f"https://www.roblox.com/users/{UserId}/profile"
    driver.get(Profile_Url)

    # Accept cookies prompt (Again??!)
    if HasCookiePrompt(driver):
        ClickButton(driver, Accept_All, True)

    # Follow user
    ClickButton(driver, Profile_Options)
    sleep(1)
    ClickButton(driver, Follow_User)

    # Check for capture prompts
    sleep(5)
    CaptureCheck(driver)

def ProblemCheck(driver):
    Use_Nopecha = Capture["Use_Nopecha"]

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

def HasCookiePrompt(driver):
    Has_Cookies_Prompt = Core["Has_Cookies_Prompt"]
    
    if Has_Cookies_Prompt: 
        return True
    
    # Some people don't edit the configuation and complain it doesn't work
    # This is needed to prevent my inbox spam of complaints sadly
    try:
        Banner = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, Cookie_Banner))
        )
        Child = Banner.find_element(By.XPATH, "./*")

        if Child:
            return True
    except:
        return False

def GenerateAccount():
    # Initilase web driver
    driver = BrowserClient
    ResetDriver(driver)

    # Goto signup page
    driver.get("https://www.roblox.com")

    # Accept all cookes (without your consent muhahaha... or not)
    if HasCookiePrompt(driver):
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

    #FollowUser(driver, 0)

    return Username, Password, Cookie

def Banner():
    FlushConsole()
    Info("Depso's Roblox account generator")

def Generation():
    global BrowserClient
    Create_Count = Core["Accounts_To_Create"]

    # Creation loop
    for i in range(1, Create_Count):
        try:
            BrowserClient = CheckDriver(BrowserClient)
            GenerateAccount()
        except WebDriverException:
            Info("Window closed! Now exiting...")
            break
        except Exception as e:
            BrowserClient = None
            Error(e)

    Success("Job finished!")

if __name__ == "__main__":
    Banner()
    Generation()

    print("Press enter to exit...")
    input()
    exit(1)