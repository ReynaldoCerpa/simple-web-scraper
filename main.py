from selenium import webdriver
from selenium.webdriver.common.by import By

import csv
import time
import re

def scrape_google_reviews(url):
    driver = webdriver.Chrome()
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
    with open(f'output/{filename}', 'w') as output:
        writer = csv.writer(output)
        for item in reviews:
            writer.writerow([item['user'], item['comment']])

    return reviews

fixed_url = 'https://www.google.com/search?q=cafe+vainilla&oq=cafe+vainilla&gs_lcrp=EgZjaHJvbWUqBggAEEUYOzIGCAAQRRg7MgYIARAuGEDSAQgxNTY3ajBqMagCALACAA&sourceid=chrome&ie=UTF-8#lrd=0x80d88fc9ecbe05e9:0x55c3e664040f1fb7,1,,,,'
url = input('Enter url: ')
reviews = scrape_google_reviews(url)
print(f'Finished succesfully, {len(reviews)} results')
# for review in reviews:
#     print(f"User: {review['user']}, Comment: {review['comment']}")
