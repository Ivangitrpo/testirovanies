#!/usr/bin/env python3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import unittest
import time

class OpenBMCAuthTests(unittest.TestCase):
    def setUp(self):
        # Настройки OpenBMC
        self.bmc_url = "https://127.0.0.1:2443"  # Update if necessary
        self.username = "root"
        self.password = "0penBmc"
        self.wrong_password = "wrongpass"

        # Настройка WebDriver
        options = webdriver.ChromeOptions()
        options.add_argument('--ignore-certificate-errors')
        # options.add_argument('--headless')  # Disabled for debugging
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 20)  # Increased timeout

    def tearDown(self):
        self.driver.quit()

    def login(self, username, password):
        """Функция для авторизации"""
        try:
            self.driver.get(self.bmc_url)
            print(f"Navigated to {self.bmc_url}, Current URL: {self.driver.current_url}")
            print(f"Page title: {self.driver.title}")
            # Wait for the username field instead of the form
            self.wait.until(EC.presence_of_element_located((By.ID, "username")))
            print("Username field found")

            # Input credentials
            username_field = self.driver.find_element(By.ID, "username")
            username_field.clear()
            username_field.send_keys(username)

            password_field = self.driver.find_element(By.ID, "password")
            password_field.clear()
            password_field.send_keys(password)

            # Click login button
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()
            print("Login button clicked")
        except Exception as e:
            print(f"Ошибка при авторизации: {str(e)}")
            print(f"Page source:\n{self.driver.page_source}")
            self.driver.save_screenshot("error_screenshot.png")
            raise

    def test_successful_login(self):
        """Тест успешной авторизации"""
        try:
            self.login(self.username, self.password)
            # Проверяем, что мы на странице Dashboard
            self.wait.until(EC.presence_of_element_located((By.XPATH, "//h1[contains(text(), 'Overview')]")))
            print("✅ Успешная авторизация: PASSED")
        except Exception as e:
            print(f"❌ Успешная авторизация: FAILED - {str(e)}")
            raise

    def test_invalid_credentials(self):
        """Тест неверных учетных данных"""
        try:
            self.login(self.username, self.wrong_password)
            # Проверяем сообщение об ошибке
            error_msg = self.wait.until(EC.presence_of_element_located(
                (By.XPATH, "//div[contains(text(), 'Invalid')]")))
            self.assertIn("Invalid", error_msg.text)
            print("✅ Неверные учетные данные: PASSED")
        except Exception as e:
            print(f"❌ Неверные учетные данные: FAILED - {str(e)}")
            raise

    def test_account_lockout(self):
        """Тест блокировки учетной записи"""
        try:
            for _ in range(5):  # 5 неудачных попыток
                try:
                    self.login(self.username, self.wrong_password)
                    time.sleep(2)
                except:
                    continue

            # Проверяем сообщение о блокировке
            lockout_msg = self.wait.until(EC.presence_of_element_located(
                (By.XPATH, "//div[contains(text(), 'lock') or contains(text(), 'Lock')]")))
            self.assertTrue("lock" in lockout_msg.text.lower())
            print("✅ Блокировка учетной записи: PASSED")
        except Exception as e:
            print(f"❌ Блокировка учетной записи: FAILED - {str(e)}")
            raise

if __name__ == "__main__":
    unittest.main(verbosity=2)
