#    .--.
#    |   :
#    |   | .-. .,-. .--. .-.
#    |   ;(.-' |   )`--.(   )
#    '--'  `--'|`-' `--' `-'
#              |
#              '
# Created by depso and by the help of the lord

# --- GUI and Threading Imports ---
import tkinter as tk
from tkinter import scrolledtext
import threading
import sys
# ---------------------------------

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.keys import Keys

from random import choice as randchoice, randint, randrange
from time import sleep
from colorama import Fore, init

from modules import Usernames
from modules import Webhooks

import requests
import os
import yaml

# Initialize colorama
init()

# --- Main Application Class with GUI ---
class AccountGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Roblox Account Generator")
        self.root.geometry("700x500")
        self.root.configure(bg='black')

        self.is_running = False
        self.generator_thread = None
        self.BrowserClient = None

        # --- Load Configuration ---
        with open('config.yml', 'r') as f:
            self.Config = yaml.safe_load(f)
        self.Core = self.Config["Core"]
        self.Browser = self.Config["Browser"]
        self.Capture = self.Config["Capture"]
        self.Accounts = self.Config["Accounts"]
        self.Webhook = self.Config["Webhook"]
        Webhooks.LoadConfig(self.Webhook)
        # ---------------------------

        # --- GUI Widgets ---
        self.log_area = scrolledtext.ScrolledText(root, state='disabled', bg='black', fg='white', font=("Consolas", 10))
        self.log_area.pack(pady=10, padx=10, expand=True, fill='both')

        button_frame = tk.Frame(root, bg='black')
        button_frame.pack(pady=10, fill='x')

        self.start_button = tk.Button(button_frame, text="Start Generator", command=self.start_generator, bg='green', fg='white', width=20)
        self.start_button.pack(side='left', padx=(20, 10), expand=True)

        self.stop_button = tk.Button(button_frame, text="Stop Generator", command=self.stop_generator, bg='red', fg='white', width=20, state='disabled')
        self.stop_button.pack(side='right', padx=(10, 20), expand=True)
        # -------------------

        # Redirect stdout to the log area
        sys.stdout = self.RedirectText(self)

    class RedirectText:
        def __init__(self, app_instance):
            self.app_instance = app_instance

        def write(self, string):
            self.app_instance.log_area.config(state='normal')
            self.app_instance.log_area.insert(tk.END, string)
            self.app_instance.log_area.see(tk.END)
            self.app_instance.log_area.config(state='disabled')

        def flush(self):
            pass

    def start_generator(self):
        self.is_running = True
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.generator_thread = threading.Thread(target=self.Generation, daemon=True)
        self.generator_thread.start()

    def stop_generator(self):
        print(f"{Fore.RED}--- STOP SIGNAL RECEIVED --- Will stop after the current attempt.{Fore.RESET}")
        self.is_running = False
        self.stop_button.config(state='disabled')
        # The start button will be re-enabled when the thread fully stops.

    # --- All generator functions are now methods of the class ---

    def MakePassword(self):
        Random_Password = self.Accounts["Random_Password"]
        Fixed_Password = self.Accounts["Fixed_Password"]
        return Usernames.RandomString(10, 20) if Random_Password else Fixed_Password

    def MakeUsername(self):
        Use_Username_Base = self.Accounts["Use_Username_Base"]
        Username_Base = self.Accounts["Username_Base"]
        while True:
            Username = Usernames.MakeRandomUsername(Username_Base) if Use_Username_Base else Usernames.MakeWordedUsername()
            if Usernames.UsernameAllowed(Username):
                return Username

    def ResetDriver(self, driver):
        driver.delete_all_cookies()

    def ClickButton(self, driver, Xpath, Move=False):
        try:
            Button = WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.XPATH, Xpath)))
        except:
            Button = driver.find_element(By.XPATH, Xpath)
        if Move:
            ActionChains(driver).move_to_element(Button).click().perform()
        else:
            Button.click()
        return Button

    def SelectDropdown(self, driver, Xpath, Min, Max):
        Index = randint(Min, Max)
        Option_Xpath = f"{Xpath}/option[{Index}]"
        self.ClickButton(driver, Xpath)
        self.ClickButton(driver, Option_Xpath)

    def SetBirthDay(self, driver):
        self.SelectDropdown(driver, '//*[@id="MonthDropdown"]', 1, 12)
        self.SelectDropdown(driver, '//*[@id="DayDropdown"]', 1, 20)
        self.SelectDropdown(driver, '//*[@id="YearDropdown"]', 24, 37)

    def CreateOptions(self):
        options = Options()
        if self.Browser["Headless"]: options.add_argument("--headless")
        if self.Browser["Use_Proxy"]: options.add_argument(f"--proxy-server={self.Browser['Proxy']}")
        if self.Capture["Use_Nopecha"]:
            Extention_Path = "extra/ext.crx"
            with open(Extention_Path, 'wb+') as f: f.write(requests.get('https://nopecha.com/f/ext.crx').content)
            options.add_extension(Extention_Path)
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_argument(f"--lang={self.Browser['Language']}")
        options.add_argument("log-level=3")
        options.add_argument('--incognito')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        return options

    def CreateDriver(self):
        options = self.CreateOptions()
        # MODIFICATION: Use Brave Browser on macOS
        options.binary_location = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
        driver = webdriver.Chrome(options=options)
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": "Object.defineProperty(navigator, 'webdriver', { get: () => undefined })"})
        if self.Capture["Use_Nopecha"]: self.SetNopechaKey(driver, self.Capture["NOPECHA_KEY"])
        return driver
    
    def SetNopechaKey(self, driver, Key):
        driver.get(f"https://nopecha.com/setup#{Key}")
        sleep(1)

    def LogDetails(self, Username, Password, Cookie):
        if self.Webhook["Use_Webhooks"]: Webhooks.SendWebhook({"Username": Username, "Password": Password})
        with open(self.Core["Accounts_File"], "a") as f: f.write(f"{Username} : {Password}\n")
        with open(self.Core["Cookies_File"], "a") as f: f.write(f"{Cookie}\n")

    def EnterValue(self, driver, Xpath, Text, Clear=False):
        TextBox = self.ClickButton(driver, Xpath)
        if Clear: self.ClearValue(TextBox)
        TextBox.send_keys(Text)

    def ClearValue(self, Element):
        Control = Keys.COMMAND if self.Core["MacOS"] else Keys.CONTROL
        Element.send_keys(Control + "a")
        Element.send_keys(Keys.BACKSPACE)

    def Username_Birthday_Loop(self, driver):
        while self.is_running:
            Username = self.MakeUsername()
            self.EnterValue(driver, '//*[@id="signup-username"]', Username, True)
            sleep(2)
            Error_Message = driver.find_element(By.XPATH, "//p[@id='signup-usernameInputValidation']").text
            if "birthday" in Error_Message.lower():
                self.SetBirthDay(driver)
                continue
            if len(Error_Message) < 3: return Username
        return None

    def CheckTermsOfUse(self, driver):
        try:
            Terms = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH, '//*[@id="signup-checkbox"]')))
            if not Terms.is_selected(): self.ClickButton(driver, '//*[@id="signup-checkbox"]', Move=True)
            print(f"{Fore.YELLOW}Clicked Terms of Use checkbox.{Fore.RESET}")
        except TimeoutException: pass

    def WaitForCreation(self, driver, Timeout):
        try:
            WebDriverWait(driver, Timeout).until(EC.url_contains("www.roblox.com/home"))
            return True
        except TimeoutException:
            return False

    def ProblemCheck(self, driver):
        try: # CAPTCHA Check
            if self.Capture["Allow_Manual_Completion"]:
                print(f"{Fore.YELLOW}Waiting for manual CAPTCHA completion...{Fore.RESET}")
                if self.WaitForCreation(driver, self.Capture["Capture_Timeout_Minutes"] * 60):
                    return True
        except Exception: pass
        try: # Error check
            if "An unknown error occurred" in driver.find_element(By.XPATH, "//div[@id='GeneralErrorText']").text:
                print(f"{Fore.RED}Rate limit hit! Waiting...{Fore.RESET}")
                sleep(self.Core["Request_Limit_Wait_Minutes"] * 60)
                return False
        except Exception: pass
        return True

    def GenerateAccount(self):
        # Initilase web driver
        self.ResetDriver(self.BrowserClient)
        self.BrowserClient.get("https://www.roblox.com")
        if self.Core["Has_Cookies_Prompt"]: self.ClickButton(self.BrowserClient, '//button[contains(@class, "btn-cta-lg") and contains(@class, "cookie-btn")]', True)
        
        self.SetBirthDay(self.BrowserClient)
        Username = self.Username_Birthday_Loop(self.BrowserClient)
        if not Username: return # Stopped by user

        Password = self.MakePassword()
        self.EnterValue(self.BrowserClient, '//*[@id="signup-password"]', Password, True)
        
        Gender = "Male" if randint(1, 2) == 1 else "Female"
        self.ClickButton(self.BrowserClient, f"//button[@id='{Gender}Button']")
        
        self.CheckTermsOfUse(self.BrowserClient)
        self.ClickButton(self.BrowserClient, '//*[@id="signup-button"]')
        
        Created = self.WaitForCreation(self.BrowserClient, 8)
        if not Created:
            print(f"{Fore.YELLOW}Creation timeout.. Checking for problems.{Fore.RESET}")
            if not self.ProblemCheck(self.BrowserClient):
                print(f"{Fore.RED}Account creation failed! Capture/rate-limit error!{Fore.RESET}")
                self.ResetDriver(self.BrowserClient)
                return
            if not self.WaitForCreation(self.BrowserClient, 60):
                print(f"{Fore.RED}Account creation failed! Exceeded timeout.{Fore.RESET}")
                return

        print(f"{Fore.GREEN}Success! {Fore.WHITE}User: {Fore.CYAN}{Username}{Fore.WHITE}, Pass: {Fore.CYAN}{Password}{Fore.WHITE}, Gender: {Fore.CYAN}{Gender}{Fore.RESET}")
        Cookie = self.BrowserClient.get_cookie(".ROBLOSECURITY")["value"]
        self.LogDetails(Username, Password, Cookie)

    def Generation(self):
        Create_Count = self.Core["Accounts_To_Create"]
        print(f"{Fore.CYAN}--- Depso's Roblox Account Generator ---{Fore.RESET}")

        for i in range(1, Create_Count + 1):
            if not self.is_running: break
            print(f"\n{Fore.MAGENTA}--- Generating Account #{i} of {Create_Count} ---{Fore.RESET}")
            try:
                if not self.BrowserClient: self.BrowserClient = self.CreateDriver()
                self.GenerateAccount()
            except WebDriverException:
                print(f"{Fore.RED}Browser window was closed! Stopping generator...{Fore.RESET}")
                break
            except Exception as e:
                print(f"{Fore.RED}An unexpected error occurred: {e}{Fore.RESET}")
                if self.BrowserClient:
                    self.BrowserClient.quit()
                    self.BrowserClient = None
                sleep(5) # Wait before retrying
        
        # --- Cleanup after loop ---
        if self.is_running:
             print(f"\n{Fore.GREEN}--- Job Finished! ---{Fore.RESET}")
        else:
             print(f"\n{Fore.RED}--- Generator Stopped ---{Fore.RESET}")

        self.is_running = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        if self.BrowserClient:
            self.BrowserClient.quit()
            self.BrowserClient = None

if __name__ == "__main__":
    root = tk.Tk()
    app = AccountGeneratorApp(root)
    root.mainloop()