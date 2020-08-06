from config import get_chrome_options, get_chrome_webdriver
from varname import nameof

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

options = get_chrome_options()
driver = get_chrome_webdriver(options)

driver.get('https://www.amazon.com/product-reviews/B010N06VA4')


while True:

    try:
        driver.implicitly_wait(2)
        next_page_btn = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'li[class="a-last"]')))
        # next_page_avalible = self.driver.find_element_by_css_selector('ul[class = "a-pagination"]')
        next_page_btn.click()
        driver.implicitly_wait(1)

    except Exception as e:
        print(e)
        print('FAILED LAST PAGE REACHED')
        break

