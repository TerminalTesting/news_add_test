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

    def setUp(self):
        #delete old screenshot artifacts
        os.system('find -iname \*.png -delete')
    
        self.SITE = 'http://nsk.%s/' % os.getenv('SITE')
        self.ARTSOURCE = '%sartifact/' % os.getenv('BUILD_URL')
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(5)

        self.TEST_NEWS = {'header': 'AUTOTEST NEWS HEADER',
                          'anons': 'Autotest news anons',
                          'text': 'This is autotest made news. I hope it`s add alright'}


    def tearDown(self):
        """Удаление переменных для всех тестов. Остановка приложения"""
        
        self.driver.get('%slogout' % self.SITE)
        self.driver.close()
        if sys.exc_info()[0]:   
            print sys.exc_info()[0]

    def is_element_present(self, how, what, timeout=10):
        """ Поиск элемента по локатору

            По умолчанию таймаут 10 секунд, не влияет на скорость выполнения теста
            если элемент найден, если нет - ждет его появления 10 сек
            
            Параметры:
               how - метод поиска
               what - локатор
            Методы - атрибуты класса By:
             |  CLASS_NAME = 'class name'
             |  
             |  CSS_SELECTOR = 'css selector'
             |  
             |  ID = 'id'
             |  
             |  LINK_TEXT = 'link text'
             |  
             |  NAME = 'name'
             |  
             |  PARTIAL_LINK_TEXT = 'partial link text'
             |  
             |  TAG_NAME = 'tag name'
             |  
             |  XPATH = 'xpath'
                                             """
	try:
            return WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((how, what)))
	except:
            print u'Элемент не найден'
	    print 'URL: ', self.driver.current_url
	    print u'Метод поиска: ', how
	    print u'Локатор: ', what
	    screen_name = '%d.png' % int(time.time())
	    self.driver.get_screenshot_as_file(screen_name)
	    print u'Скриншот страницы: ', self.ARTSOURCE + screen_name
	    raise Exception('ElementNotPresent')

    def test_news_add(self):
        cnt=0

        driver = self.driver
        TEST_NEWS = self.TEST_NEWS
        element = self.is_element_present
        
        driver.get('%slogin' % self.SITE)
        element(By.ID, 'username').send_keys(os.getenv('AUTH'))
        element(By.ID, 'password').send_keys(os.getenv('AUTHPASS'))
        element(By.CLASS_NAME, 'btn-primary').click()
        time.sleep(5)
        driver.get('%sterminal/admin/' % self.SITE)
        element(By.PARTIAL_LINK_TEXT, u'тестовый режим').click()
        driver.get('%sterminal/admin/site/terminal/tnews/list' % self.SITE)
        element(By.LINK_TEXT, u'Добавить новый').click()

        #добавляем заголовок новости
        element(By.CSS_SELECTOR, 'input[id*="_name"]').send_keys(TEST_NEWS['header'])

        #берем текущую дату
        current = time.strftime("%Y/%m/%d").split('/')

        startDate_year = element(By.CSS_SELECTOR, 'select[id*="_startDate_year"]')
        for y in startDate_year.find_elements_by_tag_name('option'):
            if y.text == current[0]:#change to current year
		y.click()

	startDate_month = element(By.CSS_SELECTOR, 'select[id*="_startDate_month"]')
	for m in startDate_month.find_elements_by_tag_name('option'):
            if m.text == current[1]:#change to current month
		m.click()

	startDate_day = element(By.CSS_SELECTOR, 'select[id*="_startDate_day"]')
	for d in startDate_day.find_elements_by_tag_name('option'):
            if d.text == current[2]:#change to current day
		d.click()

	endDate_year = element(By.CSS_SELECTOR, 'select[id*="_endDate_year"]')
	for ey in endDate_year.find_elements_by_tag_name('option'):
            if ey.text == '2019':#change to maximal year parameter
		ey.click()

        #выбираем Новосибирск, в последствии можно добавить проверку и по городам
	element(By.CSS_SELECTOR, 'input[id*="_cities_1"]').click()

        #Заполняем анонс новости(сообщение выводящееся на странице новостей)
	element(By.CSS_SELECTOR, 'textarea[id*="_anounce"]').send_keys(TEST_NEWS['anons'])

	#переключаемся на фрейм, т.к. контент ckeditor`а во фрейме
	driver.switch_to_frame(element(By.TAG_NAME, 'iframe'))
	#добавляем скриптом текст новости в тег p
	driver.execute_script('document.getElementsByTagName("p")[0].innerHTML = "%s";' % TEST_NEWS['text'])

        #переключение в основной контент из фрейма
	driver.switch_to_default_content()
	#сохранение данных
	element(By.CLASS_NAME, 'btn-primary').click()

	news_url = driver.current_url

	#переходим на страницу новостей, чтобы проверить текст анонса
	driver.get('%snews/' % self.SITE)

	#выбираем последнюю новость
	last_news = element(By.CLASS_NAME, 'news-list__item')

	#проверяем дату публикации на странице новостей
        if time.strftime("%d-%m-%Y") != last_news.find_element_by_tag_name('time').get_attribute('datetime').strip():
            cnt += 1
            print 'Некорректная дата публикации, нужно - ', time.strftime("%d-%m-%Y")
            print 'На странице -', last_news.find_element_by_tag_name('time').get_attribute('datetime').strip()
            print '*'*80
	
        #проверяем заголовок новости на странице новостей
        if TEST_NEWS['header'] != last_news.find_element_by_tag_name('a').text:
            cnt += 1
            print 'Некорректный заголовок новости, нужно - ', TEST_NEWS['header']
            print 'Hа странице -', last_news.find_element_by_tag_name('a').text
            print '*'*80

        #проверяем анонс новости на странице новостей
        if TEST_NEWS['anons'] != last_news.find_element_by_tag_name('p').text:
            cnt += 1
            print 'Некорректный анонс новости, нужно - ', TEST_NEWS['anons']
            print 'Hа странице -', last_news.find_element_by_tag_name('p').text
            print '*'*80

        #переходим на страницу новости
        last_news.find_element_by_tag_name('a').click()

        #ссылаемся на новый объект
        last_news = element(By.TAG_NAME, 'article')

        #проверяем дату публикации на странице новости
        if time.strftime("%d-%m-%Y") != last_news.find_element_by_tag_name('time').get_attribute('datetime').strip():
            cnt += 1
            print 'Некорректная дата публикации на странице новости, нужно - ', time.strftime("%d-%m-%Y")
            print 'Hа странице -', last_news.find_element_by_tag_name('time').get_attribute('datetime').strip()
            print '*'*80
	
        #проверяем заголовок новости на странице новости
        if TEST_NEWS['header'] != last_news.find_element_by_tag_name('h1').text:
            cnt += 1
            print 'Некорректный заголовок новости на странице новости, нужно - ', TEST_NEWS['header']
            print 'Hа странице -', last_news.find_element_by_tag_name('h1').text
            print '*'*80

        #проверяем анонс новости на странице новости
        if TEST_NEWS['text'] != last_news.find_elements_by_tag_name('p')[1].text:
            cnt += 1
            print 'Некорректный текст на странице новости, нужно - ', TEST_NEWS['text']
            print 'Hа странице -', last_news.find_elements_by_tag_name('p')[1].text
            print '*'*80

        driver.get(news_url)
        element(By.LINK_TEXT, u'Удалить').click()
        element(By.CSS_SELECTOR, 'input.btn.btn-danger').click()

        news_id = news_url[len(self.SITE):].split('/')[5]

        try:
            element(By.LINK_TEXT, news_id)
            cnt += 1
            print 'Новость не удалилась'
            print '*'*80
        except:
            pass

        assert cnt==0, ('Errors: %d\nnews_id:%s' % cnt, news_id)
        
       
