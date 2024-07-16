import pytest
import asyncio
from unittest.mock import Mock, patch
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException

# Import your classes here
from main import DriverManager, LanguageDetector, ReviewScraper, CSVWriter, Config, scrape_google_reviews

@pytest.fixture
def mock_driver():
    return Mock()

@pytest.fixture
def mock_wait():
    return Mock(spec=WebDriverWait)

@pytest.fixture
def review_scraper(mock_driver, mock_wait):
    scraper = ReviewScraper(mock_driver)
    scraper.wait = mock_wait
    return scraper

def test_driver_manager_initialize_driver():
    with patch('main.webdriver.Chrome') as mock_chrome:
        DriverManager.initialize_driver()
        mock_chrome.assert_called_once()

@pytest.mark.parametrize("text,expected", [
    ("This is English text", "ingles"),
    ("Este es texto en español", "español"),
    ("Ceci est du texte français", "español"),
])
def test_language_detector(text, expected):
    assert LanguageDetector.detect(text) == expected

def test_get_info(review_scraper, mock_wait):
    mock_name_element = Mock()
    mock_name_element.text = "Business Name\nOther Info"
    mock_review_count_element = Mock()
    mock_review_count_element.text = "100 reviews"

    mock_wait.until.side_effect = [mock_name_element, mock_review_count_element]

    name, num_reviews = review_scraper.get_info()

    assert name == "Business Name"
    assert num_reviews == 100

@pytest.mark.asyncio
async def test_extract_reviews(review_scraper, mock_wait):
    mock_containers = [Mock() for _ in range(3)]
    mock_wait.until.return_value = mock_containers

    with patch.object(review_scraper, '_extract_single_review', side_effect=[
        {'user': 'User1', 'comment': 'Comment1'},
        {'user': 'User2', 'comment': 'Comment2'},
        {'user': 'User3', 'comment': 'Comment3'},
    ]):
        reviews = await review_scraper.extract_reviews(3)

    assert len(reviews) == 3
    assert reviews[0]['user'] == 'User1'
    assert reviews[1]['comment'] == 'Comment2'

@pytest.mark.asyncio
async def test_extract_single_review(review_scraper, mock_wait):
    mock_container = Mock(spec=WebElement)
    mock_user_element = Mock()
    mock_user_element.text = "User Name"
    mock_comment_element = Mock()
    mock_comment_element.text = "Comment text"
    mock_date_element = Mock()
    mock_date_element.text = "2023-07-01"
    mock_stars_element = Mock()
    mock_stars_element.get_attribute.return_value = "5 stars"

    mock_wait.until.side_effect = [mock_user_element, mock_comment_element]
    mock_container.find_element.side_effect = [mock_date_element, mock_stars_element]

    with patch.object(review_scraper, '_expand_review'), \
         patch.object(review_scraper, '_get_image_count', return_value=0), \
         patch('main.LanguageDetector.detect', return_value='ingles'):
        review = await review_scraper._extract_single_review(mock_container)

    assert review == {
        'user': "User Name",
        'comment': "Comment text",
        'date': "2023-07-01",
        'images': 0,
        'stars': "5 stars",
        'lang': 'ingles'
    }

def test_expand_review(review_scraper):
    mock_container = Mock(spec=WebElement)
    mock_button = Mock()
    mock_container.find_element.return_value = mock_button

    with patch.object(review_scraper.wait, 'until') as mock_wait_until:
        review_scraper._expand_review(mock_container)

    mock_button.click.assert_called_once()
    mock_wait_until.assert_called_once()

def test_get_comment_element_success(review_scraper, mock_wait):
    mock_element = Mock()
    mock_wait.until.return_value = mock_element

    result = review_scraper._get_comment_element(Mock())

    assert result == mock_element

def test_get_comment_element_fallback(review_scraper, mock_wait):
    mock_element = Mock()
    mock_wait.until.side_effect = [TimeoutException, mock_element]

    result = review_scraper._get_comment_element(Mock())

    assert result == mock_element

@pytest.mark.parametrize("text,expected", [
    ("", "Sin comentarios"),
    ("Más", "Sin comentarios"),
    ("Actual comment", "Actual comment"),
])
def test_get_comment_text(text, expected):
    mock_element = Mock()
    mock_element.text = text
    assert ReviewScraper._get_comment_text(mock_element) == expected

def test_get_image_count(review_scraper):
    mock_container = Mock(spec=WebElement)
    mock_images_container = Mock()
    mock_container.find_element.return_value = mock_images_container
    mock_images_container.find_elements.return_value = [Mock(), Mock(), Mock()]

    assert review_scraper._get_image_count(mock_container) == 3

def test_save_reviews_to_csv():
    reviews = [
        {'user': 'User1', 'comment': 'Comment1', 'date': '2023-07-01', 'images': 0, 'stars': '5 stars', 'lang': 'ingles'},
        {'user': 'User2', 'comment': 'Comment2', 'date': '2023-07-02', 'images': 1, 'stars': '4 stars', 'lang': 'español'},
    ]

    with patch('main.open', create=True) as mock_open, \
         patch('main.csv.DictWriter') as mock_dict_writer:
        mock_file = mock_open.return_value.__enter__.return_value
        mock_writer = mock_dict_writer.return_value

        CSVWriter.save_reviews_to_csv("Test_Business", reviews)

        mock_open.assert_called_once_with(f'{Config.OUTPUT_DIR}/Test_Business.csv', 'w', encoding='utf-8', newline='')
        mock_writer.writeheader.assert_called_once()
        assert mock_writer.writerow.call_count == 2

@pytest.mark.asyncio
async def test_scrape_google_reviews():
    mock_driver = Mock()
    mock_scraper = Mock()
    mock_scraper.get_info.return_value = ("Test Business", 3)
    mock_scraper.extract_reviews.return_value = [{'user': f'User{i}'} for i in range(3)]

    with patch('main.DriverManager.initialize_driver', return_value=mock_driver), \
         patch('main.ReviewScraper', return_value=mock_scraper), \
         patch('main.CSVWriter.save_reviews_to_csv') as mock_save:
        reviews = await scrape_google_reviews("https://www.google.com/search?q=cafe+vainilla&oq=cafe&gs_lcrp=EgZjaHJvbWUqBggAEEUYOzIGCAAQRRg7MgYIARBFGDkyBggCEEUYPTIGCAMQRRg8MgYIBBBFGEEyBggFEC4YQNIBBzg1OWowajGoAgCwAgA&sourceid=chrome&ie=UTF-8#lrd=0x80d88fc9ecbe05e9:0x55c3e664040f1fb7,1,,,,")

    assert len(reviews) == 3
    mock_driver.get.assert_called_once_with("https://www.google.com/search?q=cafe+vainilla&oq=cafe&gs_lcrp=EgZjaHJvbWUqBggAEEUYOzIGCAAQRRg7MgYIARBFGDkyBggCEEUYPTIGCAMQRRg8MgYIBBBFGEEyBggFEC4YQNIBBzg1OWowajGoAgCwAgA&sourceid=chrome&ie=UTF-8#lrd=0x80d88fc9ecbe05e9:0x55c3e664040f1fb7,1,,,,")
    mock_scraper.get_info.assert_called_once()
    mock_scraper.extract_reviews.assert_called_once_with(3)
    mock_save.assert_called_once()
    mock_driver.quit.assert_called_once()