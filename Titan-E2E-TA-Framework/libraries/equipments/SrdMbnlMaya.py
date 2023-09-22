from __future__ import print_function
import logging as logger
from encodings.punycode import selective_find
from selenium.webdriver.common.action_chains import ActionBuilder
from equipments.Vmm import Vmm
from chariot.chariot_error import ChariotError
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
from selenium.webdriver.support.ui import Select
from time import gmtime, strftime
from suds.client import Client
from suds.sax.element import Element
import datetime
import re
import traceback
from equipments.Vmm import Vmm


class SrdMbnlMaya(Vmm):
	"""Virtual machine manager"""

	def __init__(self, name, **kwargs):
		self.plmns = []
		self.driver = ''
		self.parent_win = ''
		Vmm.__init__(self, name, **kwargs)

	def login_bmc_qa(self):
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

			#global parent_win
			self.parent_win = self.driver.window_handles[0]

		except BaseException as be:
			logger.fatal("Fatal exception {} occurred inside login_bmc() while logging in to BMC {}".format(be, self.name))
			logger.error(traceback.print_exc())
			self.driver.quit()


	def bmc_logout_qa(self):
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

	def switchToSecondWindow(self):
		self.second_window = self.driver.window_handles[0]
		self.driver.switch_to_window(self.second_window)
		self.driver.maximize_window()

	def search_srd(self,kwargs):
			logger.info("Executing bmc_logout()")
			self.driver.switch_to.window(self.parent_win)
			time.sleep(5)
			#Reqest=self.driver.kwargs['Request']
			self.driver.find_element_by_link_text('Catalog').click()
			Srd_name=self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div/ui-view/div/div/div[2]/div/div[2]/div/input')
			Srd_name.send_keys(kwargs['Request'])
			self.driver.execute_script("document.body.style.zoom='50%'")
			self.driver.save_screenshot("+kwargs['Request']+.png")
			self.driver.execute_script("document.body.style.zoom='100%'")
			#clicking on search Action
			self.driver.find_element_by_xpath('//div[text()="'+kwargs['Request']+'"]').click()
			time.sleep(3)
			Name = self.driver.find_element_by_xpath('//h3[@class="support-modal__srd-header-title"]')
			Request = Name.text
			print(Request)
			self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div[1]/ins').click()
			self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div/ui-view/div/div/div[2]/div[1]/div[2]/ins[2]').click()
			return True

	def verify_display_options_main(self, kwargs):
		time.sleep(3)
		my_activity =  self.driver.find_element(By.XPATH, "//button[@id='toggle-my-profile-sub-menu']")
		my_activity.click()
		time.sleep(1)
		my_activity.click()
		time.sleep(3)
		requests = self.driver.find_element(By.LINK_TEXT, "All activity")
		requests.click()
		time.sleep(5)
		search_btn =  self.driver.find_element(By.XPATH, "//ins[@name='uiTestEnterTimelineSearchModeBtn']")
		search_btn.click()
		time.sleep(3)
		search_req = self.driver.find_element(By.XPATH, "/html/body/div/div/div/div/ui-view/main/div[2]/div[2]/div[1]/div[3]/div[1]/div/input")
		search_req.send_keys(kwargs['request_id'])
		time.sleep(1)
		activity = self.driver.find_element(By.XPATH, "/html/body/div/div/div/div/ui-view/main/div[2]/div[2]/div[2]/div[3]/div[1]/div/div/div[1]/div[1]/div[2]/div[1]/span")
		# time.sleep(2)
		activity.click()
		time.sleep(7)
		# request_id = self.driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[3]/div/div[1]/div/div[2]/div[3]/span").text
		# logger.info("Request with ID" + request_id + "is created. ")
		# close_btm = self.driver.find_element(By.XPATH, "//ins[@name='uiTestCloseModalBtn']")
		# close_btm.click()
		# time.sleep(2)
		# request_details = self.driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[3]/div/div[2]/div[2]")
		request_details =  self.driver.find_element(By.XPATH, "//h3[contains(text(),'Request Details')]")
		request_details.click()
		time.sleep(7)
		hide_list = []
		show_list = []
		if kwargs["Request"] =="New Report Request" or kwargs["Request"]=="Answer Question" or kwargs["Request"] == "Request Scheduling Report" or kwargs["Request"] == "Provide Ticket Status":
			hide_list = ["Price", "Date Required", "Phone", "Quantity", "Service Coordinator", "Approvals", "End User Process View"]
			show_list = ["Turnaround Time", "Expected Completion", "Email", "Request Details"]
		elif kwargs["Request"] == "Account Related Request" or kwargs['Request'] == "Account Password Reset":
			hide_list = ["Price", "Date Required", "Phone", "Quantity", "Service Coordinator", "End User Process View"]
			show_list = ["Turnaround Time", "Expected Completion", "Email", "Additional Information"]
		hide_status = [] #Will contain True if all the hide parameters pass the test
		show_status = []# Will contain True if all the show parameters pass the test
		parameter_string = ""
		request_status = self.driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[1]/td[2]').text
		logger.info("Current status of the request is: {}".format(request_status))
		if kwargs['request_status'] == "check completed status":
			close_btm = self.driver.find_element(By.XPATH, "//ins[@name='uiTestCloseModalBtn']")
			close_btm.click()
			time.sleep(2)
			if request_status == "Completed":
				return True
			else:
				return False

		elif kwargs['request_status'] == "verify display options":
			if kwargs['Request'] == "New Report Request":
				visible_Parameters = []
				for i in range(1, 14):
					parameter = self.driver.find_element(By.XPATH,
														 "/html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[{}]/td[1]".format(
															 i)).text
					visible_Parameters.append(parameter[:-1])
				parameter_string = ",".join(
					visible_Parameters)  # String containing all the parameters in the SRD details window
				logger.info(parameter_string)

			if kwargs['Request'] == "Answer Question":
				visible_Parameters = []
				for i in range(1, 13):
					parameter = self.driver.find_element(By.XPATH,
														 "/html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[{}]/td[1]".format(
															 i)).text
					visible_Parameters.append(parameter[:-1])
				parameter_string = ",".join(
					visible_Parameters)  # String containing all the parameters in the SRD details window
				logger.info(parameter_string)

			if kwargs['Request'] == "Request Scheduling Report":
				visible_Parameters = []
				for i in range(1, 15):
					parameter = self.driver.find_element(By.XPATH,
														 "/html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[{}]/td[1]".format(
															 i)).text
					visible_Parameters.append(parameter[:-1])
				parameter_string = ",".join(
					visible_Parameters)  # String containing all the parameters in the SRD details window
				logger.info(parameter_string)

			if kwargs['Request'] == "Provide Ticket Status":
				visible_Parameters = []
				for i in range(1, 12):
					parameter = self.driver.find_element(By.XPATH,
														 "/html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[{}]/td[1]".format(
															 i)).text
					visible_Parameters.append(parameter[:-1])
				parameter_string = ",".join(
					visible_Parameters)  # String containing all the parameters in the SRD details window
				logger.info(parameter_string)

			if kwargs['Request'] == "Account Related Request":
				visible_Parameters = []
				for i in range(1, 18):
					parameter = self.driver.find_element(By.XPATH,
														 "/html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[{}]/td[1]".format(
															 i)).text
					visible_Parameters.append(parameter[:-1])
				parameter_string = ",".join(
					visible_Parameters)  # String containing all the parameters in the SRD details window
				logger.info(parameter_string)

			if kwargs['Request'] == "Account Password Reset":
				visible_Parameters = []
				for i in range(1, 16):
					parameter = self.driver.find_element(By.XPATH,
														 "/html/body/div[1]/div/div/div[3]/div/div[2]/div/table/tbody/tr[{}]/td[1]".format(
															 i)).text
					visible_Parameters.append(parameter[:-1])
				parameter_string = ",".join(
					visible_Parameters)  # String containing all the parameters in the SRD details window
				logger.info(parameter_string)

			close_btm = self.driver.find_element(By.XPATH, "//ins[@name='uiTestCloseModalBtn']")
			close_btm.click()
			time.sleep(2)

			logger.info("Hide list: {}".format(hide_list))
			logger.info("Sow list: {}".format(show_list))

			for i in hide_list:
				if i in parameter_string:
					hide_status.append(False)
				else:
					hide_status.append(True)
			logger.info(hide_status)
			if all(hide_status):
				logger.info("The hidden display options are verified.")
			else:
				logger.info("The hidden display options are not verified")

			for i in show_list:
				if i in parameter_string:
					show_status.append(True)
				else:
					show_status.append(False)
			logger.info(show_status)
			if all(show_status):
				logger.info("The shown display options are verified")
			else:
				logger.info("The shown display options are not verified")
			return all(show_status) and all(hide_status)


	def get_request_id(self, kwargs):
		my_activity =  self.driver.find_element(By.XPATH, "//button[@id='toggle-my-profile-sub-menu']")
		my_activity.click()
		time.sleep(1)
		my_activity.click()
		time.sleep(3)
		requests = self.driver.find_element(By.LINK_TEXT, "Requests")
		requests.click()
		time.sleep(5)
		activity = self.driver.find_element(By.XPATH, "/html/body/div/div/div/div/ui-view/main/div[2]/div[2]/div[2]/div[3]/div[1]/div/div/div[1]/div[1]/div[2]/div[1]/span")
		activity.click()
		time.sleep(7)
		request_id = self.driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[3]/div/div[1]/div/div[2]/div[3]/span").text
		logger.info("Request with ID" + request_id + "is created. ")
		close_btm = self.driver.find_element(By.XPATH, "//ins[@name='uiTestCloseModalBtn']")
		close_btm.click()
		time.sleep(2)

		return request_id

	def bmc_approval(self,kwargs):
			#
			time.sleep(3)
			my_activity = self.driver.find_element(By.XPATH, "//button[@id='toggle-my-profile-sub-menu']")
			my_activity.click()
			time.sleep(1)
			my_activity.click()
			time.sleep(3)
			all_activity = self.driver.find_element(By.LINK_TEXT, "All activity")
			all_activity.click()
			time.sleep(5)


			time.sleep(5)
			search_btn = self.driver.find_element(By.XPATH, "//ins[@name='uiTestEnterTimelineSearchModeBtn']")
			search_btn.click()
			time.sleep(3)
			search_req = self.driver.find_element(By.XPATH, "/html/body/div/div/div/div/ui-view/main/div[2]/div[2]/div[1]/div[3]/div[1]/div/input")
			search_req.send_keys(kwargs['request_id'])
			self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div/ui-view/main/div[2]/div[2]/div[2]/div[3]/div[1]/div/div/div/div[2]/div[2]/button[1]').click()
			time.sleep(3)


			self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div/ui-view/main/div[2]/div[2]/div[2]/div[3]/div[1]/div/div/div/div[1]/div[2]/div[1]/img').click()
			time.sleep(3)
			self.switchToSecondWindow()
			time.sleep(5)
			status=self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div[3]/div[3]/div/div/div[2]')
			a=status.text
			print(a)
			time.sleep(2)
			self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div[1]/ins').click()
			if a == 'Approved':
				return True
			else:
				return False

	def bmc_request_form(self,kwargs):

			if kwargs['Request']== 'Account Related Request':
				time.sleep(3)
				self.switchToSecondWindow()
				time.sleep(3)
				#Application Category
				self.driver.find_element_by_xpath('(//div[@class="dropdown"])[1]').click()
				time.sleep(2)
				category=self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[1]/div/div/div[2]/div/div/div/div/input')
				category.send_keys(kwargs['Category'])
				time.sleep(2)
				self.driver.find_element_by_xpath("/html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[1]/div/div/div[2]/div/div/select/option[2]").click()
				#Application Sub Category
				time.sleep(3)
				self.driver.find_element_by_xpath('(//div[@class="dropdown"])[2]').click()
				Sub_category=self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[2]/div/div/div[2]/div/div/div/div/input')
				Sub_category.send_keys(kwargs['Sub_category'])
				time.sleep(2)
				self.driver.find_element_by_xpath("/html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[2]/div/div/div[2]/div/div/select/option[2]").click()
				#Tools
				time.sleep(3)
				self.driver.find_element_by_xpath('(//div[@class="dropdown"])[3]').click()
				Tool = self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[3]/div/div/div[2]/div/div/div/div/input')
				Tool.send_keys(kwargs['Tool'])
				time.sleep(2)
				self.driver.find_element_by_xpath("/html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[3]/div/div/div[2]/div/div/select/option[2]").click()
				#Request
				time.sleep(2)
				if(kwargs['Request1']=='Create Account'):
						self.driver.find_element_by_xpath('//input[@value="Create Account"]').click()
				if (kwargs['Request1'] == 'Modify Account'):
					self.driver.find_element_by_xpath('//input[@value="Modify Account"]').click()
				if (kwargs['Request1'] == 'Remove Account'):
					self.driver.find_element_by_xpath('//input[@value="Remove Account"]').click()
				if (kwargs['Request1'] == 'Unlock Account'):
					self.driver.find_element_by_xpath('//input[@value="Unlock Account"]').click()
				#Details
 				Name=self.driver.find_element_by_xpath('//input[@name="QSGAA5V0F6M2OAPOWXTOPNZNSBH8WT"]')
				Name.send_keys(kwargs['Name'])
				user_id = self.driver.find_element_by_xpath('//input[@name="QSGAA5V0F6M2OAPOWXTPPNZNSCH8WV"]')
				user_id.send_keys(kwargs['user_id'])
				email=self.driver.find_element_by_xpath('//input[@name="QSGAA5V0F6M2OAPOWXTRPNZNSEH8WX"]')
				email.send_keys(kwargs['email'])
				Addition_info=self.driver.find_element_by_xpath('//input[@name="QSGAA5V0F6M2OAPOWXTSPNZNSFH8WZ"]')
				Addition_info.send_keys(kwargs['Additional_info'])
				time.sleep(2)
				#Submit Button
				self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div[3]/div/div[2]/form/div/div/button[1]').click()
				time.sleep(3)
				self.driver.switch_to.window(self.parent_win)
				time.sleep(4)
				self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div/ui-view/div/div/div[2]/div[1]/div[2]/ins[2]').click()
				return self.get_request_id(kwargs)

			if kwargs['Request'] == 'Account Password Reset':
				time.sleep(3)
				self.switchToSecondWindow()
				time.sleep(3)
				# Application Category
				self.driver.find_element_by_xpath('(//div[@class="dropdown"])[1]').click()
				time.sleep(2)
				category = self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[1]/div/div/div[2]/div/div/div/div/input')
				category.send_keys(kwargs['Category'])
				time.sleep(2)
				self.driver.find_element_by_xpath("/html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[1]/div/div/div[2]/div/div/select/option[2]").click()
				# Application Sub Category
				time.sleep(3)
				self.driver.find_element_by_xpath('(//div[@class="dropdown"])[2]').click()
				Sub_category = self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[2]/div/div/div[2]/div/div/div/div/input')
				Sub_category.send_keys(kwargs['Sub_category'])
				time.sleep(2)
				self.driver.find_element_by_xpath("/html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[2]/div/div/div[2]/div/div/select/option[2]").click()
				# Tools
				time.sleep(3)
				self.driver.find_element_by_xpath('(//div[@class="dropdown"])[3]').click()
				Tool = self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[3]/div/div/div[2]/div/div/div/div/input')
				Tool.send_keys(kwargs['Tool'])
				time.sleep(2)
				self.driver.find_element_by_xpath("/html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[3]/div/div/div[2]/div/div/select/option[2]").click()
				# Details
				Name = self.driver.find_element_by_xpath('//input[@name="QSGAA5V0F6M2OAPOWWPNPNZMOAH768"]')
				Name.send_keys(kwargs['Name'])
				user_id = self.driver.find_element_by_xpath('//input[@name="QSGAA5V0F6M2OAPOWWPPPNZMOCH76K"]')
				user_id.send_keys(kwargs['user_id'])
				email = self.driver.find_element_by_xpath('//input[@name="QSGAA5V0F6M2OAPOWWPRPNZMOEH76M"]')
				email.send_keys(kwargs['email'])
				Addition_info = self.driver.find_element_by_xpath('//input[@name="QSGAA5V0F6M2OAPOWWPTPNZMOGH76O"]')
				Addition_info.send_keys(kwargs['Additional_info'])
				time.sleep(2)
				# Submit Button
				self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div[3]/div/div[2]/form/div/div/button[1]').click()
				time.sleep(3)
				self.driver.switch_to.window(self.parent_win)
				time.sleep(4)
				self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div/ui-view/div/div/div[2]/div[1]/div[2]/ins[2]').click()
				return self.get_request_id(kwargs)

			if kwargs['Request'] == 'Answer Question':
				#Details
				Reuest_details=self.driver.find_element_by_xpath('//input[@name="QSGAA5V0F5S6EAPS3ATPPR5LQBU5CK"]')
				Reuest_details.send_keys(kwargs['Request_details'])
				time.sleep(2)
				#Related Tool
				self.driver.find_element_by_xpath('//button[@name="QSGAA5V0F5S6EAPS3AV3PR5LRPU5CQ"]').click()
				time.sleep(2)
				tool=self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[2]/div/div/div[2]/div/div/div/input')
				tool.send_keys(kwargs['Tool'])
				time.sleep(2)
				self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[2]/div/div/div[2]/div/select/option[2]').click()
				#module
				time.sleep(2)
				self.driver.find_element_by_xpath('//button[@name="QSGAA5V0F5S6EAPS3BWUPR5MTGU5FR"]').click()
				time.sleep(2)
				module=self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[3]/div/div/div[2]/div/div/div/div/input')
				module.send_keys(kwargs['Module'])
				time.sleep(2)
				self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[3]/div/div/div[2]/div/div/select/option[2]').click()
				#submit Button
				self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div[3]/div/div[2]/form/div/div/button[1]').click()
				time.sleep(3)
				self.driver.switch_to.window(self.parent_win)
				time.sleep(4)
				self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div/ui-view/div/div/div[2]/div[1]/div[2]/ins[2]').click()
				return self.get_request_id(kwargs)

			if kwargs['Request'] == 'New Report Request':
				time.sleep(3)
				#Related Tool
				self.driver.find_element_by_xpath('//button[@name="QSGAA5V0F5S6EAPS2YCPPR58ZBU4O3"]').click()
				time.sleep(2)
				tool = self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[1]/div/div/div[2]/div/div/div/input')
				tool.send_keys(kwargs['Tool'])
				time.sleep(2)
				self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[1]/div/div/div[2]/div/select/option[2]').click()
				#Detail
				detail=self.driver.find_element_by_xpath('//textarea[@name="QSGAA5V0F5S6EAPS2YCTPR58ZFU4O5"]')
				detail.send_keys(kwargs['Detail'])
				#Component
				time.sleep(4)
				self.driver.find_element_by_xpath('//button[@name="QSGAA5V0F5S6EAPS2YVFPR59R7U4UL"]').click()
				time.sleep(2)
				Component = self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[4]/div/div/div[2]/div/div/div/div/input')
				Component.send_keys(kwargs['Component'])
				time.sleep(2)
				self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[4]/div/div/div[2]/div/div/select/option[2]').click()
				# submit Button
				self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div[3]/div/div[2]/form/div/div/button[1]').click()
				time.sleep(3)
				self.driver.switch_to.window(self.parent_win)
				time.sleep(4)
				self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div/ui-view/div/div/div[2]/div[1]/div[2]/ins[2]').click()
				return self.get_request_id(kwargs)

			if kwargs['Request'] == 'Provide Ticket Status':
				time.sleep(4)
				if kwargs['Ticket'] == 'INC':
					self.driver.find_element_by_xpath('//input[@value="INC -Incident"]').click()
				if kwargs['Ticket'] == 'WO':
					self.driver.find_element_by_xpath('//input[@value="WO -Work Order"]').click()
				if kwargs['Ticket'] == 'CRQ':
					self.driver.find_element_by_xpath('//input[@value="CRQ -Change Request"]').click()
				if kwargs['Ticket'] == 'KBA':
					self.driver.find_element_by_xpath('//input[@value="KBA -Knowledge Base Article"]').click()
				if kwargs['Ticket'] == 'PBI':
					self.driver.find_element_by_xpath('//input[@value="PBI - Problem Invetigation"]').click()
				#Detail
				time.sleep(2)
				Detail=self.driver.find_element_by_xpath('//textarea[@name="QSGAA5V0F5S6EAPSZDC0PSBNECDIGQ"]')
				Detail.send_keys(kwargs['Detail'])
				time.sleep(3)
				# submit Button
				self.driver.find_element_by_xpath(
					'/html/body/div[1]/div/div/div[3]/div/div[2]/form/div/div/button[1]').click()
				time.sleep(3)
				self.driver.switch_to.window(self.parent_win)
				time.sleep(4)
				self.driver.find_element_by_xpath(
					'/html/body/div[1]/div/div/div/ui-view/div/div/div[2]/div[1]/div[2]/ins[2]').click()
				return self.get_request_id(kwargs)

			if kwargs['Request'] == 'Request Scheduling Report':
				time.sleep(4)
				if kwargs['Ticket'] == 'Create new Report Schedule':
					self.driver.find_element_by_xpath('//input[@value="Create new Report Schedule"]').click()
				if kwargs['Ticket'] == 'Modify existing Report Schedule':
					self.driver.find_element_by_xpath('//input[@value="Modify existing Report Schedule"]').click()
				#TOOL
				time.sleep(2)
				self.driver.find_element_by_xpath('//button[@name="QSGAA5V0F5S6EAPSQFSLPRSQGFBRM5"]').click()
				time.sleep(2)
				tool=self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[2]/div/div/div[2]/div/div/div/input')
				time.sleep(2)
				tool.send_keys(kwargs['Tool'])
				time.sleep(3)
				self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[2]/div/div/div[2]/div/select/option[2]').click()
				time.sleep(3)
				#Details
				detail=self.driver.find_element_by_xpath('//textarea[@name="QSGAA5V0F5S6EAPSQGAZPRSQ49BRNT"]')
				detail.send_keys(kwargs['Detail'])

				time.sleep(3)
				#Component
				self.driver.find_element_by_xpath('//button[@name="QSGAA5V0F5S6EAPSQGH1PRSQKVBROO"]').click()
				time.sleep(2)
				component=self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[5]/div/div/div[2]/div/div/div/div/input')
				component.send_keys(kwargs['component'])
				time.sleep(2)
				self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div[3]/div/div[2]/form/ng-include/div/div[3]/div[5]/div/div/div[2]/div/div/select/option[2]').click()

				# submit Button
				self.driver.find_element_by_xpath(
					'/html/body/div[1]/div/div/div[3]/div/div[2]/form/div/div/button[1]').click()
				time.sleep(3)
				self.driver.switch_to.window(self.parent_win)
				time.sleep(4)
				self.driver.find_element_by_xpath(
					'/html/body/div[1]/div/div/div/ui-view/div/div/div[2]/div[1]/div[2]/ins[2]').click()
				return self.get_request_id(kwargs)

	def bmc_search_form_catalog(self,kwargs):
			logger.info("Executing bmc_logout()")
			self.driver.switch_to.window(self.parent_win)
			time.sleep(5)
			#Reqest=self.driver.kwargs['Request']
			self.driver.find_element_by_link_text('Catalog').click()
			Srd_name=self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div/ui-view/div/div/div[2]/div/div[2]/div/input')
			Srd_name.send_keys(kwargs['Request'])
			self.driver.execute_script("document.body.style.zoom='50%'")
			self.driver.save_screenshot("+kwargs['Request']+.png")
			self.driver.execute_script("document.body.style.zoom='100%'")
			#clicking on search Action
			self.driver.find_element_by_xpath('//div[text()="'+kwargs['Request']+'"]').click()
			#form
			request_id = self.bmc_request_form(kwargs)
			return request_id[12:]

	def bmc_logout(self):
		try:
			logger.info("Executing bmc_logout()")
			self.driver.switch_to.window(self.parent_win)
			time.sleep(5)
			self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div/header/div/div[2]/div[2]/button/img').click()
			self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div/header/div/div[2]/div[2]/button/img').click()

			logout = self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div/header/div/div[2]/div[2]/div/span')
			logout.send_keys('\n')
			time.sleep(2)
			#verify popup

			self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div[3]/div/button[1]').click()


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


	def workorder_return(self,kwargs):
		time.sleep(2)
		request_id=self.driver.find_element_by_xpath('//*[@id="arid_WIN_0_302258625"]')
		request_id.send_keys(kwargs['request_id'])
		time.sleep(2)
		request_id.send_keys(Keys.ENTER)
		time.sleep(2)
		self.switchToSecondWindow()
		Workorder=self.driver.find_element_by_xpath('//*[@id="T1000003952"]/tbody/tr[3]/td[1]/nobr/span').text
		if kwargs['Request'] == 'Answer Question':
			Workorder = self.driver.find_element_by_xpath('//*[@id="T1000003952"]/tbody/tr[2]/td[1]/nobr/span').text
		if kwargs['Request'] == 'Provide Ticket Status':
			Workorder = self.driver.find_element_by_xpath('//*[@id="T1000003952"]/tbody/tr[2]/td[1]/nobr/span').text
		return Workorder


	def form_check_srd(self,kwargs):

		try:
			for k in kwargs:
				logger.info("arguments are - {}:{}".format(k, kwargs[k]))
			Status = False
			self.login_bmc()
			Status=self.bmc_search_form_catalog(kwargs)

		except BaseException as be:
			logger.fatal("Fatal exception occured in create_change_id() in {}".format(self.name))
			logger.error(traceback.print_exc())

		finally:
			self.bmc_logout()
			return Status


	def approval(self,kwargs):
		global Status
		try:
			for k in kwargs:
				logger.info("arguments are {}{}".format(k, kwargs[k]))
			self.login_bmc()
			Status=False
			Status=self.bmc_approval(kwargs)
		except BaseException as be:
			logger.fatal("Fatal exception occured in create_change_id() in {}".format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.bmc_logout()
			return Status

	def Search(self,kwargs):
		global Status
		try:
			for k in kwargs:
				logger.info("arguments are {}{}".format(k, kwargs[k]))
			Status = False
			self.login_bmc()
			Status = self.search_srd(kwargs)

		except BaseException as be:
			logger.fatal("Fatal exception occured in create_change_id() in {}".format(self.name))
			logger.error(traceback.print_exc())

		finally:
			self.bmc_logout()
			return Status

	def verify_display_options(self, kwargs):
		global status
		try:
			for k in kwargs.keys():
				logger.info("Arguements are -{}: {}".format(k, kwargs[k]))
			self.login_bmc()
			status = self.verify_display_options_main(kwargs)
		except BaseException as be:
			logger.fatal("Fatal exception occured in create_incidents_with_different_priority in {}".format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.bmc_logout()
			return status

	def workorder_id_return(self, kwargs):
		global status
		try:
			self.login_bmc_qa()
			status = self.workorder_return(kwargs)
		except BaseException as be:
			logger.fatal("Fatal exception occured in create_incidents_with_different_priority in {}".format(self.name))
			logger.error(traceback.print_exc())
		finally:
			self.bmc_logout_qa()
			return status
