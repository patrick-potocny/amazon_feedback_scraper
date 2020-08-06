from varname import nameof
import json
import csv
from config import (LINKS_PATH, BASE_URL, get_chrome_webdriver,
                    get_chrome_options)

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


class GetLinks:
    def __init__(self, file_path, base_url):
        self.file_path = file_path
        self.base_url = base_url

    def run(self):
        asins = self.get_asins_from_links_file(self.file_path)
        review_links = self.get_review_links(asins)
        print(review_links)
        return review_links

    def get_asins_from_links_file(self, file_path):
        asins = []
        with open(file_path) as links:
            links_list = csv.reader(links)
            print('Openning file....')
            print('Extracting links...')
            for row in links_list:
                link = row[0]
                asin = link[link.find('/dp/') + 4: link.find('/ref')]
                asins.append(asin)
        print(f'Extracted {len(asins)} products')
        return asins

    def get_review_links(self, asins):
        review_links = []
        for asin in asins:
            link = self.base_url + asin
            review_links.append(link)
        print(f'Made {len(review_links)} product review links')
        return review_links


class Scraping:
    def __init__(self, product_links):
        self.product_links = product_links
        options = get_chrome_options()
        self.driver = get_chrome_webdriver(options)

    def run(self):
        print('Opening links....')
        for product_link in self.product_links:
            print(f'Scraping data from: {product_link}')
            asin = product_link[product_link.find('reviews/') + 8: ]
            data = self.get_review_data(product_link)
            print("Making result file for currentproduct....")
            with open(f'results/{asin}.txt', 'w') as outfile:
                json.dump(data, outfile)
            print("File has been made...")
        self.driver.quit()
        print("SCRAPING FINISHED CHECK RESULTS FOLDER.")

    def get_review_data(self, product_link):
        data = {}
        self.driver.get(product_link)
        while True:
            print(self.driver.current_url)
            try:
                reviews_div = WebDriverWait(self.driver, 10).until(
                    EC.visibility_of_element_located((By.ID, "cm_cr-review_list")))
            except :
                print('MAIN DIV NOT FOUND')

            reviews = reviews_div.find_elements_by_css_selector('div[data-hook="review"]')
            if len(reviews) > 10:
                reviews.pop()
            print(f'Got {len(reviews)} reviews.')
            for review in reviews:
                review_id = review.get_attribute('id')
                print(f"Getting info from review with id: {review_id}")
                data[f'{review_id}'] = {}
                data[f'{review_id}']['By: '] = self.get_review_by(review)
                data[f'{review_id}']['Stars: '] = self.get_review_star_rating(review)
                data[f'{review_id}']['Title: '] = self.get_review_title(review)
                data[f'{review_id}']['Purchase: '] = self.get_review_verified_purchase(review)
                data[f'{review_id}']['Text: '] = self.get_review_text(review)
                data[f'{review_id}']['Images: '] = self.get_review_images(review)

            try:
                next_page_btn = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'li[class="a-last"]')))
                next_page_btn.click()
                print('Going to next page')
                time.sleep(5)

            except Exception as e:
                print(e)
                print('LAST PAGE REACHED')
                break

        return data

    def get_review_by(self, review):
        try:
            by = "User unknown"
            by = review.find_element_by_css_selector('span[class="a-profile-name"]').text
        except Exception as e:
            print(f"UNABLE TO GET ELEMENT {nameof(by)}")
            print(f"ERROR: {e}")
        return by

    def get_review_star_rating(self, review):
        try:
            star_rating = review.find_element_by_css_selector('i[data-hook="review-star-rating"]')
            star_rating = star_rating.get_attribute("textContent")
        except Exception as e:
            print(f"UNABLE TO GET ELEMENT {nameof(star_rating)}")
            print(f"ERROR: {e}")
        return star_rating

    def get_review_title(self, review):
        try:
            title = 'No title'
            title = review.find_element_by_css_selector('a[data-hook="review-title"]').text
        except Exception as e:
            print(f"UNABLE TO GET ELEMENT {nameof(title)}")
            print(f"ERROR: {e}")
        return title

    def get_review_verified_purchase(self, review):
        try:
            verified_purchase = review.find_element_by_css_selector('span[data-hook="avp-badge"]').text
        except:
            try:
                verified_purchase = review.find_element_by_css_selector('span[class="a-color-success a-text-bold"]').text
            except Exception as e :
                verified_purchase = 'Not verified'
                print("NOT VERIFIED")


        return verified_purchase

    def get_review_text(self, review):
        try:
            text = 'No text description'
            text = review.find_element_by_css_selector('span[data-hook="review-body"]').text
        except Exception as e:
            print(f"UNABLE TO GET ELEMENT {nameof(text)}")
            print(f"ERROR: {e}")
        return text

    def get_review_images(self, review):
        try:
            # images = 'No images found'
            images = review.find_elements_by_tag_name('img')
            if len(images) > 1:
                images.pop(0)
            else:
                images = 'No images found'
            images = [image.get_attribute("src") for image in images]
        except:
            images = 'No images found'
        return images


if __name__ == '__main__':
    links = GetLinks(LINKS_PATH, BASE_URL)
    product_links = links.run()
    scraping = Scraping(product_links)
    scraping.run()

