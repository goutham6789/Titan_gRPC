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


class BmcChangeManagement(Vmm):
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
	
	def verify_create_change_and_search_change(self, kwargs):
		WebDriverWait(self.driver, 50).until(
			expected_conditions.presence_of_element_located((By.XPATH, '//*[@id="reg_img_304316340"]')))

		self.driver.find_element_by_xpath('//*[@id="reg_img_304316340"]').click()  # Appliacation
		time.sleep(2)
		self.driver.find_element_by_link_text('Change Management').click()  # Change
		time.sleep(2)
		self.driver.find_element_by_link_text('Change Management Console').click()
		time.sleep(3)
		self.driver.find_element_by_xpath('//*[@id="sub-301626300"]/div[1]/span').click()  # Created new Change-
		time.sleep(2)
		change_id = self.driver.find_element_by_xpath('//*[@id="WIN_0_304248710"]/fieldset/div/dl/dd[5]/span[2]/a').text
		change_id = change_id[:-06]
		time.sleep(2)

		"""Filling and Submitting Incident Creation Form"""

		"""Filling service+"""
		WebDriverWait(self.driver, 50).until(
			expected_conditions.presence_of_element_located((By.XPATH, '//*[@id="arid_WIN_4_303497300"]')))

		service = self.driver.find_element_by_xpath('//*[@id="arid_WIN_4_303497300"]')
		service.click()
		service.send_keys(kwargs['Service'])
		time.sleep(2)
		service.send_keys(Keys.DOWN)
		service.send_keys(Keys.ENTER)

		"""Filling Summary"""
		WebDriverWait(self.driver, 50).until(
			expected_conditions.presence_of_element_located((By.XPATH, '//*[@id="arid_WIN_4_1000000000"]')))
		summary = self.driver.find_element_by_xpath('//*[@id="arid_WIN_4_1000000000"]')
		summary.send_keys(kwargs['Summary'])#This is sample

		"""Filling Class"""
		WebDriverWait(self.driver, 50).until(
			expected_conditions.presence_of_element_located((By.XPATH, '//*[@id="arid_WIN_4_1000000568"]')))
		class_var = self.driver.find_element_by_xpath('//*[@id="arid_WIN_4_1000000568"]')#class_var = self.driver.find_element_by_xpath('/html/body/div[3]/div[2]/table/tbody/tr[3]/td[1]')# Latent
		class_var.click()
		class_var.send_keys(Keys.DOWN)
		class_var.send_keys(kwargs['class_value'])
		class_var.send_keys(Keys.ENTER)


		"""window_index[1]"""
		time.sleep(3)
		window_before = self.driver.window_handles[1]
		self.driver.switch_to.window(window_before)
		time.sleep(2)

		"""YES"""
		WebDriverWait(self.driver, 50).until(
			expected_conditions.presence_of_element_located((By.XPATH, '//*[@id="WIN_0_302180500"]/div/div')))

		self.driver.find_element_by_xpath('//*[@id="WIN_0_302180500"]/div/div').click()

		"""window_index[0]"""
		time.sleep(2)
		window_after = self.driver.window_handles[0]
		self.driver.switch_to.window(window_after)

		'''Filling Manager Group'''
		WebDriverWait(self.driver, 50).until(
			expected_conditions.presence_of_element_located((By.XPATH, '//*[@id="arid_WIN_4_1000000015"]')))

		mngr = self.driver.find_element_by_xpath('//*[@id="arid_WIN_4_1000000015"]')
		mngr.send_keys(kwargs['Manager'])#CHN_Bill Fulfillment
		time.sleep(2)
		mngr.send_keys(Keys.DOWN)
		mngr.send_keys(Keys.ENTER)

		"""Add change manager"""
		WebDriverWait(self.driver, 50).until(
			expected_conditions.presence_of_element_located((By.XPATH, '//*[@id="arid_WIN_4_1000000403"]')))

		mngr = self.driver.find_element_by_xpath('//*[@id="arid_WIN_4_1000000403"]')
		mngr.send_keys(kwargs['Change_mang'])
		time.sleep(2)
		mngr.send_keys(Keys.DOWN)
		mngr.send_keys(Keys.ENTER)

		'''Add work info'''
		WebDriverWait(self.driver, 50).until(
			expected_conditions.presence_of_element_located((By.XPATH, '//*[@id="arid_WIN_4_304247080"]')))

		work_info = self.driver.find_element_by_xpath('//*[@id="arid_WIN_4_304247080"]')  # add work info
		work_info.send_keys(kwargs['Work'])#Sample work info

		'''Click - Add'''
		WebDriverWait(self.driver, 50).until(
			expected_conditions.presence_of_element_located((By.XPATH, '//*[@id="WIN_4_304247110"]/div/div')))

		self.driver.find_element_by_xpath('//*[@id="WIN_4_304247110"]/div/div').click()

		"""Date/System"""
		WebDriverWait(self.driver, 50).until(
			expected_conditions.presence_of_element_located((By.XPATH, '//*[@id="WIN_4_303868800"]/div[2]/div[2]/div/dl/dd[5]/span[2]/a')))

		self.driver.find_element_by_xpath('//*[@id="WIN_4_303868800"]/div[2]/div[2]/div/dl/dd[5]/span[2]/a').click()

		"""Actual Start/End date"""
		WebDriverWait(self.driver, 50).until(
			expected_conditions.presence_of_element_located((By.XPATH, '//*[@id="arid_WIN_4_1000000348"]')))

		str_date = self.driver.find_element_by_xpath('//*[@id="arid_WIN_4_1000000348"]')  # start
		str_date.send_keys(kwargs['startdate'])#'01/09/2018 00:00:00'

		end_date = self.driver.find_element_by_xpath('//*[@id="arid_WIN_4_1000000364"]')  # end
		end_date.send_keys(kwargs['enddate'])#'05/09/2018 00:00:00'

		"""Click - save"""
		WebDriverWait(self.driver, 50).until(
			expected_conditions.presence_of_element_located((By.XPATH, '//*[@id="WIN_4_1001"]/div/div')))

		self.driver.find_element_by_xpath('//*[@id="WIN_4_1001"]/div/div').click()

		"""Click on serach image"""
		WebDriverWait(self.driver, 50).until(
			expected_conditions.element_to_be_clickable((By.XPATH, '//*[@id="WIN_0_304276710"]/div')))
		enter_id = self.driver.find_element_by_xpath('//*[@id="WIN_0_304276710"]/div')
		time.sleep(10)
		enter_id.click()

		"""Filling Change ID"""
		WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH, '//*[@id="arid_WIN_6_1000000182"]')))
		enter_id = self.driver.find_element_by_xpath('//*[@id="arid_WIN_6_1000000182"]')

		time.sleep(1)
		enter_id.send_keys(change_id)  # change id enter

		"""Then search"""
		WebDriverWait(self.driver, 50).until(
			expected_conditions.element_to_be_clickable((By.XPATH, '//*[@id="WIN_6_1002"]/div/div')))
		obj = self.driver.find_element_by_xpath('//*[@id="WIN_6_1002"]/div/div')  # search button
		time.sleep(1)
		obj.click()

		"""Approving"""
		WebDriverWait(self.driver, 50).until(
			expected_conditions.element_to_be_clickable((By.XPATH, '//*[@id="WIN_6_301899300"]/div[1]')))
		app = self.driver.find_element_by_xpath('//*[@id="WIN_6_301899300"]/div[1]')
		time.sleep(3)
		app.click()

		return change_id
	
	def search_change_for_second_approval(self, change_id):
		"""Appliaction"""
		WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH, '//*[@id="reg_img_304316340"]')))
		self.driver.find_element_by_xpath('//*[@id="reg_img_304316340"]').click()#Appliacation

		WebDriverWait(self.driver, 50).until(
			expected_conditions.element_to_be_clickable((By.LINK_TEXT, 'Change Management')))

		self.driver.find_element_by_link_text('Change Management').click()  # Change

		WebDriverWait(self.driver, 50).until(
			expected_conditions.element_to_be_clickable((By.LINK_TEXT, 'Search Change')))
		self.driver.find_element_by_link_text('Search Change').click()  # Search Change

		"""Change ID"""
		WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH, '//*[@id="arid_WIN_3_1000000182"]')))
		enter_id = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_1000000182"]')
		enter_id.send_keys(change_id)  # change id enter

		"""Then search"""
		WebDriverWait(self.driver, 50).until(
			expected_conditions.element_to_be_clickable((By.XPATH, '//*[@id="WIN_3_1002"]/div/div')))
		obj = self.driver.find_element_by_xpath('//*[@id="WIN_3_1002"]/div/div')  # search button
		time.sleep(1)
		obj.click()

		"""Approving"""
		WebDriverWait(self.driver, 50).until(
			expected_conditions.element_to_be_clickable((By.XPATH, '//*[@id="WIN_3_301899300"]/div[2]/div')))
		app = self.driver.find_element_by_xpath('//*[@id="WIN_3_301899300"]/div[2]/div')
		time.sleep(3)
		app.click()

		return True
	
	def verify_search_change_id_for_next_stage(self, change_id):

		WebDriverWait(self.driver, 50).until(
			expected_conditions.presence_of_element_located((By.XPATH, '//*[@id="reg_img_304316340"]')))

		self.driver.find_element_by_xpath('//*[@id="reg_img_304316340"]').click()  # Appliacation

		WebDriverWait(self.driver, 50).until(
			expected_conditions.element_to_be_clickable((By.LINK_TEXT, 'Change Management')))
		self.driver.find_element_by_link_text('Change Management').click()  # Change

		WebDriverWait(self.driver, 50).until(
			expected_conditions.element_to_be_clickable((By.LINK_TEXT, 'Search Change')))
		self.driver.find_element_by_link_text('Search Change').click()  # Search Change

		"""Change ID"""
		WebDriverWait(self.driver, 50).until(
			expected_conditions.element_to_be_clickable((By.XPATH, '//*[@id="arid_WIN_3_1000000182"]')))
		enter_id = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_1000000182"]')
		enter_id.send_keys(change_id)  # change id enter

		"""Then search"""
		WebDriverWait(self.driver, 50).until(
			expected_conditions.element_to_be_clickable((By.XPATH, '//*[@id="WIN_3_1002"]/div/div')))
		obj = self.driver.find_element_by_xpath('//*[@id="WIN_3_1002"]/div/div')  # search button
		time.sleep(1)
		obj.click()

		"""Next stage"""
		WebDriverWait(self.driver, 50).until(
			expected_conditions.element_to_be_clickable((By.XPATH, '//*[@id="WIN_3_301542200"]/a')))
		obj = self.driver.find_element_by_xpath('//*[@id="WIN_3_301542200"]/a')  # search button
		time.sleep(1)
		obj.click()

		WebDriverWait(self.driver, 50).until(
			expected_conditions.element_to_be_clickable((By.XPATH, '/html/body/div[4]/div[2]/table/tbody/tr[1]/td[1]')))
		obj = self.driver.find_element_by_xpath('/html/body/div[4]/div[2]/table/tbody/tr[1]/td[1]')  # search button
		time.sleep(1)
		obj.click()

		"""To validate getting value of Disabled field"""
		WebDriverWait(self.driver, 50).until(
			expected_conditions.element_to_be_clickable((By.XPATH, '//*[@id="arid_WIN_3_303502600"]')))

		status_obj = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_303502600"]')
		time.sleep(2)
		status_str = status_obj.get_attribute('value')

		if (status_str == "Closed"):
			logger.info("Change ID: {} has successfully Closed".format(change_id))
			return True

		return False
	
	def verify_risk_assessments_change_tickets(self, kwargs):

		"""clicking on Applications"""
		logger.info("click on Application")
		application = self.driver.find_element_by_xpath('//*[@id="reg_img_304316340"]')
		application.click()
		time.sleep(6)

		"""clicking on Change Management"""
		logger.info("click on change management console")
		change_management = self.driver.find_element_by_link_text('Change Management')
		change_management.click()
		time.sleep(2)

		"""clicking on New Change"""
		logger.info("click on new change")
		newchange = self.driver.find_element_by_link_text('New Change')
		newchange.click()
		time.sleep(4)

		"""selection of assessments questions image"""
		logger.info("click on Assessments questions image")
		window_before = self.driver.window_handles[0]
		assessments = self.driver.find_element_by_xpath('//*[@id="reg_img_301346600"]')
		assessments.click()
		WebDriverWait(self.driver, 10).until(expected_conditions.number_of_windows_to_be(2))
		window_after = self.driver.window_handles[1]
		self.driver.switch_to.window(window_after)

		"""Screen shot taken"""
		self.driver.get_screenshot_as_file('D:\git\November192018\Screenshots\quesscreenshots1.png')

		"""select xpath for 1st question"""
		logger.info("collecting the xpaths for the questions from 1 to 5")
		quesa = self.driver.find_element_by_xpath('//*[@id="arid_WIN_0_300994800"]')
		valuea = quesa.get_attribute('value')
		logger.info("question1 =  {}".format(valuea))

		logger.info("xpath collected for 1st question")

		"""select xpath for 2nd question"""
		quesb = self.driver.find_element_by_xpath('//*[@id="arid_WIN_0_301018600"]')
		valueb = quesb.get_attribute('value')
		logger.info("Question2 =  {}".format(valueb))

		logger.info("xpath collected for 2nd question")

		"""select xpath for 3rd question"""
		quesc = self.driver.find_element_by_xpath('//*[@id="arid_WIN_0_301028400"]')
		valuec = quesc.get_attribute('value')
		logger.info("Question3 =  {}".format(valuec))

		logger.info("xpath collected for 3rd question")

		"""select xpath for 4th question"""
		quesd = self.driver.find_element_by_xpath('//*[@id="arid_WIN_0_301876300"]')
		valued = quesd.get_attribute('value')
		logger.info("Question4 =  {}".format(valued))

		logger.info("xpath collected for 4th question")

		"""select xpath for 5th question"""
		quese = self.driver.find_element_by_xpath('//*[@id="arid_WIN_0_301877000"]')
		valuee = quese.get_attribute('value')
		logger.info("Question5 =  {}".format(valuee))

		logger.info("xpath collected for 5th question")

		logger.info("Select the drop down menu")

		drop_a = self.driver.find_element_by_xpath('//*[@id="WIN_0_300996200"]/a/img')
		drop_a.click()
		time.sleep(4)

		logger.info("select the answer from the list")
		ans_a = self.driver.find_element_by_xpath('/html/body/div[3]/div[2]/table/tbody/tr[1]/td[1]')
		ans_a.click()

		"""similarly do it upto 5th questions"""
		drop_b = self.driver.find_element_by_xpath('//*[@id="WIN_0_301019100"]/a/img')
		drop_b.click()
		time.sleep(4)
		ans_b = self.driver.find_element_by_xpath('/html/body/div[3]/div[2]/table/tbody/tr[2]/td[1]')
		ans_b.click()

		drop_c = self.driver.find_element_by_xpath('//*[@id="WIN_0_301029000"]/a/img')
		drop_c.click()
		time.sleep(4)
		ans_c = self.driver.find_element_by_xpath('/html/body/div[3]/div[2]/table/tbody/tr[1]/td[1]')
		ans_c.click()

		drop_d = self.driver.find_element_by_xpath('//*[@id="WIN_0_301876200"]/a/img')
		drop_d.click()
		time.sleep(4)
		ans_d = self.driver.find_element_by_xpath('/html/body/div[3]/div[2]/table/tbody/tr[1]/td[1]')
		ans_d.click()

		drop_e = self.driver.find_element_by_xpath('//*[@id="WIN_0_301876900"]/a/img')
		drop_e.click()
		time.sleep(4)
		ans_e = self.driver.find_element_by_xpath('/html/body/div[3]/div[2]/table/tbody/tr[1]/td[1]')
		ans_e.click()

		"""clicking on Next button"""
		logger.info("click on next button")
		next_button = self.driver.find_element_by_xpath('//*[@id="WIN_0_300994900"]/div/div')
		next_button.click()
		time.sleep(4)

		"""Screen shot taken"""
		self.driver.get_screenshot_as_file('D:\git\November192018\Screenshots\quesscreenshots2.png')

		logger.info("Collecting xpaths for the questions from 6 to 10")
		"""select xpath for 6th question"""
		quesf = self.driver.find_element_by_xpath('//*[@id="arid_WIN_0_300994800"]')
		valuef = quesf.get_attribute('value')
		logger.info("Question6 =  {}".format(valuef))
		logger.info("xpath collected for question6")

		"""select xpath for 7th question"""
		quesg = self.driver.find_element_by_xpath('//*[@id="arid_WIN_0_301018600"]')
		valueg = quesg.get_attribute('value')
		logger.info("Question7 =  {}".format(valueg))
		logger.info("xpath collected for question7")

		"""select xpath for 8th question"""
		quesh = self.driver.find_element_by_xpath('//*[@id="arid_WIN_0_301028400"]')
		valueh = quesh.get_attribute('value')
		logger.info("Question8 =  {}".format(valueh))
		logger.info("xpath collected for question8")

		"""select xpath for 9th question"""
		quesi = self.driver.find_element_by_xpath('//*[@id="arid_WIN_0_301876300"]')
		valuei = quesi.get_attribute('value')
		logger.info("Question9 =  {}".format(valuei))
		logger.info("xpath collected for question9")

		"""select xpath for 10th question"""
		quesj = self.driver.find_element_by_xpath('//*[@id="arid_WIN_0_301877000"]')
		valuej = quesj.get_attribute('value')
		logger.info("Question10 =  {}".format(valuej))
		logger.info("xpath collected for question10")

		"""select the answers for remaining questions"""

		drop_f = self.driver.find_element_by_xpath('//*[@id="WIN_0_300996200"]/a/img')
		drop_f.click()
		time.sleep(4)
		ans_f = self.driver.find_element_by_xpath('/html/body/div[3]/div[2]/table/tbody/tr[1]/td[1]')
		ans_f.click()

		drop_g = self.driver.find_element_by_xpath('//*[@id="WIN_0_301019100"]/a/img')
		drop_g.click()
		time.sleep(4)
		ans_g = self.driver.find_element_by_xpath('/html/body/div[3]/div[2]/table/tbody/tr[2]/td[1]')
		ans_g.click()

		drop_h = self.driver.find_element_by_xpath('//*[@id="WIN_0_301029000"]/a/img')
		drop_h.click()
		time.sleep(4)
		ans_h = self.driver.find_element_by_xpath('/html/body/div[3]/div[2]/table/tbody/tr[2]/td[1]')
		ans_h.click()

		drop_i = self.driver.find_element_by_xpath('//*[@id="WIN_0_301876200"]/a/img')
		drop_i.click()
		time.sleep(4)
		ans_i = self.driver.find_element_by_xpath('/html/body/div[3]/div[2]/table/tbody/tr[2]/td[1]')
		ans_i.click()

		drop_j = self.driver.find_element_by_xpath('//*[@id="WIN_0_301876900"]/a/img')
		drop_j.click()
		time.sleep(4)
		ans_j = self.driver.find_element_by_xpath('/html/body/div[3]/div[2]/table/tbody/tr[1]/td[1]')
		ans_j.click()

		"""click on save button"""
		save_button = self.driver.find_element_by_xpath('//*[@id="WIN_0_300994900"]/div/div')
		save_button.click()
		time.sleep(4)
		logger.info(" changes has been saved successfully")

		"""Verification of Risk asssessments questions"""
		string = list()
		if valuea != kwargs['questiona']:
			string.append(1)

		if valueb != kwargs['questionb']:
			string.append(2)

		if valuec != kwargs['questionc']:
			string.append(3)

		if valued != kwargs['questiond']:
			string.append(4)

		if valuee != kwargs['questione']:
			string.append(5)

		if valuef != kwargs['questionf']:
			string.append(6)

		if valueg != kwargs['questiong']:
			string.append(7)

		if valueh != kwargs['questionh']:
			string.append(8)

		if valuei != kwargs['questioni']:
			string.append(9)

		if valuej != kwargs['questionj']:
			string.append(10)

		if len(string) == 0:
			logger.info("All the risk assessments questions verified successfully")
			return True
		else:
			logger.info("The incorrect questions are =  {} ".format(string))
		return False
	
	def identification_of_affected_CIs(self, kwargs):
		"""clicking on Applications"""
		logger.info("click on Application")
		application = self.driver.find_element_by_xpath('//*[@id="reg_img_304316340"]')
		application.click()
		time.sleep(6)

		"""clicking on Change Management"""
		logger.info("click on change management console")
		change_management = self.driver.find_element_by_link_text('Change Management')
		change_management.click()
		time.sleep(2)

		"""clicking on New Change"""
		logger.info("click on new change")
		newchange = self.driver.find_element_by_link_text('New Change')
		newchange.click()
		time.sleep(20)

		"""Filling and Submitting Incident Creation Form"""

		'''Filling Service'''
		logger.info("filling service field")
		service = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_303497300"]')
		service.click()
		service.send_keys(kwargs['Service'])
		time.sleep(3)
		service.send_keys(Keys.DOWN)
		service.send_keys(Keys.ENTER)

		"""Filling Summary"""
		summary = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_1000000000"]')
		summary.send_keys(kwargs['Summary'])  # This is sample
		logger.info(" summary filled")

		'''Filling Manager Group'''
		mngr = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_1000000015"]')
		mngr.send_keys(kwargs['Manager'])  # Three Service Desk
		time.sleep(2)
		mngr.send_keys(Keys.DOWN)
		mngr.send_keys(Keys.ENTER)
		time.sleep(1)
		logger.info("Manager group filled")

		'''Add work info'''
		work_info = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_304247080"]')  # add work info
		work_info.send_keys(kwargs['Work'])  # Sample work info
		logger.info("Work info filled")

		'''Click - Add'''
		self.driver.find_element_by_xpath('//*[@id="WIN_3_304247110"]/div/div').click()

		"""Date/System"""
		self.driver.find_element_by_link_text('Date/System').click()
		time.sleep(8)
		logger.info("clicked on Date")

		"""Actual Start/End date"""
		self.driver.get_screenshot_as_file('D:\git\November192018\Screenshots\s1.png')
		str_date = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_1000000350"]')  # start
		str_date.send_keys(kwargs['startdate'])  # '01/09/2018 00:00:00'
		logger.info("clicked on start date")
		time.sleep(8)

		self.driver.get_screenshot_as_file('D:\git\November192018\Screenshots\s2.png')
		end_date = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_1000000362"]')  # end
		end_date.send_keys(kwargs['enddate'])  # '05/09/2018 00:00:00'
		logger.info("clicked on end date")

		"""Managing CIs"""
		window_before = self.driver.window_handles[0]
		manage_cis = self.driver.find_element_by_xpath('//*[@id="sub-301626600"]/div[6]').click()
		logger.info("clicked on Manage CI xpath")
		time.sleep(5)
		WebDriverWait(self.driver, 10).until(expected_conditions.number_of_windows_to_be(2))
		window_after = self.driver.window_handles[1]
		self.driver.switch_to.window(window_after)
		logger.info("image opened")
		ci_type = self.driver.find_element_by_xpath('//*[@id="WIN_0_301189500"]/a/img').click()
		logger.info("Option opened")
		time.sleep(4)
		self.driver.find_element_by_xpath('/html/body/div[3]/div[2]/table/tbody/tr[10]').click()
		ci_value = "'" + kwargs['ci_type'] + "'"
		time.sleep(4)
		self.driver.get_screenshot_as_file('D:\git\November192018\Screenshots\s3.png')
		self.driver.find_element_by_xpath(
			"//td[@class='MenuEntryNoSub' and @arvalue=" + ci_value + "]").click()
		logger.info("passed")
		logger.info("ci type filled")

		"""click on search"""
		search = self.driver.find_element_by_xpath('//*[@id="WIN_0_300001100"]/div/div').click()
		logger.info("clicked on search")
		time.sleep(5)

		"""select the CI type"""
		select = self.driver.find_element_by_xpath('//*[@id="WIN_0_301399400"]/div/div').click()
		logger.info("clicked on CI type")
		time.sleep(5)

		"""Handling new windows"""
		WebDriverWait(self.driver, 10).until(expected_conditions.number_of_windows_to_be(2))
		window_after = self.driver.window_handles[1]
		self.driver.switch_to.window(window_after)
		time.sleep(5)

		"""click on finish"""
		finish = self.driver.find_element_by_xpath('//*[@id="WIN_0_301698500"]/div/div').click()
		time.sleep(4)
		logger.info("clicked on finish")
		time.sleep(5)
		self.driver.close()

		"""save button"""
		self.driver.switch_to.window(window_before)
		time.sleep(5)
		save_button = self.driver.find_element_by_link_text('Save')
		time.sleep(2)
		save_button.send_keys(Keys.PAGE_DOWN)
		time.sleep(5)
		save_button.click()
		time.sleep(5)
		logger.info("clicked on save")
	
	def identification_of_affected_CIs(self, kwargs):
		"""clicking on Applications"""
		logger.info("click on Application")
		application = self.driver.find_element_by_xpath('//*[@id="reg_img_304316340"]')
		application.click()
		time.sleep(6)

		"""clicking on Change Management"""
		logger.info("click on change management console")
		change_management = self.driver.find_element_by_link_text('Change Management')
		change_management.click()
		time.sleep(2)

		"""clicking on New Change"""
		logger.info("click on new change")
		newchange = self.driver.find_element_by_link_text('New Change')
		newchange.click()
		time.sleep(20)

		"""Filling and Submitting Incident Creation Form"""

		'''Filling Service'''
		logger.info("filling service field")
		service = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_303497300"]')
		service.click()
		service.send_keys(kwargs['Service'])
		time.sleep(3)
		service.send_keys(Keys.DOWN)
		service.send_keys(Keys.ENTER)

		"""Filling Summary"""
		summary = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_1000000000"]')
		summary.send_keys(kwargs['Summary'])  # This is sample
		logger.info(" summary filled")

		'''Filling Manager Group'''
		mngr = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_1000000015"]')
		mngr.send_keys(kwargs['Manager'])  # Three Service Desk
		time.sleep(2)
		mngr.send_keys(Keys.DOWN)
		mngr.send_keys(Keys.ENTER)
		time.sleep(1)
		logger.info("Manager group filled")

		'''Add work info'''
		work_info = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_304247080"]')  # add work info
		work_info.send_keys(kwargs['Work'])  # Sample work info
		logger.info("Work info filled")

		'''Click - Add'''
		self.driver.find_element_by_xpath('//*[@id="WIN_3_304247110"]/div/div').click()

		"""Date/System"""
		self.driver.find_element_by_link_text('Date/System').click()
		time.sleep(8)
		logger.info("clicked on Date")

		"""Actual Start/End date"""
		self.driver.get_screenshot_as_file('D:\git\November192018\Screenshots\s1.png')
		str_date = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_1000000350"]')  # start
		str_date.send_keys(kwargs['startdate'])  # '01/09/2018 00:00:00'
		logger.info("clicked on start date")
		time.sleep(8)

		self.driver.get_screenshot_as_file('D:\git\November192018\Screenshots\s2.png')
		end_date = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_1000000362"]')  # end
		end_date.send_keys(kwargs['enddate'])  # '05/09/2018 00:00:00'
		logger.info("clicked on end date")

		"""Managing CIs"""
		window_before = self.driver.window_handles[0]
		manage_cis = self.driver.find_element_by_xpath('//*[@id="sub-301626600"]/div[6]').click()
		logger.info("clicked on Manage CI xpath")
		time.sleep(5)
		WebDriverWait(self.driver, 10).until(expected_conditions.number_of_windows_to_be(2))
		window_after = self.driver.window_handles[1]
		self.driver.switch_to.window(window_after)
		logger.info("image opened")
		ci_type = self.driver.find_element_by_xpath('//*[@id="WIN_0_301189500"]/a/img').click()
		logger.info("Option opened")
		time.sleep(4)
		self.driver.find_element_by_xpath('/html/body/div[3]/div[2]/table/tbody/tr[10]').click()
		ci_value = "'" + kwargs['ci_type'] + "'"
		time.sleep(4)
		self.driver.get_screenshot_as_file('D:\git\November192018\Screenshots\s3.png')
		self.driver.find_element_by_xpath(
			"//td[@class='MenuEntryNoSub' and @arvalue=" + ci_value + "]").click()
		logger.info("passed")
		logger.info("ci type filled")

		"""click on search"""
		search = self.driver.find_element_by_xpath('//*[@id="WIN_0_300001100"]/div/div').click()
		logger.info("clicked on search")
		time.sleep(5)

		"""select the CI type"""
		select = self.driver.find_element_by_xpath('//*[@id="WIN_0_301399400"]/div/div').click()
		logger.info("clicked on CI type")
		time.sleep(5)

		"""Handling new windows"""
		WebDriverWait(self.driver, 10).until(expected_conditions.number_of_windows_to_be(2))
		window_after = self.driver.window_handles[1]
		self.driver.switch_to.window(window_after)
		time.sleep(5)

		"""click on finish"""
		finish = self.driver.find_element_by_xpath('//*[@id="WIN_0_301698500"]/div/div').click()
		time.sleep(4)
		logger.info("clicked on finish")
		time.sleep(5)
		self.driver.close()

		"""save button"""
		self.driver.switch_to.window(window_before)
		time.sleep(5)
		save_button = self.driver.find_element_by_link_text('Save')
		time.sleep(2)
		save_button.send_keys(Keys.PAGE_DOWN)
		time.sleep(5)
		save_button.click()
		time.sleep(5)
		logger.info("clicked on save")
	
	def change_creation(self, kwargs):
		logger.info("Executing change_creation()")
		""" Clicking on Application"""
		appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
		appl.click()

		"""Clicking on change Management -> New Incident"""
		incmgmt = self.driver.find_element_by_link_text('Change Management')
		incmgmt.click()
		incmgmtcon = self.driver.find_element_by_link_text('New Change')
		incmgmtcon.click()

		"""Filling and Submitting change Creation Form"""
		time.sleep(5)
		'''changecod=self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_1000003230"]')
		changecod.click()
		changecod.clear()
		changecod.send_keys(kwargs['changecodd'])
		time.sleep(2)
		changecod.send_keys(Keys.DOWN)
		changecod.send_keys(Keys.ENTER)'''

		summary = self.driver.find_element_by_id("arid_WIN_3_1000000000")
		summary.send_keys(kwargs['Summary'])


		service = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_303497300"]')
		service.click()
		service.send_keys(kwargs['Service'])
		time.sleep(3)
		service.send_keys(Keys.DOWN)
		service.send_keys(Keys.ENTER)

		'''chgclass = self.driver.find_element_by_id("arid_WIN_3_1000000568")
		chgclass.click()
		chgclass.send_keys(Keys.DOWN)
		time.sleep(3)
		chgclass.send_keys(kwargs['Class'])
		chgclass.send_keys(Keys.ENTER)'''

		impact = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_1000000163"]')
		impact.click()
		impact.send_keys(Keys.DOWN)
		impact.send_keys(kwargs['Impact'])
		impact.send_keys(Keys.ENTER)

		urgency = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_1000000162"]')
		urgency.click()
		urgency.send_keys(Keys.DOWN)
		urgency.send_keys(kwargs['Urgency'])
		urgency.send_keys(Keys.ENTER)

		managergroup = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_1000000015"]')
		managergroup.click()
		managergroup.send_keys(kwargs['managergroup'])
		time.sleep(2)
		managergroup.send_keys(Keys.DOWN)
		managergroup.send_keys(Keys.ENTER)

		Notes = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_304247080"]').send_keys(kwargs['Notes'])

		time.sleep(3)
		'Click on Add '
		self.driver.find_element_by_xpath('//*[@id="WIN_3_304247110"]/div/div').click()
		time.sleep(5)
		changeid=self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_1000000182"]').get_attribute("value")

		'Save'
		self.driver.find_element_by_xpath('//*[@id="WIN_3_1001"]/div').click()
		return changeid

	def change_complete(self, kwargs):
		logger.info("Execuitng incident_creation()")
		""" Clicking on Application"""
		appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
		appl.click()

		"""Clicking on Incident Management -> New Incident"""
		incmgmt = self.driver.find_element_by_link_text('Change Management')
		incmgmt.click()
		incmgmtcon = self.driver.find_element_by_link_text('Search Change')
		incmgmtcon.click()

		time.sleep(5)

		self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_1000000182"]').send_keys(kwargs['changeid'])
		time.sleep(3)
		action = ActionChains(self.driver)
		action.send_keys(u'\ue007')  # Used for pressing the ENTER Key
		action.perform()

		time.sleep(5)

		self.driver.find_element_by_xpath('//*[@id="WIN_3_303060100"]/div/div').click()

		time.sleep(3)
		return True
	
	def change_complete_final(self, kwargs):
		logger.info("Execuitng incident_creation()")
		""" Clicking on Application"""
		appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
		appl.click()

		"""Clicking on Incident Management -> New Incident"""
		incmgmt = self.driver.find_element_by_link_text('Change Management')
		incmgmt.click()
		incmgmtcon = self.driver.find_element_by_link_text('Search Change')
		incmgmtcon.click()

		time.sleep(5)

		self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_1000000182"]').send_keys(kwargs['changeid'])
		time.sleep(3)
		action = ActionChains(self.driver)
		action.send_keys(u'\ue007')  # Used for pressing the ENTER Key
		action.perform()
		time.sleep(5)
		window_before = self.driver.window_handles[0]
		self.driver.find_element_by_xpath('//*[@id="WIN_3_303060100"]/div/div').click()

		time.sleep(4)

		self.driver.find_element_by_xpath('//*[@id="WIN_3_303060100"]/div/div').click()
		time.sleep(3)
		window_after = self.driver.window_handles[1]
		self.driver.switch_to.window(window_after)
		time.sleep(3)
		self.driver.maximize_window()
		time.sleep(4)
		self.driver.find_element_by_xpath('//*[@id="arid_WIN_0_1000000348"]').send_keys(kwargs['actualstartdate'])
		self.driver.find_element_by_xpath('//*[@id="arid_WIN_0_1000000364"]').send_keys(kwargs['actualenddate'])
		time.sleep(3)
		self.driver.find_element_by_xpath('//*[@id="WIN_0_301533500"]/div').click()
		time.sleep(3)
		return True


	def change_complete_next(self, kwargs):
		logger.info("Execuitng incident_creation()")
		""" Clicking on Application"""
		appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
		appl.click()

		"""Clicking on Incident Management -> New Incident"""
		incmgmt = self.driver.find_element_by_link_text('Change Management')
		incmgmt.click()
		incmgmtcon = self.driver.find_element_by_link_text('Search Change')
		incmgmtcon.click()

		time.sleep(5)
		window_before = self.driver.window_handles[0]
		self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_1000000182"]').send_keys(kwargs['changeid'])
		time.sleep(3)
		action = ActionChains(self.driver)
		action.send_keys(u'\ue007')  # Used for pressing the ENTER Key
		action.perform()
		time.sleep(3)
		manager = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_1000000403"]')
		manager.click()
		manager.send_keys(kwargs['manager'])
		time.sleep(2)
		manager.send_keys(Keys.DOWN)
		manager.send_keys(Keys.ENTER)

		time.sleep(5)
		"""Next stage click"""
		self.driver.find_element_by_xpath('//*[@id="WIN_3_303060100"]/div/div').click()
		time.sleep(3)
		window_after = self.driver.window_handles[1]
		self.driver.switch_to.window(window_after)

		time.sleep(3)
		self.driver.maximize_window()
		time.sleep(2)
		"""Date selection"""
		self.driver.find_element_by_xpath('//*[@id="arid_WIN_0_1000000350"]').send_keys(kwargs['startdate'])
		self.driver.find_element_by_xpath('//*[@id="arid_WIN_0_1000000362"]').send_keys(kwargs['enddate'])
		time.sleep(3)
		"""Save"""
		self.driver.find_element_by_xpath('//*[@id="WIN_0_301533500"]/div/div').click()
		time.sleep(4)

		self.driver.switch_to.window(window_before)
		time.sleep(6)
		"""Next stage click"""
		self.driver.find_element_by_xpath('//*[@id="WIN_3_303060100"]/div').click()
		time.sleep(3)

		return True

	def approve_complete_next(self, kwargs):
		logger.info("Execuitng incident_creation()")
		""" Clicking on Application"""
		appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
		appl.click()

		"""Clicking on Incident Management -> New Incident"""
		incmgmt = self.driver.find_element_by_link_text('Change Management')
		incmgmt.click()
		incmgmtcon = self.driver.find_element_by_link_text('Search Change')
		incmgmtcon.click()

		time.sleep(7)

		self.driver.find_element_by_xpath('//*[@id="arid_WIN_2_1000000182"]').send_keys(kwargs['chanid'])
		time.sleep(3)
		action = ActionChains(self.driver)
		action.send_keys(u'\ue007')  # Used for pressing the ENTER Key
		action.perform()
		'''refresh'''
		time.sleep(4)
		self.driver.find_element_by_xpath('//*[@id="WIN_2_1020"]/div[1]/table/tbody/tr/td[3]/a[2]').click()
		time.sleep(5)
		'''Approve click'''
		self.driver.find_element_by_xpath('//*[@id="WIN_2_301899300"]/div[2]/div').click()
		time.sleep(5)
		'''print test approval'''
		approval1=self.driver.find_element_by_xpath('//*[@id="T301389923"]/tbody/tr[2]/td[2]/nobr/span').text
		print("approval 1:-")
		print (approval1)
		'''refresh'''
		time.sleep(4)
		self.driver.find_element_by_xpath('//*[@id="WIN_2_1020"]/div[1]/table/tbody/tr/td[3]/a[2]').click()
		time.sleep(6)

		return True


	def approve_complete(self, kwargs):
		logger.info("Execuitng incident_creation()")
		""" Clicking on Application"""
		appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
		appl.click()

		"""Clicking on Incident Management -> New Incident"""
		incmgmt = self.driver.find_element_by_link_text('Change Management')
		incmgmt.click()
		incmgmtcon = self.driver.find_element_by_link_text('Search Change')
		incmgmtcon.click()

		time.sleep(7)

		self.driver.find_element_by_xpath('//*[@id="arid_WIN_2_1000000182"]').send_keys(kwargs['chanid'])
		time.sleep(3)
		action = ActionChains(self.driver)
		action.send_keys(u'\ue007')  # Used for pressing the ENTER Key
		action.perform()
		'''refresh'''
		time.sleep(4)
		self.driver.find_element_by_xpath('//*[@id="WIN_2_1020"]/div[1]/table/tbody/tr/td[3]/a[2]').click()
		time.sleep(5)
		'''Approve click'''
		self.driver.find_element_by_xpath('//*[@id="WIN_2_301899300"]/div[2]/div').click()
		time.sleep(5)
		'''print test approval'''
		approval1=self.driver.find_element_by_xpath('//*[@id="T301389923"]/tbody/tr[2]/td[2]/nobr/span').text
		print("approval 1:-")
		print (approval1)
		'''refresh'''
		time.sleep(4)
		self.driver.find_element_by_xpath('//*[@id="WIN_2_1020"]/div[1]/table/tbody/tr/td[3]/a[2]').click()
		time.sleep(6)
		'''Approve click'''
		self.driver.find_element_by_xpath('//*[@id="WIN_2_301899300"]/div[2]/div').click()
		time.sleep(5)
		'''print test approval'''
		approval2=self.driver.find_element_by_xpath('//*[@id="T301389923"]/tbody/tr[2]/td[2]/nobr/span').text
		print("approval 2:-")
		print(approval2)
		'''refresh'''
		time.sleep(5)
		self.driver.find_element_by_xpath('//*[@id="WIN_2_1020"]/div[1]/table/tbody/tr/td[3]/a[2]').click()
		time.sleep(3)
		return True
	
	def change_Management_lifecycle_verification_gui(self, kwargs):
		logger.info("clicking on Applications")
		appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
		appl.click()

		logger.info("clicking on change Management")
		time.sleep(2)
		self.driver.find_element_by_link_text('Change Management').click()
		time.sleep(2)

		logger.info("clicking on new change")
		self.driver.find_element_by_link_text('New Change').click()
		time.sleep(20)

		"""Filling and Submitting Change Creation Form"""

		"""Filling Summary"""
		logger.info("Filling Summary")
		summary = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_1000000000"]')
		summary.send_keys(kwargs['Summary'])  # This is sample
		logger.info(" summary filled")

		'''Filling Service'''
		logger.info("filling service field")
		service = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_303497300"]')
		service.click()
		service.send_keys(kwargs['Service'])
		time.sleep(3)
		service.send_keys(Keys.DOWN)
		service.send_keys(Keys.ENTER)

		'''filling Impact'''
		logger.info("Filling impact")
		impact = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_1000000163"]')
		impact.click()
		impact.send_keys(Keys.DOWN)
		impact.send_keys(kwargs['Impact'])
		impact.send_keys(Keys.ENTER)

		'''filling urgency'''
		logger.info("Filling Urgency")
		urgency = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_1000000162"]')
		urgency.click()
		urgency.send_keys(Keys.DOWN)
		urgency.send_keys(kwargs['Urgency'])
		urgency.send_keys(Keys.ENTER)

		'''Filling Manager Group'''
		logger.info("filling Manager group")
		mngr = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_1000000015"]')
		mngr.send_keys(kwargs['Manager'])  # Three Service Desk
		time.sleep(2)
		mngr.send_keys(Keys.DOWN)
		mngr.send_keys(Keys.ENTER)
		time.sleep(1)
		logger.info("Manager group filled")

		'''Add work info'''
		logger.info("filling work info")
		work_info = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_304247080"]')  # add work info
		work_info.send_keys(kwargs['Work'])  # Sample work info
		logger.info("Work info filled")

		'''Click - Add'''
		logger.info("click on add")
		self.driver.find_element_by_xpath('//*[@id="WIN_3_304247110"]/div/div').click()
		time.sleep(2)

		self.driver.save_screenshot('D:\git\screenshots\save1.png')
		logger.info("click on save")
		save_button = self.driver.find_element_by_link_text('Save')
		time.sleep(2)
		save_button.send_keys(Keys.PAGE_DOWN)
		time.sleep(5)
		save_button.click()
		time.sleep(8)
		logger.info("clicked on save")

		logger.info("click on Next stage")
		next_stage = self.driver.find_element_by_xpath('//*[@id="WIN_3_303060100"]/div/div').click()
		time.sleep(3)

		logger.info("getting CI ")
		# change_id = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_1000000182"]').text
		change_id = self.driver.find_element_by_xpath('//*[@id="WIN_0_304248710"]/fieldset/div/dl/dd[5]/span[2]/a').text
		logger.info("id is = {}".format(change_id))
		time.sleep(2)

		logger.info("returning CI IDs")
		return change_id

	def change_Management_approvers_permission_gui(self, change_id):
		logger.info("Clicking on Applications")
		appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
		appl.click()

		logger.info("clicking on change Management")
		time.sleep(2)
		self.driver.find_element_by_link_text('Change Management').click()
		time.sleep(2)

		logger.info("clicking on Search change")
		self.driver.find_element_by_link_text('Search Change').click()
		time.sleep(5)

		logger.info("filling Problem ID")
		time.sleep(3)
		enter_id = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_1000000182"]')
		enter_id.send_keys(change_id)  # change id enter
		time.sleep(3)

		logger.info("Then search")
		self.driver.find_element_by_xpath('//*[@id="WIN_3_1002"]/div/div').click()
		time.sleep(5)
		'''refresh'''
		logger.info("click on refresh")
		time.sleep(4)
		self.driver.find_element_by_xpath('//*[@id="WIN_3_301389923"]/div[1]/table/tbody/tr/td[2]/a[2]').click()
		time.sleep(3)

		'''Approve click'''
		self.driver.save_screenshot('D:\git\screenshots\approve1.png')
		logger.info("click on approve")
		WebDriverWait(self.driver, 30).until(
			expected_conditions.element_to_be_clickable((By.XPATH, '//*[@id="reg_img_301899300"]')))
		self.driver.find_element_by_xpath('//*[@id="reg_img_301899300"]').click()
		time.sleep(5)

		'''refresh'''
		logger.info("click on refresh")
		self.driver.find_element_by_xpath('//*[@id="WIN_3_301389923"]/div[1]/table/tbody/tr/td[2]/a[2]').click()
		time.sleep(3)

		'''Approve click'''
		logger.info("click on approve")
		self.driver.find_element_by_xpath('//*[@id="reg_img_301899300"]').click()
		time.sleep(4)
		return True

	def change_management_refresh_scheduled_date_gui(self, change_id, kwargs):
		logger.info("Clicking on Applications")
		appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
		appl.click()

		logger.info("clicking on change Management")
		time.sleep(2)
		self.driver.find_element_by_link_text('Change Management').click()
		time.sleep(2)

		logger.info("clicking on Search change")
		self.driver.find_element_by_link_text('Search Change').click()
		time.sleep(5)

		window_before = self.driver.window_handles[0]

		logger.info("filling Problem ID")
		time.sleep(3)
		enter_id = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_1000000182"]')
		enter_id.send_keys(change_id)  # change id enter
		time.sleep(3)

		logger.info("Then search")
		self.driver.find_element_by_xpath('//*[@id="WIN_3_1002"]/div/div').click()
		time.sleep(3)

		logger.info("clicking on refresh")
		self.driver.find_element_by_xpath('//*[@id="reg_img_304352241"]').click()

		time.sleep(3)
		logger.info("filling Manager field")
		manager = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_1000000403"]')
		manager.click()
		manager.send_keys(kwargs['Manager'])
		time.sleep(2)
		manager.send_keys(Keys.DOWN)
		manager.send_keys(Keys.ENTER)
		time.sleep(15)

		"""Next stage click"""
		logger.info("clicking on Next Stage")
		self.driver.find_element_by_xpath('//*[@id="WIN_3_303060100"]/div/div').click()
		time.sleep(5)
		window_after = self.driver.window_handles[1]
		self.driver.switch_to.window(window_after)

		time.sleep(5)
		self.driver.maximize_window()
		time.sleep(5)
		"""Date selection"""
		logger.info("Filling scheduled Start and End dates")
		self.driver.find_element_by_xpath('//*[@id="arid_WIN_0_1000000350"]').send_keys(kwargs['startdate'])
		self.driver.find_element_by_xpath('//*[@id="arid_WIN_0_1000000362"]').send_keys(kwargs['enddate'])
		time.sleep(5)
		self.driver.save_screenshot('D:\git\screenshots\schedule1.png')

		logger.info("clicking on save")
		"""Save"""
		self.driver.find_element_by_xpath('//*[@id="WIN_0_301533500"]/div/div').click()
		time.sleep(5)

		self.driver.switch_to.window(window_before)
		time.sleep(6)

		logger.info("clicking on Next Stage")
		"""Next stage click"""
		self.driver.find_element_by_xpath('//*[@id="WIN_3_303060100"]/div').click()
		time.sleep(3)

		return True

	def change_management_refresh_next_gui(self, change_id, kwargs):
		logger.info("Execuitng change_management_actual_date()")
		""" Clicking on Application"""
		appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
		appl.click()

		"""Clicking on Change Management -> Search Change"""
		change_mgmt = self.driver.find_element_by_link_text('Change Management')
		change_mgmt.click()
		change_mgmticon = self.driver.find_element_by_link_text('Search Change')
		change_mgmticon.click()

		time.sleep(5)

		self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_1000000182"]').send_keys(change_id)
		time.sleep(3)
		action = ActionChains(self.driver)
		action.send_keys(u'\ue007')  # Used for pressing the ENTER Key
		action.perform()
		time.sleep(5)

		logger.info("clicking on refresh")
		self.driver.find_element_by_xpath('//*[@id="reg_img_304352241"]').click()

		window_before = self.driver.window_handles[0]
		self.driver.find_element_by_xpath('//*[@id="WIN_3_303060100"]/div/div').click()

		time.sleep(4)
		logger.info("clicking on Next Stage")
		self.driver.find_element_by_xpath('//*[@id="WIN_3_303060100"]/div/div').click()
		time.sleep(6)

		window_after = self.driver.window_handles[1]
		self.driver.switch_to.window(window_after)
		time.sleep(3)
		self.driver.maximize_window()
		time.sleep(4)

		logger.info("Filling actual start and end dates")
		self.driver.find_element_by_xpath('//*[@id="arid_WIN_0_1000000348"]').send_keys(kwargs['actualstartdate'])
		self.driver.find_element_by_xpath('//*[@id="arid_WIN_0_1000000364"]').send_keys(kwargs['actualenddate'])
		time.sleep(3)
		self.driver.save_screenshot('D:\git\screenshots\actual1.png')

		logger.info("clicking on inner save")
		self.driver.find_element_by_xpath('//*[@id="WIN_0_301533500"]/div').click()
		time.sleep(3)
		return True

	def change_Management_Final_stage(self, change_id):
		logger.info("Clicking on Applications")
		appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
		appl.click()

		logger.info("clicking on change Management")
		time.sleep(2)
		self.driver.find_element_by_link_text('Change Management').click()
		time.sleep(2)

		logger.info("clicking on Search change")
		self.driver.find_element_by_link_text('Search Change').click()
		time.sleep(5)

		logger.info("filling Problem ID")
		time.sleep(3)
		enter_id = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_1000000182"]')
		enter_id.send_keys(change_id)  # change id enter
		time.sleep(3)

		logger.info("Then search")
		self.driver.find_element_by_xpath('//*[@id="WIN_3_1002"]/div/div').click()
		time.sleep(2)

		logger.info("click on refresh")
		self.driver.find_element_by_xpath('//*[@id="reg_img_304352241"]').click()
		time.sleep(5)
		self.driver.save_screenshot('D:\git\screenshots\status1.png')

		logger.info("click on Next stage")
		next_stage = self.driver.find_element_by_xpath('//*[@id="WIN_3_303060100"]/div/div').click()
		time.sleep(10)
		self.driver.save_screenshot('D:\git\screenshots\status2.png')

		"""To validate getting value of Disabled field"""
		logger.info("getting status value")
		self.driver.save_screenshot('D:\git\screenshots\status3.png')
		status = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_303502600"]')
		status_value = status.get_attribute('value')
		logger.info("The status is{}".format(status_value))

		if (status_value == "Closed"):
			logger.info(
				"Change ID: {} has successfully Closed and change life cycle also completed successfully ".format(
					change_id))
			return True
		return False
	
	def search_change_and_change_status_main(self, kwargs):
		logger.info("Execuitng incident_creation()")
		""" Clicking on Application"""
		appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
		appl.click()
		
		"""Clicking on Incident Management -> New Incident"""
		incmgmt = self.driver.find_element_by_link_text('Change Management')
		incmgmt.click()
		incmgmtcon = self.driver.find_element_by_link_text('Search Change')
		incmgmtcon.click()
		
		time.sleep(5)
		
		self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_1000000182"]').send_keys(kwargs['changeid'])
		time.sleep(3)
		action = ActionChains(self.driver)
		action.send_keys(u'\ue007')  # Used for pressing the ENTER Key
		action.perform()
		
		time.sleep(7)
		
		status = self.driver.find_element(By.XPATH, "//div[@id='WIN_3_303502600']//a[@class='btn btn3d menu']")
		status.click()
		for i in range(int(kwargs['Iterations'])):
			status.send_keys(Keys.DOWN)
			time.sleep(5)
		status.send_keys(Keys.ENTER)
		time.sleep(3)
		logger.info("Status changed to {}".format(kwargs['Status']))
		if kwargs['Status'] == "Pending":
			status_reason = self.driver.find_element(By.XPATH,
			                                         "//div[@id='WIN_3_1000000881']//a[@class='btn btn3d menu']")
			status_reason.click()
			status_reason.send_keys(Keys.DOWN)
			time.sleep(3)
			status_reason.send_keys(Keys.DOWN)
			time.sleep(3)
			status_reason.send_keys(Keys.ENTER)
			time.sleep(3)
			logger.info("Status reason given")
		
		'Save'
		self.driver.find_element_by_xpath('//*[@id="WIN_3_1003"]/div/div').click()
		time.sleep(10)
		return True
	
	def create_change_and_search_change(self, kwargs):
		try:
			for k in kwargs:
				logger.info("arguments are {}{}".format(k, kwargs[k]))
			self.login_bmc()
			changeid = False
			changeid = self.verify_create_change_and_search_change(kwargs)
		except BaseException as be:
			logger.fatal("Fatal exception occured in create_change_id() in {}".format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.bmc_logout()
			return changeid
	
	def search_change_id_for_second_approval(self, changeid):
		try:
			self.login_bmc()
			status = False
			status = self.search_change_for_second_approval(changeid)
		except BaseException as be:
			logger.fatal("Fatal exception occured in search_change_id() in {}".format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.bmc_logout()
			return status
	
	def search_change_id_for_next_stage(self, changeid):
		try:
			self.login_bmc()
			status = False
			status = self.verify_search_change_id_for_next_stage(changeid)
		except BaseException as be:
			logger.fatal("Fatal exception occured in search_change_id() in {}".format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.bmc_logout()
			return status
		
	def verify_risk_assessments_questions_of_change_tickets_via_gui(self, kwargs):
		try:
			self.login_bmc()
			status = False
			status = self.verify_risk_assessments_change_tickets(kwargs)
		except BaseException as be:
			logger.fatal('fatal exception occured in verify_risk_assessments_questions_of_change_tickets_via_gui() in {}'.format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.bmc_logout()
			return status
	
	def create_change_tickets_via_gui(self, kwargs):
		try:
			self.login_bmc()
			status = False
			status = self.identification_of_affected_CIs(kwargs)
		except BaseException as be:
			logger.fatal(
				'fatal exception occured in create_change_tickets_via_gui() in {}'.format(
					self.name))
			logger.error(traceback.print_exc())
		finally:
			self.bmc_logout()
			return status
	
	def identification_of_affected_CIs_of_change_tickets_via_gui(self, kwargs):
		try:
			self.login_bmc()
			status = False
			status = self.identification_of_affected_CIs(kwargs)
			status = self.hasXpath()
		except BaseException as be:
			logger.fatal(
				'Fatal exception occured in identification_of_affected_CIs_of_change_tickets_via_gui() in {}'.format(
					self.name))
			logger.error(traceback.print_exc())
		finally:
			self.bmc_logout()
			return status
	
	def create_priority_change_gui(self, kwargs):
		try:
			for k in kwargs.keys():
				logger.info("arguments are {}{}".format(k, kwargs[k]))
			self.login_bmc()
			changeid = False
			changeid = self.change_creation(kwargs)
		except BaseException as be:
			logger.fatal("Fatal exception occured in create_priority_change_gui() in {}".format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.bmc_logout()
			return changeid

	def complete_priority_change_gui(self, kwargs):
		try:
			for k in kwargs.keys():
				logger.info("arguments are {}{}".format(k, kwargs[k]))
			self.login_bmc()
			changeid = False
			changeid = self.change_complete(kwargs)
		except BaseException as be:
			logger.fatal("Fatal exception occured in create_priority_incident_gui() in {}".format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.bmc_logout()
			return changeid
	
	def complete_priority_change_final_gui(self, kwargs):
		try:
			for k in kwargs.keys():
				logger.info("arguments are {}{}".format(k, kwargs[k]))
			self.login_bmc()
			changeid = False
			changeid = self.change_complete_final(kwargs)
		except BaseException as be:
			logger.fatal("Fatal exception occured in create_priority_incident_gui() in {}".format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.bmc_logout()
			return changeid

	def complete_priority_change_next_gui(self, kwargs):
		try:
			for k in kwargs.keys():
				logger.info("arguments are {}{}".format(k, kwargs[k]))
			self.login_bmc()
			changeid = False
			changeid = self.change_complete_next(kwargs)
		except BaseException as be:
			logger.fatal("Fatal exception occured in create_priority_incident_gui() in {}".format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.bmc_logout()
			return changeid

	def approve_priority_change_gui(self, kwargs):
		try:
			for k in kwargs.keys():
				logger.info("arguments are {}{}".format(k, kwargs[k]))
			self.login_bmc()
			changeid = False
			changeid = self.approve_complete(kwargs)
		except BaseException as be:
			logger.fatal("Fatal exception occured in create_priority_incident_gui() in {}".format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.bmc_logout()
			return changeid

	def approve_priority_change_next_gui(self, kwargs):
		try:
			for k in kwargs.keys():
				logger.info("arguments are {}{}".format(k, kwargs[k]))
			self.login_bmc()
			changeid = False
			changeid = self.approve_complete_next(kwargs)
		except BaseException as be:
			logger.fatal("Fatal exception occured in create_priority_incident_gui() in {}".format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.bmc_logout()
			return changeid
	
	def change_Management_lifecycle_verification(self, kwargs):
		try:
			self.login_bmc()
			status = False
			status = self.change_Management_lifecycle_verification_gui(kwargs)
		except BaseException as be:
			logger.fatal(
				'Fatal exception occured in change_Management_lifecycle_verification() in {}'.format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.bmc_logout()
			return status

	def change_Management_approvers_verification(self, change_id):
		try:
			self.login_bmc()
			status = False
			status = self.change_Management_approvers_permission_gui(change_id)
		except BaseException as be:
			logger.fatal(
				'Fatal exception occured in change_Management_approvers_permission() in {}'.format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.bmc_logout()
			return status

	def change_management_refresh_scheduled_date(self, change_id, kwargs):
		try:
			self.login_bmc()
			status = False
			status = self.change_management_refresh_scheduled_date_gui(change_id, kwargs)
		except BaseException as be:
			logger.fatal(
				'Fatal exception occured in change_management_refresh_scheduled_date() in {}'.format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.bmc_logout()
			return status

	def change_management_refresh_next(self, change_id, kwargs):
		try:
			self.login_bmc()
			status = False
			status = self.change_management_refresh_next_gui(change_id, kwargs)
		except BaseException as be:
			logger.fatal(
				'Fatal exception occured in change_management_refresh_next() in {}'.format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.bmc_logout()
			return status

	def change_Management_Final_stage_gui(self, change_id):
		try:
			self.login_bmc()
			status = False
			status = self.change_Management_Final_stage(change_id)
		except BaseException as be:
			logger.fatal(
				'Fatal exception occured in change_Management_Final_stage() in {}'.format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.bmc_logout()
			return status
	
	def search_change_and_change_status(self, kwargs):
		try:
			self.login_bmc()
			status = self.search_change_and_change_status_main(kwargs)
		except BaseException as be:
			logger.fatal("Fatal exception occured in open_smart_reporting_mbnl_all_lib() in {}".format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.bmc_logout()
			return status