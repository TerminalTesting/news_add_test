#! /usr/bin/python
# -*- coding: utf-8 -*-
import unittest
import sys
import os, time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class NewsAddTest(unittest.TestCase):
    
    SITE = 'http://nsk.%s/' % os.getenv('SITE')
    ARTSOURCE = '%sartifact/' % os.getenv('BUILD_URL')
    driver = webdriver.Firefox()

    os.system('find -iname \*.png -delete')

    TEST_NEWS = {'header': 'AUTOTEST NEWS HEADER',
                 'anons': 'Autotest news anons',
                 'text': 'This is autotest made news. I hope it`s add alright'}


    def tearDown(self):
        """Удаление переменных для всех тестов. Остановка приложения"""
        
        self.driver.get('%slogout' % self.SITE)
        self.driver.close()
        if sys.exc_info()[0]:   
            print sys.exc_info()[0]

    def test_news_add(self):
        cnt=0
        
        self.driver.get('%slogin' % self.SITE)
        self.driver.find_element_by_id('username').send_keys(os.getenv('AUTH'))
        self.driver.find_element_by_id('password').send_keys(os.getenv('AUTHPASS'))
        self.driver.find_element_by_class_name('btn-primary').click()
        self.driver.get('%sterminal/admin/' % self.SITE)
        time.sleep(5)
        #self.driver.find_element_by_partial_link_text(u'тестовый режим').click()
        self.driver.get('%sterminal/admin/site/terminal/tnews/list' % self.SITE)
        self.driver.find_element_by_link_text(u'Добавить новый').click()

        #добавляем заголовок новости
        self.driver.find_element_by_css_selector('input[id*="_name"]').send_keys(self.TEST_NEWS['header'])

        #берем текущую дату
        current = time.strftime("%Y/%m/%d").split('/')

        startDate_year = self.driver.find_element_by_css_selector('select[id*="_startDate_year"]')
        for y in startDate_year.find_elements_by_tag_name('option'):
            if y.text == current[0]:#change to current year
		y.click()

	startDate_month = self.driver.find_element_by_css_selector('select[id*="_startDate_month"]')
	for m in startDate_month.find_elements_by_tag_name('option'):
            if m.text == current[1]:#change to current month
		m.click()

	startDate_day = self.driver.find_element_by_css_selector('select[id*="_startDate_day"]')
	for d in startDate_day.find_elements_by_tag_name('option'):
            if d.text == current[2]:#change to current day
		d.click()

	endDate_year = self.driver.find_element_by_css_selector('select[id*="_endDate_year"]')
	for ey in endDate_year.find_elements_by_tag_name('option'):
            if ey.text == '2019':#change to maximal year parameter
		ey.click()

        #выбираем Новосибирск, в последствии можно добавить проверку и по городам
	self.driver.find_element_by_css_selector('input[id*="_cities_1"]').click()

        #Заполняем анонс новости(сообщение выводящееся на странице новостей)
	self.driver.find_element_by_css_selector('textarea[id*="_anounce"]').send_keys(self.TEST_NEWS['anons'])

	#переключаемся на фрейм, т.к. контент ckeditor`а во фрейме
	self.driver.switch_to_frame(self.driver.find_element_by_tag_name("iframe"))
	#добавляем скриптом текст новости в тег p
	self.driver.execute_script('document.getElementsByTagName("p")[0].innerHTML = "%s";' % self.TEST_NEWS['text'])

        #переключение в основной контент из фрейма
	self.driver.switch_to_default_content()
	#сохранение данных
	self.driver.find_element_by_class_name('btn-primary').click()

	news_url = self.driver.current_url

	#переходим на страницу новостей, чтобы проверить текст анонса
	self.driver.get('%snews/' % self.SITE)

	#выбираем последнюю новость
	last_news = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'news-list__item')))

	#проверяем дату публикации на странице новостей
        if time.strftime("%d-%m-%Y") != last_news.find_element_by_tag_name('time').get_attribute('datetime').strip():
            cnt += 1
            print 'Некорректная дата публикации, нужно - ', time.strftime("%d-%m-%Y")
            print 'На странице -', last_news.find_element_by_tag_name('time').get_attribute('datetime').strip()
            print '*'*80
	
        #проверяем заголовок новости на странице новостей
        if self.TEST_NEWS['header'] != last_news.find_element_by_tag_name('a').text:
            cnt += 1
            print 'Некорректный заголовок новости, нужно - ', self.TEST_NEWS['header']
            print 'Hа странице -', last_news.find_element_by_tag_name('a').text
            print '*'*80

        #проверяем анонс новости на странице новостей
        if self.TEST_NEWS['anons'] != last_news.find_element_by_tag_name('p').text:
            cnt += 1
            print 'Некорректный анонс новости, нужно - ', self.TEST_NEWS['anons']
            print 'Hа странице -', last_news.find_element_by_tag_name('p').text
            print '*'*80

        #переходим на страницу новости
        last_news.find_element_by_tag_name('a').click()

        #ссылаемся на новый объект
        last_news = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'article')))

        #проверяем дату публикации на странице новости
        if time.strftime("%d-%m-%Y") != last_news.find_element_by_tag_name('time').get_attribute('datetime').strip():
            cnt += 1
            print 'Некорректная дата публикации на странице новости, нужно - ', time.strftime("%d-%m-%Y")
            print 'Hа странице -', last_news.find_element_by_tag_name('time').get_attribute('datetime').strip()
            print '*'*80
	
        #проверяем заголовок новости на странице новости
        if self.TEST_NEWS['header'] != last_news.find_element_by_tag_name('h1').text:
            cnt += 1
            print 'Некорректный заголовок новости на странице новости, нужно - ', TEST_NEWS['header']
            print 'Hа странице -', last_news.find_element_by_tag_name('h1').text
            print '*'*80

        #проверяем анонс новости на странице новости
        if self.TEST_NEWS['text'] != last_news.find_element_by_tag_name('p').text:
            cnt += 1
            print 'Некорректный текст на странице новости, нужно - ', self.TEST_NEWS['text']
            print 'Hа странице -', last_news.find_elements_by_tag_name('p')[1].text
            print '*'*80

        self.driver.get(news_url)
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.LINK_TEXT, u'Удалить'))).click()
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[class="btn-danger"]'))).click()

        news_id = news_url[len(self.SITE):].split('/')[5]

        try:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.LINK_TEXT, news_id)))
            cnt += 1
            print 'Новость не удалилась'
            print '*'*80
        except:
            pass

        assert cnt==0, ('Errors: %d\nnews_id:%s' % cnt, news_id)
        
       
