from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
import time
import config

# Initialize the Chrome WebDriver
driver = webdriver.Chrome()
wait = WebDriverWait(driver, 25)

def parse_due_date(date_str):
    """Parse different date formats from the library system"""
    try:
        # Try common date formats
        formats = ["%d/%m/%Y", "%m/%d/%Y", "%Y-%m-%d", "%d-%b-%Y"]
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        return None
    except Exception:
        return None

try:
    # Step 1: Navigate to English login page
    driver.get("https://www.hkpl.gov.hk/en/login.html")
    print("Step 1: Login page loaded")

    # Step 2: Enter credentials and submit
    username_field = wait.until(EC.presence_of_element_located((By.NAME, "USER")))
    password_field = wait.until(EC.presence_of_element_located((By.NAME, "PASSWORD")))
    
    username_field.send_keys(config.LIB_USERNAME)
    password_field.send_keys(config.LIB_PASSWORD)
    password_field.submit()
    print("Step 2: Credentials submitted")

    # Step 3: Wait for index page and confirm login
    wait.until(EC.url_contains("index.html"))
    print("Step 3: Login successful - redirected to index page")
    
    # Step 4: Handle popup and overlay
    try:
        # Remove overlay
        overlay = driver.find_element(By.ID, "isd-overlay")
        driver.execute_script("arguments[0].remove();", overlay)
        print("Step 4: Removed overlay with JavaScript")
    except:
        print("Step 4: No overlay found")

    # Step 5: Get the current window handle (original tab)
    original_window = driver.current_window_handle
    print(f"Original window handle: {original_window}")
    
    # Step 6: Click the "Go" button which opens a new tab
    go_link = wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, "a.ac_logout_btn")
    ))
    go_link.click()
    print("Step 5: Clicked Go button - new tab should open")
    
    # Step 7: Wait for the new tab to open and switch to it
    WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))
    
    # Loop through until we find a new window handle
    for window_handle in driver.window_handles:
        if window_handle != original_window:
            driver.switch_to.window(window_handle)
            print(f"Step 6: Switched to new window: {window_handle}")
            break
    
    # Step 8: Wait for the account page to load in the new tab
    wait.until(EC.url_contains("PatronAccountPage"))
    print(f"Step 7: Account page loaded: {driver.current_url}")
    
    # Step 9: Extract borrowed books and identify near-due items
    print("Step 8: Extracting borrowed books...")
    
    # Wait for the checkout table to load
    table = wait.until(EC.presence_of_element_located((By.ID, "checkout")))
    print("Found checkout table")
    
    rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
    today = datetime.now()
    near_due_books = []
    
    if rows:
        print("\nYour Borrowed Books:")
        print("=" * 50)
        for row_index, row in enumerate(rows):
            cols = row.find_elements(By.TAG_NAME, "td")
            if len(cols) >= 5:
                # Get book title
                title = cols[1].text.strip()
                
                # Get due date
                due_date_str = cols[4].text.strip()
                due_date = parse_due_date(due_date_str)
                
                if due_date:
                    # Calculate days until due
                    days_until_due = (due_date - today).days
                    
                    print(f"Title: {title}")
                    print(f"Due Date: {due_date_str} ({days_until_due} days remaining)")
                    
                    # Check if book is near due (less than 5 days)
                    if 0 <= days_until_due < 5:
                        print("⚠️ Book is near due - will select for renewal")
                        near_due_books.append(row_index)
                else:
                    print(f"Title: {title}")
                    print(f"Due Date: {due_date_str} (format not recognized)")
                
                print("-" * 50)
        
        print(f"Total books: {len(rows)}")
        print(f"Books near due: {len(near_due_books)}")
    else:
        print("No borrowed books found")
    
    # Step 10: Select near-due books for renewal
    if near_due_books:
        print("\nSelecting near-due books for renewal...")
        for row_index in near_due_books:
            row = rows[row_index]
            cols = row.find_elements(By.TAG_NAME, "td")
            if cols:
                # Find the checkbox in the first column
                checkbox = cols[0].find_element(By.TAG_NAME, "input")
                if checkbox.get_attribute("type") == "checkbox":
                    if not checkbox.is_selected():
                        checkbox.click()
                        print(f"Selected: {cols[1].text.strip()}")
        
        # Step 11: Click the renew button
        try:
            renew_button = wait.until(EC.element_to_be_clickable((By.ID, "button.renew")))
            renew_button.click()
            print("Clicked renew button")
            
            # Wait for renewal confirmation
            # after renew, then logout and send email to notify (to be done)
            
        except Exception as e:
            print(f"Error during renewal: {str(e)}")
    else:
        print("No near-due books to renew")

except Exception as e:
    print(f"\n❌ An error occurred: {str(e)}")
    print(f"Current URL: {driver.current_url}")
    print(f"Page title: {driver.title}")
    
    # Save debugging information
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    with open(f"error_page_{timestamp}.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    driver.save_screenshot(f"error_screenshot_{timestamp}.png")
    print(f"Saved error_page_{timestamp}.html and error_screenshot_{timestamp}.png")

finally:
    driver.quit()
    print("Browser closed")
