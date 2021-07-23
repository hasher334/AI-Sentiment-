import random
from time import sleep

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    StaleElementReferenceException, TimeoutException,
    ElementClickInterceptedException,
)

from utils import set_viewport_size, get_random_user_agent


def scrape_posts_comments(post_url):
    chromedriver_path = '/home/ih/Documents/python_stuff/chromedriver'

    options = Options()
    options.add_argument("--disable-infobars")
    options.add_argument("start-maximized")
    options.add_argument("--disable-extensions")

    options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.notifications": 2
    })
    options.add_argument('--headless')
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-sh-usage")

    user_agent = get_random_user_agent(min_version=86)

    options.add_argument('--user-agent=%s' % user_agent)

    driver = webdriver.Chrome(executable_path=chromedriver_path, options=options)
    set_viewport_size(driver, 1920, 1080)

    print('############# Logging into Facebook account started #############')
    url = 'https://www.facebook.com/login/?__tn__=*F'
    driver.get(url=url)

    # Fill in email and password
    email_name = 'email'
    password_name = 'pass'
    login_btn_name = 'login'

    email = 'illia.cgerasimenko@gmail.com'
    password = 'RthD&Ngu1'

    sleep(2 + random.random())
    driver.find_element_by_name(email_name).send_keys(email)
    sleep(1 + random.random())
    driver.find_element_by_name(password_name).send_keys(password)
    driver.find_element_by_name(login_btn_name).click()

    ############# SCRAPING THE POST #############
    sleep(5 + random.random())

    print('############# Post scraping started #############')
    driver.get(url=post_url)

    try:
        wait = WebDriverWait(driver, 10)
        view_more_comments_btn = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.fv0vnmcu .m9osqain')))
        if 'View' in view_more_comments_btn.text and 'comment' in view_more_comments_btn.text:
            while True:
                try:
                    view_more_comments_btn.click()
                    sleep(random.random() + 2)
                    wait = WebDriverWait(driver, 3)
                    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.fv0vnmcu .m9osqain')))
                    view_more_comments_btn = driver.find_element_by_css_selector('.fv0vnmcu .m9osqain')
                    if 'View' not in view_more_comments_btn.text and 'comment' in view_more_comments_btn.text:
                        raise TimeoutException
                except ElementClickInterceptedException:
                    page_height = driver.execute_script(
                        "window.scrollTo(0, document.body.scrollHeight); return document.body.scrollHeight;")
                except TimeoutException as e:
                    print('Comments are fully expanded')
                    break
        else:
            raise TimeoutException
    except TimeoutException as e:
        print('Load more comments btn not found')

    # Expand all the replies
    tags_to_text = lambda tags: list(map(lambda tag: tag.text, tags))

    while True:
        are_replies_expanded = True
        reply_btns = driver.find_elements_by_css_selector(
            '.j83agx80.fv0vnmcu.hpfvmrgz > .d2edcug0.hpfvmrgz.qv66sw1b.c1et5uql')
        for reply_btn in reply_btns:
            try:
                if 'repl' in reply_btn.text.lower() and not (
                        'hide' in reply_btn.text.lower() or 'write' in reply_btn.text.lower()):
                    driver.execute_script("arguments[0].scrollIntoView();", reply_btn)
                    sleep(random.random() + 0.2)
                    reply_btn.click()
                    sleep(random.random() + 0.5)
                    are_replies_expanded = False
            except StaleElementReferenceException as e:
                print(e)
        if are_replies_expanded:
            print('Replies are fully expanded')
            break

    # Show more all the comments
    show_more_btns = driver.find_elements_by_css_selector('div.lrazzd5p')

    for show_more_btn in show_more_btns:
        if 'See More' == show_more_btn.text:
            driver.execute_script("arguments[0].scrollIntoView(); window.scrollTo(0, window.scrollY - 200);",
                                  show_more_btn)
            sleep(random.random() + 0.2)
            show_more_btn.click()
            sleep(random.random() + 0.5)
    else:
        print('Long comments are fully expanded')

    # Scraping the comments
    comments = tags_to_text(driver.find_elements_by_css_selector('.kvgmc6g5.cxmmr5t8.oygrvhab.hcukyx3x.c1et5uql'))

    return comments
