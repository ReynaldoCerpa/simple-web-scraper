import asyncio
import csv
import re
from typing import List, Tuple, Dict

import langid
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException

class Config:
    OUTPUT_DIR = 'output'
    WAIT_TIMEOUT = 5  # seconds

class DriverManager:
    @staticmethod
    def initialize_driver() -> webdriver.Chrome:
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        return webdriver.Chrome(options=options)

class LanguageDetector:
    @staticmethod
    def detect(text: str) -> str:
        lang, _ = langid.classify(text)
        return 'español' if lang == 'es' else 'ingles' if lang == 'en' else 'español'

class ReviewScraper:
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, Config.WAIT_TIMEOUT)

    def get_info(self) -> Tuple[str, int]:
        name_element = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'Lhccdd')))
        raw_business_name = name_element.text.split('\n')[0]
        review_count_element = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'z5jxId')))
        sanitized_num_reviews = re.sub(r'\D', '', review_count_element.text.split(' ')[0])
        num_reviews = int(sanitized_num_reviews.replace(' ', ''))
        return raw_business_name, num_reviews

    async def extract_reviews(self, num_reviews: int) -> List[Dict]:
        reviews = []
        offset = 0

        while len(reviews) < num_reviews:
            review_containers = self.wait.until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 'gws-localreviews__google-review'))
            )
            if offset == len(review_containers):
                break

            for container in review_containers[offset:]:
                review = await self._extract_single_review(container)
                if review:
                    reviews.append(review)

            offset = len(review_containers)
            await self._scroll_reviews()

        return reviews

    async def _extract_single_review(self, container: WebElement) -> Dict:
        try:
            user_element = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'TSUbDb')))
            self._expand_review(container)
            comment_element = self._get_comment_element(container)

            self.driver.execute_script("arguments[0].scrollIntoView(true);", container)

            user = user_element.text
            comment = self._get_comment_text(comment_element)
            lang = LanguageDetector.detect(comment)
            date_published = container.find_element(By.CLASS_NAME, 'dehysf').text
            number_of_images = self._get_image_count(container)
            stars = self._get_star_rating(container)

            return {
                'user': user, 'comment': comment, 'date': date_published,
                'images': number_of_images, 'stars': stars, 'lang': lang
            }
        except (TimeoutException, StaleElementReferenceException) as e:
            print(f"Error extracting review: {e}")
            return None

    def _expand_review(self, container: WebElement) -> None:
        try:
            mas_button = container.find_element(By.CLASS_NAME, 'review-more-link')
            mas_button.click()
            self.wait.until(EC.staleness_of(mas_button))
        except:
            pass

    def _get_comment_element(self, container: WebElement) -> WebElement:
        try:
            return self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'f5axBf')))
        except TimeoutException:
            return self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'Jtu6Td')))

    @staticmethod
    def _get_comment_text(comment_element: WebElement) -> str:
        return 'Sin comentarios' if not comment_element.text or comment_element.text == 'Más' else comment_element.text

    def _get_image_count(self, container: WebElement) -> int:
        try:
            images_container = container.find_element(By.CLASS_NAME, 'EDblX ')
            return len(images_container.find_elements(By.TAG_NAME, 'a'))
        except:
            return 0

    def _get_star_rating(self, container: WebElement) -> str:
        number_of_stars = container.find_element(By.CLASS_NAME, 'z3HNkc')
        return number_of_stars.get_attribute('aria-label')

    async def _scroll_reviews(self) -> None:
        scrollable_div = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'review-dialog-list')))
        self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
        await asyncio.sleep(0.5)  # Short sleep to allow content to load after scrolling

class CSVWriter:
    @staticmethod
    def save_reviews_to_csv(raw_business_name: str, reviews: List[Dict]) -> None:
        sanitized_business_name = re.sub(r'[\\/*?:"<>|]', "_", raw_business_name)
        filename = f'{Config.OUTPUT_DIR}/{sanitized_business_name}.csv'
        with open(filename, 'w', encoding='utf-8', newline='') as output:
            writer = csv.DictWriter(output, fieldnames=['usuario', 'Comentario', 'Fecha', '# Imagenes', 'Calificacion', 'Idioma'])
            writer.writeheader()
            for item in reviews:
                writer.writerow({
                    'usuario': item['user'],
                    'Comentario': item['comment'],
                    'Fecha': item['date'],
                    '# Imagenes': item['images'],
                    'Calificacion': item['stars'],
                    'Idioma': item['lang']
                })

async def scrape_google_reviews(url: str) -> List[Dict]:
    driver = DriverManager.initialize_driver()
    driver.get(url)
    
    scraper = ReviewScraper(driver)
    raw_business_name, num_reviews = scraper.get_info()
    # TO-DO check why awaiting the following 'async' function was throwing error
    reviews = scraper.extract_reviews(num_reviews)

    driver.quit()
    CSVWriter.save_reviews_to_csv(raw_business_name, reviews)
    return reviews

async def main():
    url = input('Enter URL: ')
    reviews = await scrape_google_reviews(url)
    print(f'\nFinished successfully, scraped {len(reviews)} reviews')

if __name__ == '__main__':
    asyncio.run(main())