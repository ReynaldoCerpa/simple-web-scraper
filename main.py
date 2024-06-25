from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

def scrape_google_reviews(url, num_reviews=10):
    # Initialize the WebDriver
    driver = webdriver.Chrome()  # Ensure chromedriver is in your PATH or provide the path to the executable
    driver.get(url)

    # Give some time for the page to load
    time.sleep(2)

    # Collect review details
    reviews = []

    while len(reviews) < num_reviews:
        review_containers = driver.find_elements(By.CLASS_NAME, 'gws-localreviews__google-review')

        for container in review_containers:
            try:
                user_element = container.find_element(By.CLASS_NAME, 'TSUbDb')
                comment_element = container.find_element(By.CLASS_NAME, 'f5axBf')

                # Scroll the element into view
                driver.execute_script("arguments[0].scrollIntoView(true);", container)
                time.sleep(1)  # Wait for the scrolling to complete

                user = user_element.text
                comment = comment_element.text

                reviews.append({'user': user, 'comment': comment})

                if len(reviews) >= num_reviews:
                    break
            except Exception as e:
                print(f"Error extracting review: {e}")

        # Scroll down to load more reviews
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
        time.sleep(2)  # Adjust sleep time as necessary

    # Close the WebDriver
    driver.quit()

    return reviews

# Example usage
url = 'https://www.google.com/search?q=CANNERIA+cerveceria&sca_esv=cf2d8ca50076abe9&sca_upv=1&ei=dNR6Ztn2EJHFkPIP0P6GkAk&ved=0ahUKEwjZgK3i-_aGAxWRIkQIHVC_AZIQ4dUDCBA&uact=5&oq=CANNERIA+cerveceria&gs_lp=Egxnd3Mtd2l6LXNlcnAiE0NBTk5FUklBIGNlcnZlY2VyaWEyEBAuGIAEGMcBGA0YjgUYrwEyCBAAGBYYChgeMggQABiABBiiBDIIEAAYgAQYogQyCBAAGIAEGKIEMggQABiABBiiBDIIEAAYgAQYogQyHxAuGIAEGMcBGA0YjgUYrwEYlwUY3AQY3gQY4ATYAQFIwSVQ3gZYwiNwAXgAkAEAmAHJAaABsA-qAQYwLjExLjG4AQPIAQD4AQH4AQKYAgygApsSqAIAwgIOEC4YgAQYxwEYjgUYrwHCAgcQABiABBgKwgIHEC4YgAQYCsICExAuGIAEGMcBGJgFGJkFGAoYrwHCAg0QLhiABBjHARgKGK8BwgIFEAAYgATCAh0QLhiABBjHARiOBRivARiXBRjcBBjeBBjgBNgBAcICBhAuGAoYHsICCBAuGAUYChgewgIIEAAYBRgKGB7CAgQQABgewgIGEAAYBRgewgICECaYAwa6BgYIARABGBSSBwUwLjkuM6AHimg&sclient=gws-wiz-serp#lrd=0x80d892770ca23585:0x2a93fd7bf8fbe615,1,,,,'  # Replace with the actual URL of the reviews
reviews = scrape_google_reviews(url, num_reviews=5)
for review in reviews:
    print(f"User: {review['user']}, Comment: {review['comment']}\n\n")
