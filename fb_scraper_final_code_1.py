#!/usr/bin/env python
# coding: utf-8
import os
import re
import time
import json
import yaml
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from bs4 import BeautifulSoup
#from date_fetch import DateHandler
#from urls_check import URLsChecking

current_path = os.getcwd()
folder_path = os.path.join(current_path)
file_path = os.path.join(folder_path, 'secret.yaml')


try:
    with open(file_path, 'r') as f:
        secret = yaml.load(f, Loader=yaml.FullLoader)
        my_user_name = secret['credentials']['username']
        my_password = secret['credentials']['password']
except (FileNotFoundError, yaml.YAMLError) as e:
    print(f"Error loading YAML confidential file: {e}")

options = Options()
options.headless = True
options.add_experimental_option("detach", True)
options.add_argument('--disable-notifications')
options.add_argument("--disable-infobars")
options.add_argument("start-maximized")
options.add_argument("--disable-extensions")
options.add_experimental_option("prefs", { \
    "profile.default_content_setting_values.notifications": 1
})

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
driver.get("http://www.facebook.com")
WebDriverWait(driver, 2)

try:
    cookies_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//button[text()="Allow all cookies"]'))
    )
    cookies_button.click()
except TimeoutException:
    print("Allow all cookies button not found within the specified time.")

driver.find_element(By.NAME, "email").send_keys(my_user_name)
driver.find_element(By.NAME, "pass").send_keys(my_password)
driver.find_element(By.NAME, "login").click()


def right_format_data_collection(*args):
    comment_parts = list(args)
    if comment_parts[0].lower() == 'top fan':
        comment_parts.pop(0)
    author = comment_parts[0]
    like_index = comment_parts.index('Like')
    date_index = like_index - 1
    date = comment_parts[date_index]
    text = ' '.join(comment_parts[1:date_index])

    return {'Commentor': author, 'text': text, 'date of Comment': date, 'timestamp': datetime.timestamp(datetime.now())}


def create_url_with_keys(keys):
    base_url = "https://www.facebook.com/search/posts/?q="
    for key in keys:
        base_url += key + "%20"
    url = base_url[:-3]
    return url


# get superlinks from element.
def get_superlinks(element):
    links = []
    ele_html = element.get_attribute('outerHTML')
    soup = BeautifulSoup(ele_html, 'html.parser')
    a_links = soup.find_all('a')
    # Iterate through the anchor elements and print their href attributes
    for a_link in a_links:
        link = a_link.get('href')

        links.append(link)
    return links


def extract_link(links):
    company_name = None
    post_hash = None
    for link in links:
        # Use regular expressions to extract group_id, post_id, and user_id
        company_name_match = re.search(r'facebook\.com/([^/]+)/posts/', link)
        post_hash_match = re.search(r'/posts/([^/?]+)', link)

        if company_name_match and post_hash_match:
            return link

    return False


def check_comments(list_text):
    for text in list_text:
        text = text.lower()
        if text.endswith((" comments", " comment")):
            return True, text
    return False


time.sleep(4)
keys = input("Enter the keyword you want to scrap post for...")
keys_copy = keys
keys = [keys]
url = create_url_with_keys(keys)
driver.get(url)
time.sleep(2)
a = input("please wait because i need to select public post")


def get_extension_elements():
    elements_with_view_replies = driver.find_elements(By.XPATH,
                                                      "//span[contains(text(), 'View ') and contains(text(), ' repl')]")
    elements_with_see_more = driver.find_elements(By.XPATH, "//div[contains(text(), 'See more')]")
    elements_with_auther_reply = driver.find_elements(By.XPATH, "//div[contains(text(), ' repl')]")
    # elements_with_view_more_comments = driver.find_elements(By.XPATH, "//span[contains(text(), 'View ') and  contains(text(), ' more comments')]")
    return elements_with_view_replies + elements_with_see_more + elements_with_auther_reply  # + elements_with_view_more_comments


def extract_post_text(post_url):
        response = requests.get(post_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        extracted_text = soup.find('meta', property='og:description')['content']
        return extracted_text


def get_extension(elements):
    while True:
        # Process the found elements (scroll to and click on each)
        for element in elements:
            try:
                # Scroll to the element to ensure it's in view
                ActionChains(driver).move_to_element(element).perform()
                driver.execute_script("arguments[0].scrollIntoView();", element)

                # Click on the element
                element.click()
                time.sleep(3)

                # Optional: Pause to observe the result or let the page load
                driver.implicitly_wait(3)
            except:
                pass
        break


"""
Initialise the variables and

"""
"""1. slelect all the posts, and analyse one by one
"""

nth_of_records = 0
nth_of_posts = 0
parent_element_xpath = f"//*[@id[starts-with(., 'mount_0_')] and descendant::*[@role='feed']]/div/div/div/div[3]/div/div/div[1]/div[1]/div[2]/div/div/div/div/div/div"
post_list = []
context_list = []
"""1. slelect all the posts, and analyse one by one
"""
import time
from datetime import datetime

while True:
    print("...........................................................................")
    print("")
    print("nth of post: ", nth_of_posts + 1)
    """
    1. if possible move bottom of the element to the bottom of window screen
    """
    # Get all elements of all posts so far

    all_posts = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.XPATH, parent_element_xpath)))
    print("the Number of all current posts: ", len(all_posts))
    # Get the height of the browser window
    window_height = driver.execute_script("return window.innerHeight;")

    # Get the bottom position of the element relative to the viewport
    element_bottom = driver.execute_script("return arguments[0].getBoundingClientRect().bottom;",
                                           all_posts[nth_of_posts])

    # Calculate the scroll distance needed to align the bottom of the element with the bottom of the screen
    scroll_distance = element_bottom - window_height

    if scroll_distance > 0:
        # Scroll to the calculated distance
        driver.execute_script("window.scrollBy(0, arguments[0]);", scroll_distance)
        time.sleep(5)

    time.sleep(5)
    """
    2. Get information of current element
    """

    # get all info of current element
    post_detail = all_posts[nth_of_posts].text
    # Get all reaction part
    reaction_list = post_detail.split('All reactions:')[-1].split('\n')
    # Get post detail part
    list_details_of_post = post_detail.split('All reactions:')[0].split('\n')
    print('post list:', post_detail)

    """
    3. if there are comments, collect post information and move the bottom of element to the the bottom of the browser window
    click comments button

    """

    # initialise data of doctionary
    post_info = {
        'SN': None,
        'key words': '',
        'facebook url': '',
        'Author': '',
        'n_comments': 0,
        'date of commnent': '',
        'timestamp': '',
        'comments': [],
        "post_text": ''
    }

    if check_comments(reaction_list):
        """ find comments button and click on it to open a new content"""

        post_info['n_comments'] = check_comments(reaction_list)[1]
        time.sleep(3)

        try:
            time.sleep(3)
            print("post_info.get('n_comments')", post_info.get('n_comments'))
            all_c = WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located((By.XPATH, f'//span[text()="{post_info.get("n_comments")}"]')))
            for ele in all_c:
                try:

                    ele.click()
                    print("right button clicked")
                    break
                except Exception as e:
                    print(f"An error occurred when clicking comments button contains, will try next: {e}")
                    continue

        except Exception as e:
            time.sleep(3)
            print(f"An error occurred when opening comment pop up contains: {e}")
            # driver.quit()


        # locate post clickable element and click on it to open the post page
        post_xpath = '/html/body/div[1]/div/div[1]/div/div[4]/div/div/div[1]/div/div[2]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[1]/div/div/div/div/div/div/div/div/div/div/div[8]/div/div/div[2]/div/div[2]/div/div[2]/span/span/span[2]/span'
        try:
            time.sleep(3)
            post_elems = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(
                (By.XPATH, '//span[2]/span/a[@role="link"] | //span[4]/span/a[@role="link"]')))
            print("post_elems", post_elems)
            post_elems[-1].click()
            time.sleep(5)
            print(get_superlinks(post_elems[-1]))

        except Exception as e:
            print("post element are not found: ", e)

        post_url = driver.current_url

        try:
            urls_checking_obj = URLsChecking()
            new_post_text = urls_checking_obj.extract_post_text(post_url=post_url)

            if urls_checking_obj.check_url_existence(
                    new_post_url=post_url,
                    new_post_text=new_post_text
            ):
                print("Post URL already exists in data. Skipping scraping for this post.")
                driver.back()
                time.sleep(3)
                # if there is no close button
                try:
                    close_buttons = WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, '[aria-label="Close"]')),
                    )
                    time.sleep(2)
                    # Click the button
                    try:
                        if len(close_buttons) == 1:
                            close_buttons[0].click()
                            print("incrementing the post by one")
                            nth_of_posts += 1
                            continue
                        else:
                            for close_button in close_buttons.reverse():
                                close_button.click()
                            print("incrementing the post by one")
                            nth_of_posts += 1
                            continue
                    except Exception as e:
                        print("What is the exception {}".format(e))
                        # Simulate pressing the Escape key
                        try:
                            # Simulate pressing the Escape key
                            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                            print("incrementing the post by one")
                            nth_of_posts += 1
                            continue
                        except Exception as escape_exception:
                            # TODO: Because if by chance there is no close button and escape is not working
                            print("Exception while simulating Escape key press: {}".format(escape_exception))

                except Exception as e:
                    try:
                        # Simulate pressing the Escape key
                        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                        nth_of_posts += 1
                        print("incrementing the post by one")
                        continue
                    except Exception as escape_exception:
                        # think here
                        print("Exception while simulating Escape key press: {}".format(escape_exception))



        except Exception as e:
            print(f"Show the exception:::{e}")
            pass


            # here you need to check post content with the post content saved
        post_hash_match = re.search(r'/posts/([^/?]+)', post_url)

        if not post_hash_match:
            time.sleep(2)
            driver.back()
            time.sleep(2)
            try:
                close_buttons = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, '[aria-label="Close"]')))

            # Click the button
                close_buttons[-1].click()
                nth_of_posts += 1
                print("post url doesn't meet requirement, move on to next post i.e increment post by one")
                continue
            except Exception as e:
                print("show the error if close button is not found", e)
                driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                nth_of_posts += 1
                print("post url doesn't meet requirement, move on to next post i.e increment post by one")
                continue
            # video_post_hash_match = re.search(r'/videos/([^/?]+)', post_url)
            # if video_post_hash_match:
            #        call your class object and get the data
            #     video_close_button = WebDriverWait(driver, 10).until(
            #         EC.presence_of_element_located((By.CSS_SELECTOR, '[aria-label="Close Video and scroll"]')))
            #     video_close_button.click()


            # print("post_info: ", post_info)
            # print("post_url: ", post_url)

            # continue


        post_list.append(post_url)
        try:
            # Wait again for the span element after scrolling
            time.sleep(3)
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
                (By.XPATH, '//span[text()="Top comments" or text()="Most relevant"]'))).click()

        except Exception as e:
            print(f"Comment selection button not found even after scrolling: {e}")
        # Click on the element with text "Top comments" or "All comments" using explicit wait
        try:
            time.sleep(3)
            all_comments_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//span[text()="All comments" or text()="Oldest"]'))
            )
            all_comments_button.click()
            time.sleep(5)
        except Exception as e:
            print(f"Error clicking on all comments button: {e}")
            pass

        # get author information
        # How to make this looks dynamic
        author_elem_xpath = '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[2]/div[1]/div/div/div/div/div/div/div/div/div/div/div/div/div/div[8]/div/div/div[2]/div/div[2]/div/div[1]/span/h2/span[1]/a/strong/span'
        try:
            author_elem = driver.find_element(By.XPATH, author_elem_xpath)
            post_info['Author'] = author_elem.text

        except Exception as e:
            print("No author name found")
            post_info['Author'] = ''

        post_info['SN'] = nth_of_records + 1
        post_info['key words'] = keys[0]

        post_info['facebook url'] = post_url
        post_text = extract_post_text(post_url=post_url)
        post_info['post_text'] =post_text

        list_row_comments = []
        row_comments = list()
        # What is the meaning of execute script and window.scrollY
        original_position = driver.execute_script("return window.scrollY;")
        while True:

            try:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(5)

                view_more_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//span[contains(text(), " more comments")]'))
                )
                view_more_button.click()
                time.sleep(5)


            except Exception as e:
                print("No more comments: ", e)
                break

        comments_xpath = "//div[contains(@aria-label, 'Comment by') or contains(@aria-label, 'Reply by')]"
        number_of_extenable_comments = 0

        while True:
            driver.execute_script('window.scrollTo(0, 0);')

            extenable_elements = get_extension_elements()
            if len(extenable_elements) == number_of_extenable_comments:
                break

            get_extension(extenable_elements)  # clicking on see more and opening the comment
            number_of_extenable_comments = len(extenable_elements)
            time.sleep(4)
            comments_section = driver.find_elements(By.XPATH, comments_xpath)
            try:
                for comment in comments_section:

                    row_comments.append(comment.text)
                    if len(comment.text) == 0:
                        continue
                    print("success.................", comment.text)
                break
            except:
                pass

        for row_comment in row_comments:
            if not row_comment or row_comment == "Write a comment…":
                break
            comment_info = right_format_data_collection(*row_comment.split('\n'))
            date_handler_obj = DateHandler(comment_info)
            comment_info = date_handler_obj.actual_date_format()
            list_row_comments.append(comment_info)

        post_info['comments'] = list_row_comments

        try:
            try:
                with open("data_list.json", "r", encoding='utf-16') as file:
                    existing_data_list = json.load(file)
            except Exception as e:
                print("error in utf-16 so moving to utf-8", e)
                with open("data_list.json", "r", encoding='utf-8') as file:
                    existing_data_list = json.load(file)

        except FileNotFoundError:
            existing_data_list = []

        # Append the new dictionary to the list
        existing_data_list.append(post_info)

        # Write the updated list of dictionaries back to the file
        try:
            with open("data_list.json", "w", encoding='utf-16') as file:
                json.dump(existing_data_list, file,  indent=2)
        except Exception as e:
            print("error in utf-16 so moving to utf-8", e)
            with open("data_list.json", "w", encoding='utf-8') as file:
                json.dump(existing_data_list, file, indent=2)

        time.sleep(3)
        # what is the meaning of f"window.scrollTo(0, {original_position})
        driver.execute_script(f"window.scrollTo(0, {original_position});")
        time.sleep(2)
        driver.back()
        time.sleep(3)
        # if there is no close button
        try:
            close_buttons = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, '[aria-label="Close"]')),
            )
            time.sleep(2)
            # Click the button
            try:
                time.sleep(2)
                if len(close_buttons) == 1:
                    close_buttons[0].click()
                    nth_of_posts += 1
                else:
                    for close_button in close_buttons.reverse():
                        close_button.click()
                        nth_of_posts += 1
            except Exception as e:
                print("What is the exception {}".format(e))
                # Simulate pressing the Escape key
                try:
                    # Simulate pressing the Escape key
                    time.sleep(2)
                    driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                    nth_of_posts += 1
                except Exception as escape_exception:
                    # think here
                    print("Exception while simulating Escape key press: {}".format(escape_exception))

        except Exception as e:
                print("close button has some error", e)
                try:
                    # Simulate pressing the Escape key
                    time.sleep(2)
                    driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                    nth_of_posts += 1
                except Exception as escape_exception:
                    # think here by using right mouse
                    print("Exception while simulating Escape key press: {}".format(escape_exception))

        print('post_info:', post_info)


        if nth_of_records == 2: # number of post would be nth_of_records + 1
            driver.quit()
            break
        nth_of_records += 1

    else:
        nth_of_posts += 1
        print('comments are not there and hence moving to next post')
