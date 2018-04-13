from selenium import webdriver
import random
import time
import pandas as pd
import bs4
from datetime import datetime


def direct_open(url):
    driver = webdriver.Chrome(executable_path= './chromedriver')
    driver.get(url)

    return driver

def verified_only(driver):
    element = driver.find_element_by_id('a-autoid-5-announce')
    element.click()
    element = driver.find_element_by_id('reviewer-type-dropdown_1')
    element.click()
    return driver


def one_page_data_extracter(driver):
    start_date = 'January 1, 2017'
    start_date = datetime.strftime(datetime.strptime(start_date, '%B %d, %Y'), '%Y-%m-%d')

    element = driver.find_element_by_id('cm_cr-review_list')
    data_html = element.get_attribute('innerHTML')
    soup = bs4.BeautifulSoup(data_html, 'html5lib')
    reviews_li = soup.find_all('div', attrs={'data-hook': "review"})
    user_review_info_li = []
    error = 0
    error_li = []
    for i in range(len(reviews_li)):
        review_tag = reviews_li[i]
        review_tag_attr = review_tag.attrs

        date_tag = review_tag.find('span', attrs={'data-hook': 'review-date'})
        review_date_raw = date_tag.text
        review_date = review_date_raw[3:]
        review_date = datetime.strftime(datetime.strptime(review_date, '%B %d, %Y'), '%Y-%m-%d')

        if review_date >= start_date:

            user_id = review_tag_attr['id']

            star_tag = review_tag.find('a', attrs={'class': 'a-link-normal'}).attrs
            review_rating = star_tag['title']

            title_tag = review_tag.find('a', attrs={'data-hook': 'review-title'})
            review_title = title_tag.text

            name_tag = review_tag.find('a', attrs={'data-hook': 'review-author'})
            user_name = name_tag.text

            product_type_tag = review_tag.find('a', attrs={'data-hook': 'format-strip'})
            product_pattern = product_type_tag.text

            review_text_tag = review_tag.find('span', attrs={'data-hook': 'review-body'})
            review_text_raw = review_text_tag.text
            start_idx = review_text_raw.find('Install Flash Player')
            if start_idx != -1:
                start_idx += 21
                review_text = review_text_raw[start_idx:]
            else:
                review_text = review_text_raw

            user_review_info = {'user_id': user_id, "review_rating": review_rating,
                                "review_title": review_title, "user_name": user_name,
                                "review_date": review_date, "product_pattern": product_pattern,
                                "review_text": review_text}

            user_review_info_li.append(user_review_info)
        else:
            print('The date before January 1st, 2017!')
            error += 1
            error_li.append(review_date)
            log = [error, error_li]

    return driver, user_review_info_li, log

def next_page(driver):
    element = driver.find_element_by_class_name("a-last")
    data_html = element.get_attribute('innerHTML')
    soup = bs4.BeautifulSoup(data_html,'html5lib')
    next_page_tag = soup.find('a').attrs
    next_page_link = next_page_tag['href']
    amazon_url = 'https://www.amazon.com/'
    url = amazon_url+next_page_link
    driver.get(url)
    return driver


def all_pages_extracter(driver):
    log_li = []
    driver, user_review_info_li, log = one_page_data_extracter(driver)
    reviews_df = pd.DataFrame(user_review_info_li)
    log_li.append(log)

    for i in range(150):
        try:
            driver = next_page(driver)
            driver, user_review_info_li_more, log_more = one_page_data_extracter(driver)
            reviews_df_more = pd.DataFrame(user_review_info_li_more)
            log_li.append(log_more)
            reviews_df = pd.concat([reviews_df, reviews_df_more], axis=0, names=None, ignore_index=True)
            normal_delay = random.normalvariate(2, 0.5)
            time.sleep(normal_delay)
        except:
            pass
    df = reviews_df
    df = df.drop_duplicates()
    df.to_json("reviews.json")
    return driver, df, log_li

def main():
    driver = direct_open('https://www.amazon.com/RockBirds-Flashlights-Bright-Aluminum-Flashlight/product-reviews/B00X61AJYM')
    driver = verified_only(driver)
    driver,df,log_li = all_pages_extracter(driver)
    driver.close()
    return df, log_li

if __name__ == '__main__':
    main()