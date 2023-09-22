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


class BmcAPI(Vmm):
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

	def Create_incident_api_fun(self, kwargs):

		# url = "https://threeuk-qa.onbmc.com/arsys/WSDL/public/onbmc-s/H3G_SA_SM_HPD_IncidentInterface_Staging_WS"
		url = self.loginurl
		# user= kwargs['usna']
		# pas = kwargs['pass']
		client = self.set_authorization_header()
		# client = Client(url)

		Status_IncidentType = kwargs["statusincidenttype"]
		Service_TypeType = kwargs["servicetype"]
		ImpactType = kwargs["Impact"]
		Reported_SourceType = kwargs["reportedsourcetype"]
		UrgencyType = kwargs["Urgency"]
		ServiceCI = kwargs["serviceci"]
		CI = kwargs["CI"]
		Action = kwargs["Action"]
		Primary_Event_ID = kwargs["Primary_Event_ID"]
		Work_Info_Type = kwargs["Work_Info_Type"]
		Work_Info_Notes = kwargs["Work_Info_Notes"]
		Summary = kwargs["Summary"]
		Company = kwargs["Company"]
		Notes = kwargs["Notes"]
		Work_Info_Attachment = kwargs["Work_Info_Attachment"]

		response = client.service.Create_Incident("Assigned" , "Voice", "FO - Stock Check" ,"INC_CREATE", "", "", "Service Assurance", "000","","", "Test", "Hutchison 3G UK Limited","User Service Request","Test", "1-Extensive/Widespread","Dynatrace","","cid:368705169437","","2-High")
		logger.info("The response is{} ", format(response))
		print response
		print("Type of response  -  {}".format(type(response)))
		print("Status_Incident  -  {}".format(response.Status_Incident))

		respstr = str(response)
		message = respstr[73:-118]
		incid = respstr[73:-143]
		errcode = respstr[-8:-3]
		print incid
		print message
		print errcode
		return incid, message, errcode

	def Incident_creation_api_fun(self, kwargs):
		try:
			incident = False
			incident = self.Create_incident_api_fun(kwargs)
		except BaseException as be:
			logger.fatal("Fatal exception occured in create incident api() in {}".format(self.name))
			logger.error(traceback.print_exc())
		finally:
			return incident

	def update_incident_api_fun(self, kwargs):

		# url = "https://threeuk-qa.onbmc.com/arsys/WSDL/public/onbmc-s/H3G_SA_SM_HPD_IncidentInterface_Staging_WS"
		url = self.loginurl
		# user= kwargs['usna']
		# pas = kwargs['pass']
		client = self.set_authorization_header()
		# client = Client(url)
		SM_Incident_Number = kwargs['incidentid']
		Status_Incident = kwargs['statusincidenttype']
		Status_Reason = kwargs['Status_ReasonType']
		ImpactType = kwargs['Impact']
		UrgencyType = kwargs['Urgency']
		ServiceCI = kwargs['ServiceCI']
		CI = kwargs['CI']
		Resolution = kwargs['Resolution']
		Action = kwargs['Action']
		response = client.service.Update_Incident_Fields(SM_Incident_Number, Status_Incident, Status_Reason, ImpactType,
														 UrgencyType, ServiceCI, CI, Resolution, Action)
		logger.info("The response is{} ", format(response))
		print response
		return response

	def update_incident_api(self, kwargs):
		try:
			updateincident = False
			updateincident = self.update_incident_api_fun(kwargs)
		except BaseException as be:
			logger.fatal("Fatal exception occured in create incident api() in {}".format(self.name))
			logger.error(traceback.print_exc())
		finally:
			return updateincident

