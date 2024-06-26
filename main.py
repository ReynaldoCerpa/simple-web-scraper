from selenium import webdriver
from selenium.webdriver.common.by import By

import csv
import time
import re

def scrape_google_reviews(url):

    # Disable log output to the terminal on windows
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    driver = webdriver.Chrome(options=options)
    driver.get(url)

    time.sleep(1)

    name = driver.find_element(By.CLASS_NAME, 'Lhccdd')
    vendor_name = name.text.split('\n')[0]
    review_count_element = driver.find_element(By.CLASS_NAME, 'z5jxId')
    num_reviews = int(review_count_element.text.split(' ')[0])

    reviews = []
    OFFSET = 0

    while len(reviews) < num_reviews:
        review_containers = driver.find_elements(By.CLASS_NAME, 'gws-localreviews__google-review')

        if OFFSET == len(review_containers):
            break

        for i in range(OFFSET, len(review_containers)):
            try:
                container = review_containers[i]
                user_element = container.find_element(By.CLASS_NAME, 'TSUbDb')
                try:
                    comment_element = container.find_element(By.CLASS_NAME, 'f5axBf')
                except:
                    comment_element = container.find_element(By.CLASS_NAME, 'Jtu6Td')
                driver.execute_script("arguments[0].scrollIntoView(true);", container)
                time.sleep(.2)
                user = user_element.text
                comment = 'Sin comentarios' if not comment_element.text or comment_element.text == 'Más' else comment_element.text
                reviews.append({'user': user, 'comment': comment})
            except Exception as e:
                print(f"Error extracting review: {e}")

        OFFSET = len(review_containers)
        time.sleep(.2)

    driver.quit()
    sanitized_business_name = re.sub(r'[\\/*?:"<>|]', "_", vendor_name)
    filename = f'{sanitized_business_name}.csv'
    with open(f'output/{filename}', 'w', encoding='utf-8') as output:
        writer = csv.writer(output)
        for item in reviews:
            writer.writerow([item['user'], item['comment']])

    return reviews

url = input('Enter url: ')
reviews = scrape_google_reviews(url)
print(f'Finished succesfully, {len(reviews)} reviews')
# for review in reviews:
#     print(f"User: {review['user']}, Comment: {review['comment']}")
