from selenium import webdriver
from selenium.webdriver.common.by import By

import csv
import time

def scrape_google_reviews(url):
    # Initialize the WebDriver
    driver = webdriver.Chrome()  # Ensure chromedriver is in your PATH or provide the path to the executable
    driver.get(url)

    time.sleep(5)
    # z5jxId

    business_name = driver.find_element(By.CLASS_NAME, 'Lhccdd')
    # Lhccdd
    review_count_element = driver.find_element(By.CLASS_NAME, 'z5jxId')
    num_reviews = int(review_count_element.text.split(' ')[0])
    time.sleep(1)

    # Collect review details
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

                # Scroll the element into view
                driver.execute_script("arguments[0].scrollIntoView(true);", container)
                time.sleep(.3)  # Wait for the scrolling to complete

                user = user_element.text
                comment = 'Sin comentarios' if not comment_element.text else comment_element.text

                reviews.append({'user': user, 'comment': comment})

                if len(reviews) >= num_reviews:
                    break
            except Exception as e:
                print(f"Error extracting review: {e}")

        # Scroll down to load more reviews
        #driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
        OFFSET = len(review_containers)
        time.sleep(.2)  # Adjust sleep time as necessary

    # Close the WebDriver
    driver.quit()

    with open(f'{business_name.text}', 'w') as output:
        writer = csv.writer(output)
        for item in reviews:
            writer.writerow([item['user'], item['comment']])

    return reviews

# Example usage
fixed_url = 'https://www.google.com/search?q=cafe+vainilla&oq=cafe+vainilla&gs_lcrp=EgZjaHJvbWUqBggAEEUYOzIGCAAQRRg7MgYIARAuGEDSAQgxNTY3ajBqMagCALACAA&sourceid=chrome&ie=UTF-8#lrd=0x80d88fc9ecbe05e9:0x55c3e664040f1fb7,1,,,,'
url = input('Enter url: ')
reviews = scrape_google_reviews(url)
# for review in reviews:
#     print(f"User: {review['user']}, Comment: {review['comment']}")
