import pyotp
import time
from kiteconnect import KiteConnect
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urlparse, parse_qs

cred = {
    "USER_ID": "",
    "PASSWORD": "",
    "API_KEY": "",
    "API_SECRET": "",
    "TOTP": "",
}

driver = None  # Initialize driver as None
try:
    login_url = f"https://kite.trade/connect/login?api_key={cred['API_KEY']}&v=3"

    totp_secret = cred["TOTP"]

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    driver.get(login_url)

    time.sleep(3)

    userid = driver.find_element(By.ID, "userid")
    userid.send_keys(cred["USER_ID"])

    password = driver.find_element(
        By.ID, "password"
    )  # Fixed variable name to avoid confusion
    password.send_keys(cred["PASSWORD"])

    login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
    login_button.click()

    time.sleep(3)

    totp = pyotp.TOTP(totp_secret).now()

    print("Generated TOTP:", totp)

    totp_input = driver.find_element(
        By.ID, "userid"
    )  # Verify if this is the correct ID for TOTP input
    totp_input.send_keys(totp)

    time.sleep(3)

    current_url = driver.current_url

    parsed_url = urlparse(current_url)
    query_params = parse_qs(parsed_url.query)
    request_token = query_params.get("request_token", [None])[0]

    if request_token:
        print(f"Request Token: {request_token}")
    else:
        print("Request Token not found in the URL.")
        driver.quit()
        exit()

    kite = KiteConnect(api_key=cred["API_KEY"])

    session_data = kite.generate_session(
        request_token=request_token, api_secret=cred["API_SECRET"]
    )

    with open("access_token.txt", "w") as file:
        file.write(session_data["access_token"])

    kite.set_access_token(session_data["access_token"])

    print("Access Token:", session_data["access_token"])
    print("Login successful!")
finally:
    if driver is not None:  # Only quit if driver was initialized
        driver.quit()
