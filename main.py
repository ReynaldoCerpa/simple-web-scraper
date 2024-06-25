from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

def scrape_google_reviews(url):
    # Initialize the WebDriver
    driver = webdriver.Chrome()  # Ensure chromedriver is in your PATH or provide the path to the executable
    driver.get(url)

    time.sleep(1)
    # z5jxId
    review_count_element = driver.find_element(By.CLASS_NAME, 'z5jxId')
    num_reviews = int(review_count_element.text.split(' ')[0])

    # Give some time for the page to load
    # time.sleep(2000)

    # Collect review details
    reviews = []

    while len(reviews) < num_reviews:
        review_containers = driver.find_elements(By.CLASS_NAME, 'gws-localreviews__google-review')

        for i in range(len(review_containers)):
            try:
                container = review_containers[i]
                user_element = container.find_element(By.CLASS_NAME, 'TSUbDb')

                try:
                    comment_element = container.find_element(By.CLASS_NAME, 'f5axBf')
                except:
                    comment_element = container.find_element(By.CLASS_NAME, 'Jtu6Td')

                # Scroll the element into view
                driver.execute_script("arguments[0].scrollIntoView(true);", container)
                time.sleep(.5)  # Wait for the scrolling to complete

                user = user_element.text
                comment = comment_element.text

                print(f'{user}: {comment}')

                reviews.append({'user': user, 'comment': comment})

                if len(reviews) >= num_reviews:
                    break
            except Exception as e:
                print(f"Error extracting review: {e}")

        # Scroll down to load more reviews
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
        time.sleep(1)  # Adjust sleep time as necessary

    # Close the WebDriver
    driver.quit()

    return reviews

# Example usage
url = 'https://www.google.com/search?q=cafe+vainilla&sca_esv=cf2d8ca50076abe9&sca_upv=1&sxsrf=ADLYWIIk-JvPOj3AinS-gpclkrMa-6xjww%3A1719329825652&ei=IeR6ZvXDJ6zIkPIP-pioyAw&ved=0ahUKEwi12InciveGAxUsJEQIHXoMCskQ4dUDCA8&uact=5&oq=cafe+vainilla&gs_lp=Egxnd3Mtd2l6LXNlcnAiDWNhZmUgdmFpbmlsbGEyBRAAGIAEMgUQABiABDIFEAAYgAQyBRAAGIAEMgUQABiABDIFEAAYgAQyBxAAGIAEGAoyBxAAGIAEGAoyBxAAGIAEGAoyBxAAGIAEGApIixdQ9AhY-xFwA3gAkAEAmAGIAaABoQuqAQQwLjEzuAEDyAEA-AEBmAIQoALsC8ICExAuGIAEGLADGMcBGA0YjgUYrwHCAgsQABiwAxgIGAoYHsICCxAAGIAEGLADGKIEwgIKECMYgAQYJxiKBcICBBAjGCfCAgsQABiABBiRAhiKBcICCxAuGIAEGJECGIoFwgILEC4YgAQY0QMYxwHCAg4QLhiABBiRAhjUAhiKBcICERAuGIAEGJECGNEDGMcBGIoFwgILEAAYgAQYkgMYigXCAg0QABiABBhDGMkDGIoFwgILEC4YgAQYxwEYrwHCAggQABiABBjJA8ICDRAuGIAEGMcBGAoYrwGYAwDiAwUSATEgQIgGAZAGB5IHBDMuMTOgB7h2&sclient=gws-wiz-serp#lrd=0x80d88fc9ecbe05e9:0x55c3e664040f1fb7,1,,,,'
reviews = scrape_google_reviews(url)
for review in reviews:
    print(f"User: {review['user']}, Comment: {review['comment']}\n\n")
