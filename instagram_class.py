from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium_config import *
import time
import random
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import requests
import os
import re


class InstagramBot():

    def __init__(self, username, password):

        self.username = username
        self.password = password
        self.browser = webdriver.Chrome(path_browser)

    # метод для закрытия браузера
    def close_browser(self):

        self.browser.close()
        self.browser.quit()

    # метод логина
    def login(self):

        browser = self.browser
        browser.get('https://www.instagram.com')
        time.sleep(random.randrange(3, 5))

        username_input = browser.find_element_by_name('username')
        username_input.clear()
        username_input.send_keys(username)

        time.sleep(2)

        password_input = browser.find_element_by_name('password')
        password_input.clear()
        password_input.send_keys(password)

        password_input.send_keys(Keys.ENTER)
        time.sleep(5)

    # метод ставит лайки по hashtag
    def like_photo_by_hashtag(self, hashtag):

        browser = self.browser
        browser.get(f'https://www.instagram.com/explore/tags/{hashtag}/')
        time.sleep(5)

        for i in range(1, 4):
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.randrange(3, 5))

        hrefs = browser.find_elements_by_tag_name('a')
        posts_urls = [item.get_attribute('href') for item in hrefs if "/p/" in item.get_attribute('href')]

        for url in posts_urls:
            try:
                browser.get(url)
                time.sleep(3)
                like_button = browser.find_element_by_xpath(
                    '/html/body/div[1]/section/main/div/div[1]/article/div[3]/section[1]/span[1]/button').click()
                time.sleep(random.randrange(80, 100))
            except Exception as ex:
                print(ex)
                self.close_browser()

    # метод проверяет по xpath существует ли элемент на странице
    def xpath_exists(self, url):

        browser = self.browser
        try:
            browser.find_element_by_xpath(url)
            exist = True
        except NoSuchElementException:
            exist = False
        return exist

    # метод ставит лайк на пост по прямой ссылке
    def put_exactly_like(self, userpost):

        browser = self.browser
        browser.get(userpost)
        time.sleep(4)

        wrong_userpage = "/html/body/div[1]/section/main/div/h2"
        if self.xpath_exists(wrong_userpage):
            print("Такого поста не существует, проверьте URL")
            self.close_browser()
        else:
            print("Пост успешно найден, ставим лайк!")
            time.sleep(2)

            like_button = "/html/body/div[1]/section/main/div/div[1]/article/div/div[2]/div/div[2]/section[2]/span[1]/button"
            browser.find_element_by_xpath(like_button).click()
            # button = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, like_button)))
            # button.click()

            time.sleep(2)

            print(f"Лайк на пост: {userpost} поставлен!")
            self.close_browser()

    # метод собирает ссылки на посты пользователя
    def get_all_posts_urls(self, userpage):
        browser = self.browser
        browser.get(userpage)
        time.sleep(4)

        wrong_userpage = "/html/body/div[1]/section/main/div/h2"
        if self.xpath_exists(wrong_userpage):
            print("Такого пользователя не существует, проверьте URL")
            self.close_browser()
        else:
            print("Пользователь успешно найден!")
            time.sleep(2)

            posts_count = int(browser.find_element_by_xpath(
                "/html/body/div[1]/section/main/div/header/section/ul/li[1]/span/span").text)
            print(posts_count)
            loops_count = int(posts_count / 12)
            print(loops_count)

            posts_urls = []
            for i in range(0, loops_count):
                hrefs = browser.find_elements_by_tag_name('a')
                hrefs = [item.get_attribute('href') for item in hrefs if "/p/" in item.get_attribute('href')]

                for href in hrefs:
                    posts_urls.append(href)

                browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(random.randrange(2, 4))
                print(f"Итерация #{i}")

            file_name = userpage.split("/")[-2]

            # with open(f'{file_name}.txt', 'a') as file:
            #     for post_url in posts_urls:
            #         file.write(post_url + "\n")

            set_posts_urls = set(posts_urls)
            set_posts_urls = list(set_posts_urls)

            with open(f'{file_name}_set.txt', 'w') as file:
                for post_url in set_posts_urls:
                    file.write(post_url + '\n')

    # метод ставит лайки по ссылке на аккаунт пользователя
    def put_many_likes(self, userpage):

        browser = self.browser
        self.get_all_posts_urls(userpage)
        file_name = userpage.split("/")[-2]
        time.sleep(4)
        browser.get(userpage)
        time.sleep(4)

        with open(f'{file_name}_set.txt') as file:
            urls_list = file.readlines()

            for post_url in urls_list:
                try:
                    browser.get(post_url)
                    time.sleep(2)

                    like_button = "/html/body/div[1]/section/main/div/div[1]/article/div/div[2]/div/div[2]/section[2]/span[1]/button"
                    browser.find_element_by_xpath(like_button).click()
                    # time.sleep(random.randrange(80, 100))
                    time.sleep(2)

                    print(f"Лайк на пост: {post_url} успешно поставлен!")
                except Exception as ex:
                    print(ex)
                    self.close_browser()

        self.close_browser()

    # метод скачивает контент со страницы пользователя
    def download_userpage_content(self, user):
        browser = self.browser
        self.get_all_posts_urls(user)
        file_name = user.split("/")[-2]
        time.sleep(4)
        browser.get(user)
        time.sleep(4)
        img_and_video_src_urls = []

        with open(f'{file_name}_set.txt') as file:
            urls_list = file.readlines()

            for post_url in urls_list[1:5]:
                try:
                    browser.get(post_url)
                    time.sleep(2)

                    img_src = """//*[@id="react-root"]/section/main/div/div[1]/article/div/div[2]/div/div/div[1]/img"""
                    video_src = """//*[@id="react-root"]/section/main/div/div[1]/article/div/div[2]/div/div/div[1]/div/div/video"""
                    post_id = post_url.split("/")[-2]

                    if self.xpath_exists(img_src):
                        img_src_url = browser.find_element_by_xpath(img_src).get_attribute("src")
                        img_and_video_src_urls.append(img_src_url)
                        # сохраняем изображение
                        get_img = requests.get(img_src_url)

                        with open(f'{post_id}_img.jpg', 'a') as file:
                            file.write(get_img.content)
                    elif self.xpath_exists(video_src):
                        video_src_url = browser.find_element_by_xpath(video_src).get_attribute("src")
                        img_and_video_src_urls.append(video_src_url)

                        get_video = requests.get(video_src_url)
                        with open(f'{post_id}_video.mp4', 'a') as file:
                            for chunk in get_video.iter_content(chunk_size=1824 * 1024):
                                if chunk:
                                    file.write(chunk)
                    else:
                        print('Что-то пошло не так')
                        img_and_video_src_urls.append(f'{post_url}, нет ссылки')
                    # time.sleep(random.randrange(80, 100))
                    time.sleep(2)

                    print(f"Контент: {post_url} успешно спизжен!")
                except Exception as ex:
                    print(ex)
                    self.close_browser()
            self.close_browser()
        with open(f'img_and_video_src_urls.txt', 'a') as file:
            for i in img_and_video_src_urls:
                file.write(i + "\n")

    # метод подписки на всех подписчиков переданного аккаунта
    def get_all_followers(self, userpage):

        browser = self.browser
        browser.get(userpage)
        time.sleep(4)
        file_name = userpage.split("/")[-2]

        # создаём папку с именем пользователя для чистоты проекта
        if os.path.exists(f"{file_name}"):
            print(f"Папка {file_name} уже существует!")
        else:
            print(f"Создаём папку пользователя {file_name}.")
            os.mkdir(file_name)

        wrong_userpage = "/html/body/div[1]/section/main/div/h2"
        if self.xpath_exists(wrong_userpage):
            print(f"Пользователя {file_name} не существует, проверьте URL")
            self.close_browser()
        else:
            print(f"Пользователь {file_name} успешно найден, начинаем скачивать ссылки на подписчиков!")
            time.sleep(2)

            followers_button = browser.find_element_by_xpath(
                "/html/body/div[1]/section/main/div/header/section/ul/li[2]/a/span")
            followers_count = followers_button.get_attribute('title').replace(' ','') # ебаный костыль
            print(f"Количество подписчиков: {followers_count}")
            time.sleep(2)

            loops_count = int(followers_count) / 2000
            loops_count = int(loops_count)
            print(f"Число итераций: {loops_count}")
            time.sleep(4)

            followers_button.click()
            time.sleep(4)

            followers_ul = browser.find_element_by_xpath("/html/body/div[6]/div/div/div[2]/ul")
            #followers_ul = browser.find_elements_by_tag_name('div')

            try:
                followers_urls = []
                for i in range(1, loops_count + 1):
                    browser.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", followers_ul)
                    time.sleep(random.randrange(2, 4))
                    print(f"Итерация #{i}")

                all_urls_div = followers_ul.find_elements_by_tag_name("li")

                for url in all_urls_div:
                    url = url.find_element_by_tag_name("a").get_attribute("href")
                    followers_urls.append(url)

                # сохраняем всех подписчиков пользователя в файл
                with open(f"{file_name}/{file_name}.txt", "a") as text_file:
                    for link in followers_urls:
                        text_file.write(link + "\n")

                with open(f"{file_name}/{file_name}.txt") as text_file:
                    users_urls = text_file.readlines()

                    for user in users_urls[0:10]:
                        try:
                            try:
                                with open(f'{file_name}/{file_name}_subscribe_list.txt',
                                          'r') as subscribe_list_file:
                                    lines = subscribe_list_file.readlines()
                                    if user in lines:
                                        print(f'Мы уже подписаны на {user}, переходим к следующему пользователю!')
                                        continue

                            except Exception as ex:
                                print('Файл со ссылками ещё не создан!')
                                # print(ex)

                            browser = self.browser
                            browser.get(user)
                            page_owner = user.split("/")[-2]

                            if self.xpath_exists("/html/body/div[1]/section/main/div/header/section/div[1]/div/a"):

                                print("Это наш профиль, уже подписан, пропускаем итерацию!")
                            elif self.xpath_exists(
                                    "/html/body/div[1]/section/main/div/header/section/div[1]/div[1]/div/div[2]/div/span/span[1]/button"):
                                print(f"Уже подписаны, на {page_owner} пропускаем итерацию!")
                            else:
                                time.sleep(random.randrange(4, 8))

                                if self.xpath_exists(
                                        "/html/body/div[1]/section/main/div/div/article/div[1]/div/h2"):
                                    try:
                                        follow_button = browser.find_element_by_xpath(
                                            "/html/body/div[1]/section/main/div/header/section/div[1]/div[1]/div/div/button").click()
                                        print(f'Запросили подписку на пользователя {page_owner}. Закрытый аккаунт!')
                                    except Exception as ex:
                                        print(ex)
                                else:
                                    try:
                                        if self.xpath_exists(
                                                "/html/body/div[1]/section/main/div/header/section/div[1]/div[1]/div/div/div/span/span[1]/button"):
                                            follow_button = browser.find_element_by_xpath(
                                                "/html/body/div[1]/section/main/div/header/section/div[1]/div[1]/div/div/div/span/span[1]/button").click()
                                            print(f'Подписались на пользователя {page_owner}. Открытый аккаунт!')
                                        else:
                                            follow_button = browser.find_element_by_xpath(
                                                "/html/body/div[1]/section/main/div/header/section/div[1]/div[1]/div/span/span[1]/button").click()
                                            print(f'Подписались на пользователя {page_owner}. Открытый аккаунт!')
                                    except Exception as ex:
                                        print(ex)

                                # записываем данные в файл для ссылок всех подписок, если файла нет, создаём, если есть - дополняем
                                with open(f'{file_name}/{file_name}_subscribe_list.txt',
                                          'a') as subscribe_list_file:
                                    subscribe_list_file.write(user)

                                time.sleep(random.randrange(7, 15))

                        except Exception as ex:
                            print(ex)
                            self.close_browser()

            except Exception as ex:
                print(ex)
                self.close_browser()

        self.close_browser()

    def send_direct_massage(self, username = '', massage = ''):
        browser = self.browser
        time.sleep(random.randrange(2, 4))

        direct_massage_button = '/html/body/div[1]/section/nav/div[2]/div/div/div[3]/div/div[2]/a'
        browser.find_element_by_xpath(direct_massage_button).click()

        time.sleep(2)

        unable_notify_button = '/html/body/div[6]/div/div/div/div[3]/button[2]'
        browser.find_element_by_xpath(unable_notify_button).click()

        time.sleep(2)

        send_massage_button = '/html/body/div[1]/section/div/div[2]/div/div/div[2]/div/div[3]/div/button'
        browser.find_element_by_xpath(send_massage_button).click()

        time.sleep(2)

        text_box_path = '/html/body/div[6]/div/div/div[2]/div[1]/div/div[2]/input'
        text_box = browser.find_element_by_xpath(text_box_path)
        text_box.clear()
        text_box.send_keys(username)

        time.sleep(2)

        usernames_list_path = '/html/body/div[6]/div/div/div[2]/div[2]'
        usernames_list = browser.find_element_by_xpath(usernames_list_path).find_element_by_tag_name('button').click()

        time.sleep(2)

        button_next = '/html/body/div[6]/div/div/div[1]/div/div[2]/div/button'
        browser.find_element_by_xpath(button_next).click()

        time.sleep(2)

        text_box_path = '/html/body/div[1]/section/div/div[2]/div/div/div[2]/div[2]/div/div[2]/div/div/div[2]/textarea'
        text_box = browser.find_element_by_xpath(text_box_path)
        text_box.clear()
        text_box.send_keys(massage)

        time.sleep(2)

        text_box.send_keys(Keys.ENTER)


with open('Omar.txt','r', encoding='utf-8') as file:
    massage = file.read()

# основная программа
my_bot = InstagramBot(username, password)
my_bot.login()
# my_bot.put_many_likes("https://www.instagram.com/tyxapb/")
#my_bot.download_userpage_content("https://www.instagram.com/tyxapb/")
#my_bot.get_all_followers('https://www.instagram.com/kami_yeahyellow/')
my_bot.send_direct_massage(username = 'Zahra', massage = massage)
# my_bot.put_exactly_like("https://www.instagram.com/p/CFNUBh1FCJj/")
