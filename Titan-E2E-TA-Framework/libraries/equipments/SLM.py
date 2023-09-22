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


class BmcSLM(Vmm):
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
	
	def slm_maya_seven_ok_case_main(self, kwargs):
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
		saveinc = self.driver.find_element_by_xpath(
			'//a[@id="WIN_3_301614800"]/div[@class="btntextdiv"]/div[@class="f1"]')
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
		
		"""Getting the text of title goals, .etc"""
		inqw = self.driver.find_element_by_xpath('//textarea[@id ="arid_WIN_0_303738000"]')
		time.sleep(3)
		incid = inqw.get_attribute("value")
		logger.info("{}".format(incid))
		time.sleep(3)
		svttitle1 = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[2]/td[1]').text
		logger.info("SVT title1 =  {}".format(svttitle1))
		svttitle2 = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[3]/td[1]').text
		logger.info("SVT title2 =  {}".format(svttitle2))
		goal_response = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[2]/td[2]').text
		logger.info("Goal1 Attached =  {}".format(goal_response))
		goal_restoration = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[3]/td[2]').text
		logger.info("Goal2 Attached =  {}".format(goal_restoration))
		time.sleep(3)
		response_milestone = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[2]/td[3]').text
		logger.info("Incident 50% milestone for response: {}".format(response_milestone))
		response_status = self.driver.find_element_by_xpath('//*[@id="WIN_0_301466100"]/table/tbody/tr/td').text
		logger.info("Response Status = {}".format(response_status))
		resolution_milestones = self.driver.find_element(By.XPATH, '//*[@id="T300427600"]/tbody/tr[3]')
		time.sleep(3)
		resolution_milestones.click()
		time.sleep(2)
		restoration_status = self.driver.find_element_by_xpath('//*[@id="WIN_0_301369900"]/table/tbody/tr/td').text
		logger.info("Resolution Status = {}".format(restoration_status))
		resolution_milestone1 = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[2]/td[3]').text
		logger.info("Incident resolution 50% milestome: {}".format(resolution_milestone1))
		resolution_milestone2 = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[3]/td[3]').text
		logger.info("Incident resolution 75% milestome: {}".format(resolution_milestone2))
		resolution_milestone3 = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[4]/td[3]').text
		logger.info("Incident resolution 90% milestome: {}".format(resolution_milestone3))
		response_progress = self.driver.find_element(By.XPATH, '//*[@id="T300427600"]/tbody/tr[2]/td[7]').text
		logger.info("Response progress: {}".format(response_progress))
		resolution_progress = self.driver.find_element(By.XPATH, '//*[@id="T300427600"]/tbody/tr[3]/td[7]').text
		logger.info("Resolution progress: {}".format(resolution_progress))
		
		colorcode = self.driver.find_element_by_xpath('//*[@id="WIN_0_301466100"]')
		ccode = colorcode.get_attribute('style')
		colocode = re.findall(r'(rgb[(\d\s,)]*)', ccode)[0]  # To extract RGB code
		logger.info("Colorcode before Resolution = {}".format(colocode))
		
		self.driver.close()
		time.sleep(3)
		self.driver.switch_to.window(window_before)
		
		"""Validations"""
		matching = True
		if goal_response != kwargs["Goal1"]:
			matching = False
			logger.info("Response goal did not match")
		if goal_restoration != kwargs["Goal2"]:
			matching = False
			logger.info("restoration response did not match")
		if response_milestone != kwargs["Response_milestone"]:
			matching = False
			logger.info("Response milestone did not match")
		if resolution_milestone1 != kwargs["Resolution_milestone1"]:
			matching = False
			logger.info("resolution milestone1 did not match")
		if resolution_milestone2 != kwargs["Resolution_milestone1"]:
			matching = False
			logger.info("resolution milestone2 did not match")
		if resolution_milestone3 != kwargs["Resolution_milestone1"]:
			matching = False
			logger.info("resolution milestone3 did not match")
		if response_progress != kwargs["Response_Progress"]:
			matching = False
			logger.info("response progress did not match")
		if resolution_progress != kwargs["Resolution_Progress"]:
			matching = False
			logger.info("resolution progress did not match")
		if colocode != kwargs["Colorcode"]:
			matching = False
			logger.info("Colour code did not match")
		if response_status != kwargs["Status1"]:
			matching = False
			logger.info("response status did not match")
		if restoration_status != kwargs["Status2"]:
			matching = False
			logger.info("Resolution status did not match")
		if svttitle1 != kwargs["Svttitle1"]:
			matching = False
			logger.info("SVT response title did not match")
		if svttitle2 != kwargs["Svttitle2"]:
			matching = False
			logger.info("SVT resolution title did not match")
		return matching
	
	def create_incident_verify_slm(self, kwargs):
		logger.info("Executing create_incident_verify_slm()")
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

		""" Getting the SLA details """
		time.sleep(3)
		window_before = self.driver.window_handles[0]
		#logger.info(window_before)
		self.driver.find_element_by_xpath('//div[@id= "WIN_3_303579500"]').click()
		WebDriverWait(self.driver, 10).until(
			expected_conditions.number_of_windows_to_be(2))
		window_after = self.driver.window_handles[1]
		self.driver.switch_to.window(window_after)
		#logger.info(window_after)

		inqw = self.driver.find_element_by_xpath('//textarea[@id ="arid_WIN_0_303738000"]')
		time.sleep(3)
		incid = inqw.get_attribute("value")
		time.sleep(3)
		slatitle = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[2]/td[1]').text
		logger.info("SLA title =  {}".format(slatitle))
		goal = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[2]/td[2]').text
		logger.info("Goal Attached =  {}".format(goal))
		time.sleep(3)
		hours = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[2]/td[3]').text
		logger.info("Hours Attached = {}".format(hours))
		due = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[2]/td[6]').text
		logger.info("DueDate and Time for Resolution = {}".format(due))
		#timeuntildue = self.driver.find_element_by_xpath('//*[@id="WIN_0_303367100"]').text
		#logger.info("Time Until Due for Resolution = {}".format(timeuntildue))
		status = self.driver.find_element_by_xpath('//*[@id="WIN_0_301369900"]/table/tbody/tr/td').text
		logger.info("Status before Resolution  = {}".format(status))
		colorcode = self.driver.find_element_by_xpath('//*[@id="WIN_0_301466100"]')
		ccode = colorcode.get_attribute('style')
		colcode = ccode[86:]
		colocode = colcode[:15]
		logger.info("Colorcode before Resolution = {}".format(colocode))
		progress = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[2]/td[7]').text
		logger.info("Progress before Resolution = {}".format(progress))

		"Validating SLA Details"
		matching = True
		if slatitle != kwargs['Slatitle']:
			logger.error(
				"The SLA Title '{}' is not matching with expected SlA Title '{}'".format(slatitle, kwargs['Slatitle']))
			# raise ValueError
			matching = False
		if goal != kwargs['Goal']:
			logger.error(
				"The Attached Goal'{}' is not matching with expected Goal '{}'".format(goal, kwargs['Goal']))
			# raise ValueError
			matching = False
		elif hours != kwargs['Hours']:
			logger.error(
				"Hours '{}' is not matching with expected Hours '{}'".format(hours, kwargs['Hours']))
			# raise ValueError
			matching = False
		elif status != kwargs['Status']:
			logger.error(
				"Status '{}' is not matching with expected Status '{}'".format(status, kwargs['Status']))
			# raise ValueError
			matching = False
		elif colocode != kwargs['Colorcode']:
			logger.error(
				"Color code '{}' is not matching with expected Colorcode '{}'".format(colocode, kwargs['Colorcode']))
			# raise ValueError
			matching = False
		elif progress != kwargs['Progress']:
			logger.error(
				"Progress '{}' is not matching with expected Progress '{}'".format(progress, kwargs['Progress']))
			# raise ValueError
			matching = False
		else:
			logger.info("Pass")


		"""
		"Validate SLA Details"
		assert (slatitle == kwargs['Slatitle'])
		assert (goal == kwargs['Goal'])
		assert (hours == kwargs['Hours'])
		assert (status == kwargs['Status'])
		assert (colocode == kwargs['Colorcode'])
		assert (progress == kwargs['Progress'])
		logger.info('Pass')
		self.driver.close()
		self.driver.switch_to.window(window_before)
		"""

		self.driver.close()
		time.sleep(3)
		self.driver.switch_to.window(window_before)

		"Assigning Incident to assignee and save Incident"
		assigneedrdn = self.driver.find_element_by_xpath('//textarea[@id="arid_WIN_3_1000000218"]')
		assigneedrdn.click()
		assigneedrdn.send_keys(kwargs['Assignee'])
		time.sleep(2)
		assigneedrdn.send_keys(Keys.DOWN)
		assigneedrdn.send_keys(Keys.ENTER)
		time.sleep(3)
		savebtn = self.driver.find_element_by_link_text('Save')
		savebtn.click()
		time.sleep(3)

		logger.info("Exiting create_incident_verify_slm()")
		return incid, matching
	
	def search_incident_verify_slm(self, kwargs):
		logger.info("Executing search_incident_verify_slm()")
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
		time.sleep(2)

		"Resolving Incident and Save"
		statuschnge = self.driver.find_element_by_xpath('//input[@id="arid_WIN_3_7"]')
		statuschnge.click()
		statuschnge.send_keys(Keys.DOWN)
		statuschnge.send_keys(kwargs['Newstatus'])
		statuschnge.send_keys(Keys.ENTER)
		time.sleep(2)
		statusreason = self.driver.find_element_by_xpath('//textarea[@id="arid_WIN_3_1000000881"]')
		statusreason.click()
		statusreason.send_keys(Keys.DOWN)
		statuschnge.send_keys(kwargs['Statusreason'])
		statusreason.send_keys(Keys.ENTER)
		time.sleep(2)
		resolution = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_1000000156"]')
		resolution.send_keys(kwargs['Resolution'])
		time.sleep(2)
		savebtn = self.driver.find_element_by_link_text('Save')
		savebtn.click()

		""" Getting the SLA details """
		time.sleep(3)
		window_before = self.driver.window_handles[0]
		#logger.info (window_before)
		self.driver.find_element_by_xpath('//div[@id= "WIN_3_303579500"]').click()
		WebDriverWait(self.driver, 10).until(
			expected_conditions.number_of_windows_to_be(2))
		window_after = self.driver.window_handles[1]
		self.driver.switch_to.window(window_after)
		#logger.info(window_after)

		inqw = self.driver.find_element_by_xpath('//textarea[@id ="arid_WIN_0_303738000"]')
		time.sleep(3)
		incid = inqw.get_attribute("value")
		time.sleep(3)
		slatitle = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[2]/td[1]').text
		logger.info("SLA title =  {}".format(slatitle))
		goal = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[2]/td[2]').text
		logger.info("Goal Attached =  {}".format(goal))
		time.sleep(3)
		hours = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[2]/td[3]').text
		logger.info("Hours Attached = {}".format(hours))
		duedate = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[2]/td[6]').text
		logger.info("DueDate and Time for Resolution = {}".format(duedate))
		#completion = self.driver.find_element_by_xpath('//*[@id="WIN_0_303367100"]').text
		#logger.info("Completion Time for Resolution = {}".format(completion))
		status = self.driver.find_element_by_xpath('//*[@id="WIN_0_301466100"]/table/tbody/tr/td').text
		logger.info("Status after Resolution  = {}".format(status))
		colorcode = self.driver.find_element_by_xpath('//*[@id="WIN_0_301466100"]')
		#colorcode = self.driver.find_element_by_xpath('//*[@id="WIN_0_301466100"]/table/tbody/tr/td')
		ccode = colorcode.get_attribute('style')
		colcode = ccode[86:]
		colocode = colcode[:15]
		logger.info("Colorcode after Resolution = {}".format(colocode))
		progress = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[2]/td[7]').text
		logger.info("Progress after Resolution = {}".format(progress))

		"Validating SLA Details"
		matching = True
		if slatitle != kwargs['Slatitle']:
			logger.error(
				"The SLA Title '{}' is not matching with expected SlA Title '{}'".format(slatitle, kwargs['Slatitle']))
			# raise ValueError
			matching = False
		if goal != kwargs['Goal']:
			logger.error(
				"The Attached Goal'{}' is not matching with expected Goal '{}'".format(goal, kwargs['Goal']))
			# raise ValueError
			matching = False
		elif hours != kwargs['Hours']:
			logger.error(
				"Hours '{}' is not matching with expected Hours '{}'".format(hours, kwargs['Hours']))
			# raise ValueError
			matching = False
		elif status != kwargs['Status']:
			logger.error(
				"Status '{}' is not matching with expected Status '{}'".format(status, kwargs['Status']))
			# raise ValueError
			matching = False
		elif colocode != kwargs['Colorcode']:
			logger.error(
				"Color code '{}' is not matching with expected Colorcode '{}'".format(colocode, kwargs['Colorcode']))
			# raise ValueError
			matching = False
		elif progress != kwargs['Progress']:
			logger.error(
				"Progress '{}' is not matching with expected Progress '{}'".format(progress, kwargs['Progress']))
			# raise ValueError
			matching = False
		else:
			logger.info("Pass")

		"""
		"Validating SLA Details"
		assert (slatitle == kwargs['Slatitle'])
		assert (goal == kwargs['Goal'])
		assert (hours == kwargs['Hours'])
		assert (status == kwargs['Status'])
		assert (colocode == kwargs['Colorcode'])
		assert (progress == kwargs['Progress'])
		logger.info('Pass')
		"""

		self.driver.close()
		time.sleep(3)
		self.driver.switch_to.window(window_before)
		body = self.driver.find_element_by_css_selector('body')
		body.click()
		body.send_keys(Keys.PAGE_UP)
		logger.info("Exiting search_incident_verify_slm()")
		return incid, matching
	
	def create_incident_maya_verify_slm(self, kwargs):
		logger.info("Executing create_incident_verify_slm()")
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

		""" Getting the SLA details """
		time.sleep(3)
		window_before = self.driver.window_handles[0]
		#logger.info(window_before)
		self.driver.find_element_by_xpath('//div[@id= "WIN_3_303579500"]').click()
		WebDriverWait(self.driver, 10).until(
			expected_conditions.number_of_windows_to_be(2))
		window_after = self.driver.window_handles[1]
		self.driver.switch_to.window(window_after)
		#logger.info(window_after)

		inqw = self.driver.find_element_by_xpath('//textarea[@id ="arid_WIN_0_303738000"]')
		time.sleep(3)
		incid = inqw.get_attribute("value")
		time.sleep(3)
		slatitle = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[2]/td[1]').text
		logger.info("SLA title =  {}".format(slatitle))
		goal = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[2]/td[2]').text
		logger.info("Goal Attached =  {}".format(goal))
		time.sleep(3)
		hours = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[2]/td[3]').text
		logger.info("Hours Attached = {}".format(hours))
		due = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[2]/td[6]').text
		logger.info("DueDate and Time for Resolution = {}".format(due))
		#timeuntildue = self.driver.find_element_by_xpath('//*[@id="WIN_0_303367100"]').text
		#logger.info("Time Until Due for Resolution = {}".format(timeuntildue))
		status = self.driver.find_element_by_xpath('//*[@id="WIN_0_301466100"]/table/tbody/tr/td').text
		logger.info("Status before Resolution  = {}".format(status))
		colorcode = self.driver.find_element_by_xpath('//*[@id="WIN_0_301466100"]')
		ccode = colorcode.get_attribute('style')
		colcode = ccode[86:]
		colocode = colcode[:15]
		logger.info("Colorcode before Resolution = {}".format(colocode))
		progress = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[2]/td[7]/nobr/span').text
		logger.info("Progress before Resolution = {}".format(progress))
		"Validating SLA Details"
		matching = True
		if slatitle != kwargs['Slatitle']:
			logger.error(
				"The SLA Title '{}' is not matching with expected SlA Title '{}'".format(slatitle, kwargs['Slatitle']))
			# raise ValueError
			matching = False
		if goal != kwargs['Goal']:
			logger.error("The Attached Goal'{}' is not matching with expected Goal '{}'".format(goal, kwargs['Goal']))
			# raise ValueError
			matching = False
		elif hours != kwargs['Hours']:
			logger.error(
				"Hours '{}' is not matching with expected Hours '{}'".format(hours, kwargs['Hours']))
			# raise ValueError
			matching = False
		elif status != kwargs['Status']:
			logger.error(
				"Status '{}' is not matching with expected Status '{}'".format(status, kwargs['Status']))
			# raise ValueError
			matching = False
		elif colocode != kwargs['Colorcode']:
			logger.error(
				"Color code '{}' is not matching with expected Colorcode '{}'".format(colocode, kwargs['Colorcode']))
			# raise ValueError
			matching = False
		elif progress != kwargs['Progress']:
			logger.error(
				"Progress '{}' is not matching with expected Progress '{}'".format(progress, kwargs['Progress']))
			# raise ValueError
			matching = False
		else:
			logger.info("Pass")

		slatitle1 = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[3]/td[1]/nobr/span').text
		logger.info("SLA title =  {}".format(slatitle1))
		goal1 = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[3]/td[2]/nobr/span').text
		logger.info("Goal Attached =  {}".format(goal1))
		time.sleep(3)
		hours1 = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[3]/td[3]/nobr/span').text
		logger.info("Hours Attached = {}".format(hours1))
		due1 = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[3]/td[4]/nobr/span').text
		logger.info("DueDate and Time for Resolution = {}".format(due1))
		# timeuntildue = self.driver.find_element_by_xpath('//*[@id="WIN_0_303367100"]').text
		# logger.info("Time Until Due for Resolution = {}".format(timeuntildue))
		status1 = self.driver.find_element_by_xpath('//*[@id="WIN_0_301466100"]/table/tbody/tr/td').text
		logger.info("Status before Resolution  = {}".format(status1))
		colorcode1 = self.driver.find_element_by_xpath('//*[@id="WIN_0_301466100"]')
		ccode = colorcode1.get_attribute('style')
		colcode = ccode[86:]
		colocode1 = colcode[:15]
		logger.info("Colorcode before Resolution = {}".format(colocode1))
		progress1 = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[2]/td[7]/nobr/span').text
		logger.info("Progress before Resolution = {}".format(progress1))
		"""Milestones"""
		logger.info("milestone for resolution")
		mile1 = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[2]/td[1]/nobr/span').text
		logger.info("Title =  {}".format(mile1))
		mile2 = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[2]/td[2]/nobr/span').text
		logger.info("Execurion Time =  {}".format(mile2))
		mile3 = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[2]/td[3]/nobr/span').text
		logger.info("Status =  {}".format(mile3))

		"Validating SLA Details"
		matching1 = True
		if slatitle1 != kwargs['Slatitle1']:
			logger.error(
				"The SLA Title '{}' is not matching with expected SlA Title '{}'".format(slatitle, kwargs['Slatitle1']))
			# raise ValueError
			matching1 = False
		if goal1 != kwargs['Goal1']:
			logger.error(
				"The Attached Goal'{}' is not matching with expected Goal '{}'".format(goal, kwargs['Goal1']))
			# raise ValueError
			matching1 = False
		elif hours1 != kwargs['Hours1']:
			logger.error(
				"Hours '{}' is not matching with expected Hours '{}'".format(hours, kwargs['Hours1']))
			# raise ValueError
			matching1 = False
		elif status1 != kwargs['Status1']:
			logger.error(
				"Status '{}' is not matching with expected Status '{}'".format(status, kwargs['Status1']))
			# raise ValueError
			matching1 = False
		elif colocode1 != kwargs['Colorcode1']:
			logger.error(
				"Color code '{}' is not matching with expected Colorcode '{}'".format(colocode, kwargs['Colorcode1']))
			# raise ValueError
			matching1 = False
		elif progress1 != kwargs['Progress']:
			logger.error(
				"Progress '{}' is not matching with expected Progress '{}'".format(progress, kwargs['Progress1']))
			# raise ValueError
			matching1 = False
		else:
			logger.info("Pass")
		self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[3]/td[1]/nobr/span').click()
		time.sleep(3)
		"""Printing Milestones"""
		logger.info("milestone for restoration")

		mile1  = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[2]/td[1]/nobr/span').text
		logger.info("Title =  {}".format(mile1))
		mile2 = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[2]/td[2]/nobr/span').text
		logger.info("Execution Time =  {}".format(mile2))
		mile3 = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[2]/td[3]/nobr/span').text
		logger.info("status =  {}".format(mile3))
		mile4 = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[3]/td[1]/nobr/span').text
		logger.info("Title =  {}".format(mile4))
		mile5 = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[3]/td[2]/nobr/span').text
		logger.info("Execurion Time =  {}".format(mile5))
		mile6 = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[3]/td[3]/nobr/span').text
		logger.info("Status =  {}".format(mile6))
		mile7 = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[4]/td[1]/nobr/span').text
		logger.info("Title =  {}".format(mile7))
		mile8 = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[4]/td[2]/nobr/span').text
		logger.info("Execution Time =  {}".format(mile8))
		mile9 = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[4]/td[3]/nobr/span').text
		logger.info("Status =  {}".format(mile9))

		"""
		"Validate SLA Details"
		assert (slatitle == kwargs['Slatitle'])
		assert (goal == kwargs['Goal'])
		assert (hours == kwargs['Hours'])
		assert (status == kwargs['Status'])
		assert (colocode == kwargs['Colorcode'])
		assert (progress == kwargs['Progress'])
		logger.info('Pass')
		self.driver.close()
		self.driver.switch_to.window(window_before)
		"""

		self.driver.close()
		time.sleep(3)
		self.driver.switch_to.window(window_before)

		"Assigning Incident to assignee and save Incident"
		assigneedrdn = self.driver.find_element_by_xpath('//textarea[@id="arid_WIN_3_1000000218"]')
		assigneedrdn.click()
		assigneedrdn.send_keys(kwargs['Assignee'])
		time.sleep(2)
		assigneedrdn.send_keys(Keys.DOWN)
		assigneedrdn.send_keys(Keys.ENTER)
		time.sleep(3)
		savebtn = self.driver.find_element_by_link_text('Save')
		savebtn.click()
		time.sleep(3)

		logger.info("Exiting create_incident_verify_slm()")
		return incid, matching, matching1

	def search_incident_maya_verify_slm(self, kwargs):
		logger.info("Executing search_incident_verify_slm()")
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
		time.sleep(2)

		"Resolving Incident and Save"
		statuschnge = self.driver.find_element_by_xpath('//input[@id="arid_WIN_3_7"]')
		statuschnge.click()
		statuschnge.send_keys(Keys.DOWN)
		statuschnge.send_keys(kwargs['Newstatus'])
		statuschnge.send_keys(Keys.ENTER)
		time.sleep(2)
		statusreason = self.driver.find_element_by_xpath('//textarea[@id="arid_WIN_3_1000000881"]')
		statusreason.click()
		statusreason.send_keys(Keys.DOWN)
		statuschnge.send_keys(kwargs['Statusreason'])
		statusreason.send_keys(Keys.ENTER)
		time.sleep(2)
		resolution = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_1000000156"]')
		resolution.send_keys(kwargs['Resolution'])
		time.sleep(2)
		savebtn = self.driver.find_element_by_link_text('Save')
		savebtn.click()

		""" Getting the SLA details """
		time.sleep(3)
		window_before = self.driver.window_handles[0]
		#logger.info (window_before)
		self.driver.find_element_by_xpath('//div[@id= "WIN_3_303579500"]').click()
		WebDriverWait(self.driver, 10).until(
			expected_conditions.number_of_windows_to_be(2))
		window_after = self.driver.window_handles[1]
		self.driver.switch_to.window(window_after)
		#logger.info(window_after)

		inqw = self.driver.find_element_by_xpath('//textarea[@id ="arid_WIN_0_303738000"]')
		time.sleep(3)
		incid = inqw.get_attribute("value")
		time.sleep(3)
		slatitle1 = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[3]/td[1]/nobr/span').text
		logger.info("SLA title =  {}".format(slatitle1))
		goal1 = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[3]/td[2]/nobr/span').text
		logger.info("Goal Attached =  {}".format(goal1))
		time.sleep(3)
		hours1 = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[3]/td[3]/nobr/span').text
		logger.info("Hours Attached = {}".format(hours1))
		due1 = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[3]/td[4]/nobr/span').text
		logger.info("DueDate and Time for Resolution = {}".format(due1))
		# timeuntildue = self.driver.find_element_by_xpath('//*[@id="WIN_0_303367100"]').text
		# logger.info("Time Until Due for Resolution = {}".format(timeuntildue))
		status1 = self.driver.find_element_by_xpath('//*[@id="WIN_0_301466100"]/table/tbody/tr/td').text
		logger.info("Status before Resolution  = {}".format(status1))
		colorcode1 = self.driver.find_element_by_xpath('//*[@id="WIN_0_301466100"]')
		ccode = colorcode1.get_attribute('style')
		colcode = ccode[86:]
		colocode1 = colcode[:15]
		logger.info("Colorcode before Resolution = {}".format(colocode1))
		progress1 = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[2]/td[7]/nobr/span').text
		logger.info("Progress before Resolution = {}".format(progress1))

		"Validating SLA Details"
		matching1 = True
		if slatitle1 != kwargs['Slatitle1']:
			logger.error(
				"The SLA Title '{}' is not matching with expected SlA Title '{}'".format(slatitle1, kwargs['Slatitle1']))
			# raise ValueError
			matching1 = False
		if goal1 != kwargs['Goal1']:
			logger.error(
				"The Attached Goal'{}' is not matching with expected Goal '{}'".format(goal1, kwargs['Goal1']))
			# raise ValueError
			matching1 = False
		elif hours1 != kwargs['Hours1']:
			logger.error(
				"Hours '{}' is not matching with expected Hours '{}'".format(hours1, kwargs['Hours1']))
			# raise ValueError
			matching1 = False
		elif status1 != kwargs['Status1']:
			logger.error(
				"Status '{}' is not matching with expected Status '{}'".format(status1, kwargs['Status1']))
			# raise ValueError
			matching1 = False
		elif colocode1 != kwargs['Colorcode']:
			logger.error(
				"Color code '{}' is not matching with expected Colorcode '{}'".format(colocode1, kwargs['Colorcode']))
			# raise ValueError
			matching1 = False
		elif progress1 != kwargs['Progress']:
			logger.error(
				"Progress '{}' is not matching with expected Progress '{}'".format(progress1, kwargs['Progress1']))
			# raise ValueError
			matching1 = False
		else:
			logger.info("Pass")
		logger.info("milestones for restoration")
		time.sleep(3)
		if kwargs['p'] == 'P0':
			self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[3]/td[1]/nobr/span').click()

		"""Printing Milestones"""
		mile1 = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[2]/td[1]/nobr/span').text
		logger.info("Title =  {}".format(mile1))
		mile2 = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[2]/td[2]/nobr/span').text
		logger.info("Execution Time =  {}".format(mile2))
		mile3 = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[2]/td[3]/nobr/span').text
		logger.info("status =  {}".format(mile3))
		mile4 = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[3]/td[1]/nobr/span').text
		logger.info("Title =  {}".format(mile4))
		mile5 = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[3]/td[2]/nobr/span').text
		logger.info("Execurion Time =  {}".format(mile5))
		mile6 = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[3]/td[3]/nobr/span').text
		logger.info("Status =  {}".format(mile6))
		mile7 = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[4]/td[1]/nobr/span').text
		logger.info("Title =  {}".format(mile7))
		mile8 = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[4]/td[2]/nobr/span').text
		logger.info("Execution Time =  {}".format(mile8))
		mile9 = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[4]/td[3]/nobr/span').text
		logger.info("Status =  {}".format(mile9))

		slatitle = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[2]/td[1]').text
		logger.info("SLA title =  {}".format(slatitle))
		goal = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[2]/td[2]').text
		logger.info("Goal Attached =  {}".format(goal))
		time.sleep(3)
		hours = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[2]/td[3]').text
		logger.info("Hours Attached = {}".format(hours))
		duedate = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[2]/td[6]').text
		logger.info("DueDate and Time for Resolution = {}".format(duedate))
		#completion = self.driver.find_element_by_xpath('//*[@id="WIN_0_303367100"]').text
		#logger.info("Completion Time for Resolution = {}".format(completion))
		status = self.driver.find_element_by_xpath('//*[@id="WIN_0_301466100"]/table/tbody/tr/td').text
		logger.info("Status after Resolution  = {}".format(status))
		colorcode = self.driver.find_element_by_xpath('//*[@id="WIN_0_301466100"]')
		#colorcode = self.driver.find_element_by_xpath('//*[@id="WIN_0_301466100"]/table/tbody/tr/td')
		ccode = colorcode.get_attribute('style')
		colcode = ccode[86:]
		colocode = colcode[:15]
		logger.info("Colorcode after Resolution = {}".format(colocode))
		progress = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[2]/td[7]').text
		logger.info("Progress after Resolution = {}".format(progress))

		"Validating SLA Details"
		matching = True
		if slatitle != kwargs['Slatitle']:
			logger.error(
				"The SLA Title '{}' is not matching with expected SlA Title '{}'".format(slatitle, kwargs['Slatitle']))
			# raise ValueError
			matching = False
		if goal != kwargs['Goal']:
			logger.error(
				"The Attached Goal'{}' is not matching with expected Goal '{}'".format(goal, kwargs['Goal']))
			# raise ValueError
			matching = False
		elif hours != kwargs['Hours']:
			logger.error(
				"Hours '{}' is not matching with expected Hours '{}'".format(hours, kwargs['Hours']))
			# raise ValueError
			matching = False
		elif status != kwargs['Status']:
			logger.error(
				"Status '{}' is not matching with expected Status '{}'".format(status, kwargs['Status']))
			# raise ValueError
			matching = False
		elif colocode != kwargs['Colorcode']:
			logger.error(
				"Color code '{}' is not matching with expected Colorcode '{}'".format(colocode, kwargs['Colorcode']))
			# raise ValueError
			matching = False
		elif progress != kwargs['Progress']:
			logger.error(
				"Progress '{}' is not matching with expected Progress '{}'".format(progress, kwargs['Progress']))
			# raise ValueError
			matching = False
		else:
			logger.info("Pass")

		logger.info("Milestones for resolution")
		self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[3]/td[1]/nobr/span').click()
		mile1 = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[2]/td[1]/nobr/span').text
		logger.info("Title =  {}".format(mile1))
		mile2 = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[2]/td[2]/nobr/span').text
		logger.info("Execution Time =  {}".format(mile2))
		mile3 = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[2]/td[3]/nobr/span').text
		logger.info("status =  {}".format(mile3))
		"""Validating SLA Details
		assert (slatitle == kwargs['Slatitle'])
		assert (goal == kwargs['Goal'])
		assert (hours == kwargs['Hours'])
		assert (status == kwargs['Status'])
		assert (colocode == kwargs['Colorcode'])
		assert (progress == kwargs['Progress'])
		logger.info('Pass')"""
		self.driver.close()
		time.sleep(3)
		self.driver.switch_to.window(window_before)
		body = self.driver.find_element_by_css_selector('body')
		body.click()
		body.send_keys(Keys.PAGE_UP)
		logger.info("Exiting search_incident_verify_slm()")
		return incid, matching1, matching
	
	def slm_maya_seven_critical_case_main(self, kwargs):
		logger.info("Executing search_incident_verify_slm()")
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
		time.sleep(2)
		
		""" Getting the SLA details """
		time.sleep(3)
		window_before = self.driver.window_handles[0]
		# logger.info (window_before)
		self.driver.find_element_by_xpath('//div[@id= "WIN_3_303579500"]').click()
		WebDriverWait(self.driver, 10).until(
			expected_conditions.number_of_windows_to_be(2))
		window_after = self.driver.window_handles[1]
		self.driver.switch_to.window(window_after)
		# logger.info(window_after)
		resolution_milestones = self.driver.find_element(By.XPATH, '//*[@id="T300427600"]/tbody/tr[2]')
		time.sleep(3)
		resolution_milestones.click()
		time.sleep(2)
		restoration_status = self.driver.find_element_by_xpath('//*[@id="WIN_0_301370000"]/table/tbody/tr/td').text
		logger.info("Resolution Status  = {}".format(restoration_status))
		resolution_milestone1 = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[2]/td[3]').text
		logger.info("Incident resolution 50% milestome: {}".format(resolution_milestone1))
		resolution_milestone2 = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[3]/td[3]').text
		logger.info("Incident resolution 75% milestome: {}".format(resolution_milestone2))
		resolution_milestone3 = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[4]/td[3]').text
		logger.info("Incident resolution 90% milestome: {}".format(resolution_milestone3))
		colorcode = self.driver.find_element_by_xpath('//*[@id="WIN_0_301370000"]')
		ccode = colorcode.get_attribute('style')
		# colcode = ccode[86:]
		colocode = re.findall(r'(rgb[(\d\s,)]*)', ccode)[0]
		logger.info("ccode : {}".format(ccode))
		logger.info("Colorcode before Resolution = {}".format(colocode))
		restoration_status = self.driver.find_element(By.XPATH, '//*[@id="WIN_0_301370000"]/table/tbody/tr/td').text
		logger.info("Restoration status is {}".format(restoration_status))
		resolution_progress = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[2]/td[7]').text
		logger.info("Restoration Progress: {}".format(resolution_progress))
		
		"""Validations"""
		matching = True
		if resolution_milestone1 != kwargs["Resolution_milestone1"]:
			matching = False
			logger.info("resolution milestone1 did not match")
		if resolution_milestone2 != kwargs["Resolution_milestone1"]:
			matching = False
			logger.info("resolution milestone2 did not match")
		if resolution_milestone3 != kwargs["Resolution_milestone1"]:
			matching = False
			logger.info("resolution milestone3 did not matcht")
		if resolution_progress != kwargs["Resolution_Progress"]:
			matching = False
			logger.info("resolution progress did not match")
		if colocode != kwargs["Colorcode"]:
			matching = False
			logger.info("Colour code did not match")
		if restoration_status != kwargs["Status2"]:
			matching = False
			logger.info("Resolution status did not match")
		self.driver.close()
		time.sleep(3)
		self.driver.switch_to.window(window_before)
		time.sleep(3)
		return matching
	
	def slm_maya_seven_warning_case_main(self, kwargs):
		logger.info("Executing search_incident_verify_slm()")
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
		time.sleep(2)
		
		""" Getting the SLA details """
		time.sleep(3)
		window_before = self.driver.window_handles[0]
		# logger.info (window_before)
		self.driver.find_element_by_xpath('//div[@id= "WIN_3_303579500"]').click()
		WebDriverWait(self.driver, 10).until(
			expected_conditions.number_of_windows_to_be(2))
		window_after = self.driver.window_handles[1]
		self.driver.switch_to.window(window_after)
		time.sleep(3)
		resolution_milestones = self.driver.find_element(By.XPATH, '//*[@id="T300427600"]/tbody/tr[2]')
		time.sleep(3)
		resolution_milestones.click()
		time.sleep(2)
		resolution_milestone1 = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[2]/td[3]').text
		logger.info("Incident resolution 50% milestome: {}".format(resolution_milestone1))
		resolution_milestone2 = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[3]/td[3]').text
		logger.info("Incident resolution 75% milestome: {}".format(resolution_milestone2))
		resolution_milestone3 = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[4]/td[3]').text
		logger.info("Incident resolution 90% milestome: {}".format(resolution_milestone3))
		colorcode = self.driver.find_element_by_xpath('//*[@id="WIN_0_300132000"]')
		ccode = colorcode.get_attribute('style')
		colocode = re.findall(r'(rgb[(\d\s,)]*)', ccode)[0]
		logger.info("ccode : {}".format(ccode))
		logger.info("Colorcode before Resolution = {}".format(colocode))
		restoration_status = self.driver.find_element(By.XPATH, '//*[@id="WIN_0_301370100"]/table/tbody/tr/td').text
		logger.info("Restoration status is {}".format(restoration_status))
		resolution_progress = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[2]/td[7]').text
		logger.info("Restoration Progress: {}".format(resolution_progress))
		
		"""Validations"""
		matching = True
		if resolution_milestone1 != kwargs["Resolution_milestone1"]:
			matching = False
			logger.info("resolution milestone1 did not match")
		if resolution_milestone2 != kwargs["Resolution_milestone2"]:
			matching = False
			logger.info("resolution milestone2 did not match")
		if resolution_milestone3 != kwargs["Resolution_milestone3"]:
			matching = False
			logger.info("resolution milestone3 did not match")
		if resolution_progress != kwargs["Resolution_Progress"]:
			matching = False
			logger.info("resolution progress did not match")
		if colocode != kwargs["Colorcode"]:
			matching = False
			logger.info('Colour code did not match')
		if restoration_status != kwargs["Status2"]:
			matching = False
			logger.info("Resolution status did not match")
		
		"""Closing the SLM window"""
		self.driver.close()
		time.sleep(3)
		self.driver.switch_to.window(window_before)
		time.sleep(3)
		return matching
	
	def create_incident_verify_p2_slm(self, kwargs):
		logger.info("Executing create_incident_verify_p2_slm()")
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

		""" Getting the SLA details """
		time.sleep(3)
		window_before = self.driver.window_handles[0]
		#logger.info(window_before)
		self.driver.find_element_by_xpath('//div[@id= "WIN_3_303579500"]').click()
		WebDriverWait(self.driver, 10).until(
			expected_conditions.number_of_windows_to_be(2))
		window_after = self.driver.window_handles[1]
		self.driver.switch_to.window(window_after)
		#logger.info(window_after)

		inqw = self.driver.find_element_by_xpath('//textarea[@id ="arid_WIN_0_303738000"]')
		time.sleep(3)
		incid = inqw.get_attribute("value")
		time.sleep(3)
		slatitle = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[2]/td[1]').text
		logger.info("SLA title =  {}".format(slatitle))
		goal = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[2]/td[2]').text
		logger.info("Goal Attached =  {}".format(goal))
		time.sleep(3)
		hours = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[2]/td[3]').text
		logger.info("Hours Attached = {}".format(hours))
		due = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[2]/td[6]').text
		logger.info("DueDate and Time for Resolution = {}".format(due))
		#timeuntildue = self.driver.find_element_by_xpath('//*[@id="WIN_0_303367100"]').text
		#logger.info("Time Until Due for Resolution = {}".format(timeuntildue))
		status = self.driver.find_element_by_xpath('//*[@id="WIN_0_301369900"]/table/tbody/tr/td').text
		logger.info("Status before Resolution  = {}".format(status))
		colorcode = self.driver.find_element_by_xpath('//*[@id="WIN_0_301466100"]')
		ccode = colorcode.get_attribute('style')
		colcode = ccode[86:]
		colocode = colcode[:15]
		logger.info("Colorcode before Resolution = {}".format(colocode))
		progress = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[2]/td[7]').text
		logger.info("Progress before Resolution = {}".format(progress))

		"Validating SLA Details"
		matching = True
		if slatitle != kwargs['Slatitle']:
			logger.error(
				"The SLA Title '{}' is not matching with expected SlA Title '{}'".format(slatitle, kwargs['Slatitle']))
			# raise ValueError
			matching = False
		if goal != kwargs['Goal']:
			logger.error(
				"The Attached Goal'{}' is not matching with expected Goal '{}'".format(goal, kwargs['Goal']))
			# raise ValueError
			matching = False
		elif hours != kwargs['Hours']:
			logger.error(
				"Hours '{}' is not matching with expected Hours '{}'".format(hours, kwargs['Hours']))
			# raise ValueError
			matching = False
		elif status != kwargs['Status']:
			logger.error(
				"Status '{}' is not matching with expected Status '{}'".format(status, kwargs['Status']))
			# raise ValueError
			matching = False
		elif colocode != kwargs['Colorcode']:
			logger.error(
				"Color code '{}' is not matching with expected Colorcode '{}'".format(colocode, kwargs['Colorcode']))
			# raise ValueError
			matching = False
		elif progress != kwargs['Progress']:
			logger.error(
				"Progress '{}' is not matching with expected Progress '{}'".format(progress, kwargs['Progress']))
			# raise ValueError
			matching = False
		else:
			logger.info("Pass")

		"""Printing Milestones"""
		logger.info("milestone for restoration before Incident resolution")

		mile1  = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[2]/td[1]/nobr/span').text
		logger.info("Title =  {}".format(mile1))
		mile2 = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[2]/td[2]/nobr/span').text
		logger.info("Execution Time =  {}".format(mile2))
		mile3 = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[2]/td[3]/nobr/span').text
		logger.info("status =  {}".format(mile3))
		mile4 = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[3]/td[1]/nobr/span').text
		logger.info("Title =  {}".format(mile4))
		mile5 = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[3]/td[2]/nobr/span').text
		logger.info("Execurion Time =  {}".format(mile5))
		mile6 = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[3]/td[3]/nobr/span').text
		logger.info("Status =  {}".format(mile6))
		mile7 = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[4]/td[1]/nobr/span').text
		logger.info("Title =  {}".format(mile7))
		mile8 = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[4]/td[2]/nobr/span').text
		logger.info("Execution Time =  {}".format(mile8))
		mile9 = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[4]/td[3]/nobr/span').text
		logger.info("Status =  {}".format(mile9))

		"""
		"Validate SLA Details"
		assert (slatitle == kwargs['Slatitle'])
		assert (goal == kwargs['Goal'])
		assert (hours == kwargs['Hours'])
		assert (status == kwargs['Status'])
		assert (colocode == kwargs['Colorcode'])
		assert (progress == kwargs['Progress'])
		logger.info('Pass')
		self.driver.close()
		self.driver.switch_to.window(window_before)
		"""

		self.driver.close()
		time.sleep(3)
		self.driver.switch_to.window(window_before)

		"Assigning Incident to assignee and save Incident"
		assigneedrdn = self.driver.find_element_by_xpath('//textarea[@id="arid_WIN_3_1000000218"]')
		assigneedrdn.click()
		assigneedrdn.send_keys(kwargs['Assignee'])
		time.sleep(2)
		assigneedrdn.send_keys(Keys.DOWN)
		assigneedrdn.send_keys(Keys.ENTER)
		time.sleep(3)
		savebtn = self.driver.find_element_by_link_text('Save')
		savebtn.click()
		time.sleep(3)

		logger.info("Exiting create_incident_verify_p2_slm()")
		return incid, matching


	def search_incident_verify_p2_slm(self, kwargs):
		logger.info("Executing search_incident_verify_p2_slm()")
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
		time.sleep(2)

		"Resolving Incident and Save"
		statuschnge = self.driver.find_element_by_xpath('//input[@id="arid_WIN_3_7"]')
		statuschnge.click()
		statuschnge.send_keys(Keys.DOWN)
		statuschnge.send_keys(kwargs['Newstatus'])
		statuschnge.send_keys(Keys.ENTER)
		time.sleep(2)
		statusreason = self.driver.find_element_by_xpath('//textarea[@id="arid_WIN_3_1000000881"]')
		statusreason.click()
		statusreason.send_keys(Keys.DOWN)
		statuschnge.send_keys(kwargs['Statusreason'])
		statusreason.send_keys(Keys.ENTER)
		time.sleep(2)
		resolution = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_1000000156"]')
		resolution.send_keys(kwargs['Resolution'])
		time.sleep(2)
		savebtn = self.driver.find_element_by_link_text('Save')
		savebtn.click()

		""" Getting the SLA details """
		time.sleep(3)
		window_before = self.driver.window_handles[0]
		#logger.info (window_before)
		self.driver.find_element_by_xpath('//div[@id= "WIN_3_303579500"]').click()
		WebDriverWait(self.driver, 10).until(
			expected_conditions.number_of_windows_to_be(2))
		window_after = self.driver.window_handles[1]
		self.driver.switch_to.window(window_after)
		#logger.info(window_after)

		inqw = self.driver.find_element_by_xpath('//textarea[@id ="arid_WIN_0_303738000"]')
		time.sleep(3)
		incid = inqw.get_attribute("value")
		time.sleep(3)
		slatitle = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[2]/td[1]').text
		logger.info("SLA title =  {}".format(slatitle))
		goal = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[2]/td[2]').text
		logger.info("Goal Attached =  {}".format(goal))
		time.sleep(3)
		hours = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[2]/td[3]').text
		logger.info("Hours Attached = {}".format(hours))
		duedate = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[2]/td[6]').text
		logger.info("DueDate and Time for Resolution = {}".format(duedate))
		#completion = self.driver.find_element_by_xpath('//*[@id="WIN_0_303367100"]').text
		#logger.info("Completion Time for Resolution = {}".format(completion))
		status = self.driver.find_element_by_xpath('//*[@id="WIN_0_301466100"]/table/tbody/tr/td').text
		logger.info("Status after Resolution  = {}".format(status))
		colorcode = self.driver.find_element_by_xpath('//*[@id="WIN_0_301466100"]')
		#colorcode = self.driver.find_element_by_xpath('//*[@id="WIN_0_301466100"]/table/tbody/tr/td')
		ccode = colorcode.get_attribute('style')
		colcode = ccode[86:]
		colocode = colcode[:15]
		logger.info("Colorcode after Resolution = {}".format(colocode))
		progress = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[2]/td[7]').text
		logger.info("Progress after Resolution = {}".format(progress))

		"Validating SLA Details"
		matching = True
		if slatitle != kwargs['Slatitle']:
			logger.error(
				"The SLA Title '{}' is not matching with expected SlA Title '{}'".format(slatitle, kwargs['Slatitle']))
			# raise ValueError
			matching = False
		if goal != kwargs['Goal']:
			logger.error(
				"The Attached Goal'{}' is not matching with expected Goal '{}'".format(goal, kwargs['Goal']))
			# raise ValueError
			matching = False
		elif hours != kwargs['Hours']:
			logger.error(
				"Hours '{}' is not matching with expected Hours '{}'".format(hours, kwargs['Hours']))
			# raise ValueError
			matching = False
		elif status != kwargs['Status']:
			logger.error(
				"Status '{}' is not matching with expected Status '{}'".format(status, kwargs['Status']))
			# raise ValueError
			matching = False
		elif colocode != kwargs['Colorcode']:
			logger.error(
				"Color code '{}' is not matching with expected Colorcode '{}'".format(colocode, kwargs['Colorcode']))
			# raise ValueError
			matching = False
		elif progress != kwargs['Progress']:
			logger.error(
				"Progress '{}' is not matching with expected Progress '{}'".format(progress, kwargs['Progress']))
			# raise ValueError
			matching = False
		else:
			logger.info("Pass")

		"""Printing Milestones"""
		logger.info("Milestone for restoration after Incident Resolution")

		mile1 = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[2]/td[1]/nobr/span').text
		logger.info("Title =  {}".format(mile1))
		mile2 = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[2]/td[2]/nobr/span').text
		logger.info("Execution Time =  {}".format(mile2))
		mile3 = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[2]/td[3]/nobr/span').text
		logger.info("status =  {}".format(mile3))
		mile4 = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[3]/td[1]/nobr/span').text
		logger.info("Title =  {}".format(mile4))
		mile5 = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[3]/td[2]/nobr/span').text
		logger.info("Execurion Time =  {}".format(mile5))
		mile6 = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[3]/td[3]/nobr/span').text
		logger.info("Status =  {}".format(mile6))
		mile7 = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[4]/td[1]/nobr/span').text
		logger.info("Title =  {}".format(mile7))
		mile8 = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[4]/td[2]/nobr/span').text
		logger.info("Execution Time =  {}".format(mile8))
		mile9 = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[4]/td[3]/nobr/span').text
		logger.info("Status =  {}".format(mile9))
		"""
		"Validating SLA Details"
		assert (slatitle == kwargs['Slatitle'])
		assert (goal == kwargs['Goal'])
		assert (hours == kwargs['Hours'])
		assert (status == kwargs['Status'])
		assert (colocode == kwargs['Colorcode'])
		assert (progress == kwargs['Progress'])
		logger.info('Pass')
		"""

		self.driver.close()
		time.sleep(3)
		self.driver.switch_to.window(window_before)
		body = self.driver.find_element_by_css_selector('body')
		body.click()
		body.send_keys(Keys.PAGE_UP)
		logger.info("Exiting search_incident_verify_p2_slm()")
		return incid, matching
	
	def priority_change_verification_main(self, kwargs):
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
		self.driver.find_element_by_xpath('//div[@id= "WIN_3_303579500"]').click()
		WebDriverWait(self.driver, 10).until(
			expected_conditions.number_of_windows_to_be(2))
		window_after = self.driver.window_handles[1]
		self.driver.switch_to.window(window_after)

		"""Getting the text of title goals, .etc"""
		inqw = self.driver.find_element_by_xpath('//textarea[@id ="arid_WIN_0_303738000"]')
		time.sleep(3)
		incid = inqw.get_attribute("value")
		logger.info("{}".format(incid))
		time.sleep(3)
		svttitle1 = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[2]/td[1]').text
		logger.info("SVT title1 =  {}".format(svttitle1))
		svttitle2 = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[3]/td[1]').text
		logger.info("SVT title2 =  {}".format(svttitle2))
		goal_response = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[2]/td[2]').text
		logger.info("Goal1 Attached =  {}".format(goal_response))
		goal_restoration = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[3]/td[2]').text
		logger.info("Goal2 Attached =  {}".format(goal_restoration))
		time.sleep(3)
		response_milestone = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[2]/td[3]').text
		logger.info("Incident 50% milestone for response: {}".format(response_milestone))
		response_status = self.driver.find_element_by_xpath('//*[@id="WIN_0_301466100"]/table/tbody/tr/td').text
		logger.info("Response Status = {}".format(response_status))
		resolution_milestones = self.driver.find_element(By.XPATH, '//*[@id="T300427600"]/tbody/tr[3]')
		time.sleep(3)
		resolution_milestones.click()
		time.sleep(2)
		restoration_status = self.driver.find_element_by_xpath('//*[@id="WIN_0_301369900"]/table/tbody/tr/td').text
		logger.info("Resolution Status = {}".format(restoration_status))
		resolution_milestone1 = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[2]/td[3]').text
		logger.info("Incident resolution 50% milestome: {}".format(resolution_milestone1))
		resolution_milestone2 = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[3]/td[3]').text
		logger.info("Incident resolution 75% milestome: {}".format(resolution_milestone2))
		resolution_milestone3 = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[4]/td[3]').text
		logger.info("Incident resolution 90% milestome: {}".format(resolution_milestone3))
		response_progress = self.driver.find_element(By.XPATH, '//*[@id="T300427600"]/tbody/tr[2]/td[7]').text
		logger.info("Response progress: {}".format(response_progress))
		progress_critical = self.driver.find_element(By.XPATH, '//*[@id="T300427600"]/tbody/tr[3]/td[7]').text
		logger.info("Resolution progress at critical priority: {}".format(progress_critical))

		"""Gettin the color code"""
		colorcode = self.driver.find_element_by_xpath('//*[@id="WIN_0_301466100"]')
		ccode = colorcode.get_attribute('style')
		colocode = re.findall(r'(rgb[(\d\s,)]*)', ccode)[0]
		logger.info("Colorcode before Resolution = {}".format(colocode))
		self.driver.close()
		time.sleep(3)
		self.driver.switch_to.window(window_before)
		time.sleep(4)

		"""changing the priority"""
		urgency = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_1000000162"]')
		urgency.click()
		time.sleep(2)
		urgency.send_keys(Keys.DOWN)
		urgency.send_keys("2-High")
		time.sleep(2)
		urgency.send_keys(Keys.ENTER)
		time.sleep(3)
		urgency.send_keys(kwargs['Urgency'])
		time.sleep(2)
		saveinc.click()
		logger.info("Incident priority changed to 2-High")
		time.sleep(7)

		"""Refreshing the browser"""
		time.sleep(3)
		self.driver.refresh()
		time.sleep(3)

		logger.info("Executing search_incident_verify_slm()")
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
		inciid.send_keys(incid)
		inciid.send_keys(Keys.ENTER)
		time.sleep(2)

		window_before = self.driver.window_handles[0]
		slm = self.driver.find_element_by_xpath('//*[@id="WIN_3_303579500"]')
		time.sleep(4)
		slm.click()
		WebDriverWait(self.driver, 10).until(
			expected_conditions.number_of_windows_to_be(2))
		window_after = self.driver.window_handles[1]
		self.driver.switch_to.window(window_after)
		time.sleep(10)
		svt_title_detached = self.driver.find_element(By.XPATH, '//*[@id="T300427600"]/tbody/tr[2]/td[1]').text
		goal_restoration_detached = self.driver.find_element(By.XPATH, '//*[@id="T300427600"]/tbody/tr[2]/td[2]').text
		progress_critical_detached = self.driver.find_element(By.XPATH, '//*[@id="T300427600"]/tbody/tr[2]/td[7]').text
		progress_tab = self.driver.find_element(By.XPATH, '//*[@id="WIN_0_300427600"]/div[2]/div/div/div/div[7]')
		time.sleep(3)
		progress_tab.click()
		time.sleep(5)
		svt_title_attached = self.driver.find_element(By.XPATH, '//*[@id="T300427600"]/tbody/tr[2]/td[1]').text
		goal_restoration_attached = self.driver.find_element(By.XPATH, '//*[@id="T300427600"]/tbody/tr[2]/td[2]').text
		progress_high_attached = self.driver.find_element(By.XPATH, '//*[@id="T300427600"]/tbody/tr[2]/td[7]').text
		logger.info("Before: "+ svt_title_detached + " : " + goal_restoration_detached + " : " + progress_critical_detached)
		logger.info("Before: " + svt_title_attached + " : " + goal_restoration_attached + " : " + progress_high_attached)
		self.driver.close()
		time.sleep(2)
		self.driver.switch_to.window(window_before)
		"""Refreshing the browser"""
		time.sleep(3)
		self.driver.refresh()
		time.sleep(3)
		logger.info("Executing search_incident_verify_slm()")

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
		inciid.send_keys(incid)
		inciid.send_keys(Keys.ENTER)
		time.sleep(2)

		"""changing the priority"""
		urgency = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_1000000162"]')
		urgency.click()
		time.sleep(2)
		urgency.send_keys(Keys.DOWN)
		urgency.send_keys("3-Medium")
		time.sleep(2)
		urgency.send_keys(Keys.ENTER)
		time.sleep(3)
		urgency.send_keys(kwargs['Urgency'])
		time.sleep(2)
		saveinc = self.driver.find_element_by_xpath('//a[@id="WIN_3_301614800"]/div[@class="btntextdiv"]/div[@class="f1"]')

		saveinc.click()
		logger.info("Incident priority changed to 3-Medium")
		time.sleep(7)
		window_before = self.driver.window_handles[0]
		slm = self.driver.find_element_by_xpath('//*[@id="WIN_3_303579500"]')
		time.sleep(4)
		slm.click()

		WebDriverWait(self.driver, 10).until(
			expected_conditions.number_of_windows_to_be(2))
		window_after = self.driver.window_handles[1]
		self.driver.switch_to.window(window_after)
		time.sleep(10)
		svt_title_detached = self.driver.find_element(By.XPATH, '//*[@id="T300427600"]/tbody/tr[2]/td[1]').text
		goal_restoration_detached = self.driver.find_element(By.XPATH, '//*[@id="T300427600"]/tbody/tr[2]/td[2]').text
		progress_high_detached = self.driver.find_element(By.XPATH, '//*[@id="T300427600"]/tbody/tr[2]/td[7]').text
		progress_tab = self.driver.find_element(By.XPATH, '//*[@id="WIN_0_300427600"]/div[2]/div/div/div/div[7]')
		time.sleep(3)
		progress_tab.click()
		time.sleep(5)
		svt_title_attached = self.driver.find_element(By.XPATH, '//*[@id="T300427600"]/tbody/tr[2]/td[1]').text
		goal_restoration_attached = self.driver.find_element(By.XPATH, '//*[@id="T300427600"]/tbody/tr[2]/td[2]').text
		progress_medium_attached = self.driver.find_element(By.XPATH, '//*[@id="T300427600"]/tbody/tr[2]/td[7]').text
		logger.info("Before: " + svt_title_detached + " : " + goal_restoration_detached + " : " + progress_high_detached)
		logger.info("Before: " + svt_title_attached + " : " + goal_restoration_attached + " : " + progress_medium_attached)
		self.driver.close()
		self.driver.switch_to.window(window_before)
		time.sleep(3)

		"""Refreshing the browser"""
		time.sleep(3)
		self.driver.refresh()
		time.sleep(3)

		logger.info("Executing search_incident_verify_slm()")
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
		inciid.send_keys(incid)
		inciid.send_keys(Keys.ENTER)
		time.sleep(2)

		"""changing the priority"""
		urgency = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_1000000162"]')
		urgency.click()
		time.sleep(2)
		urgency.send_keys(Keys.DOWN)
		urgency.send_keys("4-Low")
		time.sleep(2)
		urgency.send_keys(Keys.ENTER)
		time.sleep(3)
		urgency.send_keys(kwargs['Urgency'])
		time.sleep(2)
		saveinc = self.driver.find_element_by_xpath('//a[@id="WIN_3_301614800"]/div[@class="btntextdiv"]/div[@class="f1"]')

		saveinc.click()
		logger.info("Incident priority changed to 3-Medium")
		time.sleep(7)
		window_before = self.driver.window_handles[0]
		# logger.info (window_before)
		slm = self.driver.find_element_by_xpath('//*[@id="WIN_3_303579500"]')
		time.sleep(4)
		slm.click()

		WebDriverWait(self.driver, 10).until(
			expected_conditions.number_of_windows_to_be(2))
		window_after = self.driver.window_handles[1]
		self.driver.switch_to.window(window_after)
		time.sleep(10)
		svt_title_detached = self.driver.find_element(By.XPATH, '//*[@id="T300427600"]/tbody/tr[2]/td[1]').text
		goal_restoration_detached = self.driver.find_element(By.XPATH, '//*[@id="T300427600"]/tbody/tr[2]/td[2]').text
		progress_medium_detached = self.driver.find_element(By.XPATH, '//*[@id="T300427600"]/tbody/tr[2]/td[7]').text
		progress_tab = self.driver.find_element(By.XPATH, '//*[@id="WIN_0_300427600"]/div[2]/div/div/div/div[7]')
		time.sleep(3)
		progress_tab.click()
		time.sleep(5)
		svt_title_attached = self.driver.find_element(By.XPATH, '//*[@id="T300427600"]/tbody/tr[2]/td[1]').text
		goal_restoration_attached = self.driver.find_element(By.XPATH, '//*[@id="T300427600"]/tbody/tr[2]/td[2]').text
		progress_low_attached = self.driver.find_element(By.XPATH, '//*[@id="T300427600"]/tbody/tr[2]/td[7]').text
		logger.info("Before: " + svt_title_detached + " : " + goal_restoration_detached + " : " + progress_medium_detached)
		logger.info("Before: " + svt_title_attached + " : " + goal_restoration_attached + " : " + progress_low_attached)
		self.driver.close()
		self.driver.switch_to.window(window_before)
		time.sleep(3)

		"""Validations"""
		matching = True
		if progress_critical != kwargs["Progress_critical"]:
			matching = False
			logger.info("The progress of critical priority did not match.")
		if progress_critical_detached != kwargs["Progress_critical_detached"]:
			matching = False
			logger.info("The progress of critical priority did not detach.")
		if progress_high_attached != kwargs["Progress_high_attached"]:
			matching = False
			logger.info("The progress of high priority did not attached.")
		if progress_high_detached != kwargs["Progress_high_detached"]:
			matching = False
			logger.info("The progress of high priority did not detach.")
		if progress_medium_attached != kwargs["Progress_medium_attached"]:
			matching = False
			logger.info("The progress of medium priority did not attached.")
		if progress_medium_detached != kwargs["Progress_medium_detached"]:
			matching = False
			logger.info("The progress of medium priority did not detach.")
		if progress_low_attached != kwargs["Progress_low_attached"]:
			matching = False
			logger.info("The progress of low priority did not attached.")
		return matching
	
	def create_incident_fail_response_sla_main(self, kwargs):
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
		logger.info("Waiting for 15 minutes before saving the incident")
		time.sleep(900)
		saveinc = self.driver.find_element_by_xpath(
			'//a[@id="WIN_3_301614800"]/div[@class="btntextdiv"]/div[@class="f1"]')
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
		time.sleep(2)
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
		
		"""Logout Application"""
		self.driver.close()
		self.driver.switch_to.window(window_before)
		logger.info("Exiting incident_creation()")
		return incid
	
	def slm_maya_main(self, kwargs):
		logger.info("Executing search_incident_verify_slm()")
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
		time.sleep(2)
		
		""" Getting the Incident ID """
		
		time.sleep(3)
		window_before = self.driver.window_handles[0]
		# print window_before
		self.driver.find_element_by_xpath('//div[@id= "WIN_3_303579500"]').click()
		WebDriverWait(self.driver, 10).until(
			expected_conditions.number_of_windows_to_be(2))
		window_after = self.driver.window_handles[1]
		self.driver.switch_to.window(window_after)
		
		"""Getting the text of title goals, .etc"""
		inqw = self.driver.find_element_by_xpath('//textarea[@id ="arid_WIN_0_303738000"]')
		time.sleep(3)
		incid = inqw.get_attribute("value")
		logger.info("{}".format(incid))
		time.sleep(3)
		svttitle1 = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[2]/td[1]').text
		logger.info("SVT title1 =  {}".format(svttitle1))
		svttitle2 = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[3]/td[1]').text
		logger.info("SVT title2 =  {}".format(svttitle2))
		goal_response = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[2]/td[2]').text
		logger.info("Goal1 Attached =  {}".format(goal_response))
		goal_restoration = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[3]/td[2]').text
		logger.info("Goal2 Attached =  {}".format(goal_restoration))
		time.sleep(3)
		response_milestone = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[2]/td[3]').text
		logger.info("Incident 50% milestone for response: {}".format(response_milestone))
		response_status = self.driver.find_element_by_xpath('//*[@id="WIN_0_301466100"]/table/tbody/tr/td').text
		logger.info("Response Status = {}".format(response_status))
		resolution_milestones = self.driver.find_element(By.XPATH, '//*[@id="T300427600"]/tbody/tr[3]')
		time.sleep(3)
		resolution_milestones.click()
		time.sleep(2)
		restoration_status = self.driver.find_element_by_xpath('//*[@id="WIN_0_301369900"]/table/tbody/tr/td').text
		logger.info("Resolution Status = {}".format(restoration_status))
		resolution_milestone1 = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[2]/td[3]').text
		logger.info("Incident resolution 50% milestome: {}".format(resolution_milestone1))
		resolution_milestone2 = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[3]/td[3]').text
		logger.info("Incident resolution 75% milestome: {}".format(resolution_milestone2))
		resolution_milestone3 = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[4]/td[3]').text
		logger.info("Incident resolution 90% milestome: {}".format(resolution_milestone3))
		response_progress = self.driver.find_element(By.XPATH, '//*[@id="T300427600"]/tbody/tr[2]/td[7]').text
		logger.info("Response progress: {}".format(response_progress))
		resolution_progress = self.driver.find_element(By.XPATH, '//*[@id="T300427600"]/tbody/tr[3]/td[7]').text
		logger.info("Resolution progress: {}".format(resolution_progress))
		
		service_restoration_sla = self.driver.find_element(By.XPATH,
		                                                   '//*[@id="T300427600"]/tbody/tr[3]/td[3]/nobr/span').text
		logger.info(service_restoration_sla)
		
		colorcode = self.driver.find_element_by_xpath('//*[@id="WIN_0_301466100"]')
		ccode = colorcode.get_attribute('style')
		colocode = re.findall(r'(rgb[(\d\s,)]*)', ccode)[0]  # To extract RGB code
		logger.info("Colorcode before Resolution = {}".format(colocode))
		
		self.driver.close()
		time.sleep(3)
		self.driver.switch_to.window(window_before)
		
		"""Validations"""
		matching = True
		if goal_response != kwargs["Goal1"]:
			matching = False
			logger.info("Response goal did not match")
		if goal_restoration != kwargs["Goal2"]:
			matching = False
			logger.info("restoration response did not match")
		if response_milestone != kwargs["Response_milestone"]:
			matching = False
			logger.info("Response milestone did not match")
		if resolution_milestone1 != kwargs["Resolution_milestone1"]:
			matching = False
			logger.info("resolution milestone1 did not match")
		if resolution_milestone2 != kwargs["Resolution_milestone1"]:
			matching = False
			logger.info("resolution milestone2 did not match")
		if resolution_milestone3 != kwargs["Resolution_milestone1"]:
			matching = False
			logger.info("resolution milestone3 did not match")
		if response_progress != kwargs["Response_Progress"]:
			matching = False
			logger.info("response progress did not match")
		if resolution_progress != kwargs["Resolution_Progress"]:
			matching = False
			logger.info("resolution progress did not match")
		if colocode != kwargs["Colorcode"]:
			matching = False
			logger.info("Colour code did not match")
		if response_status != kwargs["Status1"]:
			matching = False
			logger.info("response status did not match")
		if restoration_status != kwargs["Status2"]:
			matching = False
			logger.info("Resolution status did not match")
		if svttitle1 != kwargs["Svttitle1"]:
			matching = False
			logger.info("SVT response title did not match")
		if svttitle2 != kwargs["Svttitle2"]:
			matching = False
			logger.info("SVT resolution title did not match")
		time_in_hours = int(re.findall(r'(\d+).0', service_restoration_sla)[0])
		logger.info(time_in_hours * 3600)
		
		return int(time_in_hours * 3600)
	
	def slm_maya_seven_ok_case_1_main(self, kwargs):
		logger.info("Executing search_incident_verify_slm()")
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
		time.sleep(2)
		
		""" Getting the Incident ID """
		
		time.sleep(3)
		window_before = self.driver.window_handles[0]
		# print window_before
		self.driver.find_element_by_xpath('//div[@id= "WIN_3_303579500"]').click()
		WebDriverWait(self.driver, 10).until(
			expected_conditions.number_of_windows_to_be(2))
		window_after = self.driver.window_handles[1]
		self.driver.switch_to.window(window_after)
		
		"""Getting the text of title goals, .etc"""
		inqw = self.driver.find_element_by_xpath('//textarea[@id ="arid_WIN_0_303738000"]')
		time.sleep(3)
		incid = inqw.get_attribute("value")
		logger.info("{}".format(incid))
		time.sleep(3)
		svttitle1 = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[2]/td[1]').text
		logger.info("SVT title1 =  {}".format(svttitle1))
		svttitle2 = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[3]/td[1]').text
		logger.info("SVT title2 =  {}".format(svttitle2))
		goal_response = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[2]/td[2]').text
		logger.info("Goal1 Attached =  {}".format(goal_response))
		goal_restoration = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[3]/td[2]').text
		logger.info("Goal2 Attached =  {}".format(goal_restoration))
		time.sleep(3)
		response_milestone = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[2]/td[3]').text
		logger.info("Incident 50% milestone for response: {}".format(response_milestone))
		response_status = self.driver.find_element_by_xpath('//*[@id="WIN_0_301370000"]/table/tbody/tr/td').text
		logger.info("Response Status = {}".format(response_status))
		resolution_milestones = self.driver.find_element(By.XPATH, '//*[@id="T300427600"]/tbody/tr[3]')
		
		"""Getting the color code of the response sla"""
		colorcode_response = self.driver.find_element_by_xpath('//*[@id="WIN_0_301275400"]')
		ccode_response = colorcode_response.get_attribute('style')
		colocode_response = re.findall(r'(rgb[(\d\s,)]*)', ccode_response)[0]  # To extract RGB code
		logger.info("Colorcode before Resolution = {}".format(colocode_response))
		
		time.sleep(3)
		resolution_milestones.click()
		time.sleep(2)
		restoration_status = self.driver.find_element_by_xpath('//*[@id="WIN_0_301369900"]/table/tbody/tr/td').text
		logger.info("Resolution Status = {}".format(restoration_status))
		resolution_milestone1 = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[2]/td[3]').text
		logger.info("Incident resolution 50% milestome: {}".format(resolution_milestone1))
		resolution_milestone2 = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[3]/td[3]').text
		logger.info("Incident resolution 75% milestome: {}".format(resolution_milestone2))
		resolution_milestone3 = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[4]/td[3]').text
		logger.info("Incident resolution 90% milestome: {}".format(resolution_milestone3))
		response_progress = self.driver.find_element(By.XPATH, '//*[@id="T300427600"]/tbody/tr[2]/td[7]').text
		logger.info("Response progress: {}".format(response_progress))
		resolution_progress = self.driver.find_element(By.XPATH, '//*[@id="T300427600"]/tbody/tr[3]/td[7]').text
		logger.info("Resolution progress: {}".format(resolution_progress))
		
		colorcode_resolution = self.driver.find_element_by_xpath('//*[@id="WIN_0_301466100"]')
		ccode_resolution = colorcode_resolution.get_attribute('style')
		colocode_resolution = re.findall(r'(rgb[(\d\s,)]*)', ccode_resolution)[0]  # To extract RGB code
		logger.info("Colorcode before Resolution = {}".format(colocode_resolution))
		
		colorcode_response = self.driver.find_element_by_xpath('//*[@id="WIN_0_301275400"]')
		ccode_response = colorcode_response.get_attribute('style')
		colocode_response = re.findall(r'(rgb[(\d\s,)]*)', ccode_response)[0]  # To extract RGB code
		logger.info("Colorcode before Resolution = {}".format(colocode_response))
		
		self.driver.close()
		time.sleep(3)
		self.driver.switch_to.window(window_before)
		
		"""Validations"""
		matching = True
		if goal_response != kwargs["Goal1"]:
			matching = False
			logger.info("Response goal did not match")
		if goal_restoration != kwargs["Goal2"]:
			matching = False
			logger.info("restoration response did not match")
		if response_milestone != kwargs["Response_milestone"]:
			matching = False
			logger.info("Response milestone did not match")
		if resolution_milestone1 != kwargs["Resolution_milestone1"]:
			matching = False
			logger.info("resolution milestone1 did not match")
		if resolution_milestone2 != kwargs["Resolution_milestone1"]:
			matching = False
			logger.info("resolution milestone2 did not match")
		if resolution_milestone3 != kwargs["Resolution_milestone1"]:
			matching = False
			logger.info("resolution milestone3 did not match")
		if response_progress != kwargs["Response_Progress"]:
			matching = False
			logger.info("response progress did not match")
		if resolution_progress != kwargs["Resolution_Progress"]:
			matching = False
			logger.info("resolution progress did not match")
		if colocode_resolution != kwargs["Colorcode_resolution"]:
			matching = False
			logger.info("Colour code did not match")
		if colocode_response != kwargs["Colorcode_response"]:
			matching = False
			logger.info("Colour code did not match")
		if response_status != kwargs["Status1"]:
			matching = False
			logger.info("response status did not match")
		if restoration_status != kwargs["Status2"]:
			matching = False
			logger.info("Resolution status did not match")
		if svttitle1 != kwargs["Svttitle1"]:
			matching = False
			logger.info("SVT response title did not match")
		if svttitle2 != kwargs["Svttitle2"]:
			matching = False
			logger.info("SVT resolution title did not match")
		return matching
	
	def slm_maya_seven_auto_warning_case_main(self, kwargs):
		logger.info("Executing search_incident_verify_slm()")
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
		time.sleep(2)
		
		""" Getting the SLA details """
		time.sleep(3)
		window_before = self.driver.window_handles[0]
		# logger.info (window_before)
		self.driver.find_element_by_xpath('//div[@id= "WIN_3_303579500"]').click()
		WebDriverWait(self.driver, 10).until(
			expected_conditions.number_of_windows_to_be(2))
		window_after = self.driver.window_handles[1]
		self.driver.switch_to.window(window_after)
		time.sleep(3)
		resolution_milestones = self.driver.find_element(By.XPATH, '//*[@id="T300427600"]/tbody/tr[2]')
		time.sleep(3)
		resolution_milestones.click()
		time.sleep(2)
		resolution_milestone1 = self.driver.find_element_by_xpath(
			'//*[@id="T303397300"]/tbody/tr[2]/td[3]/nobr/span').text
		logger.info("Incident resolution 50% milestome: {}".format(resolution_milestone1))
		resolution_milestone2 = self.driver.find_element_by_xpath(
			'//*[@id="T303397300"]/tbody/tr[3]/td[3]/nobr/span').text
		logger.info("Incident resolution 75% milestome: {}".format(resolution_milestone2))
		resolution_milestone3 = self.driver.find_element_by_xpath(
			'//*[@id="T303397300"]/tbody/tr[4]/td[3]/nobr/span').text
		logger.info("Incident resolution 90% milestome: {}".format(resolution_milestone3))
		colorcode = self.driver.find_element_by_xpath('//*[@id="WIN_0_300132000"]')
		ccode = colorcode.get_attribute('style')
		colocode = re.findall(r'(rgb[(\d\s,)]*)', ccode)[0]
		logger.info("ccode : {}".format(ccode))
		logger.info("Colorcode before Resolution = {}".format(colocode))
		restoration_status = self.driver.find_element(By.XPATH, '//*[@id="WIN_0_301370100"]/table/tbody/tr/td').text
		logger.info("Restoration status is {}".format(restoration_status))
		resolution_progress = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[2]/td[7]').text
		logger.info("Restoration Progress: {}".format(resolution_progress))
		
		"""Validations"""
		matching = True
		if resolution_milestone1 != kwargs["Resolution_milestone1"]:
			matching = False
			logger.info("resolution milestone1 did not match")
		if resolution_milestone2 != kwargs["Resolution_milestone2"]:
			matching = False
			logger.info("resolution milestone2 did not match")
		if resolution_milestone3 != kwargs["Resolution_milestone3"]:
			matching = False
			logger.info("resolution milestone3 did not match")
		if resolution_progress != kwargs["Resolution_Progress"]:
			matching = False
			logger.info("resolution progress did not match")
		if colocode != kwargs["Colorcode"]:
			matching = False
			logger.info('Colour code did not match')
		if restoration_status != kwargs["Status2"]:
			matching = False
			logger.info("Resolution status did not match")
		
		"""Closing the SLM window"""
		self.driver.close()
		time.sleep(3)
		self.driver.switch_to.window(window_before)
		time.sleep(3)
		return matching
	
	def slm_maya_seven_auto_warning_case_2_main(self, kwargs):
		logger.info("Executing search_incident_verify_slm()")
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
		time.sleep(2)
		
		""" Getting the SLA details """
		time.sleep(3)
		window_before = self.driver.window_handles[0]
		# logger.info (window_before)
		self.driver.find_element_by_xpath('//div[@id= "WIN_3_303579500"]').click()
		WebDriverWait(self.driver, 10).until(
			expected_conditions.number_of_windows_to_be(2))
		window_after = self.driver.window_handles[1]
		self.driver.switch_to.window(window_after)
		time.sleep(3)
		# progress_tab = self.driver.find_element(By.XPATH, '//*[@id="WIN_0_300427600"]/div[2]/div/div/div/div[7]')
		# time.sleep(2)
		# progress_tab.click()
		# time.sleep(2)
		resolution_milestones = self.driver.find_element(By.XPATH, '//*[@id="T300427600"]/tbody/tr[2]')
		time.sleep(3)
		resolution_milestones.click()
		time.sleep(2)
		resolution_milestone1 = self.driver.find_element_by_xpath(
			'//*[@id="T303397300"]/tbody/tr[2]/td[3]/nobr/span').text
		logger.info("Incident resolution 50% milestome: {}".format(resolution_milestone1))
		resolution_milestone2 = self.driver.find_element_by_xpath(
			'//*[@id="T303397300"]/tbody/tr[3]/td[3]/nobr/span').text
		logger.info("Incident resolution 75% milestome: {}".format(resolution_milestone2))
		resolution_milestone3 = self.driver.find_element_by_xpath(
			'//*[@id="T303397300"]/tbody/tr[4]/td[3]/nobr/span').text
		logger.info("Incident resolution 90% milestome: {}".format(resolution_milestone3))
		colorcode = self.driver.find_element_by_xpath('//*[@id="WIN_0_300132000"]')
		ccode = colorcode.get_attribute('style')
		colocode = re.findall(r'(rgb[(\d\s,)]*)', ccode)[0]
		logger.info("ccode : {}".format(ccode))
		logger.info("Colorcode before Resolution = {}".format(colocode))
		restoration_status = self.driver.find_element(By.XPATH, '//*[@id="WIN_0_301370100"]/table/tbody/tr/td').text
		logger.info("Restoration status is {}".format(restoration_status))
		resolution_progress = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[2]/td[7]').text
		logger.info("Restoration Progress: {}".format(resolution_progress))
		
		"""Validations"""
		matching = True
		if resolution_milestone1 != kwargs["Resolution_milestone1"]:
			matching = False
			logger.info("resolution milestone1 did not match")
		if resolution_milestone2 != kwargs["Resolution_milestone2"]:
			matching = False
			logger.info("resolution milestone2 did not match")
		if resolution_milestone3 != kwargs["Resolution_milestone3"]:
			matching = False
			logger.info("resolution milestone3 did not match")
		if resolution_progress != kwargs["Resolution_Progress"]:
			matching = False
			logger.info("resolution progress did not match")
		if colocode != kwargs["Colorcode"]:
			matching = False
			logger.info('Colour code did not match')
		if restoration_status != kwargs["Status2"]:
			matching = False
			logger.info("Resolution status did not match")
		
		"""Closing the SLM window"""
		self.driver.close()
		time.sleep(3)
		self.driver.switch_to.window(window_before)
		time.sleep(3)
		return matching
	
	def slm_maya_seven_auto_critical_case_main(self, kwargs):
		logger.info("Executing search_incident_verify_slm()")
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
		time.sleep(2)
		
		""" Getting the SLA details """
		time.sleep(3)
		window_before = self.driver.window_handles[0]
		# logger.info (window_before)
		self.driver.find_element_by_xpath('//div[@id= "WIN_3_303579500"]').click()
		WebDriverWait(self.driver, 10).until(
			expected_conditions.number_of_windows_to_be(2))
		window_after = self.driver.window_handles[1]
		self.driver.switch_to.window(window_after)
		# logger.info(window_after)
		resolution_milestones = self.driver.find_element(By.XPATH, '//*[@id="T300427600"]/tbody/tr[2]')
		time.sleep(3)
		resolution_milestones.click()
		time.sleep(2)
		restoration_status = self.driver.find_element_by_xpath('//*[@id="WIN_0_301370000"]/table/tbody/tr/td').text
		logger.info("Resolution Status  = {}".format(restoration_status))
		resolution_milestone1 = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[2]/td[3]').text
		logger.info("Incident resolution 50% milestome: {}".format(resolution_milestone1))
		resolution_milestone2 = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[3]/td[3]').text
		logger.info("Incident resolution 75% milestome: {}".format(resolution_milestone2))
		resolution_milestone3 = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[4]/td[3]').text
		logger.info("Incident resolution 90% milestome: {}".format(resolution_milestone3))
		colorcode = self.driver.find_element_by_xpath('//*[@id="WIN_0_301370000"]')
		ccode = colorcode.get_attribute('style')
		# colcode = ccode[86:]
		colocode = re.findall(r'(rgb[(\d\s,)]*)', ccode)[0]
		logger.info("ccode : {}".format(ccode))
		logger.info("Colorcode before Resolution = {}".format(colocode))
		restoration_status = self.driver.find_element(By.XPATH, '//*[@id="WIN_0_301370000"]/table/tbody/tr/td').text
		logger.info("Restoration status is {}".format(restoration_status))
		resolution_progress = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[2]/td[7]').text
		logger.info("Restoration Progress: {}".format(resolution_progress))
		
		"""Validations"""
		matching = True
		if resolution_milestone1 != kwargs["Resolution_milestone1"]:
			matching = False
			logger.info("resolution milestone1 did not match")
		if resolution_milestone2 != kwargs["Resolution_milestone1"]:
			matching = False
			logger.info("resolution milestone2 did not match")
		if resolution_milestone3 != kwargs["Resolution_milestone1"]:
			matching = False
			logger.info("resolution milestone3 did not matcht")
		if resolution_progress != kwargs["Resolution_Progress"]:
			matching = False
			logger.info("resolution progress did not match")
		if colocode != kwargs["Colorcode"]:
			matching = False
			logger.info("Colour code did not match")
		if restoration_status != kwargs["Status2"]:
			matching = False
			logger.info("Resolution status did not match")
		self.driver.close()
		time.sleep(3)
		self.driver.switch_to.window(window_before)
		time.sleep(3)
		return matching
	
	def slm_maya_incident_creation(self, kwargs):
		logger.info("Executing incident_creation()")
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
		
		assignee = self.driver.find_element_by_xpath('//textarea[@id="arid_WIN_3_1000000218"]')
		assignee.click()
		assignee.send_keys(kwargs['Assignee'])
		time.sleep(3)
		assignee.send_keys(Keys.DOWN)
		assignee.send_keys(Keys.ENTER)
		
		status = self.driver.find_element_by_xpath('//div[@class="selection"]/input[@id="arid_WIN_3_7"]')
		status.click()
		status.send_keys(Keys.DOWN)
		status.send_keys(kwargs['Status'])
		status.send_keys(Keys.ENTER)
		self.driver.save_screenshot('D:\git\screenshots\savebutton1.png')
		saveinc = self.driver.find_element_by_xpath(
			'//a[@id="WIN_3_301614800"]/div[@class="btntextdiv"]/div[@class="f1"]')
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
		self.driver.find_element_by_xpath('//div[@id= "WIN_3_303579500"]').click()
		WebDriverWait(self.driver, 10).until(
			expected_conditions.number_of_windows_to_be(2))
		window_after = self.driver.window_handles[1]
		self.driver.switch_to.window(window_after)
		
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
		logger.info("incident id is = {}".format(incid))
		return incid
	
	def slm_maya_incident_search_and_verification_of_slm(self, incident_id, kwargs):
		logger.info("Executing verification_of_slm()")
		""" Clicking on Application"""
		appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
		appl.click()
		
		"""Clicking on Incident Management -> Search Incident"""
		incmgmt = self.driver.find_element_by_link_text('Incident Management')
		incmgmt.click()
		incmgmtcon = self.driver.find_element_by_link_text('Search Incident')
		incmgmtcon.click()
		
		"""Filling IncidenComplete Priority Change Final Via Guit ID"""
		
		time.sleep(5)
		enter_id = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_1000000161"]')
		enter_id.send_keys(incident_id)  # change id enter
		time.sleep(4)
		
		"""Then search"""
		self.driver.find_element_by_xpath('//*[@id="WIN_3_1002"]/div/div').click()  # search button
		time.sleep(4)
		
		logger.info("clicking on SLM status")
		
		time.sleep(3)
		window_before = self.driver.window_handles[0]
		self.driver.find_element_by_xpath('//div[@id= "WIN_3_303579500"]').click()
		WebDriverWait(self.driver, 10).until(
			expected_conditions.number_of_windows_to_be(2))
		window_after = self.driver.window_handles[1]
		self.driver.switch_to.window(window_after)
		self.driver.save_screenshot('D:\git\screenshots\slmstatus_before_resolving_ticket1.png')
		
		"""Getting the text of title goals, .etc"""
		logger.info("Verification of SLM status")
		time.sleep(3)
		svttitle1 = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[2]/td[1]').text
		logger.info("SVT title1 =  {}".format(svttitle1))
		svttitle2 = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[3]/td[1]').text
		logger.info("SVT title2 =  {}".format(svttitle2))
		goal_response = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[2]/td[2]').text
		logger.info("Goal1 Attached =  {}".format(goal_response))
		goal_restoration = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[3]/td[2]').text
		logger.info("Goal2 Attached =  {}".format(goal_restoration))
		time.sleep(3)
		
		hours = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[3]/td[3]/nobr/span').text
		logger.info("Hours = {}".format(hours))
		
		response_milestone = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[2]/td[3]').text
		logger.info("Incident 50% milestone for response: {}".format(response_milestone))
		response_status = self.driver.find_element_by_xpath('//*[@id="WIN_0_301466100"]/table/tbody/tr/td').text
		logger.info("Response Status = {}".format(response_status))
		resolution_milestones = self.driver.find_element(By.XPATH, '//*[@id="T300427600"]/tbody/tr[3]')
		time.sleep(3)
		resolution_milestones.click()
		time.sleep(2)
		restoration_status = self.driver.find_element_by_xpath('//*[@id="WIN_0_301369900"]/table/tbody/tr/td').text
		logger.info("Restoration Status = {}".format(restoration_status))
		resolution_milestone1 = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[2]/td[3]').text
		logger.info("Incident resolution 50% milestome: {}".format(resolution_milestone1))
		resolution_milestone2 = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[3]/td[3]').text
		logger.info("Incident resolution 75% milestome: {}".format(resolution_milestone2))
		resolution_milestone3 = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[4]/td[3]').text
		logger.info("Incident resolution 90% milestome: {}".format(resolution_milestone3))
		response_progress = self.driver.find_element(By.XPATH, '//*[@id="T300427600"]/tbody/tr[2]/td[7]').text
		logger.info("Response progress: {}".format(response_progress))
		resolution_progress = self.driver.find_element(By.XPATH, '//*[@id="T300427600"]/tbody/tr[3]/td[7]').text
		logger.info("Resolution progress: {}".format(resolution_progress))
		
		colorcode = self.driver.find_element_by_xpath('//*[@id="WIN_0_301466100"]')
		ccode = colorcode.get_attribute('style')
		colocode = re.findall(r'(rgb[(\d\s,)]*)', ccode)[0]  # To extract RGB code
		logger.info("Colorcode before Resolution = {}".format(colocode))
		
		self.driver.close()
		time.sleep(3)
		self.driver.switch_to.window(window_before)
		
		"""Validations"""
		matching = True
		if goal_response != kwargs["Goal1"]:
			matching = False
			logger.info("Response goal did not match")
		if goal_restoration != kwargs["Goal2"]:
			matching = False
			logger.info("restoration response did not match")
		if hours != kwargs["hours"]:
			matching = False
			logger.info("Hours did not match")
		if response_milestone != kwargs["Response_milestone"]:
			matching = False
			logger.info("Response milestone did not match")
		if resolution_milestone1 != kwargs["Resolution_milestone1"]:
			matching = False
			logger.info("resolution milestone1 did not match")
		if resolution_milestone2 != kwargs["Resolution_milestone1"]:
			matching = False
			logger.info("resolution milestone2 did not match")
		if resolution_milestone3 != kwargs["Resolution_milestone1"]:
			matching = False
			logger.info("resolution milestone3 did not match")
		if response_progress != kwargs["Response_Progress"]:
			matching = False
			logger.info("response progress did not match")
		if resolution_progress != kwargs["Resolution_Progress"]:
			matching = False
			logger.info("resolution progress did not match")
		if colocode != kwargs["Colorcode"]:
			matching = False
			logger.info("Colour code did not match")
		if response_status != kwargs["Status1"]:
			matching = False
			logger.info("response status did not match")
		if restoration_status != kwargs["Status2"]:
			matching = False
			logger.info("Resolution status did not match")
		if svttitle1 != kwargs["Svttitle1"]:
			matching = False
			logger.info("SVT response title did not match")
		if svttitle2 != kwargs["Svttitle2"]:
			matching = False
			logger.info("SVT resolution title did not match")
		return matching
	
	def slm_maya_incident_search_and_resolve(self, incident_id, kwargs):
		logger.info("Executing incident_resolve()")
		""" Clicking on Application"""
		appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
		appl.click()
		
		"""Clicking on Incident Management -> Search Incident"""
		incmgmt = self.driver.find_element_by_link_text('Incident Management')
		incmgmt.click()
		incmgmtcon = self.driver.find_element_by_link_text('Search Incident')
		incmgmtcon.click()
		
		"""Filling Incident ID"""
		
		time.sleep(5)
		enter_id = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_1000000161"]')
		enter_id.send_keys(incident_id)  # change id enter
		time.sleep(4)
		
		"""Then search"""
		self.driver.find_element_by_xpath('//*[@id="WIN_3_1002"]/div/div').click()  # search button
		time.sleep(4)
		
		logger.info("Change the status as resolved")
		
		status = self.driver.find_element_by_xpath('//div[@class="selection"]/input[@id="arid_WIN_3_7"]')
		status.click()
		status.send_keys(Keys.DOWN)
		status.send_keys(kwargs['Status'])
		status.send_keys(Keys.ENTER)
		self.driver.save_screenshot('D:\git\screenshots\slmresolve.png')
		time.sleep(4)
		
		self.driver.find_element_by_xpath('//*[@id="WIN_3_1000000881"]/a').click()
		time.sleep(2)
		
		arvalue = "'" + kwargs['arvalue'] + "'"
		status_reason = self.driver.find_element_by_xpath(
			"//td[@class='MenuEntryNoSub' and @arvalue=" + arvalue + "]").click()
		time.sleep(4)
		
		resolution = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_1000000156"]')
		resolution.send_keys(kwargs['Resolution'])
		time.sleep(2)
		savebtn = self.driver.find_element_by_link_text('Save')
		savebtn.click()
		time.sleep(5)
	
	def slm_maya_incident_search_and_resolve_verification_of_slm(self, incident_id, kwargs):
		logger.info("Execuitng verification_of_slm()")
		""" Clicking on Application"""
		appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
		appl.click()
		
		"""Clicking on Incident Management -> Search Incident"""
		incmgmt = self.driver.find_element_by_link_text('Incident Management')
		incmgmt.click()
		incmgmtcon = self.driver.find_element_by_link_text('Search Incident')
		incmgmtcon.click()
		
		"""Filling Incident ID"""
		
		time.sleep(5)
		enter_id = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_1000000161"]')
		enter_id.send_keys(incident_id)  # change id enter
		time.sleep(4)
		
		"""Then search"""
		self.driver.find_element_by_xpath('//*[@id="WIN_3_1002"]/div/div').click()  # search button
		time.sleep(4)
		
		logger.info("clicking on SLM status")
		
		time.sleep(3)
		window_before = self.driver.window_handles[0]
		self.driver.find_element_by_xpath('//div[@id= "WIN_3_303579500"]').click()
		WebDriverWait(self.driver, 10).until(
			expected_conditions.number_of_windows_to_be(2))
		window_after = self.driver.window_handles[1]
		self.driver.switch_to.window(window_after)
		self.driver.save_screenshot('D:\git\screenshots\slmstatus_after_resolving_ticket1.png')
		
		"""Getting the text of title goals, .etc"""
		logger.info("Verification of SLM status")
		time.sleep(3)
		svttitle1 = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[2]/td[1]').text
		logger.info("SVT title1 =  {}".format(svttitle1))
		svttitle2 = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[3]/td[1]').text
		logger.info("SVT title2 =  {}".format(svttitle2))
		goal_restoration = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[2]/td[2]').text
		logger.info("Goal1 Attached =  {}".format(goal_restoration))
		goal_response = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[3]/td[2]').text
		logger.info("Goal2 Attached =  {}".format(goal_response))
		time.sleep(3)
		
		hours = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[2]/td[3]/nobr/span').text
		logger.info("Hours = {}".format(hours))
		
		resolution_milestone1 = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[2]/td[3]').text
		logger.info("Incident resolution 50% milestome: {}".format(resolution_milestone1))
		resolution_milestone2 = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[3]/td[3]').text
		logger.info("Incident resolution 75% milestome: {}".format(resolution_milestone2))
		resolution_milestone3 = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[4]/td[3]').text
		logger.info("Incident resolution 90% milestome: {}".format(resolution_milestone3))
		
		restoration_status = self.driver.find_element_by_xpath('//*[@id="WIN_0_301466100"]/table/tbody/tr/td').text
		logger.info("Restoration Status = {}".format(restoration_status))
		
		response_milestones = self.driver.find_element(By.XPATH, '//*[@id="T300427600"]/tbody/tr[3]')
		time.sleep(3)
		response_milestones.click()
		time.sleep(2)
		response_milestone = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[2]/td[3]').text
		logger.info("Incident 50% milestone for response: {}".format(response_milestone))
		
		response_status = self.driver.find_element_by_xpath('//*[@id="WIN_0_301466100"]/table/tbody/tr/td').text
		logger.info("Response Status = {}".format(response_status))
		
		resolution_progress = self.driver.find_element(By.XPATH, '//*[@id="T300427600"]/tbody/tr[3]/td[7]').text
		logger.info("Resolution progress: {}".format(resolution_progress))
		
		response_progress = self.driver.find_element(By.XPATH, '//*[@id="T300427600"]/tbody/tr[2]/td[7]').text
		logger.info("Response progress: {}".format(response_progress))
		
		colorcode_resolution = self.driver.find_element_by_xpath('//*[@id="WIN_0_301466100"]')
		ccode = colorcode_resolution.get_attribute('style')
		colocode_resolution = re.findall(r'(rgb[(\d\s,)]*)', ccode)[0]  # To extract RGB code
		logger.info("Colorcode for Resolution = {}".format(colocode_resolution))
		
		colorcode_response = self.driver.find_element_by_xpath('//*[@id="WIN_0_301466100"]')
		ccode = colorcode_response.get_attribute('style')
		colocode_response = re.findall(r'(rgb[(\d\s,)]*)', ccode)[0]  # To extract RGB code
		logger.info("Colorcode for Response = {}".format(colocode_response))
		
		self.driver.close()
		time.sleep(3)
		self.driver.switch_to.window(window_before)
		
		"""Validations"""
		matching = True
		if goal_restoration != kwargs["Goal1"]:
			matching = False
			logger.info("Restoration goal did not match")
		if goal_response != kwargs["Goal2"]:
			matching = False
			logger.info("Response goal did not match")
		if hours != kwargs["hours"]:
			matching = False
			logger.info("Hours did not match")
		if response_milestone != kwargs["Response_milestone"]:
			matching = False
			logger.info("Response milestone did not match")
		if resolution_milestone1 != kwargs["Resolution_milestone1"]:
			matching = False
			logger.info("resolution milestone1 did not match")
		if resolution_milestone2 != kwargs["Resolution_milestone1"]:
			matching = False
			logger.info("resolution milestone2 did not match")
		if resolution_milestone3 != kwargs["Resolution_milestone1"]:
			matching = False
			logger.info("resolution milestone3 did not match")
		if response_progress != kwargs["Response_Progress"]:
			matching = False
			logger.info("response progress did not match")
		if resolution_progress != kwargs["Resolution_Progress"]:
			matching = False
			logger.info("resolution progress did not match")
		if colocode_resolution != kwargs["Colorcode"]:
			matching = False
			logger.info("Colour code did not match")
		
		if colocode_response != kwargs["Colorcode"]:
			matching = False
			logger.info("Colour code did not match")
		if response_status != kwargs["Status1"]:
			matching = False
			logger.info("response status did not match")
		if restoration_status != kwargs["Status2"]:
			matching = False
			logger.info("Resolution status did not match")
		if svttitle1 != kwargs["Svttitle1"]:
			matching = False
			logger.info("SVT response title did not match")
		if svttitle2 != kwargs["Svttitle2"]:
			matching = False
			logger.info("SVT resolution title did not match")
		return matching
	
	def slm_maya_incident_search_and_verification_of_8_hours_slm(self, incident_id, kwargs):
		logger.info("Executing verification_of_slm()")
		""" Clicking on Application"""
		appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
		appl.click()
		
		"""Clicking on Incident Management -> Search Incident"""
		incmgmt = self.driver.find_element_by_link_text('Incident Management')
		incmgmt.click()
		incmgmtcon = self.driver.find_element_by_link_text('Search Incident')
		incmgmtcon.click()
		
		"""Filling IncidenComplete Priority Change Final Via Guit ID"""
		
		time.sleep(5)
		enter_id = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_1000000161"]')
		enter_id.send_keys(incident_id)  # change id enter
		time.sleep(4)
		
		"""Then search"""
		self.driver.find_element_by_xpath('//*[@id="WIN_3_1002"]/div/div').click()  # search button
		time.sleep(4)
		
		logger.info("clicking on SLM status")
		
		time.sleep(3)
		window_before = self.driver.window_handles[0]
		self.driver.find_element_by_xpath('//div[@id= "WIN_3_303579500"]').click()
		WebDriverWait(self.driver, 10).until(
			expected_conditions.number_of_windows_to_be(2))
		window_after = self.driver.window_handles[1]
		self.driver.switch_to.window(window_after)
		
		"""Getting the text of title goals, .etc"""
		logger.info("Verification of SLM status")
		time.sleep(3)
		svttitle1 = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[2]/td[1]').text
		logger.info("SVT title1 =  {}".format(svttitle1))
		goal_restoration = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[2]/td[2]').text
		logger.info("Goal1 Attached =  {}".format(goal_restoration))
		hours = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[2]/td[3]/nobr/span').text
		logger.info("Hours = {}".format(hours))
		time.sleep(3)
		restoration_status = self.driver.find_element_by_xpath('//*[@id="WIN_0_301369900"]/table/tbody/tr/td').text
		logger.info("Restoration Status = {}".format(restoration_status))
		resolution_milestone1 = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[2]/td[3]').text
		logger.info("Incident resolution 50% milestome: {}".format(resolution_milestone1))
		resolution_milestone2 = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[3]/td[3]').text
		logger.info("Incident resolution 75% milestome: {}".format(resolution_milestone2))
		resolution_milestone3 = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[4]/td[3]').text
		logger.info("Incident resolution 90% milestome: {}".format(resolution_milestone3))
		resolution_progress = self.driver.find_element(By.XPATH, '//*[@id="T300427600"]/tbody/tr[2]/td[7]').text
		logger.info("Resolution progress: {}".format(resolution_progress))
		
		colorcode = self.driver.find_element_by_xpath('//*[@id="WIN_0_301466100"]')
		ccode = colorcode.get_attribute('style')
		colocode = re.findall(r'(rgb[(\d\s,)]*)', ccode)[0]  # To extract RGB code
		logger.info("Colorcode before Resolution = {}".format(colocode))
		
		self.driver.close()
		time.sleep(3)
		self.driver.switch_to.window(window_before)
		
		"""Validations"""
		matching = True
		if goal_restoration != kwargs["Goal1"]:
			matching = False
			logger.info("restoration response did not match")
		if hours != kwargs["hours"]:
			matching = False
			logger.info("Hours did not match")
		if resolution_milestone1 != kwargs["Resolution_milestone1"]:
			matching = False
			logger.info("resolution milestone1 did not match")
		if resolution_milestone2 != kwargs["Resolution_milestone1"]:
			matching = False
			logger.info("resolution milestone2 did not match")
		if resolution_milestone3 != kwargs["Resolution_milestone1"]:
			matching = False
			logger.info("resolution milestone3 did not match")
		if resolution_progress != kwargs["Resolution_Progress"]:
			matching = False
			logger.info("resolution progress did not match")
		if colocode != kwargs["Colorcode"]:
			matching = False
			logger.info("Colour code did not match")
		if restoration_status != kwargs["Status2"]:
			matching = False
			logger.info("Resolution status did not match")
		if svttitle1 != kwargs["Svttitle1"]:
			matching = False
			logger.info("SVT title did not match")
		return matching
	
	def slm_maya_incident_search_and_resolve_verification_of_8_hours_slm(self, incident_id, kwargs):
		logger.info("Execuitng verification_of_slm()")
		""" Clicking on Application"""
		appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
		appl.click()
		
		"""Clicking on Incident Management -> Search Incident"""
		incmgmt = self.driver.find_element_by_link_text('Incident Management')
		incmgmt.click()
		incmgmtcon = self.driver.find_element_by_link_text('Search Incident')
		incmgmtcon.click()
		
		"""Filling Incident ID"""
		
		time.sleep(5)
		enter_id = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_1000000161"]')
		enter_id.send_keys(incident_id)  # change id enter
		time.sleep(4)
		
		"""Then search"""
		self.driver.find_element_by_xpath('//*[@id="WIN_3_1002"]/div/div').click()  # search button
		time.sleep(4)
		
		logger.info("clicking on SLM status")
		
		time.sleep(3)
		window_before = self.driver.window_handles[0]
		self.driver.find_element_by_xpath('//div[@id= "WIN_3_303579500"]').click()
		WebDriverWait(self.driver, 10).until(
			expected_conditions.number_of_windows_to_be(2))
		window_after = self.driver.window_handles[1]
		self.driver.switch_to.window(window_after)
		
		"""Getting the text of title goals, .etc"""
		logger.info("Verification of SLM status")
		time.sleep(3)
		svttitle1 = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[2]/td[1]').text
		logger.info("SVT title1 =  {}".format(svttitle1))
		goal_restoration = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[2]/td[2]').text
		logger.info("Goal1 Attached =  {}".format(goal_restoration))
		time.sleep(3)
		
		hours = self.driver.find_element_by_xpath('//*[@id="T300427600"]/tbody/tr[2]/td[3]/nobr/span').text
		logger.info("Hours = {}".format(hours))
		
		resolution_milestone1 = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[2]/td[3]').text
		logger.info("Incident resolution 50% milestome: {}".format(resolution_milestone1))
		resolution_milestone2 = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[3]/td[3]').text
		logger.info("Incident resolution 75% milestome: {}".format(resolution_milestone2))
		resolution_milestone3 = self.driver.find_element_by_xpath('//*[@id="T303397300"]/tbody/tr[4]/td[3]').text
		logger.info("Incident resolution 90% milestome: {}".format(resolution_milestone3))
		
		restoration_status = self.driver.find_element_by_xpath('//*[@id="WIN_0_301466100"]/table/tbody/tr/td').text
		logger.info("Restoration Status = {}".format(restoration_status))
		
		resolution_progress = self.driver.find_element(By.XPATH, '//*[@id="T300427600"]/tbody/tr[2]/td[7]').text
		logger.info("Resolution progress: {}".format(resolution_progress))
		
		colorcode_resolution = self.driver.find_element_by_xpath('//*[@id="WIN_0_301466100"]')
		ccode = colorcode_resolution.get_attribute('style')
		colocode_resolution = re.findall(r'(rgb[(\d\s,)]*)', ccode)[0]  # To extract RGB code
		logger.info("Colorcode for Resolution = {}".format(colocode_resolution))
		
		self.driver.close()
		time.sleep(3)
		self.driver.switch_to.window(window_before)
		
		"""Validations"""
		matching = True
		if goal_restoration != kwargs["Goal1"]:
			matching = False
			logger.info("Restoration goal did not match")
		if hours != kwargs["hours"]:
			matching = False
			logger.info("Hours did not match")
		if resolution_milestone1 != kwargs["Resolution_milestone1"]:
			matching = False
			logger.info("resolution milestone1 did not match")
		if resolution_milestone2 != kwargs["Resolution_milestone1"]:
			matching = False
			logger.info("resolution milestone2 did not match")
		if resolution_milestone3 != kwargs["Resolution_milestone1"]:
			matching = False
			logger.info("resolution milestone3 did not match")
		if resolution_progress != kwargs["Resolution_Progress"]:
			matching = False
			logger.info("resolution progress did not match")
		if colocode_resolution != kwargs["Colorcode"]:
			matching = False
			logger.info("Colour code did not match")
		
		if restoration_status != kwargs["Status2"]:
			matching = False
			logger.info("Resolution status did not match")
		if svttitle1 != kwargs["Svttitle1"]:
			matching = False
			logger.info("SVT response title did not match")
		return matching
	
	def create_incident_verify_slm_gui(self, kwargs):
		try:
			for k in kwargs.keys():
				logger.info("arguments are {}{}".format(k, kwargs[k]))
			self.login_bmc()
			incidentid = False
			incidentid, ver = self.create_incident_verify_slm(kwargs)
		except BaseException as be:
			logger.fatal("Fatal exception occured in create_incident_verify_slm_gui() in {}".format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.bmc_logout()
			if not ver:
				raise BmcError("Validation failed")
			return incidentid, ver

	def search_incident_verify_slm_gui(self, kwargs):
		try:
			for k in kwargs.keys():
				logger.info("arguments are {}{}".format(k, kwargs[k]))
			self.login_bmc()
			incid = False
			incid, veri = self.search_incident_verify_slm(kwargs)
		except BaseException as be:
			logger.fatal("Fatal exception occured in search_incident_verify_slm_gui() in {}".format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.bmc_logout()
			if not veri:
				raise BmcError("Validation failed")
			return incid, veri
	
	def create_incident_verify_maya_slm_gui(self, kwargs):
		try:
			for k in kwargs.keys():
				logger.info("arguments are {}{}".format(k, kwargs[k]))
			self.login_bmc()
			incidentid = False
			incidentid, ver, ver1 = self.create_incident_maya_verify_slm(kwargs)
		except BaseException as be:
			logger.fatal("Fatal exception occured in create_incident_verify_slm_gui() in {}".format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.bmc_logout()
			if not ver:
				raise BmcError("Validation failed")
			return incidentid, ver, ver1

	def search_incident_verify_maya_slm_gui(self, kwargs):
		try:
			for k in kwargs.keys():
				logger.info("arguments are {}{}".format(k, kwargs[k]))
			self.login_bmc()
			incid = False
			incid, veri, veri1 = self.search_incident_maya_verify_slm(kwargs)
		except BaseException as be:
			logger.fatal("Fatal exception occured in search_incident_verify_slm_gui() in {}".format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.bmc_logout()
			if not veri:
				raise BmcError("Validation failed")
			return incid, veri
	
	def slm_maya_seven_ok_case(self, kwargs):
		try:
			self.login_bmc()
			status = self.slm_maya_seven_ok_case_main(kwargs)
		except BaseException as be:
			logger.fatal("Fatal exception occured in search_incident_verify_slm_gui() in {}".format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.bmc_logout()
			return status
	
	def slm_maya_seven_warning_case(self, kwargs):
		try:
			self.login_bmc()
			status = self.slm_maya_seven_warning_case_main(kwargs)
		except BaseException as be:
			logger.fatal("Fatal exception occured in search_incident_verify_slm_gui() in {}".format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.bmc_logout()
			return status
	
	def slm_maya_seven_critical_case(self, kwargs):
		try:
			self.login_bmc()
			status = self.slm_maya_seven_critical_case_main(kwargs)
		except BaseException as be:
			logger.fatal("Fatal exception occured in search_incident_verify_slm_gui() in {}".format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.bmc_logout()
			return status
	
	def create_incident_verify_p2_slm_gui(self, kwargs):
		try:
			for k in kwargs.keys():
				logger.info("arguments are {}{}".format(k, kwargs[k]))
			self.login_bmc()
			incidentid = False
			incidentid, ver = self.create_incident_verify_p2_slm(kwargs)
		except BaseException as be:
			logger.fatal("Fatal exception occured in create_incident_verify_slm_gui() in {}".format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.bmc_logout()
			if not ver:
				raise BmcError("Validation failed")
			return incidentid, ver

	def search_incident_verify_p2_slm_gui(self, kwargs):
		try:
			for k in kwargs.keys():
				logger.info("arguments are {}{}".format(k, kwargs[k]))
			self.login_bmc()
			incid = False
			incid, veri = self.search_incident_verify_p2_slm(kwargs)
		except BaseException as be:
			logger.fatal("Fatal exception occured in search_incident_verify_slm_gui() in {}".format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.bmc_logout()
			if not veri:
				raise BmcError("Validation failed")
			return incid, veri
	
	def priority_change_verification(self, kwargs):
		try:
			self.login_bmc()
			status = self.priority_change_verification_main(kwargs)
		except BaseException as be:
			logger.fatal('Fatal exception occured in search_incident_verify_slm_gui() in {}'.format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.bmc_logout()
			return status
	
	def create_incident_fail_response_sla(self, kwargs):
		try:
			self.login_bmc()
			status = False
			status = self.create_incident_fail_response_sla_main(kwargs)
		except BaseException as be:
			logger.fatal('Fatal exception occured in create_incident_fail_response_sla_lib in {}'.format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.bmc_logout()
			return status
	
	def slm_maya(self, kwargs):
		try:
			self.login_bmc()
			status = self.slm_maya_main(kwargs)
		except BaseException as be:
			logger.fatal("Fatal exception occured in slm_maya_lib in {}".format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.bmc_logout()
			return status
	
	def slm_maya_seven_ok_case_1(self, kwargs):
		try:
			self.login_bmc()
			status = self.slm_maya_seven_ok_case_1_main(kwargs)
		except BaseException as be:
			logger.fatal("Fatal exception occured in slm_maya_seven_ok_case_1() in {}".format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.bmc_logout()
			return status
	
	def slm_maya_seven_auto_warning_case(self, kwargs):
		try:
			time.sleep(int(kwargs['sleep_time']))
			self.login_bmc()
			status = self.slm_maya_seven_auto_warning_case_main(kwargs)
		except BaseException as be:
			logger.fatal("Fatal exception occured in slm_maya_seven_auto_warning_case_lib in {}".format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.bmc_logout()
			return status
	
	def slm_maya_seven_auto_warning_case_2(self, kwargs):
		try:
			time.sleep(int(kwargs['sleep_time']))
			self.login_bmc()
			status = self.slm_maya_seven_auto_warning_case_2_main(kwargs)
		except BaseException as be:
			logger.fatal("Fatal exception occured in slm_maya_seven_auto_warning_case_2_lib in {}".format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.bmc_logout()
			return status
	
	def slm_maya_seven_auto_critical_case(self, kwargs):
		try:
			time.sleep(int(kwargs['sleep_time']))
			self.login_bmc()
			status = self.slm_maya_seven_auto_critical_case_main(kwargs)
		except BaseException as be:
			logger.fatal("Fatal exception occured in slm_maya_seven_auto_critical_case_lib() in {}".format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.bmc_logout()
			return status
	
	def slm_maya_incident_creation_gui(self, kwargs):
		try:
			self.login_bmc()
			status = False
			status = self.slm_maya_incident_creation(kwargs)
		except BaseException as be:
			logger.fatal("Fatal exception occured in slm_maya_incident_creation_gui{}".format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.bmc_logout()
			return status
	
	def slm_maya_incident_search_and_verification_of_slm_gui(self, incident_id, kwargs):
		try:
			self.login_bmc()
			status = False
			status = self.slm_maya_incident_search_and_verification_of_slm(incident_id, kwargs)
		except BaseException as be:
			logger.fatal(
				"Fatal exception occured in slm_maya_incident_search_and_verification_of_slm_gui{}".format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.bmc_logout()
			return status
	
	def slm_maya_incident_search_and_resolve_gui(self, incident_id, kwargs):
		try:
			self.login_bmc()
			status = False
			status = self.slm_maya_incident_search_and_resolve(incident_id, kwargs)
		except BaseException as be:
			logger.fatal("Fatal exception occured in slm_maya_incident_search_and_resolve_gui{}".format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.bmc_logout()
			return status
	
	def slm_maya_incident_search_and_resolve_verification_of_slm_gui(self, incident_id, kwargs):
		try:
			self.login_bmc()
			status = False
			status = self.slm_maya_incident_search_and_resolve_verification_of_slm(incident_id, kwargs)
		except BaseException as be:
			logger.fatal(
				"Fatal exception occured in slm_maya_incident_search_and_resolve_verification_of_slm_gui{}".format(
					self.name))
			logger.error(traceback.print_exc())
		finally:
			self.bmc_logout()
			return status
	
	def slm_maya_incident_search_and_verification_of_8_hours_slm_gui(self, incident_id, kwargs):
		try:
			self.login_bmc()
			status = False
			status = self.slm_maya_incident_search_and_verification_of_8_hours_slm(incident_id, kwargs)
		except BaseException as be:
			logger.fatal(
				"Fatal exception occured in slm_maya_incident_search_and_verification_of_slm_gui{}".format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.bmc_logout()
			return status
	
	def slm_maya_incident_search_and_resolve_verification_of_8_hours_slm_gui(self, incident_id, kwargs):
		try:
			self.login_bmc()
			status = False
			status = self.slm_maya_incident_search_and_resolve_verification_of_8_hours_slm(incident_id, kwargs)
		except BaseException as be:
			logger.fatal(
				"Fatal exception occured in slm_maya_incident_search_and_resolve_verification_of_slm_gui{}".format(
					self.name))
			logger.error(traceback.print_exc())
		finally:
			self.bmc_logout()
			return status