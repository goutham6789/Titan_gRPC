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


class IncidentManagement(Vmm):
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
	
	def workinfonotes(self, kwargs):
	#try:
		logger.info("Executing workinfonotes()")
		appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')

		appl.click()

		srchincmgmt = self.driver.find_element_by_link_text('Incident Management')
		srchincmgmt.click()
		searchinc = self.driver.find_element_by_link_text('Search Incident')
		searchinc.click()
		time.sleep(3)

		WebDriverWait(self.driver, 100).until(
			expected_conditions.element_to_be_clickable((By.XPATH, '//input[@id="arid_WIN_3_1000000164"]')))
		prio = self.driver.find_element_by_xpath('//input[@id="arid_WIN_3_1000000164"]')
		prio.click()
		prio.send_keys(Keys.DOWN)
		prio.send_keys(kwargs['Priority'])
		prio.send_keys(Keys.ENTER)
		priority = prio.get_attribute("value")
		logger.info("Priority of Incident ={} ".format(priority))

		self.driver.find_element_by_xpath('//*[@id="WIN_3_1002"]/div/div').click()
		time.sleep(5)

		graddbtn = self.driver.find_element_by_id("WIN_3_303602800")
		graddbtn.send_keys(Keys.SPACE)


		WebDriverWait(self.driver, 20).until(
			expected_conditions.element_to_be_clickable((By.XPATH, '//textarea[@id="arid_WIN_3_304247080"]')))
		notestext = self.driver.find_element_by_xpath('//textarea[@id="arid_WIN_3_304247080"]')
		notestext.send_keys(kwargs['NotesText'])
		notestextvalue = notestext.get_attribute("value")
		logger.info("Notes Entered by User = {} ".format(notestextvalue))

		self.driver.find_element_by_xpath('//*[@id="WIN_3_304247070"]/div/a/span').click()

		workinfotype = self.driver.find_element_by_xpath('//input[@id="arid_WIN_3_304247210"]')
		# workinfotype.click()
		workinfotype.send_keys(kwargs['WorkInfoType'])
		time.sleep(3)
		workinfotype.send_keys(Keys.DOWN)
		workinfotype.send_keys(Keys.DOWN)
		workinfotype.send_keys(Keys.DOWN)
		workinfotype.send_keys(Keys.DOWN)
		workinfotype.send_keys(Keys.ENTER)

		self.driver.find_element_by_xpath('//input[@id="WIN_3_rc0id304247260"]').click()
		self.driver.find_element_by_xpath('//input[@id="WIN_3_rc1id1000000761"]').click()
		self.driver.save_screenshot('C:/Python27/Results/Screenshots/SM_IM_E2E_042_WorkInfo_Details.png')

		self.driver.find_element_by_xpath('//*[@id="WIN_3_304247110"]/div/div').click()
		time.sleep(5)
		self.driver.save_screenshot('C:/Python27/Results/Screenshots/SM_IM_E2E_042_WorkInfo_Notesadd.png')

		""" Getting in theIncident ID   """
		window_before = self.driver.window_handles[0]
		# print window_before
		self.driver.find_element_by_xpath('//div[@id= "WIN_3_303579500"]').click()
		WebDriverWait(self.driver, 10).until(
			expected_conditions.number_of_windows_to_be(2))
		window_after = self.driver.window_handles[1]
		self.driver.switch_to.window(window_after)
		# print window_after
	
		inqw = self.driver.find_element_by_xpath('//textarea[@id ="arid_WIN_0_303738000"]')
		time.sleep(3)
		incid = inqw.get_attribute("value")
		logger.info("Incident ID ={} ".format(incid))
		time.sleep(5)
		self.driver.close()
		self.driver.switch_to.window(window_before)
		logger.info("Exiting workinfonotes()")
		return notestextvalue
	
	def incident_creation(self, kwargs):
		logger.info("Execuitng incident_creation()")
		""" Clicking on Application"""
		appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
		appl.click()

		"""Clicking on Incident Management -> New Incident"""
		incmgmt = self.driver.find_element_by_link_text('Incident Management')
		incmgmt.click()
		incmgmtcon = self.driver.find_element_by_link_text('New Incident')
		incmgmtcon.click()

		"""Filling and Submitting Incident Creation Form"""
		WebDriverWait(self.driver, 20).until(
			expected_conditions.element_to_be_clickable((By.XPATH, "//textarea[@id='arid_WIN_3_303530000']")))
		customer = self.driver.find_element_by_id("arid_WIN_3_303530000")
		customer.click()
		# customer.send_keys("Karthik.s_g@nokia.com")
		customer.send_keys(kwargs['Customer'])
		time.sleep(2)
		customer.send_keys(Keys.DOWN)
		customer.send_keys(Keys.ENTER)

		summary = self.driver.find_element_by_id("arid_WIN_3_1000000000")
		summary.send_keys(kwargs['Summary'])

		service = self.driver.find_element_by_xpath('//textarea[@id="arid_WIN_3_303497300"]')
		service.click()
		service.send_keys(kwargs['Service'])
		time.sleep(3)
		service.send_keys(Keys.DOWN)
		service.send_keys(Keys.ENTER)

		impact = self.driver.find_element_by_xpath('//div[@class="selection"]/input[@id="arid_WIN_3_1000000163"]')
		impact.click()
		impact.send_keys(Keys.DOWN)
		impact.send_keys(kwargs['Impact'])
		impact.send_keys(Keys.ENTER)

		urgency = self.driver.find_element_by_xpath('//div[@class="selection"]/input[@id="arid_WIN_3_1000000162"]')
		urgency.click()
		urgency.send_keys(Keys.DOWN)
		urgency.send_keys(kwargs['Urgency'])
		urgency.send_keys(Keys.ENTER)

		prio = self.driver.find_element_by_xpath('//input[@id = "arid_WIN_3_1000000164"]')
		priority = prio.get_attribute('value')
		logger.info("Priority = {}".format(priority))

		inctype = self.driver.find_element_by_xpath('//div[@class="selection"]/input[@id="arid_WIN_3_1000000099"]')
		inctype.click()
		inctype.send_keys(Keys.DOWN)
		inctype.send_keys(kwargs['Incident_type'])
		inctype.send_keys(Keys.ENTER)

		assignedgroup = self.driver.find_element_by_xpath('//textarea[@id="arid_WIN_3_1000000217"]')
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
		saveinc = self.driver.find_element_by_xpath('//a[@id="WIN_3_301614800"]/div[@class="btntextdiv"]/div[@class="f1"]')
		saveinc.click()

		logger.info("Incident Created successfully")

		time.sleep(5)
		"""Clicking on Applications"""

		appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')

		appl.click()

		""" Clicking on Incident Management Console"""
		incmgmt = self.driver.find_element_by_link_text('Incident Management')
		incmgmt.click()
		incmgmtcon = self.driver.find_element_by_link_text('Incident Management Console')
		incmgmtcon.click()

		time.sleep(6)
		"""Filtering on Submitted by me Incidents"""
		show = self.driver.find_element_by_xpath('//*[@id="WIN_4_303174300"]/div/a')
		show.click()
		show.send_keys(Keys.DOWN)
		show.send_keys(kwargs['Filter'])
		show.send_keys(Keys.ENTER)
		time.sleep(5)

		"""Clicking on the First Incident from the List"""

		incelem = self.driver.find_element_by_xpath('//*[@id="T302087200"]/tbody/tr[2]/td[1]/nobr/span')
		action = ActionChains(self.driver)
		action.double_click(incelem)
		action.perform()

		""" Getting the Incident ID """

		time.sleep(3)
		window_before = self.driver.window_handles[0]
		# print window_before
		self.driver.find_element_by_xpath('//div[@id= "WIN_3_303579500"]').click()
		WebDriverWait(self.driver, 10).until(
			expected_conditions.number_of_windows_to_be(2))
		window_after = self.driver.window_handles[1]
		self.driver.switch_to.window(window_after)
		# print window_after

		inqw = self.driver.find_element_by_xpath('//textarea[@id ="arid_WIN_0_303738000"]')
		time.sleep(3)
		incid = inqw.get_attribute("value")
		'''
		if incid is None:
			logger.error("Unable to get incident ID after creation")
			raise BmcError('Failed to create incident via GUI in BMC {}'.format(self.name))
		logger.info("Incident ID ={} ".format(incid))
		time.sleep(5)
		'''
		"""Logout Application"""
		self.driver.close()
		self.driver.switch_to.window(window_before)
		logger.info("Exiting incident_creation()")
		return incid
	
	def search_incident_by_priority(self, priority):
		logger.info("Executing search_incident_by_priority()")
		appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
		appl.click()
		time.sleep(3)
		"""Clicking on Incident Management -> Search Incident"""
		srchincmgmt = self.driver.find_element_by_link_text('Incident Management')
		srchincmgmt.click()
		searchinc = self.driver.find_element_by_link_text('Search Incident')
		searchinc.click()
		time.sleep(3)
		logger.info("Step1")
		WebDriverWait(self.driver, 20).until(
			expected_conditions.element_to_be_clickable((By.XPATH, '//input[@id="arid_WIN_3_1000000164"]')))
		prio = self.driver.find_element_by_xpath('//input[@id="arid_WIN_3_1000000164"]')
		prio.click()
		prio.send_keys(Keys.DOWN)
		prio.send_keys(priority)
		prio.send_keys(Keys.ENTER)
		selected_priority = prio.get_attribute("value")
		logger.info("Priority of Incident ={} ".format(selected_priority))

		self.driver.find_element_by_xpath('//*[@id="WIN_3_1002"]/div/div').click()
		time.sleep(5)

		""" Getting in theIncident ID   """
		window_before = self.driver.window_handles[0]
		# print window_before
		self.driver.find_element_by_xpath('//div[@id= "WIN_3_303579500"]').click()
		WebDriverWait(self.driver, 10).until(
			expected_conditions.number_of_windows_to_be(2))
		window_after = self.driver.window_handles[1]
		self.driver.switch_to.window(window_after)
		# print window_after

		inqw = self.driver.find_element_by_xpath('//textarea[@id ="arid_WIN_0_303738000"]')
		time.sleep(3)
		incid = inqw.get_attribute("value")
		logger.info("Incident ID ={} ".format(incid))
		time.sleep(5)
		self.driver.close()
		self.driver.switch_to.window(window_before)
		logger.info("Exiting search_incident_by_priority()")
		return incid
	
	def incident_report_export(self, kwargs):
		logger.info("Executing customer_contact_search()")
		""" Clicking on Application"""

		appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
		appl.click()
		time.sleep(3)

		"""Clicking on Incident Management -> New Incident"""
		srchincmgmt = self.driver.find_element_by_link_text('Incident Management')
		srchincmgmt.click()
		searchinc = self.driver.find_element_by_link_text('Search Incident')
		searchinc.click()
		time.sleep(3)

		WebDriverWait(self.driver, 20).until(
			expected_conditions.element_to_be_clickable((By.XPATH, '//input[@id="arid_WIN_3_1000000164"]')))
		prio = self.driver.find_element_by_xpath('//input[@id="arid_WIN_3_1000000164"]')
		prio.click()
		prio.send_keys(Keys.DOWN)
		prio.send_keys(kwargs['Priority'])
		prio.send_keys(Keys.ENTER)
		priority = prio.get_attribute("value")
		logger.info("Priority of Incident ={} ".format(priority))

		self.driver.find_element_by_xpath('//*[@id="WIN_3_1002"]/div/div').click()
		time.sleep(5)


		self.driver.save_screenshot('C:/Python27/Results/Screenshots/SM_IM_E2E_017_IncidentReportExport_AfterSearch.png')

		WebDriverWait(self.driver, 20).until(
			expected_conditions.element_to_be_clickable((By.XPATH, '//*[@id="T1020"]/tbody/tr[2]/td[1]/nobr/span')))
		incelemsearch = self.driver.find_element_by_xpath('//*[@id="T1020"]/tbody/tr[2]/td[1]/nobr/span')
		action = ActionChains(self.driver)
		action.context_click(incelemsearch)
		action.perform()
		action.move_to_element(incelemsearch)
		action.send_keys(Keys.ARROW_DOWN).perform()
		action.send_keys(Keys.ENTER).perform()

		window_before = self.driver.window_handles[0]
		# print window_before
		WebDriverWait(self.driver, 10).until(
			expected_conditions.number_of_windows_to_be(2))
		window_after = self.driver.window_handles[1]
		self.driver.switch_to.window(window_after)

		WebDriverWait(self.driver, 20).until(expected_conditions.element_to_be_clickable(
			(By.XPATH, '//*[@id="T93250"]/tbody/tr[4]/td[2]/nobr/span')))
		self.driver.find_element_by_xpath('//*[@id="T93250"]/tbody/tr[4]/td[2]/nobr/span').click()
		self.driver.find_element_by_xpath('//*[@id="reg_img_93272"]').click()
		iFrame = self.driver.find_elements_by_tag_name('iframe')[1]
		self.driver.switch_to_frame(iFrame)
		logger.info("connected to second frame")
		strtdate = self.driver.find_element_by_xpath('//div[@id="parameterDialogdialogContentContainer"]/div[@class = "birtviewer_parameter_dialog"]/table/tbody/tr/td/table/tbody/tr[4]/td/input[@id= "Start Date"]')
		strtdate.send_keys(kwargs['Startdate'])
		endtdate = self.driver.find_element_by_xpath('//*[@id="End Date"]')
		endtdate.send_keys(kwargs['Enddate'])
		self.driver.find_element_by_xpath('//*[@id="parameterDialogokButton"]/input').click()
		time.sleep(5)
		report = self.driver.find_element_by_xpath('//*[@id="AUTOGENBOOKMARK_7"]')
		reportname = report.get_attribute("value")
		logger.info("Report to be exported = {} ".format(reportname))
		self.driver.save_screenshot('C:/Python27/Results/Screenshots/SM_IM_E2E_017_IncidentReportExport_AfterReportgen.png')
		self.driver.find_element_by_xpath('//*[@id="toolbar"]/table/tbody/tr[2]/td[4]/input')
		self.driver.find_element_by_xpath('//*[@id="exportReportDialogokButton"]/input')
		self.driver.save_screenshot('C:/Python27/Results/Screenshots/SM_IM_E2E_017_IncidentReportExport_AfterExport.png')

		self.driver.close()

		self.driver.switch_to.window(window_before)
		logger.info("Exiting incident_report_export()")
		return True
	
	def close_incident(self, kwargs):
		logger.info("Executing close_incident()")
		appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
		appl.click()

		""" Clicking on Search Incident"""
		srchincmgmt = self.driver.find_element_by_link_text('Incident Management')
		srchincmgmt.click()
		searchinc = self.driver.find_element_by_link_text('Search Incident')
		searchinc.click()
		time.sleep(3)

		#self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_7"]').click()

		WebDriverWait(self.driver, 20).until(expected_conditions.element_to_be_clickable((By.XPATH, '//*[@id="arid_WIN_3_1000000217"]')))
		agroup = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_1000000217"]')
		agroup.click()
		agroup.send_keys(kwargs['AssignedGroup'])
		time.sleep(3)
		agroup.send_keys(Keys.DOWN)
		agroup.send_keys(Keys.ENTER)
		time.sleep(2)

		self.driver.find_element_by_xpath('//*[@id="WIN_3_1002"]/div/div').click()

		time.sleep(3)

		self.driver.save_screenshot('C:/Python27/Results/Screenshots/SM_IM_E2E_018_ResolvedIncident_BeforeClose.png')

		nstatus = self.driver.find_element_by_xpath('//div[@class="selection"]/input[@id="arid_WIN_3_7"]')
		nstatus.click()
		nstatus.send_keys(Keys.DOWN)
		nstatus.send_keys(kwargs['Nstatus'])
		nstatus.send_keys(Keys.ENTER)
		time.sleep(3)
		assignee = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_1000000218"]')
		assignee.click()
		assignee.send_keys(kwargs['Assignee'])
		time.sleep(3)
		assignee.send_keys(Keys.DOWN)
		assignee.send_keys(Keys.ENTER)
		time.sleep(3)
		self.driver.find_element_by_xpath('//*[@id="WIN_3_301614800"]/div/div').click()

		time.sleep(3)

		self.driver.save_screenshot('C:/Python27/Results/Screenshots/SM_IM_E2E_018_ResolvedIncident_AfterClose.png')

		""" Getting in theIncident ID   """
		window_before = self.driver.window_handles[0]
		# print window_before
		self.driver.find_element_by_xpath('//div[@id= "WIN_3_303579500"]').click()
		WebDriverWait(self.driver, 10).until(
			expected_conditions.number_of_windows_to_be(2))
		window_after = self.driver.window_handles[1]
		self.driver.switch_to.window(window_after)
		# print window_after

		inqw = self.driver.find_element_by_xpath('//textarea[@id ="arid_WIN_0_303738000"]')
		time.sleep(3)
		incid = inqw.get_attribute("value")
		logger.info("Closed Incident ID ={} ".format(incid))
		time.sleep(5)
		self.driver.close()
		self.driver.switch_to.window(window_before)
		logger.info("Exiting close_incident()")
		return incid
	
	def customer_contact_search(self, kwargs):
		logger.info("Executing customer_contact_search()")
		""" Clicking on Application"""
		appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
		appl.click()

		"""Clicking on Incident Management -> New Incident"""
		incmgmt = self.driver.find_element_by_link_text('Incident Management')
		incmgmt.click()
		incmgmtcon = self.driver.find_element_by_link_text('New Incident')
		incmgmtcon.click()

		"""Filling Customer Contact details"""
		WebDriverWait(self.driver, 20).until(
			expected_conditions.element_to_be_clickable((By.XPATH, "//textarea[@id='arid_WIN_3_303530000']")))
		customer = self.driver.find_element_by_id("arid_WIN_3_303530000")
		customer.click()
		# customer.send_keys("Karthik.s_g@nokia.com")
		customer.send_keys(kwargs['Customer'])
		time.sleep(2)
		customer.send_keys(Keys.DOWN)
		customer.send_keys(Keys.ENTER)
		time.sleep(2)

		contact = self.driver.find_element_by_id("arid_WIN_3_303497600")
		contact.click()
		contact.send_keys(kwargs['Contact'])
		time.sleep(2)
		contact.send_keys(Keys.DOWN)
		contact.send_keys(Keys.ENTER)
		time.sleep(2)


		summary = self.driver.find_element_by_id("arid_WIN_3_1000000000")
		summary.send_keys(kwargs['Summary'])

		service = self.driver.find_element_by_xpath('//textarea[@id="arid_WIN_3_303497300"]')
		service.click()
		service.send_keys(kwargs['Service'])
		time.sleep(3)
		service.send_keys(Keys.DOWN)
		service.send_keys(Keys.ENTER)

		impact = self.driver.find_element_by_xpath('//div[@class="selection"]/input[@id="arid_WIN_3_1000000163"]')
		impact.click()
		impact.send_keys(Keys.DOWN)
		impact.send_keys(kwargs['Impact'])
		impact.send_keys(Keys.ENTER)

		urgency = self.driver.find_element_by_xpath('//div[@class="selection"]/input[@id="arid_WIN_3_1000000162"]')
		urgency.click()
		urgency.send_keys(Keys.DOWN)
		urgency.send_keys(kwargs['Urgency'])
		urgency.send_keys(Keys.ENTER)

		prio = self.driver.find_element_by_xpath('//input[@id = "arid_WIN_3_1000000164"]')
		priority = prio.get_attribute("value")
		logger.info("Priority = {}".format(priority))

		inctype = self.driver.find_element_by_xpath('//div[@class="selection"]/input[@id="arid_WIN_3_1000000099"]')
		inctype.click()
		inctype.send_keys(Keys.DOWN)
		inctype.send_keys(kwargs['Incident_type'])
		inctype.send_keys(Keys.ENTER)

		assignedgroup = self.driver.find_element_by_xpath('//textarea[@id="arid_WIN_3_1000000217"]')
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

		saveinc = self.driver.find_element_by_xpath(
			'//a[@id="WIN_3_301614800"]/div[@class="btntextdiv"]/div[@class="f1"]')
		saveinc.click()


		logger.info("Incident Created successfully")
		#setcustomer=customer.get_attribute("Value")
		#logger.info("Contact set by user = {}".format(setcustomer))
		#setcontact=contact.get_attribute("Value")
		#logger.info("Contact set by user = {}".format(setcontact))
		""" Getting the Incident ID """

		incid = self.driver.find_element_by_xpath('//*[@id="WIN_0_304248710"]/fieldset/div/dl/dd[5]/span[2]/a').text

		incid = incid[:-6]
		logger.info("Incident ID ={} ".format(incid))

		logger.info("Exiting customer_contact_search()")
		return incid
	
	def verify_incident_mgmt_settings(self, kwargs):
		""" Clicking on Application"""
		appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
		appl.click()

		"""Clicking on Administrator Console  -> Application Administration Console"""
		admcon = self.driver.find_element_by_link_text('Administrator Console')
		admcon.click()
		appadmcon = self.driver.find_element_by_link_text('Application Administration Console')
		appadmcon.click()

		"""Clicking on Custom Configuration"""
		WebDriverWait(self.driver, 20).until(expected_conditions.element_to_be_clickable((By.XPATH, '//*[@id="WIN_0_303635200"]/fieldset/dl/dd[3]/span[2]')))
		custconfig = self.driver.find_element_by_xpath('//*[@id="WIN_0_303635200"]/fieldset/dl/dd[3]/span[2]')
		custconfig.click()
		time.sleep(3)

		"Double click to expand Incident mAnagement"
		incmgt = self.driver.find_element_by_xpath('//*[@id="titleTN0_38_0"]')
		action = ActionChains(self.driver)
		action.double_click(incmgt)
		action.perform()

		"Double click to expand Advanced options"
		advopn = self.driver.find_element_by_xpath('// *[ @ id = "titleTN0_38_1"]')
		action = ActionChains(self.driver)
		action.double_click(advopn)
		action.perform()

		"click on Incident Management Settings"
		incmgtstng = self.driver.find_element_by_xpath('// *[ @ id = "titleTN0_39_2"]')
		incmgtstng.click()

		"Switching through windows and Verifying Incident Management Settings"
		time.sleep(3)
		window_before = self.driver.window_handles[0]
		logger.info(window_before)
		openincstg = self.driver.find_element_by_xpath('// *[ @ id = "WIN_0_500007506"] / div / div')
		openincstg.click()
		WebDriverWait(self.driver, 10).until(
			expected_conditions.number_of_windows_to_be(2))
		window_after = self.driver.window_handles[1]
		self.driver.switch_to.window(window_after)
		logger.info(window_after)

		custconsearchtype = self.driver.find_element_by_xpath('//*[@id="arid_WIN_0_303698700"]').text
		dispcustinfordilg = self.driver.find_element_by_xpath('//*[@id="arid_WIN_0_303750500"]').text
		custconnameformat = self.driver.find_element_by_xpath('// *[ @ id = "arid_WIN_0_303760500"]').text
		showinctasktab = self.driver.find_element_by_xpath('//*[@id="arid_WIN_0_304298500"]').text
		showinccatgrtab = self.driver.find_element_by_xpath('//*[@id="arid_WIN_0_304298490"]').text

		"""Validate Incident Management Settings as per Requirements"""
		logger.info('Customer and Contact Search Type set is "{}"'.format(custconsearchtype))
		logger.info('Display Customer Info Dialog set is "{}"'.format(dispcustinfordilg))
		logger.info('Customer and Contact Name Format set is "{}"'.format(custconnameformat))
		logger.info('Show Incident Task Tab set is "{}"'.format(showinctasktab))
		logger.info('Show Incident Categorization Tab set is "{}"'.format(showinccatgrtab))

		matching = True
		if custconsearchtype != kwargs['custconsearchtype']:
			logger.error('Set Value for "Customer and Contact Search Type" "{}" is wrong. Expected setting is {}'.format(custconsearchtype, kwargs['custconsearchtype']))
			matching = False
		if dispcustinfordilg != kwargs['dispcustinfordilg']:
			logger.error('Set Value for "Display Customer Info Dialog" "{}" is wrong. Expected setting is {}'.format(dispcustinfordilg, kwargs['dispcustinfordilg']))
			matching = False
		if custconnameformat != kwargs['custconnameformat']:
			logger.error('Set Value for "Customer and Contact Name Format"  "{}" is wrong. Expected setting is {}'.format(custconnameformat, kwargs['custconnameformat']))
			matching = False
		if showinctasktab != kwargs['showinctasktab']:
			logger.error('Set Value for "Show Incident Task Tab set" "{}" is wrong. Expected setting is {}'.format(showinctasktab, kwargs['showinctasktab']))
			matching = False
		if showinccatgrtab != kwargs['showinccatgrtab']:
			logger.error('Set Value for "Show Incident Categorization Tab" "{}" is wrong. Expected setting is {}'.format(showinccatgrtab, kwargs['showinccatgrtab']))
			matching = False
		if matching:
			logger.info("Pass")
		time.sleep(3)
		closestngwindow = self.driver.find_element_by_xpath('//*[@id="WIN_0_301614900"]/div/div')
		closestngwindow.click()
		self.driver.switch_to.window(window_before)
		return matching
	
	def create_incident(self, kwargs):
		logger.info("Executing incident_creation()")
		""" Clicking on Application"""
		appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
		appl.click()
		
		"""Clicking on Incident Management -> New Incident"""
		incmgmt = self.driver.find_element_by_link_text('Incident Management')
		incmgmt.click()
		incmgmtcon = self.driver.find_element_by_link_text('New Incident')
		incmgmtcon.click()
		time.sleep(5)
		"""Filling and Submitting Incident Creation Form"""
		incidtext = self.driver.find_element_by_xpath('//textarea[@id="arid_WIN_3_1000000161"]')
		incidtext = incidtext.get_attribute('value')
		WebDriverWait(self.driver, 20).until(
			expected_conditions.element_to_be_clickable((By.XPATH, "//textarea[@id='arid_WIN_3_303530000']")))
		customer = self.driver.find_element_by_id("arid_WIN_3_303530000")
		customer.click()
		customer.send_keys(kwargs['Customer'])
		time.sleep(2)
		customer.send_keys(Keys.DOWN)
		customer.send_keys(Keys.ENTER)
		
		summary = self.driver.find_element_by_id("arid_WIN_3_1000000000")
		summary.send_keys(kwargs['Summary'])
		
		service = self.driver.find_element_by_xpath('//textarea[@id="arid_WIN_3_303497300"]')
		service.click()
		service.send_keys(kwargs['Service'])
		time.sleep(3)
		service.send_keys(Keys.DOWN)
		service.send_keys(Keys.ENTER)
		
		impact = self.driver.find_element_by_xpath('//div[@class="selection"]/input[@id="arid_WIN_3_1000000163"]')
		impact.click()
		impact.send_keys(Keys.DOWN)
		impact.send_keys(kwargs['Impact'])
		impact.send_keys(Keys.ENTER)
		
		urgency = self.driver.find_element_by_xpath('//div[@class="selection"]/input[@id="arid_WIN_3_1000000162"]')
		urgency.click()
		urgency.send_keys(Keys.DOWN)
		urgency.send_keys(kwargs['Urgency'])
		urgency.send_keys(Keys.ENTER)
		
		prio = self.driver.find_element_by_xpath('//input[@id = "arid_WIN_3_1000000164"]')
		priority = prio.get_attribute('value')
		logger.info("Priority = {}".format(priority))
		
		inctype = self.driver.find_element_by_xpath('//div[@class="selection"]/input[@id="arid_WIN_3_1000000099"]')
		inctype.click()
		inctype.send_keys(Keys.DOWN)
		inctype.send_keys(kwargs['Incident_type'])
		inctype.send_keys(Keys.ENTER)
		
		assignedgroup = self.driver.find_element_by_xpath('//textarea[@id="arid_WIN_3_1000000217"]')
		assignedgroup.click()
		assignedgroup.send_keys(kwargs['Assigned_group'])
		time.sleep(3)
		assignedgroup.send_keys(Keys.DOWN)
		assignedgroup.send_keys(Keys.ENTER)
		time.sleep(3)
		
		saveinc = self.driver.find_element_by_xpath(
			'//a[@id="WIN_3_301614800"]/div[@class="btntextdiv"]/div[@class="f1"]')
		saveinc.click()
		time.sleep(5)
		status = self.driver.find_element_by_xpath('//div[@class="selection"]/input[@id="arid_WIN_3_7"]')
		statustext = status.get_attribute('value')
		time.sleep(3)
		
		logger.info("Incident Created successfully")
		logger.info("Incident ID = {} and Incident Status = {}".format(incidtext, statustext))
		return incidtext, statustext
	
	def search_incident_update_status(self, kwargs):
		logger.info("Executing search_incident_update_status()")
		"""Clicking on Applications"""
		appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
		appl.click()
		
		""" Clicking on Search Incident"""
		incmgmt = self.driver.find_element_by_link_text('Incident Management')
		incmgmt.click()
		incmgmtcon = self.driver.find_element_by_link_text('Search Incident')
		incmgmtcon.click()
		time.sleep(3)
		
		"""Searching by Incident ID"""
		inciid = self.driver.find_element_by_xpath('//textarea[@id="arid_WIN_3_1000000161"]')
		inciid.send_keys(kwargs['incidentid'])
		inciid.send_keys(Keys.ENTER)
		time.sleep(5)
		incid = inciid.get_attribute('title')
		
		"""Select Assignee """
		assignee = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_1000000218"]')
		assignee.click()
		assignee.send_keys(kwargs['Assignee'])
		assignee.send_keys(Keys.DOWN)
		assignee.send_keys(Keys.ENTER)
		time.sleep(2)
		
		savebtn = self.driver.find_element_by_link_text('Save')
		savebtn.click()
		time.sleep(3)
		
		"""Changing status"""
		statuschnge = self.driver.find_element_by_xpath('//input[@id="arid_WIN_3_7"]')
		statuschnge.click()
		statuschnge.send_keys(Keys.DOWN)
		statuschnge.send_keys(kwargs['Newstatus'])
		statuschnge.send_keys(Keys.ENTER)
		time.sleep(2)
		
		savebtn = self.driver.find_element_by_link_text('Save')
		savebtn.click()
		time.sleep(3)
		
		statusc = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_7"]')
		statustext = statusc.get_attribute('title')
		time.sleep(3)
		
		logger.info("Status changed successfully")
		logger.info("New Incident Status = {}".format(statustext))
		return statustext
	
	def search_incident_update_status_with_reason(self, kwargs):
		logger.info("Executing search_incident_update_status_with_reason()")
		"""Clicking on Applications"""
		appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
		appl.click()
		
		""" Clicking on Search Incident"""
		incmgmt = self.driver.find_element_by_link_text('Incident Management')
		incmgmt.click()
		incmgmtcon = self.driver.find_element_by_link_text('Search Incident')
		incmgmtcon.click()
		time.sleep(3)
		
		"""Searching by Incident ID"""
		inciid = self.driver.find_element_by_xpath('//textarea[@id="arid_WIN_3_1000000161"]')
		inciid.send_keys(kwargs['incidentid'])
		inciid.send_keys(Keys.ENTER)
		time.sleep(5)
		
		"""Changing status"""
		statuschnge = self.driver.find_element_by_xpath('//input[@id="arid_WIN_3_7"]')
		statuschnge.click()
		statuschnge.send_keys(Keys.DOWN)
		statuschnge.send_keys(kwargs['Newstatus'])
		statuschnge.send_keys(Keys.ENTER)
		time.sleep(2)
		
		"""Enter Status Reason """
		statusreason = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_1000000881"]')
		statusreason.click()
		statusreason.send_keys(kwargs['Statusreason'])
		statusreason.send_keys(Keys.DOWN)
		statusreason.send_keys(Keys.ENTER)
		time.sleep(2)
		statusresolution = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_1000000156"]')
		statusresolution.click()
		statusresolution.send_keys(kwargs['Statusresolution'])
		
		savebtn = self.driver.find_element_by_link_text('Save')
		savebtn.click()
		time.sleep(3)
		
		statusc = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_7"]')
		statustext = statusc.get_attribute('title')
		time.sleep(3)
		
		logger.info("Status changed successfully")
		logger.info("New Incident Status = {}".format(statustext))
		return statustext

	def add_workinfo_notes(self, kwargs):
		try:
			for k in kwargs.keys():
				logger.info("arguments are {}{}".format(k, kwargs[k]))
			self.login_bmc()
			workinfonotes = False
			workinfonotes = self.workinfonotes(kwargs)
		except BaseException as be:
			logger.fatal("Fatal exception occured in add_workinfo_notes() in {}".format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.bmc_logout()
			return workinfonotes
	
	def create_priority_incident_gui(self, kwargs):
		try:
			for k in kwargs.keys():
				logger.info("arguments are {}{}".format(k, kwargs[k]))
			self.login_bmc()
			incidentid = False
			incidentid = self.incident_creation(kwargs)
		except BaseException as be:
			logger.fatal("Fatal exception occured in create_priority_incident_gui() in {}".format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.bmc_logout()
			return incidentid
	
	def search_incident_by_priority_gui(self, priority):
		try:
			self.login_bmc()
			searchincident = False
			searchincident = self.search_incident_by_priority(priority)
		except BaseException as be:
			logger.fatal("Fatal exception occured in search_incident_by_priority_gui() in {}".format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.bmc_logout()
			return searchincident
	
	def incident_report_export_gui(self, kwargs):
		try:
			for k in kwargs.keys():
				logger.info("arguments are {}{}".format(k, kwargs[k]))
			self.login_bmc()
			response = self.incident_report_export(kwargs)
		except BaseException as be:
			logger.fatal("Fatal exception occured in incident_report_export_gui() in {}".format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.bmc_logout()
			if not response:
				raise BmcError("Incident report export via GUI failed")
	
	def close_incident_gui(self, kwargs):
		try:
			for k in kwargs.keys():
				logger.info("arguments are {}{}".format(k, kwargs[k]))
			self.login_bmc()
			closeincident = False
			closeincident = self.close_incident(kwargs)
		except BaseException as be:
			logger.fatal("Fatal exception occured in close_incident_gui() in {}".format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.bmc_logout()
			return closeincident
	
	def customer_contact_search_gui(self, kwargs):
		try:
			for k in kwargs.keys():
				logger.info("arguments are {}{}".format(k, kwargs[k]))
			self.login_bmc()
			searchcuscon = False
			searchcuscon = self.customer_contact_search(kwargs)
		except BaseException as be:
			logger.fatal("Fatal exception occured in close_incident_gui() in {}".format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.bmc_logout()
			return searchcuscon
	
	def verify_incident_mgmt_settings_gui(self, kwargs):
		try:
			for k in kwargs.keys():
				logger.info("arguments are name{} and value{}".format(k, kwargs[k]))
			self.login_bmc()
			setting = False
			setting = self.verify_incident_mgmt_settings(kwargs)
		except BaseException as be:
			logger.fatal("Fatal exception occured in verify_incident_mgmt_settings_gui() in {}".format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.bmc_logout()
			return setting
	
	def create_incident_gui(self, kwargs):
		try:
			for k in kwargs.keys():
				logger.info("arguments are {}{}".format(k, kwargs[k]))
			self.login_bmc()
			incidentid = False
			incidentid = self.create_incident(kwargs)
		except BaseException as be:
			logger.fatal("Fatal exception occured in create_priority_incident_gui() in {}".format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.bmc_logout()
			return incidentid
	
	def search_incident_update_status_gui(self, kwargs):
		try:
			for k in kwargs.keys():
				logger.info("arguments are {}{}".format(k, kwargs[k]))
			self.login_bmc()
			incidentid = False
			incidentid = self.search_incident_update_status(kwargs)
		except BaseException as be:
			logger.fatal("Fatal exception occured in create_priority_incident_gui() in {}".format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.bmc_logout()
			return incidentid
	
	def search_incident_update_status_with_reason_gui(self, kwargs):
		try:
			for k in kwargs.keys():
				logger.info("arguments are {}{}".format(k, kwargs[k]))
			self.login_bmc()
			incidentid = False
			incidentid = self.search_incident_update_status_with_reason(kwargs)
		except BaseException as be:
			logger.fatal(
				"Fatal exception occured in search_incident_update_status_with_reason_gui() in {}".format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.bmc_logout()
			return incidentid