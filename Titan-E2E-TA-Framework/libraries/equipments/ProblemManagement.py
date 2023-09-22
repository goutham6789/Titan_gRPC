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


class BmcProblemManagement(Vmm):
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
	
	def create_priority_problem(self, kwargs):
		logger.info("Executing_Create_Problem_by_priority()")
		'''application xpath'''
		app = self.driver.find_element_by_xpath('//*[@id="reg_img_304316340"]')
		app.click()
		time.sleep(3)
		'''Clicking on Problem Management -> New Problem'''
		prbmgmt = self.driver.find_element_by_link_text('Problem Management')
		prbmgmt.click()
		newprb = self.driver.find_element_by_link_text('New Problem')
		newprb.click()
		time.sleep(4)
		
		"""Populating the mandatory areas"""
		service = self.driver.find_element_by_xpath("//*[@id='arid_WIN_3_303497300']")
		service.click()
		service.send_keys(kwargs['Service'])
		time.sleep(3)
		service.send_keys(Keys.ENTER)
		
		# self.driver.find_element_by_xpath("//textarea[@id='arid_WIN_3_303497300']").send_keys(kwargs['Service'])
		# time.sleep(4)
		
		WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
			(By.XPATH, "//*[@id='arid_WIN_3_1000000000']")))
		summary = self.driver.find_element_by_xpath("//*[@id='arid_WIN_3_1000000000']")
		summary.click()
		time.sleep(1)
		summary.clear()
		summary.send_keys(kwargs['Summary'])
		summary.send_keys(Keys.ENTER)
		# time.sleep(3)
		
		urgencies = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_1000000162"]')
		urgencies.click()
		urgencies.send_keys(Keys.DOWN)
		urgencies.send_keys(kwargs['Urgency'])
		time.sleep(3)
		urgencies.send_keys(Keys.ENTER)
		# time.sleep(3)
		
		impact = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_1000000163"]')
		impact.click()
		impact.send_keys(Keys.DOWN)
		impact.send_keys(kwargs['Impact'])
		time.sleep(3)
		impact.send_keys(Keys.ENTER)
		# time.sleep(3)
		
		target_date = self.driver.find_element_by_xpath("//input[@id='arid_WIN_3_1000001571']")
		target_date.click()
		# target_date.send_keys(Keys.DOWN)
		target_date.send_keys(kwargs['Target_date'])
		time.sleep(3)
		target_date.send_keys(Keys.ENTER)
		# time.sleep(3)
		
		assignedgroup = self.driver.find_element_by_xpath("//textarea[@id='arid_WIN_3_1000000217']")
		assignedgroup.click()
		assignedgroup.clear()
		assignedgroup.send_keys(kwargs['Assigned_group'])
		time.sleep(3)
		assignedgroup.send_keys(Keys.DOWN)
		assignedgroup.send_keys(Keys.ENTER)
		
		assignee = self.driver.find_element_by_xpath("//textarea[@id='arid_WIN_3_1000000218']")
		assignee.click()
		assignee.clear()
		assignee.send_keys(kwargs['Assignee'])
		assignee.send_keys(Keys.DOWN)
		assignee.send_keys(Keys.ENTER)
		
		status = self.driver.find_element_by_xpath("//div[@id='WIN_3_7']//a[@class='btn btn3d selectionbtn']")
		status.click()
		# time.sleep(2)
		status.send_keys(Keys.DOWN)
		# status.send_keys(kwargs['Status'])
		time.sleep(2)
		status.send_keys(Keys.DOWN)
		time.sleep(2)
		status.send_keys(Keys.DOWN)
		time.sleep(2)
		status.send_keys(Keys.DOWN)
		time.sleep(2)
		status.send_keys(Keys.ENTER)
		
		# problem_id = self.driver.find_element(By.XPATH, "//textarea[@id='arid_WIN_3_1000000232']").text
		
		problem = self.driver.find_element_by_xpath('//*[@id="WIN_0_304248710"]/fieldset/div/dl/dd[5]/span[2]/a').text
		problemid = problem[:-6]
		""""Save buton click"""
		self.driver.find_element_by_xpath(
			"//a[@id='WIN_3_301614800']//div[@class='f1'][contains(text(),'Save')]").click()
		time.sleep(3)
		logger.info("Exiting Problem_creation()")
		return problemid
	
	def set_rule(self, rulepath, rulevalue):
		logger.info("Executing set_rule()")
		"""Clicking on Application"""
		appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
		appl.click()
		time.sleep(2)
		logger.info("clicking on administrator console()")
		"""Clicking on Administrator Console -> Application Administrator Console"""
		adcon = self.driver.find_element_by_link_text('Administrator Console')
		adcon.click()
		adconmng = self.driver.find_element_by_link_text('Application Administration Console')
		adconmng.click()
		logger.info("Selecting Custom Configuration tab")
		"""Selecting Custom Configuration tab"""
		time.sleep(5)
		WebDriverWait(self.driver, 30).until(
			expected_conditions.element_to_be_clickable(
				(By.XPATH, '//*[@id="WIN_0_303635200"]/fieldset/dl/dd[3]/span[2]/a')))
		cust = self.driver.find_element_by_xpath('//*[@id="WIN_0_303635200"]/fieldset/dl/dd[3]/span[2]/a')
		cust.click()
		time.sleep(5)
		logger.info("Selecting problem management")
		"""Clicking on Problem Management -> Advanced Options -> Rules"""
		probmang = self.driver.find_element_by_xpath('//*[@id="handlerTN0_49_0"]')
		probmang.click()
		advop = self.driver.find_element_by_xpath('//*[@id="handlerTN0_49_1"]')
		advop.click()
		rule = self.driver.find_element_by_xpath('//*[@id="titleTN0_54_2"]')
		rule.click()
		window_before = self.driver.window_handles[0]
		"""Clicking on open"""
		op = self.driver.find_element_by_xpath('//*[@id="WIN_0_500007506"]/div/div')
		op.click()
		WebDriverWait(self.driver, 10).until(
			expected_conditions.number_of_windows_to_be(2))
		window_after = self.driver.window_handles[1]
		self.driver.switch_to.window(window_after)
		logger.info("Setting rules")
		time.sleep(3)
		submit = self.driver.find_element_by_xpath(rulepath)
		var = submit.is_selected()
		logger.info("Actual value {} ".format(var))
		rulevalue = bool(rulevalue)
		matching = True
		if var != rulevalue:
			logger.error("The actual value '{}' is not matching with expected value '{}'".format(var, rulevalue))
			#raise ValueError
			matching = False
		else:
			logger.info("The rule name and its value is '{}' matching with actual value '{}'".format(rulevalue, var))
		cl = self.driver.find_element_by_xpath('//*[@id="WIN_0_301614900"]/div/div')
		cl.click()
		self.verify_popup()
		logger.info("Exiting from set rules")
		self.driver.switch_to.window(window_before)
		return matching
	
	def priority_problem_by_type(self,kwargs):
		logger.info("Executing_priority_problem_by_type()")
		'''application xpath'''
		app = self.driver.find_element_by_xpath('.//*[@id="reg_img_304316340"]')
		app.click()
		'''create problem management page'''
		a = self.driver.find_elements_by_xpath('//*[@id="WIN_0_80077"]/fieldset/div/div/div/div[12]/a/span')
		if (a) > 0:
			a[0].click()
		b = self.driver.find_elements_by_xpath('.//*[@id="FormContainer"]/div[5]/div/div[12]/div/div[1]/a/span')
		if (b) > 0:
			b[0].click()
		time.sleep(5)
		Window_before = self.driver.current_window_handle[0]
		self.driver.find_element_by_xpath('//*[@id="WIN_3_301429000"]/div[2]/div').click()
		WebDriverWait(self.driver, 10).until(
			expected_conditions.number_of_windows_to_be(2))
		window_after = self.driver.window_handles[1]
		self.driver.switch_to.window(window_after)
		self.driver.maximize_window()
		"""problem type"""
		a = self.driver.find_element_by_xpath('//*[@id="arid_WIN_0_301576800"]')
		a.click()
		# a.send_keys('Problem Investigation')
		time.sleep(3)
		a.send_keys(Keys.DOWN)
		a.send_keys(Keys.DOWN)
		a.send_keys(Keys.ENTER)
		time.sleep(3)
		''''"""ENTER"""
		action = ActionChains(driver)
		action.send_keys(u'\ue007')# Used for pressing the ENTER Key
		action.perform()'''
		"""ok button"""
		self.driver.find_element_by_xpath('//*[@id="WIN_0_301606400"]/div/div').click()
		window_before = self.driver.window_handles[0]
		self.driver.switch_to.window(window_before)
		time.sleep(5)
		"""summary"""
		self.driver.find_element_by_xpath('//*[@id="arid_WIN_5_1000000000"]').send_keys(kwargs['summary'])

		"""impact"""
		impact = self.driver.find_element_by_xpath('//*[@id="arid_WIN_5_1000000163"]')
		impact.click()
		impact.send_keys(Keys.DOWN)
		impact.send_keys('3-Moderate/Limited')
		time.sleep(3)
		impact.send_keys(Keys.ENTER)
		time.sleep(3)

		"""urgency"""
		urgency = self.driver.find_element_by_xpath('//*[@id="arid_WIN_5_1000000162"]')
		urgency.click()
		urgency.send_keys(Keys.DOWN)
		urgency.send_keys('3-Medium')
		time.sleep(3)
		urgency.send_keys(Keys.ENTER)
		time.sleep(3)

		service = self.driver.find_element_by_xpath('//*[@id="arid_WIN_5_303497300"]')
		service.click()
		service.send_keys('Default (IT)')
		time.sleep(3)
		service.send_keys(Keys.ENTER)
		time.sleep(3)

		elem = self.driver.find_element_by_xpath('//*[@id="WIN_0_304248710"]/fieldset/div/dl/dd[5]/span[2]/a').text
		print(elem)
		elem = elem[:-6]
		print (elem)
		"""save"""
		self.driver.find_element_by_xpath('//*[@id="WIN_5_301614800"]/div/div').click()
		"""Search problem"""
		time.sleep(5)
		'''application xpath'''
		app = self.driver.find_element_by_xpath('//*[@id="reg_img_304316340"]')
		app.click()
		"""Search"""
		a = self.driver.find_elements_by_xpath('//*[@id="WIN_0_80077"]/fieldset/div/div/div/div[12]/a/span')
		if (a) > 0:
			a[0].click()
		b = self.driver.find_elements_by_xpath('.//*[@id="FormContainer"]/div[5]/div/div[12]/div/div[3]/a/span')
		if (b) > 0:
			b[0].click()
		time.sleep(5)
		self.driver.find_element_by_xpath('//*[@id="arid_WIN_6_1000000232"]').send_keys(elem)
		action = ActionChains(self.driver)
		action.send_keys(u'\ue007')  # Used for pressing the ENTER Key
		action.perform()
		"""opening the searched incident"""
		time.sleep(5)
		self.driver.find_element_by_xpath('//*[@id="T1020"]/tbody/tr[2]/td[1]/nobr/span').click()
		action = ActionChains(self.driver)
		action.send_keys(u'\ue007')  # Used for pressing the ENTER Key
		action.perform()
		"""Switching to new opened window"""
		time.sleep(2)
		window_after = self.driver.window_handles[1]
		self.driver.switch_to.window(window_after)
		time.sleep(5)
		"""quick action to create relationship"""
		self.driver.find_element_by_xpath('//*[@id="WIN_1_304253820"]/a').click()
		window_b = self.driver.current_window_handle[1]
		time.sleep(3)
		"""Click on incident"""
		self.driver.find_element_by_xpath('(//*[@class="MenuEntryName"])[3]').click()
		time.sleep(2)
		window_a = self.driver.window_handles[2]
		self.driver.switch_to.window(window_a)
		time.sleep(5)
		self.driver.maximize_window()
		self.driver.find_element_by_xpath('//*[@id="arid_WIN_0_301737200"]').clear()
		time.sleep(5)
		self.driver.find_element_by_xpath('//*[@id="arid_WIN_0_301737200"]').send_keys(kwargs['incidentid'])
		#self.driver.find_element_by_xpath('//*[@id="arid_WIN_0_301737200"]').send_keys('INC300000001906')
		action = ActionChains(self.driver)
		action.send_keys(u'\ue007')  # Used for pressing the ENTER Key
		action.perform()
		time.sleep(6)
		self.driver.find_element_by_xpath('//*[@id="T1000003952"]/tbody/tr[2]/td[1]/nobr/span').click()
		time.sleep(5)
		self.driver.find_element_by_xpath('//*[@id="WIN_0_304253220"]/div/div').click()
		time.sleep(4)
		action = ActionChains(self.driver)
		action.send_keys(u'\ue007')  # Used for pressing the ENTER Key
		action.perform()
		#self.verify_popup()
		time.sleep(2)
		window_before=self.driver.window_handles[1]
		self.driver.switch_to.window(window_before)
		time.sleep(3)
		self.driver.find_element_by_xpath('//*[@id="WIN_1_302127600"]/div[2]/div[2]/div/dl/dd[4]/span[2]/a').click()
		inceid = self.driver.find_element_by_xpath('//*[@id="T301389439"]/tbody/tr[3]/td[3]/nobr/span').text
		print(inceid)
		inceid = inceid[:-06]
		print (inceid)
		self.driver.find_element_by_xpath('//*[@id="arid_WIN_1_1000001571"]').send_keys('12/09/2018 00:00:00')
		"""Next stage"""
		self.driver.find_element_by_xpath('//*[@id="WIN_1_301541900"]/a').click()
		time.sleep(2)
		self.driver.find_element_by_xpath('/html/body/div[4]/div[2]/table/tbody/tr[1]/td[1]').click()
		time.sleep(2)
		self.driver.find_element_by_xpath('/html/body/div[5]/div[2]/table/tbody/tr[1]/td[1]').click()
		time.sleep(3)
		"""next stage"""
		self.driver.find_element_by_xpath('//*[@id="WIN_1_301542000"]').click()
		time.sleep(2)
		self.driver.find_element_by_xpath('/html/body/div[4]/div[2]/table/tbody/tr[1]/td[1]').click()
		time.sleep(2)
		self.driver.find_element_by_xpath('/html/body/div[5]/div[2]/table/tbody/tr[1]/td[1]').click()
		window_after=self.driver.window_handles[2]
		self.driver.switch_to.window(window_after)
		time.sleep(4)
		assgroup = self.driver.find_element_by_xpath('//*[@id="arid_WIN_0_1000000217"]')
		assgroup.click()
		assgroup.clear()
		assgroup.send_keys(kwargs['assigngroup'])
		assgroup.send_keys(Keys.DOWN)
		assgroup.send_keys(Keys.ENTER)
		time.sleep(3)
		assignee = self.driver.find_element_by_xpath('//*[@id="arid_WIN_0_1000000218"]')
		assignee.click()
		assignee.send_keys('Ankit Mehrotra')
		assignee.send_keys(Keys.DOWN)
		assignee.send_keys(Keys.ENTER)
		time.sleep(3)
		self.driver.find_element_by_xpath('//*[@id="WIN_0_301533500"]/div/div').click()
		window_be = self.driver.window_handles[1]
		self.driver.switch_to.window(window_be)
		#print(window_be)
		time.sleep(3)
		self.driver.find_element_by_xpath('//*[@id="WIN_1_301542100"]/a').click()
		time.sleep(3)
		self.driver.find_element_by_xpath('/html/body/div[4]/div[2]/table/tbody/tr[1]/td[1]').click()
		time.sleep(3)
		self.driver.find_element_by_xpath('/html/body/div[5]/div[2]/table/tbody/tr[1]/td[1]').click()
		time.sleep(3)
		window_after = self.driver.window_handles[2]
		self.driver.switch_to.window(window_after)
		time.sleep(2)
		service = self.driver.find_element_by_xpath('//*[@id="arid_WIN_0_1000000881"]')
		service.click()
		service.send_keys(Keys.DOWN)
		service.send_keys(Keys.DOWN)
		time.sleep(3)
		service.send_keys(Keys.ENTER)
		time.sleep(3)
		self.driver.find_element_by_xpath('//*[@id="arid_WIN_0_303497400"]').send_keys('Explore Products')
		self.driver.find_element_by_xpath('//*[@id="WIN_0_301533500"]/div/div').click()
		time.sleep(4)
		window_af = self.driver.window_handles[1]
		self.driver.switch_to.window(window_af)
		#print(window_af)
		time.sleep(5)
		self.driver.find_element_by_xpath('//*[@id="arid_WIN_1_1000000151"]').send_keys(kwargs['notes'])
		time.sleep(2)
		self.driver.find_element_by_xpath('//*[@id="WIN_1_301614800"]/div/div').click()
		time.sleep(4)
		self.driver.find_element_by_xpath('//*[@id="WIN_1_301542200"]').click()
		time.sleep(2)
		self.driver.find_element_by_xpath('/html/body/div[4]/div[2]/table/tbody/tr[1]/td[1]').click()
		time.sleep(2)
		self.driver.find_element_by_xpath('/html/body/div[5]/div[2]/table/tbody/tr/td[1]').click()
		time.sleep(2)
		self.driver.find_element_by_xpath('//*[@id="WIN_1_301614800"]/div/div').click()
		self.driver.close()
		parentw = self.driver.window_handles[0]
		self.driver.switch_to.window(parentw)
		return elem
	
	def verify_create_problem_for_report(self, kwargs):
		logger.info("Executing_Create_Problem_by_priority()")
		'''application xpath'''
		app = self.driver.find_element_by_xpath('.//*[@id="reg_img_304316340"]')
		app.click()
		#time.sleep(3)
		'''Clicking on Problem Management -> New Problem'''
		WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located((By.LINK_TEXT, 'Problem Management')))
		prbmgmt = self.driver.find_element_by_link_text('Problem Management')
		prbmgmt.click()
		newprb = self.driver.find_element_by_link_text('New Problem')
		newprb.click()

		"""Populating the mandatory areas"""
		"""Filling Service"""
		WebDriverWait(self.driver, 50).until(
			expected_conditions.element_to_be_clickable((By.XPATH, "//textarea[@id='arid_WIN_3_303497300']")))
		service = self.driver.find_element_by_xpath("//textarea[@id='arid_WIN_3_303497300']")
		time.sleep(2)
		service.click()
		service.send_keys(kwargs['Service'])
		time.sleep(4)
		service.send_keys(Keys.ENTER)

		"""Filling Summary"""
		WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
			(By.XPATH, "//textarea[@id='arid_WIN_3_1000000000']")))
		summary = self.driver.find_element_by_xpath("//textarea[@id='arid_WIN_3_1000000000']")
		summary.click()
		time.sleep(1)
		summary.clear()
		summary.send_keys(kwargs['Summary'])
		summary.send_keys(Keys.ENTER)

		"""Filling Urgency"""
		urgencies = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_1000000162"]')
		urgencies.click()
		urgencies.send_keys(Keys.DOWN)
		urgencies.send_keys(kwargs['Urgency'])
		time.sleep(3)
		urgencies.send_keys(Keys.ENTER)
		# time.sleep(3)

		impact = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_1000000163"]')
		impact.click()
		impact.send_keys(Keys.DOWN)
		impact.send_keys(kwargs['Impact'])
		time.sleep(3)
		impact.send_keys(Keys.ENTER)
		# time.sleep(3)

		target_date = self.driver.find_element_by_xpath("//input[@id='arid_WIN_3_1000001571']")
		target_date.click()
		# target_date.send_keys(Keys.DOWN)
		target_date.send_keys(kwargs['Target_date'])
		time.sleep(3)
		target_date.send_keys(Keys.ENTER)


		assignedgroup = self.driver.find_element_by_xpath("//textarea[@id='arid_WIN_3_1000000217']")
		assignedgroup.click()
		assignedgroup.clear()
		assignedgroup.send_keys(kwargs['Assigned_group'])
		time.sleep(3)
		assignedgroup.send_keys(Keys.DOWN)
		assignedgroup.send_keys(Keys.ENTER)

		problem = self.driver.find_element_by_xpath('//*[@id="WIN_0_304248710"]/fieldset/div/dl/dd[5]/span[2]/a').text
		problemid = problem[:-6]

		""""Save buton click"""
		self.driver.find_element_by_xpath(
			"//a[@id='WIN_3_301614800']//div[@class='f1'][contains(text(),'Save')]").click()
		logger.info("Exiting Problem_creation()")
		return problemid
	
	def change_status_to_Under_Review_report(self, kwargs):
		logger.info("Executing_change_status_form_Draft_to_Under_Review_report()")

		"""Calling search_problem"""
		self.search_problem(kwargs['Problem_id'])

		"""Changing status from Draft to Under Review"""
		WebDriverWait(self.driver, 50).until(
			expected_conditions.presence_of_element_located((By.XPATH, '//*[@id="arid_WIN_3_7"]')))

		status = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_7"]')
		time.sleep(3)
		status.click()
		status.send_keys('Un')
		status.send_keys(Keys.ENTER)

		"""Saving"""
		WebDriverWait(self.driver, 50).until(
			expected_conditions.presence_of_element_located((By.XPATH, '//*[@id="WIN_3_301614800"]/div/div')))

		save = self.driver.find_element_by_xpath('//*[@id="WIN_3_301614800"]/div/div')
		save.click()
		return True
	
	def change_status_to_Assigned_report(self, kwargs):
		logger.info("Executing_change_status_form_Draft_to_Under_Review_report()")

		"""Calling search_problem"""
		self.search_problem(kwargs['Problem_id'])

		"""Changing status from Draft to Under Review"""
		WebDriverWait(self.driver, 50).until(
			expected_conditions.presence_of_element_located((By.XPATH, '//*[@id="arid_WIN_3_7"]')))

		status = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_7"]')
		time.sleep(3)
		status.click()
		status.send_keys('As')#Assigned
		status.send_keys(Keys.ENTER)

		"""Saving"""
		WebDriverWait(self.driver, 50).until(
			expected_conditions.presence_of_element_located((By.XPATH, '//*[@id="WIN_3_301614800"]/div/div')))

		save = self.driver.find_element_by_xpath('//*[@id="WIN_3_301614800"]/div/div')
		save.click()

		return True

	def change_status_to_Under_investigation_report(self, kwargs):
		logger.info("Executing_change_status_form_Draft_to_Under_Review_report()")

		"""Calling search_problem"""
		self.search_problem(kwargs['Problem_id'])

		"""Filling Assignee+"""
		WebDriverWait(self.driver, 50).until(
			expected_conditions.presence_of_element_located((By.XPATH, '//*[@id="arid_WIN_3_1000000218"]')))


		assign = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_1000000218"]')
		time.sleep(2)
		assign.click()
		assign.send_keys('SG Karthick')
		time.sleep(2)
		assign.send_keys(Keys.DOWN)
		assign.send_keys(Keys.ENTER)

		"""Changing status from Draft to Under Review"""
		WebDriverWait(self.driver, 50).until(
			expected_conditions.presence_of_element_located((By.XPATH, '//*[@id="arid_WIN_3_7"]')))

		status = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_7"]')
		time.sleep(3)
		status.click()
		status.send_keys('UnaU')#Under_investigation
		status.send_keys(Keys.ENTER)

		"""Saving"""
		WebDriverWait(self.driver, 50).until(
			expected_conditions.presence_of_element_located((By.XPATH, '//*[@id="WIN_3_301614800"]/div/div')))

		save = self.driver.find_element_by_xpath('//*[@id="WIN_3_301614800"]/div/div')
		save.click()

		return True

	def change_status_to_Pending_report(self, kwargs):
		logger.info("Executing_change_status_form_Draft_to_Under_Review_report()")

		"""Calling search_problem"""
		self.search_problem(kwargs['Problem_id'])

		"""Changing status from Draft to Pending"""
		WebDriverWait(self.driver, 50).until(
			expected_conditions.presence_of_element_located((By.XPATH, '//*[@id="arid_WIN_3_7"]')))

		status = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_7"]')
		time.sleep(3)
		status.click()
		status.send_keys('P')#Pending
		status.send_keys(Keys.ENTER)

		"""Filling status reason"""
		WebDriverWait(self.driver, 50).until(
			expected_conditions.presence_of_element_located((By.XPATH, '//*[@id="arid_WIN_3_1000000881"]')))

		sta = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_1000000881"]')
		time.sleep(2)
		sta.click()
		sta.send_keys('Client Action Required')
		sta.send_keys(Keys.ENTER)

		"""Saving"""
		WebDriverWait(self.driver, 50).until(
			expected_conditions.presence_of_element_located((By.XPATH, '//*[@id="WIN_3_301614800"]/div/div')))

		save = self.driver.find_element_by_xpath('//*[@id="WIN_3_301614800"]/div/div')
		save.click()

		return True

	def change_status_to_Completed_report(self, kwargs):
		logger.info("Executing_change_status_form_Draft_to_Under_Review_report()")

		status_obj = self.change_status_to_Under_Review_report(kwargs)

		"""Calling search_problem"""
		self.search_problem(kwargs['Problem_id'])


		"""Changing status from Draft to Pending"""
		WebDriverWait(self.driver, 50).until(
			expected_conditions.presence_of_element_located((By.XPATH, '//*[@id="arid_WIN_3_7"]')))

		status = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_7"]')
		time.sleep(3)
		status.click()
		status.send_keys('C')#Pending
		status.send_keys(Keys.ENTER)

		"""Filling CI"""
		WebDriverWait(self.driver, 50).until(
			expected_conditions.presence_of_element_located((By.XPATH, '//*[@id="arid_WIN_3_303497400"]')))

		ci = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_303497400"]')
		time.sleep(2)
		ci.click()
		ci.send_keys('test')

		"""Filling status reason"""
		WebDriverWait(self.driver, 50).until(
			expected_conditions.presence_of_element_located((By.XPATH, '//*[@id="arid_WIN_3_1000000881"]')))

		sta = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_1000000881"]')
		time.sleep(2)
		sta.click()
		sta.send_keys('Client Action Required')
		sta.send_keys(Keys.ENTER)

		"""Filling Assignee+"""
		WebDriverWait(self.driver, 50).until(
			expected_conditions.presence_of_element_located((By.XPATH, '//*[@id="arid_WIN_3_1000000218"]')))

		assign = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_1000000218"]')
		time.sleep(2)
		assign.click()
		assign.send_keys('SG Karthick')
		time.sleep(2)
		assign.send_keys(Keys.DOWN)
		assign.send_keys(Keys.ENTER)

		"""Saving"""
		WebDriverWait(self.driver, 50).until(
			expected_conditions.presence_of_element_located((By.XPATH, '//*[@id="WIN_3_301614800"]/div/div')))

		save = self.driver.find_element_by_xpath('//*[@id="WIN_3_301614800"]/div/div')
		save.click()

		if status_obj == False:
			return False
		else:
			return True


	def change_status_to_Closed_report(self, kwargs):
		logger.info("Executing_change_status_form_Draft_to_Under_Review_report()")

		status_obj = self.search_and_update_status_to_Under_investigation_for_report(kwargs)

		"""Calling search_problem"""
		self.search_problem(kwargs['Problem_id'])

		"""Changing status from Draft to Pending"""
		WebDriverWait(self.driver, 50).until(
			expected_conditions.presence_of_element_located((By.XPATH, '//*[@id="arid_WIN_3_7"]')))

		status = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_7"]')
		time.sleep(3)
		status.click()
		status.send_keys('Cc')#Closed
		status.send_keys(Keys.ENTER)

		"""Saving"""
		WebDriverWait(self.driver, 50).until(
			expected_conditions.presence_of_element_located((By.XPATH, '//*[@id="WIN_3_301614800"]/div/div')))

		save = self.driver.find_element_by_xpath('//*[@id="WIN_3_301614800"]/div/div')
		save.click()

		if status_obj == False:
			return False
		else:
			return True
	
	def config_problem_task_tab_by_priority(self, problemID):
		logger.info("Verify if Problem task tab can be configured for Show/Hide option")
		logger.info("Clicking on Application element")
		application = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
		application.click()
		logger.info("clicking on administrator console()")
		adminconsole = self.driver.find_element_by_xpath('//*[@id="FormContainer"]/div[5]/div/div[3]/a/span')
		adminconsole.click()
		applicationadminconsole = self.driver.find_element_by_xpath(
			'//*[@id="FormContainer"]/div[5]/div/div[3]/div/div/a/span')
		applicationadminconsole.click()
		logger.info("Selecting Custom Configuration tab")
		time.sleep(2)
		customconfigtab = self.driver.find_element_by_xpath('//*[@id="WIN_0_303635200"]/fieldset/dl/dd[3]/span[2]/a')
		customconfigtab.click()
		logger.info("Clicking on problem management")
		time.sleep(4)
		problemmanagement = self.driver.find_element_by_xpath('//*[@id="handlerTN0_119_0"]')
		problemmanagement.click()
		logger.info("clicking on advanced option")
		advanced = self.driver.find_element_by_xpath('//*[@id="handlerTN0_119_1"]')
		advanced.click()
		logger.info("clicking on problem management settings")
		Problemmgmtsettings = self.driver.find_element_by_xpath('//*[@id="titleTN0_123_2"]')
		Problemmgmtsettings.click()
		window_before = self.driver.window_handles[0]
		logger.info("click on open")
		open = self.driver.find_element_by_xpath('//*[@id="WIN_0_500007506"]/div/div')
		open.click()
		WebDriverWait(self.driver, 10).until(
			expected_conditions.number_of_windows_to_be(2))
		window_after = self.driver.window_handles[1]
		self.driver.switch_to.window(window_after)
		time.sleep(3)
		logger.info("click on show settings")
		showsettings = self.driver.find_element_by_xpath('//*[@id="WIN_0_303699800"]/div/div')
		showsettings.click()
		logger.info("click on the icon of show problem task tab")
		problemtask = self.driver.find_element_by_xpath('//*[@id="WIN_0_304298520"]/div/a/img')
		problemtask.click()
		logger.info("click on the value present in the dropdown")
		dropdownvalue = self.driver.find_element_by_xpath('/html/body/div[3]/div[2]/table/tbody/tr[1]/td[1]')
		dropdownvalue.click()
		time.sleep(2)
		logger.info("click on the icon of show problem categorization tab")
		showproblemcategorization = self.driver.find_element_by_xpath('//*[@id="WIN_0_304298510"]/div/a')
		showproblemcategorization.click()
		logger.info("click on the value present in the problem categorization tab")
		dropvalue = self.driver.find_element_by_xpath('html/body/div[3]/div[2]/table/tbody/tr[1]/td[1]')
		dropvalue.click()
		logger.info("click on addModify button")
		time.sleep(2)
		addmodifybutton = self.driver.find_element_by_xpath('//*[@id="WIN_0_303700400"]/div/div')
		addmodifybutton.click()
		logger.info("click on close button")
		closebutton = self.driver.find_element_by_xpath('//*[@id="WIN_0_301614900"]/div/div')
		closebutton.click()
		time.sleep(5)
		self.driver.switch_to.window(window_before)
		first_window = self.driver.window_handles[0]
		logger.info("click on home page ---> to access application element")
		homepage = self.driver.find_element_by_xpath('//*[@id="WIN_0_304248660"]/div/div')
		homepage.click()
		WebDriverWait(self.driver, 10).until(
			expected_conditions.number_of_windows_to_be(2))
		second_window = self.driver.window_handles[1]
		self.driver.switch_to.window(second_window)
		logger.info("Clicking on Application element")
		application = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
		application.click()
		logger.info("clicking on problem management()")
		problemmanagement = self.driver.find_element_by_link_text('Problem Management')
		problemmanagement.click()
		logger.info("click on search problem")
		searchproblem = self.driver.find_element_by_link_text('Search Problem')
		searchproblem.click()
		logger.info("Enter the problem id in the id field")
		time.sleep(3)
		problemid = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_1000000232"]')
		problemid.click()
		problemid.send_keys(problemID)
		logger.info("click on search button")
		searchbutton = self.driver.find_element_by_xpath('//*[@id="WIN_3_1002"]/div/div')
		searchbutton.click()
		time.sleep(3)
		self.driver.save_screenshot('D:\git\screenshots\prbtaskconfig.png')
		element = self.driver.find_element_by_xpath('//*[@id="WIN_3_302127600"]/div[2]/div[2]/div/dl/dd[2]/span[2]/a')
		categorization = element.text
		elementt = self.driver.find_element_by_xpath('//*[@id="WIN_3_302127600"]/div[2]/div[2]/div/dl/dd[3]/span[2]/a')
		tasks = elementt.text
		if (categorization == 'Categorization') and (tasks == 'Tasks'):
			logger.info("Both categorization and Task tab is present in the problem ticket console")
			return True
		elif (categorization == 'Categorization'):
			logger.info("categorization tab is present in the problem ticket console but task tab is not present in the ticket")
			return False
		elif (tasks == 'Tasks'):
			logger.info("Task tab is present in the problem ticket console but Categorization tab is not present in the ticket")
			return False
		else:
			logger.info("Both categorization and Task tab is not present in the ticket")
			return False


	def create_problem_ticket_gui(self, kwargs):
		try:
			for k in kwargs.keys():
				logger.info("arguments are {}{}".format(k, kwargs[k]))
			self.login_bmc()
			probleid = False
			probleid = self.create_priority_problem(kwargs)
		except BaseException as be:
			logger.fatal("Fatal exception occured in create_problem_ticket_gui() in {}".format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.bmc_logout()
			return probleid
	
	def config_problem_management_console(self, rulename, rulevalue):
		try:
			self.login_bmc()
			rulepath = ''
			if rulename == 'Assignment Engine Integration':
				rulepath = '//*[@id="WIN_0_rc1id301290300"]'
			elif rulename == 'Require Servise CI Related On Submit(Problem)':
				rulepath = '//*[@id="WIN_0_rc0id303515500"]'
			elif rulename == 'Require CI Related On Completed(Problem)':
				rulepath = '//*[@id="WIN_0_rc0id303515600"]'
			elif rulename == 'Require Servise CI Related On Submit(Known Error)':
				rulepath = '//*[@id="WIN_0_rc0id303946000"]'
			elif rulename == 'Require CI Related On Corrected(Known Error)':
				rulepath = '//*[@id="WIN_0_rc0id303946100"]'
			verify = False
			verify = self.set_rule(rulepath, rulevalue)
		except BaseException as be:
			logger.fatal("Fatal exception occured in config_problem_management_console() in {}".format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.bmc_logout()
			if not verify:
				raise BmcError("The values are not matching")
	
	def create_problem_relate_gui(self, kwargs):
		try:
			for k in kwargs.keys():
				logger.info("arguments are {}{}".format(k, kwargs[k]))
			self.login_bmc()
			probleid = False
			probleid = self.priority_problem_by_type(kwargs)
		except BaseException as be:
			logger.fatal("Fatal exception occured in create_problem_relate_gui() in {}".format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.bmc_logout()
			return probleid
	
	def create_problem_for_report(self, kwargs):
		try:
			self.login_bmc()
			problem_id = False
			problem_id = self.verify_create_problem_for_report(kwargs)
		except BaseException as be:
			logger.fatal('Fatal exception occured in change_Management_Final_stage() in {}'.format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.bmc_logout()
			return problem_id
	
	def search_and_update_status_to_Under_Review_for_report(self, kwargs):
		try:
			self.login_bmc()
			status = False
			status = self.change_status_to_Under_Review_report(kwargs)
		except BaseException as be:
			logger.fatal('Fatal exception occured in change_Management_Final_stage() in {}'.format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.bmc_logout()
			return status
	
	def search_and_update_status_to_Assigned_for_report(self, kwargs):
		try:
			self.login_bmc()
			status = False
			status = self.change_status_to_Assigned_report(kwargs)
		except BaseException as be:
			logger.fatal('Fatal exception occured in change_Management_Final_stage() in {}'.format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.bmc_logout()
			return status

	def search_and_update_status_to_Under_investigation_for_report(self, kwargs):
		try:
			self.login_bmc()
			status = False
			status = self.change_status_to_Under_investigation_report(kwargs)
		except BaseException as be:
			logger.fatal('Fatal exception occured in change_Management_Final_stage() in {}'.format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.bmc_logout()
			return status

	def search_and_update_status_to_Pending_for_report(self, kwargs):
		try:
			self.login_bmc()
			status = False
			status = self.change_status_to_Pending_report(kwargs)
		except BaseException as be:
			logger.fatal('Fatal exception occured in change_Management_Final_stage() in {}'.format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.bmc_logout()
			return status

	def search_and_update_status_to_Completed_for_report(self, kwargs):
		try:
			self.login_bmc()
			status = False
			status = self.change_status_to_Completed_report(kwargs)
		except BaseException as be:
			logger.fatal('Fatal exception occured in change_Management_Final_stage() in {}'.format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.bmc_logout()
			return status
	
	def search_and_update_status_to_Closed_for_report(self, kwargs):
		try:
			self.login_bmc()
			status = False
			status = self.change_status_to_Closed_report(kwargs)
		except BaseException as be:
			logger.fatal('Fatal exception occured in change_Management_Final_stage() in {}'.format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.bmc_logout()
			return status
	
	def config_problem_task_tab(self, problemID):
		try:
			self.login_bmc()
			problemtasktab = self.config_problem_task_tab_by_priority(problemID)
		except BaseException as be:
			logger.fatal("Fatal exception occured in config_problem_task_tab() in {}".format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.bmc_logout()
			return problemtasktab