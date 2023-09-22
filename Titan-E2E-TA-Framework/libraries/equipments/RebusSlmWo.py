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


class BmcRebusSlmWo(Vmm):
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
	
	def search_work_order_template(self, summary):
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
		summary_obj.send_keys(summary)  # 'Password Reset'
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
		
		"""Validation part"""
		
		work_order_list = []
		"""Getting Work Order Detail, """
		logger.info('Work Order Detail')
		work_order_list.append(
			self.driver.find_element_by_xpath('//*[@id="arid_WIN_1_1000003299"]').get_attribute('value'))
		work_order_list.append(
			self.driver.find_element_by_xpath('//*[@id="arid_WIN_1_300077001"]').get_attribute('value'))
		work_order_list.append(
			self.driver.find_element_by_xpath('//*[@id="arid_WIN_1_1000000000"]').get_attribute('value'))
		work_order_list.append(
			self.driver.find_element_by_xpath('//*[@id="arid_WIN_1_1000000181"]').get_attribute('value'))
		work_order_list.append(
			self.driver.find_element_by_xpath('//*[@id="arid_WIN_1_7"]').get_attribute('value'))
		time.sleep(2)
		"""Categoration"""
		self.driver.find_element_by_xpath('//*[@id="WIN_1_301389366"]/div[2]/div[2]/div/dl/dd[2]/span[2]/a').click()
		time.sleep(2)
		work_order_list.append(
			self.driver.find_element_by_xpath('//*[@id="arid_WIN_1_1000000001"]').get_attribute('value'))
		work_order_list.append(
			self.driver.find_element_by_xpath('//*[@id="arid_WIN_1_1000000063"]').get_attribute('value'))
		work_order_list.append(
			self.driver.find_element_by_xpath('//*[@id="arid_WIN_1_1000000064"]').get_attribute('value'))
		work_order_list.append(
			self.driver.find_element_by_xpath('//*[@id="arid_WIN_1_1000000065"]').get_attribute('value'))
		work_order_list.append(
			self.driver.find_element_by_xpath('//*[@id="arid_WIN_1_1000001270"]').get_attribute('value'))
		work_order_list.append(
			self.driver.find_element_by_xpath('//*[@id="arid_WIN_1_1000001271"]').get_attribute('value'))
		work_order_list.append(
			self.driver.find_element_by_xpath('//*[@id="arid_WIN_1_1000001272"]').get_attribute('value'))
		work_order_list.append(
			self.driver.find_element_by_xpath('//*[@id="arid_WIN_1_1000002268"]').get_attribute('value'))
		"""Request Manager"""
		bt = self.driver.find_element_by_xpath('//*[@id="WIN_1_1000000015"]/a')
		bt.click()
		bt.send_keys(Keys.DOWN)
		time.sleep(2)
		work_order_list.append(
			self.driver.find_element_by_xpath('/html/body/div[3]/div[2]/table/tbody/tr/td[1]').text)
		sc = self.driver.find_element_by_xpath('/html/body/div[3]/div[2]/table/tbody/tr/td[1]')
		sc.click()
		work_order_list.append(
			self.driver.find_element_by_xpath('/html/body/div[4]/div[2]/table/tbody/tr[15]/td[1]').text)
		so = self.driver.find_element_by_xpath('/html/body/div[4]/div[2]/table/tbody/tr[15]/td[1]')
		so.click()
		time.sleep(2)
		work_order_list.append(
			self.driver.find_element_by_xpath('//*[@id="arid_WIN_1_1000000015"]').get_attribute('value'))
		"""Request Assignee"""
		time.sleep(2)
		rs = self.driver.find_element_by_xpath('//*[@id="WIN_1_1000003229"]/a')
		rs.click()
		rs.send_keys(Keys.DOWN)
		time.sleep(2)
		work_order_list.append(
			self.driver.find_element_by_xpath('/html/body/div[3]/div[2]/table/tbody/tr/td[1]').text)
		time.sleep(2)
		sc1 = self.driver.find_element_by_xpath('/html/body/div[3]/div[2]/table/tbody/tr/td[1]')
		sc1.click()
		work_order_list.append(
			self.driver.find_element_by_xpath('/html/body/div[4]/div[2]/table/tbody/tr[15]/td[1]').text)
		so1 = self.driver.find_element_by_xpath('/html/body/div[4]/div[2]/table/tbody/tr[15]/td[1]')
		so1.click()
		work_order_list.append(
			self.driver.find_element_by_xpath('//*[@id="arid_WIN_1_1000000015"]').get_attribute('value'))
		details = self.driver.find_element_by_xpath('//*[@id="WIN_1_301389366"]/div[2]/div[2]/div/dl/dd[5]/span[2]/a')
		details.click()
		time.sleep(2)
		work_order_list.append(
			self.driver.find_element_by_xpath('//*[@id="arid_WIN_1_300070001"]').get_attribute('value'))
		
		username = self.driver.find_element_by_xpath('//*[@id="arid_WIN_1_300070002"]').get_attribute('value')
		password = self.driver.find_element_by_xpath('//*[@id="arid_WIN_1_300070003"]').get_attribute('value')
		email = self.driver.find_element_by_xpath('//*[@id="arid_WIN_1_300070004"]').get_attribute('value')
		
		logger.info("username = {}".format(username))
		logger.info("password = {}".format(password))
		logger.info("email = {}".format(email))
		
		matching = True
		if username == '':
			matching = False
		elif password == '':
			matching = False
		elif email == '':
			matching = False
		logger.info('work order list: {}'.format(work_order_list))
		return work_order_list, matching
	
	def search_work_order_and_validate_SLM(self, summary):
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
		summary_obj.send_keys(summary)#'Password Reset'

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
		"""Details"""
		self.driver.find_element_by_xpath('//*[@id="WIN_1_303669700"]/div[2]/div').click()

		"""Window poped"""
		time.sleep(4)
		"""->window[2]"""
		window2 = self.driver.window_handles[2]
		self.driver.switch_to.window(window2)

		self.driver.maximize_window()

		time.sleep(4)
		"""Validation part"""
		service_target_list = []
		"""Getting SVT title, """
		service_target_list.append(self.driver.find_element_by_xpath('//*[@id="T300427600"]//tbody//tr[2]//td[1]//nobr//span').text)
		service_target_list.append(self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[2]/td[2]/nobr/span').text)
		service_target_list.append(self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[2]/td[3]/nobr').text)
		service_target_list.append(self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[2]/td[4]/nobr').text)
		service_target_list.append(self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[2]/td[5]/nobr/span').text)
		service_target_list.append(self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[2]/td[6]/nobr').text)
		service_target_list.append(self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[2]/td[7]/nobr/span').text)

		time.sleep(3)
		"""Click Close"""
		self.driver.find_element_by_xpath('//*[@id="WIN_0_304019100"]/div/div').click()

		time.sleep(3)
		"""back to window[1]"""
		self.driver.switch_to.window(window1)

		return service_target_list
	
	def Workorder_creation(self, kwargs):
		logger.info("Execuitng incident_creation()")
		""" Clicking on Application"""
		appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
		appl.click()

		"""Clicking on Incident Management -> New Incident"""
		incmgmt = self.driver.find_element_by_link_text('Service Request Management')
		incmgmt.click()
		incmgmtcon = self.driver.find_element_by_link_text('New Work Order')
		incmgmtcon.click()

		"""Filling and Submitting Incident Creation Form"""
		WebDriverWait(self.driver, 20).until(
			expected_conditions.element_to_be_clickable((By.XPATH, "//textarea[@id='arid_WIN_3_303530000']")))
		customer = self.driver.find_element_by_id("arid_WIN_3_303530000")
		customer.click()
		window_before = self.driver.window_handles[0]
		self.driver.find_element_by_xpath('//*[@id="reg_img_304248530"]').click()
		window_after = self.driver.window_handles[1]
		self.driver.switch_to.window(window_after)
		time.sleep(5)
		customer = self.driver.find_element_by_xpath('//*[@id="arid_WIN_0_1000000018"]').send_keys(kwargs['Customer'])
		#customer.send_keys(kwargs['Customer'])
		time.sleep(2)
		self.driver.find_element_by_xpath('//*[@id="WIN_0_301867800"]/div/div').click()
		time.sleep(3)
		self.driver.find_element_by_xpath('//*[@id="T301394438"]/tbody/tr[2]/td[1]/nobr/span').click()
		time.sleep(3)
		self.driver.find_element_by_xpath('//*[@id="WIN_0_301912800"]/div/div').click()

		time.sleep(3)
		self.driver.switch_to.window(window_before)
		time.sleep(3)
		summary = self.driver.find_element_by_id("arid_WIN_3_1000000000")
		summary.send_keys(kwargs['Summary'])

		service = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_200000020"]')
		service.click()
		service.send_keys(kwargs['Service'])
		time.sleep(3)
		service.send_keys(Keys.DOWN)
		service.send_keys(Keys.ENTER)

		prio = self.driver.find_element_by_xpath('//input[@id = "arid_WIN_3_1000000164"]')
		prio.click()
		prio.send_keys(kwargs['Priority'])
		time.sleep(3)
		service.send_keys(Keys.DOWN)
		service.send_keys(Keys.ENTER)



		assignedgroup = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_1000000015"]')
		assignedgroup.click()
		assignedgroup.send_keys(kwargs['Assigned_group'])
		time.sleep(3)
		assignedgroup.send_keys(Keys.DOWN)
		assignedgroup.send_keys(Keys.ENTER)

		status = self.driver.find_element_by_xpath('//div[@class="selection"]/input[@id="arid_WIN_3_7"]')
		status.click()
		status.send_keys(Keys.DOWN)
		status.send_keys(kwargs['Status'])
		status.send_keys(Keys.ENTER)

		logger.info("Workorder Created successfully")
		inqw=self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_1000000182"]')
		workid = inqw.get_attribute("value")
		logger.info("Exiting incident_creation()")

		saveinc = self.driver.find_element_by_xpath('//*[@id="WIN_3_300000300"]/div')
		saveinc.click()
		return workid
	
	def Workorder_Search(self, kwargs):
		logger.info("Execuitng incident_creation()")
		""" Clicking on Application"""
		appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
		appl.click()

		"""Clicking on Incident Management -> New Incident"""
		incmgmt = self.driver.find_element_by_link_text('Service Request Management')
		incmgmt.click()
		incmgmtcon = self.driver.find_element_by_link_text('Search Work Order')
		incmgmtcon.click()

		"""Filling and Submitting Incident Creation Form"""
		WebDriverWait(self.driver, 20).until(
			expected_conditions.element_to_be_clickable((By.XPATH, "//textarea[@id='arid_WIN_3_303530000']")))

		#self.driver.find_element_by_xpath('//*[@id="Toolbar"]/table/tbody/tr/td[2]/a[1]/span').click()
		time.sleep(2)
		search=self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_1000000182"]').send_keys(kwargs['workiid'])
		"""Search"""
		self.driver.find_element_by_xpath('//*[@id="WIN_3_1002"]/div/div').click()
		inqw = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_1000000182"]')
		workid = inqw.get_attribute("value")
		logger.info("Exiting incident_creation()")
		time.sleep(4)

		"""Change status"""

		status = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_7"]')
		status.click()
		status.send_keys(Keys.DOWN)
		status.send_keys(kwargs['status'])
		status.send_keys(Keys.ENTER)
		"""Save"""

		saveinc = self.driver.find_element_by_xpath('//*[@id="WIN_3_300000300"]/div')
		saveinc.click()

		return workid
	
	def verify_work_order_template(self, summary):
		try:
			self.login_bmc()
			flag = False
			work_order_list, verify = self.search_work_order_template(summary)
			"""Verifying list with BMCCconstant"""
			
			for i in work_order_list:
				count = 0
				for k, v in BMCconstant.BMCContstants.WorkOrder.items():
					if i != v:
						flag = False
					else:
						flag = True
						break
					count += 1
				if count == len(work_order_list) and flag == False:
					flag = False
					break
		except BaseException as be:
			logger.fatal("Fatal exception occured in search_work_order() in {}".format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.bmc_logout()
			if not verify:
				raise BmcError("Validation Failed")
			return flag
	
	def search_work_order_and_validate_slm_fun(self, summary):
		try:
			self.login_bmc()
			flag = False
			servicetarget_list = self.search_work_order_and_validate_SLM(summary)
			"""Verifying list with BMCCconstant"""
			for i in servicetarget_list:
				count = 0
				for k, v in BMCconstant.BMCContstants.SLMServiceTags.items():
					if i != v:
						flag = False
					else:
						flag = True
						break
					count += 1
				if count == len(servicetarget_list) and flag == False:
					flag = False
					break
			if flag == True:
				logger.info('Service targets is varified in the pop up')
		except BaseException as be:
			logger.fatal("Fatal exception occured in search_work_order() in {}".format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.bmc_logout()
			return flag
	
	def create_priority_workorder_gui(self, kwargs):
		try:
			for k in kwargs.keys():
				logger.info("arguments are {}{}".format(k, kwargs[k]))
			self.login_bmc()
			incidentid = False
			incidentid = self.Workorder_creation(kwargs)
		except BaseException as be:
			logger.fatal("Fatal exception occured in create_priority_incident_gui() in {}".format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.bmc_logout()
			return incidentid
	
	def search_priority_workorder_gui(self, kwargs):
		try:
			for k in kwargs.keys():
				logger.info("arguments are {}{}".format(k, kwargs[k]))
			self.login_bmc()
			incidentid = False
			incidentid = self.Workorder_Search(kwargs)
		except BaseException as be:
			logger.fatal("Fatal exception occured in create_priority_incident_gui() in {}".format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.bmc_logout()
			return incidentid
