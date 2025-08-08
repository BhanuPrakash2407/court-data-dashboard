from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from .models import CaseQueryLog
import os
import traceback
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, NoSuchElementException
import time

class DelhiHighCourtScraperService:
    def __init__(self, case_type, case_number, filing_year):
        self.case_type = case_type
        self.case_number = case_number
        self.filing_year = filing_year
        self.driver = None

    def setup_driver(self):
        options = Options()
        # Comment out headless for debugging
        # options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)

    def fill_form(self, wait):
        # Fill Case Type
        try:
            case_type_field = wait.until(EC.visibility_of_element_located((By.NAME, "case_type")))
            self.driver.execute_script("arguments[0].value = arguments[1];", case_type_field, self.case_type)
            self.driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", case_type_field)
            print(f"Set case type: {self.case_type}")
        except TimeoutException as e:
            print(f"Timeout waiting for case type field: {str(e)}")
            print(f"Page source: {self.driver.page_source[:1000]}")
            raise Exception("Failed to locate case type field. Page structure may have changed.")

        # Fill Case Number
        try:
            case_number_field = wait.until(EC.visibility_of_element_located((By.NAME, "case_number")))
            case_number_field.clear()
            case_number_field.send_keys(self.case_number)
            print(f"Set case number: {self.case_number}")
        except TimeoutException as e:
            print(f"Timeout waiting for case number field: {str(e)}")
            raise Exception("Failed to locate case number field.")

        # Fill Year
        try:
            year_field = wait.until(EC.visibility_of_element_located((By.NAME, "case_year")))
            self.driver.execute_script("arguments[0].value = arguments[1];", year_field, self.filing_year)
            self.driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", year_field)
            print(f"Set filing year: {self.filing_year}")
        except TimeoutException as e:
            print(f"Timeout waiting for year field: {str(e)}")
            raise Exception("Failed to locate year field.")

    def handle_captcha(self, wait):
        max_captcha_retries = 2
        captcha_success = False
        for attempt in range(max_captcha_retries):
            try:
                captcha_code = wait.until(EC.presence_of_element_located((By.ID, "captcha-code"))).text
                print(f"CAPTCHA code (attempt {attempt + 1}): {captcha_code}")
                captcha_input = self.driver.find_element(By.NAME, "captchaInput")
                captcha_input.clear()
                captcha_input.send_keys(captcha_code)
                # Set hidden randomid field
                try:
                    random_id_field = self.driver.find_element(By.ID, "randomid")
                    self.driver.execute_script("arguments[0].value = arguments[1];", random_id_field, captcha_code)
                    print("Set randomid field")
                except:
                    print("No randomid field found")
                captcha_success = True
                break
            except TimeoutException as e:
                print(f"Timeout waiting for CAPTCHA code on attempt {attempt + 1}: {str(e)}")
                if attempt < max_captcha_retries - 1:
                    try:
                        self.driver.find_element(By.ID, "reload-captcha").click()
                        time.sleep(2)
                        continue
                    except:
                        print("Failed to refresh CAPTCHA")
                raise Exception("Failed to locate CAPTCHA code.")
        
        if not captcha_success:
            raise Exception("Failed to process CAPTCHA after retries.")

    def submit_form(self, wait):
        max_submit_retries = 3
        for attempt in range(max_submit_retries):
            try:
                submit_button = wait.until(EC.element_to_be_clickable((By.ID, "search")))
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", submit_button)
                time.sleep(1)  # Wait for animations/overlays
                submit_button.click()
                print(f"Form submitted on attempt {attempt + 1}")
                break
            except ElementClickInterceptedException as e:
                print(f"Click intercepted on attempt {attempt + 1}: {str(e)}")
                if attempt < max_submit_retries - 1:
                    time.sleep(2)
                    continue
                print("Attempting JavaScript click as fallback")
                self.driver.execute_script("arguments[0].click();", submit_button)
            except TimeoutException as e:
                print(f"Timeout waiting for submit button on attempt {attempt + 1}: {str(e)}")
                raise Exception("Failed to locate or click submit button.")

    def wait_for_results(self, wait):
        try:
            wait.until(EC.presence_of_element_located((By.XPATH, "//table[@id='caseTable']")))
            print("Table detected, waiting for data to load")
            long_wait = WebDriverWait(self.driver, 60)  # Increased to 60 seconds
            max_table_retries = 3
            for attempt in range(max_table_retries):
                try:
                    long_wait.until(EC.presence_of_element_located((By.XPATH, "//table[@id='caseTable']//tbody/tr[not(contains(@class, 'dt-empty'))]")))
                    print("Table populated with data")
                    time.sleep(2)  # Additional delay to ensure table is fully rendered
                    return True  # Data found
                except TimeoutException:
                    print(f"Table still empty on attempt {attempt + 1}")
                    table_html = self.driver.find_element(By.ID, "caseTable").get_attribute("outerHTML")
                    print(f"Table HTML: {table_html[:1000]}")
                    if attempt < max_table_retries - 1:
                        time.sleep(10)  # Wait longer for AJAX
                        continue
                    print(f"Input details: case_type={self.case_type}, case_number={self.case_number}, filing_year={self.filing_year}")
                    error_messages = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Invalid') or contains(text(), 'No record') or contains(text(), 'Error')]")
                    error_text = [elem.text for elem in error_messages] if error_messages else ["No error messages found"]
                    print(f"Page error messages: {error_text}")
                    return False  # No data found
        except TimeoutException as e:
            print(f"Timeout waiting for table to appear: {str(e)}")
            raise Exception("Failed to load results table.")

    def extract_data(self):
        try:
            # Log full table HTML for debugging
            table_html = self.driver.find_element(By.ID, "caseTable").get_attribute("outerHTML")
            print(f"Table HTML: {table_html[:1000]}")
            # Log tbody content specifically
            tbody = self.driver.find_element(By.XPATH, "//table[@id='caseTable']//tbody").get_attribute("outerHTML")
            print(f"Table Body HTML: {tbody[:1000]}")
            
            # Check number of rows and columns
            rows = self.driver.find_elements(By.XPATH, "//table[@id='caseTable']//tbody/tr")
            print(f"Number of rows in tbody: {len(rows)}")
            if not rows:
                raise Exception("No rows found in table body.")
            
            # Check columns in the first row
            first_row_columns = rows[0].find_elements(By.TAG_NAME, "td")
            print(f"Number of columns in first row: {len(first_row_columns)}")
            if len(first_row_columns) < 3:
                raise Exception(f"Expected at least 3 columns, found {len(first_row_columns)}.")
            
            # Extract data with dynamic column indices
            parties = first_row_columns[2].text  # Assuming 'Pet' (Petitioner) is the third column
            listing_date = first_row_columns[3].text if len(first_row_columns) > 3 else "Not Available"
            
            # Extract filing date from any row containing 'Filing Date'
            filing_date_elements = self.driver.find_elements(By.XPATH, "//td[contains(text(),'Filing Date')]/following-sibling::td")
            filing_date = filing_date_elements[0].text if filing_date_elements else "Not Available"
        except NoSuchElementException as e:
            print(f"Error extracting table data: {str(e)}")
            return {"message": "No data is available"}
        except Exception as e:
            print(f"Error extracting table data: {str(e)}")
            return {"message": "No data is available"}
        
        # Extract PDF link
        try:
            pdf_element = self.driver.find_element(By.PARTIAL_LINK_TEXT, "Download")
            pdf_link = pdf_element.get_attribute("href")
        except:
            pdf_link = "Not Available"
        
        return {
            "parties": parties,
            "filing_date": filing_date,
            "next_hearing_date": listing_date,
            "order_pdf": pdf_link
        }

    def save_log(self):
        raw_html = self.driver.page_source
        CaseQueryLog.objects.create(
            case_type=self.case_type,
            case_number=self.case_number,
            filing_year=self.filing_year,
            raw_html=raw_html
        )

    def scrape(self):
        try:
            self.setup_driver()
            self.driver.get("https://delhihighcourt.nic.in/app/get-case-type-status")
            print(f"Current URL: {self.driver.current_url}")
            wait = WebDriverWait(self.driver, 30)

            # Check for iframes
            try:
                wait.until(EC.frame_to_be_available_and_switch_to_it((By.TAG_NAME, "iframe")))
                print("Switched to iframe")
            except TimeoutException:
                print("No iframe found, continuing in main content")

            self.fill_form(wait)
            self.handle_captcha(wait)
            self.submit_form(wait)
            data_found = self.wait_for_results(wait)
            
            self.save_log()
            
            if not data_found:
                return {"message": "No data is available"}
                
            result = self.extract_data()
            return result

        except Exception as e:
            print(f"Error in DelhiHighCourtScraperService: {traceback.format_exc()}")
            if self.driver:
                with open("error_page.html", "w", encoding="utf-8") as f:
                    f.write(self.driver.page_source)
                print("Page source saved to error_page.html")
            raise e
        finally:
            if self.driver:
                self.driver.quit()