import logging as logger
from equipments.Vmm import Vmm
from bmc.BmcError import BmcError
from selenium import webdriver
import BMCconstant
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import traceback
from selenium.webdriver.common.keys import Keys


class BmcMyIT(Vmm):
	"""Virtual machine manager"""

	def __init__(self, name, **kwargs):
		self.plmns = []
		self.driver = ''
		Vmm.__init__(self, name, **kwargs)

	def login_bmc(self):
		try:
			logger.info("executing login_bmcMyIT()")
			self.driver = webdriver.Chrome()
			self.driver.get(self.loginurl)
			self.driver.maximize_window()

			username = self.driver.find_element_by_xpath('/html/body/div/div/form/div[2]/div/label/input')
			password = self.driver.find_element_by_xpath('//*[@id="login_user_password"]')
			login = self.driver.find_element_by_xpath('//*[@id="login-jsp-btn"]')

			username.send_keys(self.username)
			password.send_keys(self.password)
			login.click()
			self.verify_popup()

			time.sleep(10)
			logger.info("successfully logged in")
			logger.info("Exiting login_bmcMyIT()")
		except BaseException as be:
			logger.fatal(
				"Fatal exception {} occurred inside login_bmc() while logging in to BMC {}".format(be, self.name))
			logger.error(traceback.print_exc())
			self.driver.close()

	def verify_popup(self):
		try:
			logger.info("Executing verify_popup()")
			WebDriverWait(self.driver, 3).until(EC.alert_is_present(), 'Timed out waiting for popup to appear.')

			alert = self.driver.switch_to.alert
			logger.info('Alert is {}'.format(alert.text))
			alert.accept()
			logger.info("Exiting verify_popup")
		except TimeoutException as te:
			logger.info("No pop up occured")

	def MyIt_logout(self):
		try:
			logger.info("Executing MyIt_logout")
			# wait for Men menu to appear, then hover it
			men_menu = WebDriverWait(self.driver, 10).until(
				EC.visibility_of_element_located(
					(By.XPATH, "/html/body/div/div/div/div/header/div/div[2]/div[2]/button/img")))
			ActionChains(self.driver).move_to_element(men_menu).perform()

			# wait for signout menu item to appear, then click it
			signout = WebDriverWait(self.driver, 10).until(
				EC.visibility_of_element_located(
					(By.XPATH, "/html/body/div/div/div/div/header/div/div[2]/div[2]/div/span")))
			signout.click()
			self.driver.quit()
			logger.info("Exiting bmc_logout()")
		except BaseException:
			logger.fatal("Fatal exception occurred inside login_MyIt() while logging in to MyIt {}".format(self.name))
			logger.error(traceback.print_exc())
			self.driver.close()

	def verify_srd_menu_submit(self, kwargs):
		time.sleep(5)
		WebDriverWait(self.driver, 10).until(
			EC.visibility_of_element_located(
				(By.XPATH, '/html/body/div[1]/div/div/div/header/div/nav/ul[1]/li[3]/a')))
		self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div/header/div/nav/ul[1]/li[3]/a').click()

		time.sleep(4)
		self.driver.find_element_by_xpath('/html/body/div/div/div/div/ui-view/div/div/div[1]/div/button').click()
		self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div/ui-view/div/div/div[1]/div/nav/div/div[2]/ul/li[1]/a').click()
		time.sleep(3)
		self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div/ui-view/ui-view/main/div/ul/li[1]/div[2]/div/span').click()
		window_before = self.driver.window_handles[0]
		self.driver.switch_to.window(window_before)
		time.sleep(3)
		self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[1]/div/div/div[2]/div/button').click()
		time.sleep(3)
		self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[1]/div/div/div[2]/div/div/select/option[2]').click()
		"Second tab"
		time.sleep(3)
		self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[2]/div/div/div[2]/div/button').click()
		time.sleep(3)
		self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[2]/div/div/div[2]/div/div/select/option[2]').click()
		"Third tab"
		time.sleep(3)
		self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[3]/div/div/div[2]/div/button').click()
		time.sleep(3)
		self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[3]/div/div/div[2]/div/div/select/option[2]').click()
		time.sleep(3)
		self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[5]/div/div/input').send_keys(
			kwargs['name'])

		self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[4]/div/div/input').send_keys(
			kwargs['name'])
		# self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[3]/div/div/input').send_keys(kwargs['password'])
		self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[6]/div/div/input').send_keys(
			kwargs['email'])
		self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[7]/div/div/input').send_keys(
			kwargs['info'])
		self.driver.execute_script("document.body.style.zoom='50%'")
		self.driver.save_screenshot("passwordresetsubmitbuttom1.png")
		self.driver.execute_script("document.body.style.zoom='100%'")
		"""Submit button"""
		self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/form/div/div/button[1]').click()
		return True

	def verify_srd_display_option(self):
		time.sleep(3)
		men_menu = WebDriverWait(self.driver, 10).until(
			EC.visibility_of_element_located((By.XPATH, '//*[@id="toggle-my-profile-sub-menu"]')))
		ActionChains(self.driver).move_to_element(men_menu).perform()
		signout = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(
			(By.XPATH, "html/body/div[1]/div/div/div/header/div/nav/ul[1]/li[2]/ul/li[1]/a")))
		signout.click()
		time.sleep(3)
		self.driver.find_element_by_xpath(
			'/html/body/div/div/div/div/ui-view/main/div[2]/div[2]/div[2]/div[3]/div[1]/div/div/div[1]').click()
		time.sleep(3)
		self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div[3]/div/div[2]/div[2]/h3').click()
		data_list = []
		data_list.append(self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[1]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[2]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[3]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[4]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[5]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[6]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[7]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[8]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[9]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[10]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[11]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[12]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[13]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[14]/td[1]').text)
		self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div[1]/ins').click()
		print(data_list)

		def remove_cruft(s):
			return s[:-1]

		list1 = [remove_cruft(data_list) for data_list in data_list]
		print(list1)
		veri = False
		for i in list1:
			for k, v in BMCconstant.BMCContstants.Displayoption.items():
				if i == k and v == ['True']:
					print(v)
					veri = True
				elif i == k and v == ['False']:
					print(v)
					return False
		return veri

	def reset_password(self, kwargs):
		time.sleep(4)
		"""Catalog"""
		self.driver.find_element_by_xpath('/html/body/div/div/div/div/header/div/nav/ul[1]/li[3]/a').click()
		time.sleep(2)
		"""Browse Category"""
		self.driver.find_element_by_xpath('/html/body/div/div/div/div/ui-view/div/div/div[1]/div/button/span').click()

		time.sleep(2)
		"""Access"""
		self.driver.find_element_by_xpath(
			'/html/body/div/div/div/div/ui-view/div/div/div[1]/div/nav/div/div[2]/ul/li[1]/a').click()

		time.sleep(2)
		"""Pasword Reset"""
		self.driver.find_element_by_xpath('/html/body/div/div/div/div/ui-view/ui-view/main/div/ul/li[2]/div[2]').click()

		time.sleep(3)
		"""option - Password"""
		self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[1]/div/div/div[2]/div[1]/label/span').click()

		"""Username"""
		user = self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[2]/div/div/input')
		user.send_keys(kwargs['Username'])  # 'ssparsh'

		"""Password"""
		passw = self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[3]/div/div/input')
		passw.send_keys(kwargs['Password'])  # 'Password_'

		"""Email"""
		email = self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[4]/div/div/input')
		email.send_keys(kwargs['Email'])  # sparsh.sparsh@nokia.com

		"""Additional Information"""
		info = self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[5]/div/div/textarea')
		info.send_keys(kwargs['Info'])

		"""Click - Submit Request"""
		self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div[3]/div/div[2]/form/div/div/button[1]').click()

		"""Validation"""
		req_details = []
		"""Password reset"""

		req_details.append(self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[1]/div/div/div[2]/div[1]/label/span').text)
		req_details.append(self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[2]/div/div/div[1]/div[1]/h5/span[1]').text)
		req_details.append(self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[3]/div/div/div[1]/div/h5/span[1]').text)
		req_details.append(self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[4]/div/div/div[1]/div/h5/span[1]').text)
		req_details.append(self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[5]/div/div/div[1]/div[1]/h5/span').text)

		return req_details

	def my_it_password_reset(self):
		time.sleep(3)
		"""Catalog"""
		self.driver.find_element_by_xpath('/html/body/div/div/div/div/header/div/nav/ul[1]/li[3]/a').click()
		time.sleep(2)
		"""Password Reset"""
		self.driver.find_element_by_xpath(
			'/html/body/div/div/div/div/ui-view/ui-view/main/div[1]/div/div/div[2]/div/div/div/div/ul[2]/li[1]/div[2]/div/span').click()
		# self.driver.find_element_by_xpath('/html/body/div/div/div/div/ui-view/ui-view/main/div[1]/div/div/div[2]/div[1]/div/div/div/ul[2]/li[1]/div[2]').click()
		time.sleep(3)
		"""option - Password"""
		self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[1]/div/div/div[2]/div[1]/label/span').click()

		"""Username"""
		self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[2]/div/div/input').send_keys(
			'ssachin')
		"""Password"""
		self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[3]/div/div/input').send_keys(
			'None')
		"""Email"""
		self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[4]/div/div/input').send_keys(
			'sachin.sachin@nokia.com@nokia.com')
		"""Click - Submit Request"""
		self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div[3]/div/div[2]/form/div/div/button[1]').click()

	def report_computer_issue(self, kwargs):
		time.sleep(4)
		"""Catalog"""
		self.driver.find_element_by_xpath('/html/body/div/div/div/div/header/div/nav/ul[1]/li[3]/a').click()
		time.sleep(2)
		"""Clicking on Report Computer Issue"""
		self.driver.find_element_by_xpath(
			'/html/body/div/div/div/div/ui-view/ui-view/main/div[2]/div/div/div[2]/div/div/div/div/ul[1]/li[1]/div[2]/div/span').click()
		time.sleep(3)
		window_before = self.driver.window_handles[0]
		self.driver.switch_to.window(window_before)

		select_date = self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[2]/div/i')
		select_date.click()
		time.sleep(3)
		select_date.send_keys(Keys.DOWN)
		self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[2]/div/div/table/tbody/tr[6]/td[7]/button').click()

		computer_type = self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[1]/div/div/div[2]/button')
		computer_type.click()
		time.sleep(3)
		computer_type.send_keys(Keys.DOWN)
		self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[1]/div/div/div[2]/div/select/option[2]').click()

		computer_issue = self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[2]/div/div/div[2]/button')
		computer_issue.click()
		time.sleep(3)
		computer_issue.send_keys(Keys.DOWN)
		self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[2]/div/div/div[2]/div/select/option[2]').click()

		problem = self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[3]/div/div/textarea')
		problem.send_keys('Demo Test')
		time.sleep(5)
		self.driver.execute_script("document.body.style.zoom='50%'")
		self.driver.save_screenshot("VPN1.png")
		self.driver.execute_script("document.body.style.zoom='100%'")

		sub = self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div[3]/div/div[2]/form/div/div/button[1]')
		sub.click()
		time.sleep(5)
		self.driver.execute_script("document.body.style.zoom='50%'")
		self.driver.save_screenshot("VPN2.png")
		self.driver.execute_script("document.body.style.zoom='100%'")

		return True

	def verify_srd_display_option_computer_issue(self):
		time.sleep(3)
		men_menu = WebDriverWait(self.driver, 10).until(
			EC.visibility_of_element_located((By.XPATH, '//*[@id="toggle-my-profile-sub-menu"]')))
		ActionChains(self.driver).move_to_element(men_menu).perform()
		signout = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(
			(By.XPATH, "html/body/div[1]/div/div/div/header/div/nav/ul[1]/li[2]/ul/li[1]/a")))
		signout.click()
		time.sleep(3)
		self.driver.find_element_by_xpath(
			'/html/body/div/div/div/div/ui-view/main/div[2]/div[2]/div[2]/div[3]/div[1]/div/div/div[1]').click()
		time.sleep(3)
		data_list = []
		data_list.append(self.driver.find_element_by_xpath('html/body/div[1]/div/div/div[3]/div/div[2]/div[3]/h3').text)
		self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div[3]/div/div[2]/div[2]/h3').click()

		data_list.append(self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[1]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[2]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[3]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[4]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[5]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[6]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[7]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[8]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[9]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[10]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[11]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[12]/td[1]').text)

		self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div[1]/ins').click()
		logger.info("List = {}".format(data_list))

		def remove_cruft(s):
			return s[:-1]

		list1 = [remove_cruft(data_list) for data_list in data_list]
		logger.info("List1 = {}".format(list1))
		veri = False
		for i in list1:
			for k, v in BMCconstant.BMCContstants.Displayoption_Computer_issue.items():
				if i == k and v == ['True']:
					logger.info(k)
					logger.info(v)
					veri = True
				elif i == k and v == ['False']:
					logger.info(k)
					logger.info(v)
					return False
		return veri

	def report_mobile_issue(self, kwargs):
		time.sleep(4)
		"""Catalog"""
		self.driver.find_element_by_xpath('/html/body/div/div/div/div/header/div/nav/ul[1]/li[3]/a').click()
		time.sleep(2)
		"""Clicking on Report Mobile Issue"""
		self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div/ui-view/ui-view/main/div[2]/div/div/div[2]/div/div/div/div/ul[1]/li[3]/div[2]/div/span').click()
		time.sleep(3)
		window_before = self.driver.window_handles[0]
		self.driver.switch_to.window(window_before)

		mobile_type = self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[2]/div[1]/div/div/div[2]/button')
		mobile_type.click()
		time.sleep(3)
		mobile_type.send_keys(Keys.DOWN)
		self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[2]/div[1]/div/div/div[2]/div/select/option[2]').click()

		mobile_issue = self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[2]/div[2]/div/div/div[2]/button')
		mobile_issue.click()
		time.sleep(3)
		mobile_issue.send_keys(Keys.DOWN)
		self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[2]/div[2]/div/div/div[2]/div/select/option[2]').click()

		problem = self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[2]/div[3]/div/div/input')
		problem.send_keys('Demo Test')
		time.sleep(5)
		self.driver.execute_script("document.body.style.zoom='50%'")
		self.driver.save_screenshot("VPN1.png")
		self.driver.execute_script("document.body.style.zoom='100%'")

		sub = self.driver.find_element_by_xpath('html/body/div[1]/div/div/div[3]/div/div[2]/form/div/div/button[1]')
		sub.click()
		time.sleep(5)
		self.driver.execute_script("document.body.style.zoom='50%'")
		self.driver.save_screenshot("VPN2.png")
		self.driver.execute_script("document.body.style.zoom='100%'")

		return True

	def verify_srd_display_option_mobile_issue(self):
		time.sleep(3)
		men_menu = WebDriverWait(self.driver, 10).until(
			EC.visibility_of_element_located((By.XPATH, '//*[@id="toggle-my-profile-sub-menu"]')))
		ActionChains(self.driver).move_to_element(men_menu).perform()
		signout = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(
			(By.XPATH, "html/body/div[1]/div/div/div/header/div/nav/ul[1]/li[2]/ul/li[1]/a")))
		signout.click()
		time.sleep(3)
		self.driver.find_element_by_xpath(
			'/html/body/div/div/div/div/ui-view/main/div[2]/div[2]/div[2]/div[3]/div[1]/div/div/div[1]').click()
		time.sleep(3)
		data_list = []
		data_list.append(self.driver.find_element_by_xpath('html/body/div[1]/div/div/div[3]/div/div[2]/div[3]/h3').text)
		self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div[3]/div/div[2]/div[2]/h3').click()

		data_list.append(self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[1]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[2]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[3]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[4]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[5]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[6]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[7]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[8]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[9]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[10]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[11]/td[1]').text)

		self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div[1]/ins').click()
		logger.info("List = {}".format(data_list))

		def remove_cruft(s):
			return s[:-1]

		list1 = [remove_cruft(data_list) for data_list in data_list]
		logger.info("List1 = {}".format(list1))
		veri = False
		for i in list1:
			for k, v in BMCconstant.BMCContstants.Displayoption_Mobile_issue.items():
				if i == k and v == ['True']:
					logger.info(k)
					logger.info(v)
					veri = True
				elif i == k and v == ['False']:
					logger.info(k)
					logger.info(v)
					return False
		return veri

	def retail_peripheral_issue(self, kwargs):
		time.sleep(5)
		"""Catalog"""
		self.driver.find_element_by_xpath('/html/body/div/div/div/div/header/div/nav/ul[1]/li[3]/a').click()
		time.sleep(2)
		"""Clicking on Retail Peripheral Issue"""
		self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div/ui-view/ui-view/main/div[2]/div/div/div[2]/div/div/div/div/ul[2]/li/div[2]/div/span').click()
		time.sleep(3)
		window_before = self.driver.window_handles[0]
		self.driver.switch_to.window(window_before)

		select_date = self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[2]/div/i')
		select_date.click()
		time.sleep(3)
		select_date.send_keys(Keys.DOWN)
		self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[2]/div/div/table/tbody/tr[6]/td[7]/button').click()

		retail_store = self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[1]/div/div/div[2]/div/button')
		retail_store.click()
		time.sleep(3)
		retail_store.send_keys(Keys.DOWN)
		self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[1]/div/div/div[2]/div/div/select/option[2]').click()
		# submit.send_keys(Keys.ENTER)

		peripheral_type = self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[2]/div/div/div[2]/button')
		peripheral_type.click()
		time.sleep(3)
		peripheral_type.send_keys(Keys.DOWN)
		self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[2]/div/div/div[2]/div/select/option[2]').click()

		peripheral_issue = self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[3]/div/div/div[2]/button')
		peripheral_issue.click()
		time.sleep(3)
		peripheral_issue.send_keys(Keys.DOWN)
		self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[3]/div/div/div[2]/div/select/option[2]').click()

		problem = self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[4]/div/div/textarea')
		problem.send_keys('Demo Test')
		time.sleep(5)
		self.driver.execute_script("document.body.style.zoom='50%'")
		self.driver.save_screenshot("VPN1.png")
		self.driver.execute_script("document.body.style.zoom='100%'")

		sub = self.driver.find_element_by_xpath('html/body/div[1]/div/div/div[3]/div/div[2]/form/div/div/button[1]')
		sub.click()
		time.sleep(5)
		self.driver.execute_script("document.body.style.zoom='50%'")
		self.driver.save_screenshot("VPN2.png")
		self.driver.execute_script("document.body.style.zoom='100%'")

		return True

	def verify_srd_display_option_retail_peripheral_issue(self):
		time.sleep(3)
		men_menu = WebDriverWait(self.driver, 10).until(
			EC.visibility_of_element_located((By.XPATH, '//*[@id="toggle-my-profile-sub-menu"]')))
		ActionChains(self.driver).move_to_element(men_menu).perform()
		signout = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(
			(By.XPATH, "html/body/div[1]/div/div/div/header/div/nav/ul[1]/li[2]/ul/li[1]/a")))
		signout.click()
		time.sleep(3)
		self.driver.find_element_by_xpath(
			'/html/body/div/div/div/div/ui-view/main/div[2]/div[2]/div[2]/div[3]/div[1]/div/div/div[1]').click()
		time.sleep(3)
		data_list = []
		data_list.append(self.driver.find_element_by_xpath('html/body/div[1]/div/div/div[3]/div/div[2]/div[3]/h3').text)
		self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div[3]/div/div[2]/div[2]/h3').click()

		data_list.append(self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[1]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[2]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[3]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[4]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[5]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[6]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[7]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[8]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[9]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[10]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[11]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[12]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[13]/td[1]').text)

		self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div[1]/ins').click()
		logger.info("List = {}".format(data_list))

		def remove_cruft(s):
			return s[:-1]

		list1 = [remove_cruft(data_list) for data_list in data_list]
		logger.info("List1 = {}".format(list1))
		veri = False
		for i in list1:
			for k, v in BMCconstant.BMCContstants.Displayoption_Retail_Peripheral_issue.items():
				if i == k and v == ['True']:
					logger.info(k)
					logger.info(v)
					veri = True
				elif i == k and v == ['False']:
					logger.info(k)
					logger.info(v)
					return False
		return veri

	def verify_srd_Rebus_passwordreset_menu_submit(self, kwargs):
		time.sleep(5)
		WebDriverWait(self.driver, 10).until(
			EC.visibility_of_element_located((By.XPATH, '/html/body/div[1]/div/div/div/header/div/nav/ul[1]/li[3]/a')))
		self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div/header/div/nav/ul[1]/li[3]/a').click()

		time.sleep(4)
		self.driver.find_element_by_xpath('/html/body/div/div/div/div/ui-view/div/div/div[1]/div/button').click()
		self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div/ui-view/div/div/div[1]/div/nav/div/div[2]/ul/li[1]/a').click()
		time.sleep(3)
		self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div/ui-view/ui-view/main/div/ul/li[1]/div[2]/div/span').click()
		window_before = self.driver.window_handles[0]
		self.driver.switch_to.window(window_before)
		time.sleep(3)
		self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[1]/div/div/div[2]/div/button').click()
		time.sleep(3)
		self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[1]/div/div/div[2]/div/div/select/option[2]').click()
		"Second tab"
		time.sleep(3)
		self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[2]/div/div/div[2]/div/button').click()
		time.sleep(3)
		self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[2]/div/div/div[2]/div/div/select/option[2]').click()
		"Third tab"
		time.sleep(3)
		self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[3]/div/div/div[2]/div/button').click()
		time.sleep(3)
		self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[3]/div/div/div[2]/div/div/select/option[2]').click()
		time.sleep(3)
		self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[5]/div/div/input').send_keys(
			kwargs['name'])

		self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[4]/div/div/input').send_keys(
			kwargs['name'])
		# self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[3]/div/div/input').send_keys(kwargs['password'])
		self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[6]/div/div/input').send_keys(
			kwargs['email'])
		self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[7]/div/div/input').send_keys(
			kwargs['info'])
		self.driver.execute_script("document.body.style.zoom='50%'")
		self.driver.save_screenshot("passwordresetsubmitbuttom1.png")
		self.driver.execute_script("document.body.style.zoom='100%'")
		"""Submit button"""
		self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div[3]/div/div[2]/form/div/div/button[1]').click()
		return True

	def verify_srd_Rebus_orderasset_menu_submit(self, kwargs):
		time.sleep(4)
		self.driver.find_element_by_xpath('/html/body/div/div/div/div/header/div/nav/ul[1]/li[3]/a').click()
		time.sleep(4)
		self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div/ui-view/ui-view/main/div[1]/div/div/div[2]/div/div/div/div/ul[1]/li[4]').click()
		window_before = self.driver.window_handles[0]
		self.driver.switch_to.window(window_before)
		time.sleep(5)
		Assetorder = self.driver.find_element_by_css_selector(
			"input[type='radio'][value='" + kwargs['value'] + "']").click()
		time.sleep(3)
		self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[2]/div[3]/div/div/textarea').send_keys(
			'test')
		"""Calender"""
		self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[2]/div[4]/div/div/div[2]/div[1]/div/input[1]').click()
		time.sleep(3)
		self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[2]/div[4]/div/div/div[2]/div[1]/div/div/table/tbody/tr[5]/td[5]/button').click()
		time.sleep(3)
		"""Time"""
		self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[2]/div[3]/div/div/textarea').click()
		time.sleep(3)
		self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[2]/div[4]/div/div/div[2]/div[2]/div/input[1]').click()
		time.sleep(3)
		self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[2]/div[4]/div/div/div[2]/div[2]/div/div/table/tbody/tr[2]/td[3]/button').click()
		time.sleep(3)
		self.driver.execute_script("document.body.style.zoom='50%'")
		self.driver.save_screenshot("orderassetsubmitbuttom1.png")
		self.driver.execute_script("document.body.style.zoom='100%'")
		"""submit"""
		self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div[3]/div/div[2]/form/div/div/button[1]').click()
		time.sleep(3)
		self.driver.execute_script("document.body.style.zoom='50%'")
		self.driver.save_screenshot("orderassetsubmitbuttom2.png")
		self.driver.execute_script("document.body.style.zoom='100%'")
		return True

	def verify_srd_Rebus_BSM_menu_submit(self, kwargs):
		time.sleep(4)
		self.driver.find_element_by_xpath('/html/body/div/div/div/div/header/div/nav/ul[1]/li[3]/a').click()
		time.sleep(4)
		self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div/ui-view/ui-view/main/div[1]/div/div/div[2]/div/div/div/div/ul[1]/li[1]/div[2]/div/span').click()
		window_before = self.driver.window_handles[0]
		self.driver.switch_to.window(window_before)
		time.sleep(5)
		Assetorder = self.driver.find_element_by_css_selector(
			"input[type='radio'][value='" + kwargs['value'] + "']").click()
		time.sleep(3)
		self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[1]/div/div/div[2]/button').click()
		time.sleep(2)
		self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[1]/div/div/div[2]/div/div/div/input').send_keys(
			kwargs['value2'])
		time.sleep(2)
		self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[1]/div/div/div[2]/div/select/option[2]').click()
		"""Calender"""
		self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[2]/div/button').click()
		time.sleep(3)
		self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[2]/div/div/table/tbody/tr[5]/td[5]/button').click()
		time.sleep(3)
		"""INFO"""
		self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[4]/div/div/textarea').send_keys(
			"Test")
		self.driver.execute_script("document.body.style.zoom='50%'")
		self.driver.save_screenshot("orderassetsubmitbuttom1.png")
		self.driver.execute_script("document.body.style.zoom='100%'")
		"""submit"""
		self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div[3]/div/div[2]/form/div/div/button[1]').click()
		time.sleep(3)
		self.driver.execute_script("document.body.style.zoom='50%'")
		self.driver.save_screenshot("orderassetsubmitbuttom2.png")
		self.driver.execute_script("document.body.style.zoom='100%'")
		return True

	def verify_srd_Rebus_Mobiledeviceacc_menu_submit(self, kwargs):
		time.sleep(4)
		self.driver.find_element_by_xpath('/html/body/div/div/div/div/header/div/nav/ul[1]/li[3]/a').click()
		time.sleep(4)
		self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div/ui-view/ui-view/main/div[1]/div/div/div[2]/div/div/div/div/ul[1]/li[3]/div[2]').click()
		window_before = self.driver.window_handles[0]
		self.driver.switch_to.window(window_before)
		time.sleep(5)
		Selectservice = self.driver.find_element_by_css_selector(
			"input[type='radio'][value='" + kwargs['value'] + "']").click()
		time.sleep(3)
		selectinsideservice = self.driver.find_element_by_css_selector(
			"input[type='radio'][value='" + kwargs['insideservice'] + "']").click()
		"""Calender"""
		self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[2]/div/button').click()
		time.sleep(3)
		self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[2]/div/div/table/tbody/tr[5]/td[5]/button').click()
		time.sleep(3)
		"""INFO"""
		self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[6]/div/div/textarea').send_keys(
			"Test")
		self.driver.execute_script("document.body.style.zoom='50%'")
		self.driver.save_screenshot("Mobiledeviceacc1.png")
		self.driver.execute_script("document.body.style.zoom='100%'")
		"""submit"""
		self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div[3]/div/div[2]/form/div/div/button[1]').click()
		time.sleep(3)
		self.driver.execute_script("document.body.style.zoom='50%'")
		self.driver.save_screenshot("Mobiledeviceacc2.png")
		self.driver.execute_script("document.body.style.zoom='100%'")
		return True

	def verify_srd_Rebus_VPN_menu_submit(self, kwargs):
		time.sleep(4)
		self.driver.find_element_by_xpath('/html/body/div/div/div/div/header/div/nav/ul[1]/li[3]/a').click()
		time.sleep(4)
		self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div/ui-view/ui-view/main/div[1]/div/div/div[2]/div/div/div/div/ul[2]/li').click()
		window_before = self.driver.window_handles[0]
		self.driver.switch_to.window(window_before)
		time.sleep(5)
		# Selectservice=self.driver.find_element_by_css_selector("input[type='radio'][value='Enable VPN Access']").click()
		Selectservice = self.driver.find_element_by_css_selector(
			"input[type='radio'][value='" + kwargs['value'] + "']").click()
		"""Calender"""
		self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[2]/div/button').click()
		time.sleep(3)
		self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[2]/div/div/table/tbody/tr[5]/td[5]/button').click()
		time.sleep(3)
		"""INFO"""
		self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[2]/div/div/textarea').send_keys(
			"Test")
		self.driver.execute_script("document.body.style.zoom='50%'")
		self.driver.save_screenshot("VPN1.png")
		self.driver.execute_script("document.body.style.zoom='100%'")
		"""submit"""
		self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div[3]/div/div[2]/form/div/div/button[1]').click()
		time.sleep(3)
		self.driver.execute_script("document.body.style.zoom='50%'")
		self.driver.save_screenshot("VPN2.png")
		self.driver.execute_script("document.body.style.zoom='100%'")
		return True

	def verify_srd_Rebus_reportemailissue_menu_submit(self, kwargs):
		time.sleep(4)
		self.driver.find_element_by_xpath('/html/body/div/div/div/div/header/div/nav/ul[1]/li[3]/a').click()
		time.sleep(4)
		self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div/ui-view/ui-view/main/div[2]/div/div/div[2]/div/div/div/div/ul[1]/li[2]/div[2]/div/span').click()
		window_before = self.driver.window_handles[0]
		self.driver.switch_to.window(window_before)
		time.sleep(5)
		self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[1]/div/div/div[2]/button').click()
		time.sleep(2)
		self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[1]/div/div/div[2]/div/div/div/input').send_keys(
			kwargs['value2'])
		time.sleep(2)
		self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[1]/div/div/div[2]/div/select/option[2]').click()
		"""Calender"""
		self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[2]/div/button').click()
		time.sleep(3)
		self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[2]/div/div/table/tbody/tr[5]/td[5]/button').click()
		time.sleep(3)
		"""INFO"""
		self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[2]/div/div/textarea').send_keys(
			"Test")
		self.driver.execute_script("document.body.style.zoom='50%'")
		self.driver.save_screenshot("reportmail1.png")
		self.driver.execute_script("document.body.style.zoom='100%'")
		"""submit"""
		self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div[3]/div/div[2]/form/div/div/button[1]').click()
		time.sleep(3)
		self.driver.execute_script("document.body.style.zoom='50%'")
		self.driver.save_screenshot("reportmail2.png")
		self.driver.execute_script("document.body.style.zoom='100%'")
		return True

	def verify_srd_Rebus_exchangerequest_menu_submit(self, kwargs):
		time.sleep(4)
		self.driver.find_element_by_xpath('/html/body/div/div/div/div/header/div/nav/ul[1]/li[3]/a').click()
		time.sleep(4)
		self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div/ui-view/ui-view/main/div[1]/div/div/div[2]/div/div/div/div/ul[1]/li[2]/div[2]/div/span').click()
		window_before = self.driver.window_handles[0]
		self.driver.switch_to.window(window_before)
		time.sleep(5)
		self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[2]/div[1]/div/div/input').send_keys(
			kwargs['exchangereportsname'])
		time.sleep(2)
		Selectservice = self.driver.find_element_by_css_selector(
			"input[type='radio'][value='" + kwargs['value'] + "']").click()
		self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[2]/div[3]/div/div/div[2]/button').click()
		time.sleep(2)
		self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[2]/div[3]/div/div/div[2]/div/div/div/input').send_keys(
			kwargs['value2'])
		time.sleep(2)
		self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[2]/div[3]/div/div/div[2]/div/select/option[2]').click()
		"""INFO"""
		self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[2]/div[5]/div/div/textarea').send_keys(
			kwargs['info'])
		self.driver.execute_script("document.body.style.zoom='50%'")
		self.driver.save_screenshot("exchangereoprts1.png")
		self.driver.execute_script("document.body.style.zoom='100%'")
		"""submit"""
		self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div[3]/div/div[2]/form/div/div/button[1]').click()
		time.sleep(3)
		self.driver.execute_script("document.body.style.zoom='50%'")
		self.driver.save_screenshot("exchangereoprts2.png")
		self.driver.execute_script("document.body.style.zoom='100%'")
		return True

	def report_telephony_issue(self, kwargs):
		time.sleep(4)
		"""Catalog"""
		self.driver.find_element_by_xpath('/html/body/div/div/div/div/header/div/nav/ul[1]/li[3]/a').click()
		time.sleep(2)
		"""Clicking on Report Telephony Issue"""
		self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div/ui-view/ui-view/main/div[2]/div/div/div[2]/div/div/div/div/ul[1]/li[4]/div[2]/div/span').click()
		time.sleep(3)
		window_before = self.driver.window_handles[0]
		self.driver.switch_to.window(window_before)

		select_date = self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[2]/div/i')
		select_date.click()
		time.sleep(3)
		select_date.send_keys(Keys.DOWN)
		self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[2]/div/div/table/tbody/tr[6]/td[7]/button').click()

		report_issue = self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[1]/div/div/div[2]/button')
		report_issue.click()
		time.sleep(3)
		report_issue.send_keys(Keys.DOWN)
		self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[1]/div/div/div[2]/div/select/option[2]').click()

		problem = self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[2]/div/div/textarea')
		problem.send_keys('Demo Test')
		time.sleep(5)
		self.driver.execute_script("document.body.style.zoom='50%'")
		self.driver.save_screenshot("VPN1.png")
		self.driver.execute_script("document.body.style.zoom='100%'")

		sub = self.driver.find_element_by_xpath('html/body/div[1]/div/div/div[3]/div/div[2]/form/div/div/button[1]')
		sub.click()
		time.sleep(5)
		self.driver.execute_script("document.body.style.zoom='50%'")
		self.driver.save_screenshot("VPN2.png")
		self.driver.execute_script("document.body.style.zoom='100%'")

		return True

	def verify_srd_display_option_telephony_issue(self):
		time.sleep(3)
		men_menu = WebDriverWait(self.driver, 10).until(
			EC.visibility_of_element_located((By.XPATH, '//*[@id="toggle-my-profile-sub-menu"]')))
		ActionChains(self.driver).move_to_element(men_menu).perform()
		signout = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(
			(By.XPATH, "html/body/div[1]/div/div/div/header/div/nav/ul[1]/li[2]/ul/li[1]/a")))
		signout.click()
		time.sleep(3)
		self.driver.find_element_by_xpath(
			'/html/body/div/div/div/div/ui-view/main/div[2]/div[2]/div[2]/div[3]/div[1]/div/div/div[1]').click()
		time.sleep(3)
		data_list = []
		data_list.append(self.driver.find_element_by_xpath('html/body/div[1]/div/div/div[3]/div/div[2]/div[3]/h3').text)
		self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div[3]/div/div[2]/div[2]/h3').click()

		data_list.append(self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[1]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[2]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[3]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[4]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[5]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[6]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[7]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[8]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[9]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[10]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[11]/td[1]').text)

		self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div[1]/ins').click()
		logger.info("List = {}".format(data_list))

		def remove_cruft(s):
			return s[:-1]

		list1 = [remove_cruft(data_list) for data_list in data_list]
		logger.info("List1 = {}".format(list1))
		veri = False
		for i in list1:
			for k, v in BMCconstant.BMCContstants.Displayoption_Report_Telephony_issue.items():
				if i == k and v == ['True']:
					logger.info(k)
					logger.info(v)
					veri = True
				elif i == k and v == ['False']:
					logger.info(k)
					logger.info(v)
					return False
		return veri

	def print_service(self, kwargs):
		time.sleep(6)
		"""Catalog"""
		self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div/header/div/nav/ul[1]/li[3]/a').click()
		time.sleep(2)
		"""Clicking on Print Service"""
		self.driver.find_element_by_xpath(
			"/html/body/div[1]/div/div/div/ui-view/ui-view/main/div[1]/div/div/div[2]/div/div/div/div/ul[1]/li[4]/div[2]/div/span").click()
		time.sleep(3)
		window_before = self.driver.window_handles[0]
		self.driver.switch_to.window(window_before)

		select_date = self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[2]/div/i')
		select_date.click()
		time.sleep(3)
		select_date.send_keys(Keys.DOWN)
		self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[2]/div/div/table/tbody/tr[6]/td[7]/button').click()

		time.sleep(3)
		printer_type = self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[1]/div/div/div[2]/div[1]/label/input')
		printer_type.click()

		printer_issue = self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[2]/div/div/div[2]/button')
		printer_issue.click()
		time.sleep(3)
		printer_issue.send_keys(Keys.DOWN)
		self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[2]/div/div/div[2]/div/select/option[2]').click()

		problem = self.driver.find_element_by_xpath(
			'html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[3]/div/div/input')
		problem.send_keys('Demo Test')
		time.sleep(5)
		self.driver.execute_script("document.body.style.zoom='50%'")
		self.driver.save_screenshot("VPN1.png")
		self.driver.execute_script("document.body.style.zoom='100%'")

		sub = self.driver.find_element_by_xpath('html/body/div[1]/div/div/div[3]/div/div[2]/form/div/div/button[1]')
		sub.click()
		time.sleep(5)
		self.driver.execute_script("document.body.style.zoom='50%'")
		self.driver.save_screenshot("VPN2.png")
		self.driver.execute_script("document.body.style.zoom='100%'")

		return True

	def verify_SRD_menu(self, kwargs):
		try:
			self.login_bmc()
			submitbutton = False
			submitbutton = self.verify_srd_menu_submit(kwargs)
		except BaseException as be:
			logger.fatal("Fatal exception occured in verify_srd_menu_submit() in {}".format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.MyIt_logout()
			return submitbutton

	def verify_SRD_display_options(self):
		try:
			self.login_bmc()
			displayoption = False
			displayoption = self.verify_srd_display_option()
		except BaseException as be:
			logger.fatal("Fatal exception occured in verify_srd_menu_option() in {}".format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.MyIt_logout()
			return displayoption

	def verify_srd_Rebus_Passwordreset_display_option(self):
		time.sleep(3)
		men_menu = WebDriverWait(self.driver, 10).until(
			EC.visibility_of_element_located((By.XPATH, '//*[@id="toggle-my-profile-sub-menu"]')))
		ActionChains(self.driver).move_to_element(men_menu).perform()
		signout = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(
			(By.XPATH, "html/body/div[1]/div/div/div/header/div/nav/ul[1]/li[2]/ul/li[1]/a")))
		signout.click()
		time.sleep(3)
		time.sleep(3)
		self.driver.find_element_by_xpath(
			'/html/body/div/div/div/div/ui-view/main/div[2]/div[2]/div[2]/div[3]/div[1]/div/div/div[1]').click()
		time.sleep(3)
		self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div[3]/div/div[2]/div[2]/h3').click()
		data_list = []
		data_list.append(self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[1]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[2]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[3]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[4]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[5]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[6]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[7]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[8]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[9]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[10]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[11]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[12]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[13]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[14]/td[1]').text)
		self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div[1]/ins').click()
		print(data_list)

		def remove_cruft(s):
			return s[:-1]

		list1 = [remove_cruft(data_list) for data_list in data_list]
		print(list1)
		veri = False
		for i in list1:
			for k, v in BMCconstant.BMCContstants.DisplayoptionRebusPasswordreset.items():
				if i == k and v == ['True']:
					print(v)
					veri = True
				elif i == k and v == ['False']:
					print(v)
					return False
		return veri

	def verify_srd_Rebus_Orderasset_display_option(self):
		time.sleep(3)
		men_menu = WebDriverWait(self.driver, 10).until(
			EC.visibility_of_element_located((By.XPATH, '//*[@id="toggle-my-profile-sub-menu"]')))
		ActionChains(self.driver).move_to_element(men_menu).perform()
		signout = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(
			(By.XPATH, "html/body/div[1]/div/div/div/header/div/nav/ul[1]/li[2]/ul/li[1]/a")))
		signout.click()
		time.sleep(3)
		self.driver.find_element_by_xpath(
			'/html/body/div/div/div/div/ui-view/main/div[2]/div[2]/div[2]/div[3]/div[1]/div/div/div[1]').click()
		time.sleep(3)
		data_list = []
		data_list.append(self.driver.find_element_by_xpath('html/body/div[1]/div/div/div[3]/div/div[2]/div[3]/h3').text)
		self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div[3]/div/div[2]/div[3]').click()
		time.sleep(3)
		# data_list.append(self.driver.find_element_by_xpath('html/body/div[1]/div/div/div[3]/div/div[1]/div/div[2]/div[2]/span[2]').text)
		# data_list.append(self.driver.find_element_by_xpath('html/body/div[1]/div/div/div[3]/div/div[1]/div/div[2]/div[2]/span[3]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[1]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[2]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[3]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[4]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[5]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[6]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[7]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[8]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[9]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[10]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[11]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[12]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[13]/td[1]').text)
		data_list.append(self.driver.find_element_by_xpath(
			'/html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[14]/td[1]').text)
		# data_list.append(self.driver.find_element_by_xpath('html/body/div[1]/div/div/div[3]/div/div[1]/div/div[2]/div[2]/span[2]').text)

		self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div[1]/ins').click()
		print(data_list)
		print(BMCconstant.BMCContstants.Displayoptionorderasset)

		def remove_cruft(s):
			return s[:-1]

		list1 = [remove_cruft(data_list) for data_list in data_list]
		a = list1[0]
		a = "%ss" % a
		list1[0] = a
		print(list1)
		veri = False
		for i in list1:
			for k, v in BMCconstant.BMCContstants.Displayoptionorderasset.items():
				if i == k and v == ['True']:
					print(v)
					print(k)
					veri = True
				elif i == k and v == ['False']:
					print(v)
					return False
		return veri

	def verify_menu_options_in_the_SRD(self, kwargs):
		try:
			self.login_bmc()
			flag = False
			ques_details_list = self.reset_password(kwargs)

			"""Verifying list with BMCCconstant"""
			for i in ques_details_list:
				count = 0
				for k, v in BMCconstant.BMCContstants.QuestionDetails.items():
					if i != v:
						flag = False
					else:
						flag = True
						break
					count += 1

				if count == len(ques_details_list) and flag == False:
					flag = False
					break
			if flag == True:
				logger.info('The menu options mentioned in the SRD varified successfully')
		except BaseException as be:
			logger.fatal("Fatal exception occured in verify_menu_options_in_the_SRD() {}".format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.MyIt_logout()
			return flag

	def my_it_password_reset_fun(self):
		try:
			self.login_bmc()
			self.my_it_password_reset()
		except BaseException as be:
			logger.fatal("Fatal exception occured in my_it_password_reset_fun() in {}".format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.MyIt_logout()
			return

	def verify_srd_for_access_to_the_module_of_report_computer_issue(self, kwargs):
		try:
			self.login_bmc()
			submitbutton = False
			submitbutton = self.report_computer_issue(kwargs)
		except BaseException as be:
			logger.fatal(
				"Fatal exception occured in verify srd for access to the module of report computer issue() in {}".format(
					self.name))
			logger.error(traceback.print_exc())
		finally:
			self.MyIt_logout()
			return submitbutton

	def verify_srd_display_options_computer_issue(self):
		try:
			self.login_bmc()
			displayoption = False
			displayoption = self.verify_srd_display_option_computer_issue()
		except BaseException as be:
			logger.fatal(
				"Fatal exception occured in verify srd display options computer issue() in {}".format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.MyIt_logout()
			return displayoption

	def verify_srd_for_access_to_the_module_of_report_mobile_issue(self, kwargs):
		try:
			self.login_bmc()
			submitbutton = False
			submitbutton = self.report_mobile_issue(kwargs)
		except BaseException as be:
			logger.fatal(
				"Fatal exception occured in verify srd for access to the module of report mobile issue() in {}".format(
					self.name))
			logger.error(traceback.print_exc())
		finally:
			self.MyIt_logout()
			return submitbutton

	def verify_srd_display_options_mobile_issue(self):
		try:
			self.login_bmc()
			displayoption = False
			displayoption = self.verify_srd_display_option_mobile_issue()
		except BaseException as be:
			logger.fatal("Fatal exception occured in verify srd display options mobile issue() in {}".format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.MyIt_logout()
			return displayoption

	def verify_srd_for_access_to_the_module_of_retail_peripheral_issue(self, kwargs):
		try:
			self.login_bmc()
			submitbutton = False
			submitbutton = self.retail_peripheral_issue(kwargs)
		except BaseException as be:
			logger.fatal(
				"Fatal exception occured in verify srd for access to the module of retail peripheral issue() in {}".format(
					self.name))
			logger.error(traceback.print_exc())
		finally:
			self.MyIt_logout()
			return submitbutton

	def verify_srd_display_options_retail_peripheral_issue(self):
		try:
			self.login_bmc()
			displayoption = False
			displayoption = self.verify_srd_display_option_retail_peripheral_issue()
		except BaseException as be:
			logger.fatal("Fatal exception occured in verify srd display options retail peripheral issue() in {}".format(
				self.name))
			logger.error(traceback.print_exc())
		finally:
			self.MyIt_logout()
			return displayoption

	def verify_srd_for_access_to_the_module_of_report_telephony_issue(self, kwargs):
		try:
			self.login_bmc()
			submitbutton = False
			submitbutton = self.report_telephony_issue(kwargs)
		except BaseException as be:
			logger.fatal(
				"Fatal exception occured in verify srd for access to the module of report telephony issue() in {}".format(
					self.name))
			logger.error(traceback.print_exc())
		finally:
			self.MyIt_logout()
			return submitbutton

	def verify_srd_display_options_telephony_issue(self):
		try:
			self.login_bmc()
			displayoption = False
			displayoption = self.verify_srd_display_option_telephony_issue()
		except BaseException as be:
			logger.fatal(
				"Fatal exception occured in verify srd display options telephony issue() in {}".format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.MyIt_logout()
			return displayoption

	def verify_srd_for_access_to_the_module_of_print_service(self, kwargs):
		try:
			self.login_bmc()
			submitbutton = False
			submitbutton = self.print_service(kwargs)
		except BaseException as be:
			logger.fatal(
				"Fatal exception occured in verify srd for access to the module of print service() in {}".format(
					self.name))
			logger.error(traceback.print_exc())
		finally:
			self.MyIt_logout()
			return submitbutton

	def verify_SRD_Rebus_passwordreset_menu(self, kwargs):
		try:
			self.login_bmc()
			submitbutton = False
			submitbutton = self.verify_srd_Rebus_passwordreset_menu_submit(kwargs)
		except BaseException as be:
			logger.fatal("Fatal exception occured in verify_srd_menu_submit() in {}".format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.MyIt_logout()
			return submitbutton

	def verify_SRD_Rebus_orderasset_menu(self, kwargs):
		try:
			self.login_bmc()
			submitbutton = False
			submitbutton = self.verify_srd_Rebus_orderasset_menu_submit(kwargs)
		except BaseException as be:
			logger.fatal("Fatal exception occured in verify_srd_menu_submit() in {}".format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.MyIt_logout()
			return submitbutton

	def verify_SRD_Rebus_BSM_menu(self, kwargs):
		try:
			self.login_bmc()
			submitbutton = False
			submitbutton = self.verify_srd_Rebus_BSM_menu_submit(kwargs)
		except BaseException as be:
			logger.fatal("Fatal exception occured in verify_srd_menu_submit() in {}".format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.MyIt_logout()
			return submitbutton

	def verify_SRD_Rebus_Mobiledeviceacc_menu(self, kwargs):
		try:
			self.login_bmc()
			submitbutton = False
			submitbutton = self.verify_srd_Rebus_Mobiledeviceacc_menu_submit(kwargs)
		except BaseException as be:
			logger.fatal("Fatal exception occured in verify_srd_menu_submit() in {}".format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.MyIt_logout()
			return submitbutton

	def verify_SRD_Rebus_VPN_menu(self, kwargs):
		try:
			self.login_bmc()
			submitbutton = False
			submitbutton = self.verify_srd_Rebus_VPN_menu_submit(kwargs)
		except BaseException as be:
			logger.fatal("Fatal exception occured in verify_srd_menu_submit() in {}".format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.MyIt_logout()
			return submitbutton

	def verify_SRD_Rebus_reportemailissue_menu(self, kwargs):
		try:
			self.login_bmc()
			submitbutton = False
			submitbutton = self.verify_srd_Rebus_reportemailissue_menu_submit(kwargs)
		except BaseException as be:
			logger.fatal("Fatal exception occured in verify_srd_menu_submit() in {}".format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.MyIt_logout()
			return submitbutton

	def verify_SRD_Rebus_exchangerequest_menu(self, kwargs):
		try:
			self.login_bmc()
			submitbutton = False
			submitbutton = self.verify_srd_Rebus_exchangerequest_menu_submit(kwargs)
		except BaseException as be:
			logger.fatal("Fatal exception occured in verify_srd_menu_submit() in {}".format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.MyIt_logout()
			return submitbutton

	def verify_SRD_Rebus_Orderasset_display_options(self):
		try:
			self.login_bmc()
			displayoption = False
			displayoption = self.verify_srd_Rebus_Orderasset_display_option()
		except BaseException as be:
			logger.fatal("Fatal exception occured in verify_srd_menu_option() in {}".format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.MyIt_logout()
			return displayoption

	def verify_SRD_Rebus_Passwordreset_display_options(self):
		try:
			self.login_bmc()
			displayoption = False
			displayoption = self.verify_srd_Rebus_Passwordreset_display_option()
		except BaseException as be:
			logger.fatal("Fatal exception occured in verify_srd_menu_option() in {}".format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.MyIt_logout()
			return displayoption