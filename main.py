from selenium import webdriver
from selenium.webdriver.common.by import By
import langid
import csv
import time
import re

def initialize_driver():
    """Initialize the Chrome WebDriver with options to disable log output."""
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(options=options)
    return driver

def get_info(driver):
    """Extract vendor name and number of reviews."""
    name_element = driver.find_element(By.CLASS_NAME, 'Lhccdd')
    raw_business_name = name_element.text.split('\n')[0]
    review_count_element = driver.find_element(By.CLASS_NAME, 'z5jxId')
    num_reviews = int(review_count_element.text.split(' ')[0])
    return raw_business_name, num_reviews

def detect_language_with_langid(line): 
    pred = langid.classify(line)
    if pred[0] == 'es':
        return 'español'
    if pred[0] == 'en':
        return 'ingles'
    else:
        return 'español'


def extract_reviews(driver, num_reviews):
    """Extract reviews from the Google Reviews page."""
    reviews = []
    offset = 0

    while len(reviews) < num_reviews:
        review_containers = driver.find_elements(By.CLASS_NAME, 'gws-localreviews__google-review')
        if offset == len(review_containers):
            break

        for i in range(offset, len(review_containers)):
            try:
                container = review_containers[i]
                user_element = container.find_element(By.CLASS_NAME, 'TSUbDb')
                try:
                    if container.find_element(By.CLASS_NAME, 'review-more-link'):
                        mas_button = container.find_element(By.CLASS_NAME, 'review-more-link')
                        mas_button.click()
                except:
                    pass

                try:
                    comment_element = container.find_element(By.CLASS_NAME, 'f5axBf')
                except:
                    comment_element = container.find_element(By.CLASS_NAME, 'Jtu6Td')

                driver.execute_script("arguments[0].scrollIntoView(true);", container)
                time.sleep(0.3)
                user = user_element.text
                comment = 'Sin comentarios' if not comment_element.text or comment_element.text == 'Más' else comment_element.text
                lang = detect_language_with_langid(comment)
                # date: dehysf lTi8oc
                date_published = container.find_element(By.CLASS_NAME, 'dehysf').text
                # images: DQBZx
                number_of_images = 0
                try:
                    images_container = container.find_element(By.CLASS_NAME, 'EDblX ')
                except:
                    pass
                else:
                    # number of images: s2gQvd
                    number_of_images = len(images_container.find_elements(By.TAG_NAME, 'a'))
                # stars: lTi8oc z3HNkc
                number_of_stars = container.find_element(By.CLASS_NAME, 'z3HNkc')
                stars = number_of_stars.get_attribute('aria-label')
                reviews.append({'user': user, 'comment': comment, 'date': date_published, 'images': number_of_images, 'stars': stars, 'lang': lang})
            except Exception as e:
                print(f"Error extracting review: {e}")

        offset = len(review_containers)
        time.sleep(.2)
    return reviews

def save_reviews_to_csv(raw_business_name, reviews):
    """Save extracted reviews to a CSV file."""
    sanitized_business_name = re.sub(r'[\\/*?:"<>|]', "_", raw_business_name)
    filename = f'output/{sanitized_business_name}.csv'
    with open(filename, 'w', encoding='utf-8') as output:
        writer = csv.writer(output)
        writer.writerow(['usuario', 'Comentario', 'Fecha', '# Imagenes', 'Calificacion', 'Idioma'])
        for item in reviews:
            writer.writerow([item['user'], item['comment'], item['date'], item['images'], item['stars'], item['lang']])

def scrape_google_reviews(url):
    """Main function to scrape Google Reviews."""
    driver = initialize_driver()
    driver.get(url)
    time.sleep(.5)

    raw_business_name, num_reviews = get_info(driver)
    reviews = extract_reviews(driver, num_reviews)

    driver.quit()
    save_reviews_to_csv(raw_business_name, reviews)
    return reviews

if __name__ == '__main__':
    #url = input('Enter URL: ')
    url = 'https://www.google.com/search?q=cafe+vainilla&oq=cafe+vainilla&gs_lcrp=EgZjaHJvbWUqBggAEEUYOzIGCAAQRRg7MgYIARBFGD0yBggCEC4YQNIBCDE1MjFqMGoxqAIAsAIA&sourceid=chrome&ie=UTF-8#lrd=0x80d88fc9ecbe05e9:0x55c3e664040f1fb7,1,,,,'
    reviews = scrape_google_reviews(url)
    print(f'\nFinished successfully, scraped {len(reviews)} reviews')
