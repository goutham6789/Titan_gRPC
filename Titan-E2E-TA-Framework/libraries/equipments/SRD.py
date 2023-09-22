import logging as logger
from equipments.Vmm import Vmm
from bmc.BmcError import BmcError
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
from time import gmtime, strftime
from suds.client import Client
from suds.sax.element import Element
import datetime
import re
import traceback
import BMCconstant
#comment

class BmcSRD(Vmm):
	"""Virtual machine manager"""
	
	def __init__(self, name, **kwargs):
		self.plmns = []
		self.driver = ''
		self.parent_win = ''
		Vmm.__init__(self, name, **kwargs)
	
	def login_bmc(self):
		try:
			logger.info("executing login_bmc()")
			self.driver = webdriver.Chrome()
			self.driver.implicitly_wait(50)
			self.driver.get(self.loginurl)
			self.driver.maximize_window()
			
			username = self.driver.find_element_by_xpath('/html/body/div/div/form/div[2]/div/label/input')
			password = self.driver.find_element_by_xpath('//*[@id="login_user_password"]')
			login = self.driver.find_element_by_xpath('//*[@id="login-jsp-btn"]')
			
			username.send_keys(self.username)
			password.send_keys(self.password)
			login.click()
			self.verify_popup()
			
			time.sleep(30)
			logger.info("successfully logged in")
			logger.info("Exiting login_bmc()")
			
			# global parent_win
			self.parent_win = self.driver.window_handles[0]
		
		except BaseException as be:
			logger.fatal(
				"Fatal exception {} occurred inside login_bmc() while logging in to BMC {}".format(be, self.name))
			logger.error(traceback.print_exc())
			self.driver.quit()
	
	def set_authorization_header(self):
		try:
			logger.info("executing login_bmcMyIT()")
			url = self.loginurl
			# url = "https://threeuk-qa.onbmc.com/arsys/WSDL/public/onbmc-s/H3G_SA_SM_HPD_IncidentInterface_Staging_WS"
			client = Client(url)
			uname = self.username
			passw = self.password
			# username = Element('xsi:userName').setText("amkundu")
			# password = Element('xsi:password').setText("Password@123")
			username = Element('xsi:userName').setText(uname)
			password = Element('xsi:password').setText(passw)
			ssnp = Element("xsi:AuthenticationInfo").append(username).append(password)
			client.set_options(soapheaders=ssnp)
			logger.info("successfully logged in")
			logger.info("Exiting login_bmcsoap()")
			return client
		
		except BaseException as be:
			
			logger.fatal(
				"Fatal exception {} occurred inside login_bmc() while logging in to BMC {}".format(be, self.name))
			logger.error(traceback.print_exc())
	
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
	
	def bmc_logout(self):
		try:
			logger.info("Executing bmc_logout()")
			self.driver.switch_to.window(self.parent_win)
			time.sleep(5)
			logout = self.driver.find_element_by_link_text('Logout')
			logout.send_keys('\n')
			time.sleep(10)
			logout_message = self.driver.find_element(By.XPATH, "/html[1]/body[1]").text
			logger.info(logout_message)
			if logout_message == "You are logged out from BMC Remedy Single Sign-On":
				self.driver.quit()
			else:
				logger.info("Log out was unsuccessful")
			logger.info("Exiting bmc_logout()")
		except BaseException:
			logger.fatal("Fatal exception occurred inside logout_bmc() while logging in to BMC {}".format(self.name))
			logger.error(traceback.print_exc())
			self.driver.quit()
	
	def password_reset_main(self, work_notes):
		"""Appication"""
		self.driver.find_element_by_xpath('//*[@id="reg_img_304316340"]').click()
		self.driver.find_element_by_link_text('Service Request Management').click()
		self.driver.find_element_by_link_text('Work Order Console').click()
		
		time.sleep(2)
		"""Searching work order"""
		self.driver.find_element_by_xpath('//*[@id="sub-301626300"]/div[2]/span').click()
		time.sleep(3)
		"""Enter Summary"""
		summary_obj = self.driver.find_element_by_xpath('//*[@id="arid_WIN_4_1000000000"]')
		summary_obj.click()
		summary_obj.send_keys("Password Reset")  # 'Password Reset'
		
		"""Search the work"""
		self.driver.find_element_by_xpath('//*[@id="WIN_4_1002"]/div/div').click()
		time.sleep(2)
		
		"""Open the work by double click on that"""
		double_click_obj = self.driver.find_element_by_xpath('//*[@id="T1020"]/tbody/tr[2]/td[3]/nobr')
		action = ActionChains(self.driver)
		action.double_click(double_click_obj).perform()
		
		"""Switching to opened window"""
		window1 = self.driver.window_handles[1]
		self.driver.switch_to.window(window1)
		time.sleep(3)
		
		"""Type work info and add"""
		type_work_info = self.driver.find_element(By.ID, "arid_WIN_1_304247080")
		add_button = self.driver.find_element(By.XPATH, '//*[@id="WIN_1_304250790"]/div/div')
		add_button.click()
		add_button.click()
		type_work_info.send_keys(work_notes)
		add_button.click()
		time.sleep(3)
		
		"""Navigation to categorization tab and validation of parameters"""
		categorization_tab = self.driver.find_element(By.XPATH, "//a[contains(text(),'Categorization')]")
		categorization_tab.click()
		categorization_parameters = []
		company = self.driver.find_element(By.XPATH, '//*[@id="arid_WIN_1_1000000001"]').get_attribute('value')
		tier1 = self.driver.find_element(By.XPATH, '//*[@id="arid_WIN_1_1000000063"]').get_attribute('value')
		tier2 = self.driver.find_element(By.XPATH, '//*[@id="arid_WIN_1_1000000064"]').get_attribute('value')
		tier3 = self.driver.find_element(By.XPATH, '//*[@id="arid_WIN_1_1000000065"]').get_attribute('value')
		tier11 = self.driver.find_element(By.XPATH, '//*[@id="arid_WIN_1_1000001270"]').get_attribute('value')
		tier22 = self.driver.find_element(By.XPATH, '//*[@id="arid_WIN_1_1000001271"]').get_attribute('value')
		tier33 = self.driver.find_element(By.XPATH, '//*[@id="arid_WIN_1_1000001272"]').get_attribute('value')
		product_name = self.driver.find_element(By.XPATH, '//*[@id="arid_WIN_1_1000002268"]').get_attribute('value')
		categorization_parameters.append(company)
		categorization_parameters.append(tier1)
		categorization_parameters.append(tier2)
		categorization_parameters.append(tier3)
		categorization_parameters.append(tier11)
		categorization_parameters.append(tier22)
		categorization_parameters.append(tier33)
		categorization_parameters.append(product_name)
		if categorization_parameters != BMCconstant.BMCContstants.Categorization_parameters_list:
			logger.error("The categorzation parameters are mismatched")
			flag1 = False
		else:
			logger.info("Categorization parameters were matched.")
			flag1 = True
		
		"""Detail Tab"""
		detail_tab = self.driver.find_element(By.XPATH,
		                                      '//*[@id="WIN_1_301389366"]/div[2]/div[2]/div/dl/dd[5]/span[2]/a')
		detail_tab.click()
		requirement = self.driver.find_element(By.XPATH, '//*[@id="arid_WIN_1_300070001"]').get_attribute('vlaue')
		username = self.driver.find_element(By.XPATH, '//*[@id="arid_WIN_1_300070002"]').get_attribute('value')
		password = self.driver.find_element(By.XPATH, '//*[@id="arid_WIN_1_300070003"]').get_attribute('value')
		email = self.driver.find_element(By.XPATH, '//*[@id="arid_WIN_1_300070004"]').get_attribute('value')
		if requirement != "Password Reset" and username == '' and password == '' and email == '':
			logger.error("Details are not matched")
			flag2 = False
		else:
			logger.info("All the details were checked and found correct")
			flag2 = True
		
		"""Status"""
		status = self.driver.find_element(By.XPATH, "//div[@id='WIN_1_7']//a[@class='btn btn3d selectionbtn']")
		status.click()
		time.sleep(3)
		status.send_keys(Keys.ARROW_DOWN)
		time.sleep(3)
		status.send_keys("P")
		status.send_keys(Keys.ENTER)
		time.sleep(3)
		save_button = self.driver.find_element(By.XPATH, '//*[@id="WIN_1_300000300"]/div/div')
		save_button.click()
		time.sleep(2)
		logger.info("Status: Pending")
		
		"""status - In Progress"""
		status.click()
		time.sleep(3)
		status.send_keys(Keys.ARROW_DOWN)
		time.sleep(3)
		status.send_keys(Keys.ARROW_DOWN)
		time.sleep(3)
		status.send_keys(Keys.ARROW_DOWN)
		time.sleep(3)
		status.send_keys(Keys.ARROW_DOWN)
		time.sleep(3)
		status.send_keys(Keys.ARROW_DOWN)
		time.sleep(3)
		# status.send_keys("I")
		status.send_keys(Keys.ENTER)
		time.sleep(3)
		save_button.click()
		time.sleep(2)
		logger.info("Status: In Progress")
		
		"""status - Completed"""
		status.click()
		time.sleep(3)
		status.send_keys(Keys.ARROW_DOWN)
		time.sleep(3)
		status.send_keys(Keys.ARROW_DOWN)
		time.sleep(3)
		status.send_keys(Keys.ARROW_DOWN)
		time.sleep(3)
		status.send_keys(Keys.ARROW_DOWN)
		time.sleep(3)
		status.send_keys(Keys.ARROW_DOWN)
		time.sleep(3)
		status.send_keys(Keys.ARROW_DOWN)
		time.sleep(3)
		# status.send_keys("C")
		status.send_keys(Keys.ENTER)
		time.sleep(3)
		save_button.click()
		logger.info("Status is completed")
		time.sleep(2)
		return flag1, flag2
	
	def password_reset(self, work_notes):
		try:
			self.login_bmc()
			flag, verify = self.password_reset_main(work_notes)
		except BaseException as be:
			logger.fatal("Fatal exception occured in password_reset_request() in {}".format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.bmc_logout()
			if not verify:
				raise BmcError("Validation Failed")
			return flag