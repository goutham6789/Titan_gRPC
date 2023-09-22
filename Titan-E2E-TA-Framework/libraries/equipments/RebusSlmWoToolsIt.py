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


class BmcRebusSlmWoToolsIt(Vmm):
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
	
	def create_wo_verify_slm(self, kwargs):
		logger.info("Executing create_wo_verify_slm()")
		""" Clicking on Application"""
		appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
		appl.click()

		"""Clicking on  Service Request Management -> New Work Order"""
		servreqmgmt = self.driver.find_element_by_link_text('Service Request Management')
		servreqmgmt.click()
		nwo = self.driver.find_element_by_link_text('New Work Order')
		nwo.click()
		time.sleep(3)
		woidta = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_1000000182"]')
		woid = woidta.get_attribute("value")
		logger.info("Work Order ID is {}".format(woid))
		window_before = self.driver.window_handles[0]
		self.driver.find_element_by_id("reg_img_304248530").click()
		WebDriverWait(self.driver, 10).until(
			expected_conditions.number_of_windows_to_be(2))
		window_after = self.driver.window_handles[1]
		self.driver.switch_to.window(window_after)
		time.sleep(3)
		logid = self.driver.find_element_by_id("arid_WIN_0_304309720")
		logid.send_keys(kwargs['Loginid'])
		logid.send_keys(Keys.ENTER)
		WebDriverWait(self.driver, 20).until(
			expected_conditions.element_to_be_clickable((By.XPATH, '//*[@id="T301394438"]/tbody/tr[2]')))
		namesel = self.driver.find_element_by_xpath('//*[@id="T301394438"]/tbody/tr[2]')
		namesel.click()

		selectbtn = self.driver.find_element_by_xpath('//*[@id="WIN_0_301912800"]/div')
		selectbtn.click()
		self.driver.switch_to.window(window_before)

		summary = self.driver.find_element_by_id("arid_WIN_3_1000000000")
		summary.send_keys(kwargs['Summary'])
		sgnrm = self.driver.find_element_by_xpath('//textarea[@id="arid_WIN_3_1000000015"]')
		sgnrm.click()
		sgnrm.send_keys(kwargs['SupportGroupNameRM'])
		sgnrm.send_keys(Keys.DOWN)
		sgnrm.send_keys(Keys.ENTER)

		sgnra = self.driver.find_element_by_xpath('//textarea[@id="arid_WIN_3_1000003229"]')
		sgnra.click()
		sgnra.send_keys(kwargs['SupportGroupNameRA'])
		sgnra.send_keys(Keys.DOWN)
		sgnra.send_keys(Keys.ENTER)

		ra = self.driver.find_element_by_xpath('//textarea[@id="arid_WIN_3_1000003230"]')
		ra.click()
		ra.send_keys(kwargs['RequestAssignee'])
		time.sleep(3)
		ra.send_keys(Keys.DOWN)
		ra.send_keys(Keys.ENTER)

		status = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_7"]')
		status.click()
		status.send_keys(Keys.DOWN*4)
		#status.send_keys(kwargs['Status'])
		status.send_keys(Keys.ENTER)

		woprio = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_1000000164"]')
		woprio.click()
		woprio.send_keys(Keys.DOWN)
		woprio.send_keys(kwargs['Priority'])
		woprio.send_keys(Keys.ENTER)

		prio = self.driver.find_element_by_xpath('//input[@id = "arid_WIN_3_1000000164"]')
		priority = prio.get_attribute('value')
		logger.info("Priority = {}".format(priority))

		savewo = self.driver.find_element_by_xpath('//*[@id="WIN_3_300000300"]/div')
		savewo.click()
		logger.info("Work Order Created successfully")
		time.sleep(5)

		"""Clicking on Applications"""
		appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
		appl.click()

		""" Clicking on Search Work Order"""
		servreqmgmt = self.driver.find_element_by_link_text('Service Request Management')
		servreqmgmt.click()
		time.sleep(3)
		serchwo = self.driver.find_element_by_link_text('Search Work Order')
		serchwo.click()
		time.sleep(5)
		entwoid = self.driver.find_element_by_xpath('//*[@id="arid_WIN_5_1000000182"]')
		entwoid.click()
		entwoid.send_keys(woid)
		WebDriverWait(self.driver, 20).until(
			expected_conditions.element_to_be_clickable((By.XPATH, '//*[@id="WIN_5_1002"]/div/div')))
		serchbtn = self.driver.find_element_by_xpath('//*[@id="WIN_5_1002"]/div/div')
		serchbtn.click()
		time.sleep(3)

		""" Getting the SLA details """
		time.sleep(3)
		window_before = self.driver.window_handles[0]
		self.driver.find_element_by_xpath('//div[@id= "WIN_5_303579500"]').click()
		WebDriverWait(self.driver, 10).until(
			expected_conditions.number_of_windows_to_be(2))
		window_after = self.driver.window_handles[1]
		self.driver.switch_to.window(window_after)

		woqw = self.driver.find_element_by_xpath('//textarea[@id ="arid_WIN_0_303738000"]')
		time.sleep(3)
		woidsla = woqw.get_attribute("value")
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

		self.driver.close()
		time.sleep(3)
		self.driver.switch_to.window(window_before)

		logger.info("Exiting create_wo_verify_slm()")
		return woidsla, matching
	
	def create_wo_verify_slm_gui(self, kwargs):
		try:
			for k in kwargs.keys():
				logger.info("arguments are {}{}".format(k, kwargs[k]))
			self.login_bmc()
			woidsla = False
			woidsla, ver = self.create_wo_verify_slm(kwargs)
		except BaseException as be:
			logger.fatal("Fatal exception occured in create_wo_verify_slm_gui() in {}".format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.bmc_logout()
			if not ver:
				raise BmcError("Validation failed")
			return woidsla, ver