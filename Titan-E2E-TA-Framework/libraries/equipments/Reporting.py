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
import random
import BMCconstant


class BmcReporting(Vmm):
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

    def incident_sla_dashboard_main(self, kwargs):
        logger.info("Execuitng smart_reporting()")
        """ Clicking on Application"""
        appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
        appl.click()

        """Clicking on Smart Reporting -> Smart Reporting Console"""
        smrtrep = self.driver.find_element_by_link_text('Smart Reporting')
        smrtrep.click()
        smrtrepcon = self.driver.find_element_by_link_text('Smart Reporting Console')
        """Clicking on smart reporting console and switchingg windows"""
        window_before = self.driver.window_handles[0]
        smrtrepcon.click()
        WebDriverWait(self.driver, 10).until(expected_conditions.number_of_windows_to_be(2))
        window_after = self.driver.window_handles[1]
        self.driver.switch_to.window(window_after)
        time.sleep(3)

        search_report = self.driver.find_element(By.XPATH,
                                                 '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/input')
        search_report.send_keys(kwargs['Report Name'])
        search_report.send_keys(Keys.ENTER)
        time.sleep(2)
        """opening H3G Folder"""
        h3gopfoler = self.driver.find_element_by_xpath("//div[@title='H3G Operational Reporting']")
        time.sleep(2)
        h3gopfoler.click()
        """Opening Rebus Reports Folder"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          "/html[1]/body[1]/form[1]/div[12]/div[1]/div[2]/div[4]/div[1]/div[2]/div[3]/div[1]/div[2]/div[8]/div[1]/div[1]")))
        maya_reports = self.driver.find_element(By.XPATH,
                                                "/html[1]/body[1]/form[1]/div[12]/div[1]/div[2]/div[4]/div[1]/div[2]/div[3]/div[1]/div[2]/div[8]/div[1]/div[1]")
        maya_reports.click()
        time.sleep(3)
        """Double-click on incident-sla-dashboard report"""
        incident_sla_dashboard = self.driver.find_element(By.XPATH,
                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div[2]')
        time.sleep(2)
        action = ActionChains(self.driver)
        action.double_click(incident_sla_dashboard)
        action.perform()
        time.sleep(5)
        """Getting the text of the table name"""
        WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
            (By.XPATH, "//td[@class='rpt98354title reportOutputTitle']")))
        table_title = self.driver.find_element(By.XPATH, "//td[@class='rpt98354title reportOutputTitle']").text
        logger.info("Table title: {}".format(table_title))
        self.driver.switch_to.window(window_before)
        if table_title != kwargs['Table_title']:
            return False
        else:
            return True

    def smart_reporting(self, kwargs):
        logger.info("Executing smart_reporting()")
        """ Clicking on Application"""
        appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
        appl.click()

        """Clicking on Smart Reporting -> Smart Reporting Console"""
        smrtrep = self.driver.find_element_by_link_text('Smart Reporting')
        smrtrep.click()
        smrtrepcon = self.driver.find_element_by_link_text('Smart Reporting Console')

        """Validating Reports generated"""
        window_before = self.driver.window_handles[0]
        smrtrepcon.click()
        WebDriverWait(self.driver, 10).until(expected_conditions.number_of_windows_to_be(2))
        window_after = self.driver.window_handles[1]
        self.driver.switch_to.window(window_after)
        time.sleep(3)
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')))
        h3gopfoler = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')
        h3gopfoler.click()
        time.sleep(5)
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[2]/div[2]/div/div/div/div[2]')))
        mbnlsubfolder = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[2]/div[2]/div/div/div/div[2]')
        mbnlsubfolder.click()
        time.sleep(5)
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div[2]')))
        mbnlalltickets = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div[2]')
        action = ActionChains(self.driver)
        action.double_click(mbnlalltickets)
        action.perform()
        time.sleep(3)
        WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
            (By.XPATH, '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[1]/table[1]/tbody/tr[1]/td')))
        mbnlallticketslabel = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[1]/table[1]/tbody/tr[1]/td').text
        matching = True
        if mbnlallticketslabel != kwargs['mbnlallticketslabel']:
            logger.error('Report Populated "{}" is not correct. Expected Report is  "{}"'.format(mbnlallticketslabel,
                                                                                                 kwargs[
                                                                                                     'mbnlallticketslabel']))
            matching = False
        else:
            logger.info("Pass: '{}' Report populated is correct ".format(mbnlallticketslabel))
        inc = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[1]/td[1]').text
        logger.info(inc)
        table = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr')
        table2 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr')
        tablelist = [mbnlallticketslabel, ]
        tablelist2 = []
        for td in table.find_elements_by_tag_name("td"):
            tablelist.append(td.text)
            logger.info(tablelist)
        for td in table2.find_elements_by_tag_name("td"):
            tablelist2.append(td.text)
            logger.info(tablelist2)

        """Verifying table columns names are present as per Solution Document"""
        logger.info("kw {}".format(kwargs))
        found_list = []
        for k in kwargs.keys():
            found = False
            for elem in tablelist:
                if kwargs[k] in elem:
                    found = True
                    found_list.append(True)
                    logger.info("Expected Cloumn names {} is present".format(kwargs[k]))
                    break
            if not found:
                logger.info("Expected Column names {} is not present".format(kwargs[k]))
                found_list.append(False)
        self.driver.close()
        self.driver.switch_to.window(window_before)
        logger.info("Exiting smart_reporting()")
        return matching, all(found_list), inc, tablelist2

    def search_incident_verify_b2b_integration_info(self, kwargs):
        logger.info("Executing search_incident_verify_b2b_integration_info()")
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
        time.sleep(3)

        "Clicking on Date/System Tab"
        datesystm = self.driver.find_element_by_xpath(
            '//*[@id="WIN_3_1000000200"]/div[2]/div[2]/div/dl/dd[5]/span[2]')
        datesystm.click()
        "Verify Owner group is chosen as per requirement"
        owngrp = self.driver.find_element_by_xpath('//textarea[@id="arid_WIN_3_1000000422"]')
        owngrptext = owngrp.get_attribute('value')
        logger.info(owngrptext)
        body = self.driver.find_element_by_css_selector('body')
        body.click()
        body.send_keys(Keys.PAGE_UP)

        logger.info("Exiting search_incident_verify_b2b_integration_info()")
        return owngrptext

    def verify_status(self, kwargs):
        logger.info("Execuitng smart_reporting()")
        """ Clicking on Application"""
        appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
        appl.click()

        """Clicking on Smart Reporting -> Smart Reporting Console"""
        smrtrep = self.driver.find_element_by_link_text('Smart Reporting')
        smrtrep.click()
        smrtrepcon = self.driver.find_element_by_link_text('Smart Reporting Console')

        window_before = self.driver.window_handles[0]
        # print window_before
        smrtrepcon.click()
        WebDriverWait(self.driver, 10).until(expected_conditions.number_of_windows_to_be(2))
        window_after = self.driver.window_handles[1]
        self.driver.switch_to.window(window_after)
        # print window_after
        time.sleep(3)
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')))
        h3gopfoler = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')
        h3gopfoler.click()
        time.sleep(5)
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[2]/div[2]/div/div/div/div[2]')))
        mbnlsubfolder = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[2]/div[2]/div/div/div/div[2]')
        mbnlsubfolder.click()
        time.sleep(5)
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div[2]')))
        mbnlalltickets = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div[2]')
        action = ActionChains(self.driver)
        action.double_click(mbnlalltickets)
        action.perform()
        time.sleep(5)
        WebDriverWait(self.driver, 20).until(expected_conditions.presence_of_element_located(
            (By.XPATH, '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[1]/table[1]/tbody/tr[1]/td')))
        # mbnlallticketslabel = self.driver.find_element_by_xpath('//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[1]/table[1]/tbody/tr[1]/td').text
        matching = True
        time.sleep(5)

        "Getting values of Status from Table"
        table = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table')
        tablelist = []
        for tr in table.find_elements_by_tag_name("tr"):
            tablelist.append(tr.text)
        status_list = ['New', 'Assigned', 'In Progress', 'Pending', 'Resolved', 'Cancelled', 'Closed']

        """Verifying Status in table are present or not"""

        found_list = []

        for k in status_list:
            found = False
            for elem in tablelist:
                if k in elem:
                    found = True
                    found_list.append(True)
                    logger.info("Expected status {} is present".format(k))
                    # kwargs.pop(k)
                    break
            if not found:
                logger.info("Expected status {} is not present".format(k))
                found_list.append(False)

        logger.info("Found status = {}".format(found_list))

        if found_list[0]:
            matching = False
        elif not found_list[1]:
            matching = False
        elif not found_list[2]:
            matching = False
        elif not found_list[3]:
            matching = False
        elif not found_list[4]:
            matching = False
        elif not found_list[5]:
            matching = False
        elif not found_list[6]:
            matching = False

        self.driver.close()
        self.driver.switch_to.window(window_before)
        logger.info("Exiting smart_reporting()")
        return matching

    def smart_reporting_criteria(self, kwargs):
        logger.info("Execuitng smart_reporting()")
        """ Clicking on Application"""
        appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
        appl.click()

        """Clicking on Smart Reporting -> Smart Reporting Console"""
        smrtrep = self.driver.find_element_by_link_text('Smart Reporting')
        smrtrep.click()
        smrtrepcon = self.driver.find_element_by_link_text('Smart Reporting Console')

        """Validating Reports generated"""
        window_before = self.driver.window_handles[0]
        smrtrepcon.click()
        WebDriverWait(self.driver, 10).until(expected_conditions.number_of_windows_to_be(2))
        window_after = self.driver.window_handles[1]
        self.driver.switch_to.window(window_after)
        time.sleep(3)
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')))
        h3gopfoler = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')
        h3gopfoler.click()
        time.sleep(5)
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[2]/div[2]/div/div/div/div[2]')))
        mbnlsubfolder = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[2]/div[2]/div/div/div/div[2]')
        mbnlsubfolder.click()
        time.sleep(5)
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div[2]')))
        mbnlalltickets = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[1]/div/div[1]/div[1]/img')
        action = ActionChains(self.driver)
        action.double_click(mbnlalltickets)
        action.perform()
        time.sleep(10)
        inc = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[1]/td[1]').text
        logger.info(inc)
        table2 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr')

        tablelist2 = []
        for td in table2.find_elements_by_tag_name("td"):
            tablelist2.append(td.text)
            logger.info(tablelist2)
        print(kwargs['ownergroup'])
        print(tablelist2[2])
        if tablelist2[5] == kwargs['ownergroup']:
            criteria = 'True'
            logger.info("owner group = {}".format(kwargs['ownergroup']))
        elif tablelist2[4] == kwargs['B2BFYI']:
            criteria = 'True'
            logger.info("B2B FYI indicator = {}".format(kwargs['B2B FYI']))
        elif tablelist2[2] == kwargs['B2Borignator']:
            criteria = 'True'
            logger.info("B2B originator = {}".format(kwargs['B2Borignator']))
        elif tablelist2[2] == kwargs['B2Borignator1'] and tablelist2[3] == kwargs['B2Bassign']:
            criteria = 'True'
            logger.info(
                "B2Boriginator = {} and B2B assign is {}".format(kwargs['B2Borignator1'], kwargs['B2Bassign']))
        else:
            criteria = 'False'
        if 'Yes' == kwargs['B2Bassign']:
            criteria = 'True'
        self.driver.close()
        self.driver.switch_to.window(window_before)
        logger.info("Exiting smart_reporting()")
        return inc, tablelist2, criteria

    def smart_reporting_sorting(self, kwargs):
        logger.info("Execuitng smart_reporting()")
        """ Clicking on Application"""
        appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
        appl.click()

        """Clicking on Smart Reporting -> Smart Reporting Console"""
        smrtrep = self.driver.find_element_by_link_text('Smart Reporting')
        smrtrep.click()
        smrtrepcon = self.driver.find_element_by_link_text('Smart Reporting Console')

        window_before = self.driver.window_handles[0]
        # print window_before
        smrtrepcon.click()
        WebDriverWait(self.driver, 10).until(expected_conditions.number_of_windows_to_be(2))
        window_after = self.driver.window_handles[1]
        self.driver.switch_to.window(window_after)
        # print window_after
        time.sleep(3)
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')))
        h3gopfoler = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')
        h3gopfoler.click()
        time.sleep(5)
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[2]/div[2]/div/div/div/div[2]')))
        mbnlsubfolder = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[2]/div[2]/div/div/div/div[2]')
        mbnlsubfolder.click()
        time.sleep(5)
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div[2]')))
        mbnlalltickets = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div[2]')
        action = ActionChains(self.driver)
        action.double_click(mbnlalltickets)
        action.perform()
        time.sleep(5)
        WebDriverWait(self.driver, 20).until(expected_conditions.presence_of_element_located(
            (By.XPATH, '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[1]/table[1]/tbody/tr[1]/td')))
        mbnlallticketslabel = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[1]/table[1]/tbody/tr[1]/td').text
        matching = True
        if mbnlallticketslabel != kwargs['mbnlallticketslabel']:
            logger.error('Report Populated "{}" is not correct. Expected Report is  "{}"'.format(mbnlallticketslabel,
                                                                                                 kwargs[
                                                                                                     'mbnlallticketslabel']))
            matching = False
        else:
            logger.info("Pass: '{}' Report populated is correct ".format(mbnlallticketslabel))
        print("Before sorting(decending) of incident id")
        inc1 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[1]/td[1]').text
        inc2 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[2]/td[1]').text
        print(inc1)
        print(inc2)
        time.sleep(5)
        self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[1]/img').click()
        time.sleep(3)
        self.driver.find_element_by_xpath('/html/body/ul/li[2]/div').click()
        time.sleep(3)
        self.driver.find_element_by_xpath('/html/body/ul/li[2]/ul/li[3]/div[2]').click()
        time.sleep(4)
        inc1 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[1]/td[1]').text
        inc2 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[2]/td[1]').text
        print("After sorting(decending) for incident id")
        print(inc1)
        print(inc2)
        if inc1 > inc2:
            a = 'true'
        else:
            a = 'false'
        print("Check if incident are in decending is done")
        print(a)
        print("Before sorting(ascending) for date")
        date1 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[1]/td[10]').text
        date2 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[2]/td[10]').text
        print(date1)
        print(date2)

        time.sleep(5)
        self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[10]/img').click()
        time.sleep(3)
        self.driver.find_element_by_xpath('/html/body/ul/li[2]/div').click()
        time.sleep(3)
        self.driver.find_element_by_xpath('/html/body/ul/li[2]/ul/li[2]/div[2]').click()
        time.sleep(4)
        print("After sorting(ascending) for date")
        date1 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[1]/td[10]').text
        date2 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[2]/td[10]').text
        print(date1)
        print(date2)
        d1 = date1[:-8]
        d2 = date2[:-8]
        newdate1 = time.strptime(d1, "%d/%m/%Y ")
        newdate2 = time.strptime(d2, "%d/%m/%Y ")
        if newdate1 <= newdate2:
            b = 'true'
        else:
            b = 'false'
        print("Check if date are in ascending is done")
        print(b)
        print("Check if both ascending and descending is done")
        if a == b:
            r = True
        else:
            r = False
        self.driver.close()
        self.driver.switch_to.window(window_before)
        logger.info("Exiting smart_reporting()")
        return r

    def smart_reporting_b2b_verification(self, kwargs):
        logger.info("Executing smart_reporting()")
        """ Clicking on Application"""
        appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
        appl.click()

        """Clicking on Smart Reporting -> Smart Reporting Console"""
        smrtrep = self.driver.find_element_by_link_text('Smart Reporting')
        smrtrep.click()
        smrtrepcon = self.driver.find_element_by_link_text('Smart Reporting Console')

        """Validating Reports generated"""
        window_before = self.driver.window_handles[0]
        smrtrepcon.click()
        WebDriverWait(self.driver, 10).until(expected_conditions.number_of_windows_to_be(2))
        window_after = self.driver.window_handles[1]
        self.driver.switch_to.window(window_after)
        time.sleep(3)
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')))
        h3gopfoler = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')
        h3gopfoler.click()
        time.sleep(5)
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[2]/div[2]/div/div/div/div[2]')))
        mbnlsubfolder = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[2]/div[2]/div/div/div/div[2]')
        mbnlsubfolder.click()
        time.sleep(5)
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div[2]')))
        mbnlalltickets = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div[2]')
        action = ActionChains(self.driver)
        action.double_click(mbnlalltickets)
        action.perform()
        time.sleep(6)
        self.driver.find_element_by_xpath('//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[2]/div/div[3]').click()
        time.sleep(3)
        incidentid = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[1]/td[1]').text
        b2bincidentid = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[1]/td[7]').text
        TC = 'True'
        if b2bincidentid == '':
            TC = 'False'
            return TC
        logger.info("For incident id : {} b2b incidentid : {}".format(incidentid, b2bincidentid))
        self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[1]/table[2]/tbody/tr/td[4]/a/img').click()
        time.sleep(5)
        incidentid = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[1]/td[1]').text
        b2bincidentid = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[1]/td[7]').text
        if b2bincidentid == '':
            TC = 'False'
            return TC
        logger.info("For incident id : {} b2b incidentid : {}".format(incidentid, b2bincidentid))
        self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[1]/table[2]/tbody/tr/td[4]/a/img').click()
        time.sleep(5)
        incidentid = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[1]/td[1]').text
        b2bincidentid = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[1]/td[7]').text
        if b2bincidentid == '':
            TC = 'False'
            return TC
        logger.info("For incident id : {} b2b incidentid : {}".format(incidentid, b2bincidentid))
        self.driver.close()
        self.driver.switch_to.window(window_before)
        logger.info("Exiting smart_reporting()")
        return TC

    def upcoming_incident_sla_breach_main(self, kwargs):
        logger.info("Executing smart_reporting()")
        """ Clicking on Application"""
        appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
        appl.click()

        """Clicking on Smart Reporting -> Smart Reporting Console"""
        smrtrep = self.driver.find_element_by_link_text('Smart Reporting')
        smrtrep.click()
        smrtrepcon = self.driver.find_element_by_link_text('Smart Reporting Console')
        """Clicking on smart reporting console and switchingg windows"""
        window_before = self.driver.window_handles[0]
        smrtrepcon.click()
        WebDriverWait(self.driver, 10).until(expected_conditions.number_of_windows_to_be(2))
        window_after = self.driver.window_handles[1]
        self.driver.switch_to.window(window_after)
        time.sleep(3)
        search_report = self.driver.find_element(By.XPATH,
                                                 '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/input')
        search_report.send_keys(kwargs['Report Name'])
        search_report.send_keys(Keys.ENTER)
        time.sleep(2)
        """opening H3G Folder"""
        h3gopfoler = self.driver.find_element_by_xpath("//div[@title='H3G Operational Reporting']")
        time.sleep(2)
        h3gopfoler.click()
        """Opening rebus reports Folder"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          "/html[1]/body[1]/form[1]/div[12]/div[1]/div[2]/div[4]/div[1]/div[2]/div[3]/div[1]/div[2]/div[8]/div[1]/div[1]")))
        maya_reports = self.driver.find_element(By.XPATH,
                                                "/html[1]/body[1]/form[1]/div[12]/div[1]/div[2]/div[4]/div[1]/div[2]/div[3]/div[1]/div[2]/div[8]/div[1]/div[1]")
        maya_reports.click()
        time.sleep(3)
        """Double-click on incident-sla-dashboard report"""
        incident_sla_dashboard = self.driver.find_element(By.XPATH,
                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div[2]')
        time.sleep(2)
        action = ActionChains(self.driver)
        action.double_click(incident_sla_dashboard)
        action.perform()
        time.sleep(5)
        """Getting the text of the table names"""
        WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
            (By.XPATH, '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[1]/table/tbody/tr[1]/td')))
        table_title = self.driver.find_element(By.XPATH, '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[1]/table/tbody/tr[1]/td').text
        logger.info("Table title: {}".format(table_title))
        self.driver.switch_to.window(window_before)
        time.sleep(2)
        if table_title != kwargs['Table_title']:
            return False
        else:
            return True

    def upcoming_incident_sla_breach_main2(self, kwargs):
        logger.info("Execuitng smart_reporting()")
        """ Clicking on Application"""
        appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
        appl.click()
    
        """Clicking on Smart Reporting -> Smart Reporting Console"""
        smrtrep = self.driver.find_element_by_link_text('Smart Reporting')
        smrtrep.click()
        smrtrepcon = self.driver.find_element_by_link_text('Smart Reporting Console')
        """Clicking on smart reporting console and switchingg windows"""
        window_before = self.driver.window_handles[0]
        smrtrepcon.click()
        WebDriverWait(self.driver, 10).until(expected_conditions.number_of_windows_to_be(2))
        window_after = self.driver.window_handles[1]
        self.driver.switch_to.window(window_after)
        time.sleep(3)
    
        search_report = self.driver.find_element(By.XPATH,
                                                 '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/input')
        search_report.send_keys(kwargs['Report Name'])
        search_report.send_keys(Keys.ENTER)
        """opening H3G Folder"""
        h3gopfoler = self.driver.find_element_by_xpath("//div[@title='H3G Operational Reporting']")
        h3gopfoler.click()
        """Opening rebus reports Folder"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          "/html[1]/body[1]/form[1]/div[12]/div[1]/div[2]/div[4]/div[1]/div[2]/div[3]/div[1]/div[2]/div[8]/div[1]/div[1]")))
        maya_reports = self.driver.find_element(By.XPATH,
                                                "/html[1]/body[1]/form[1]/div[12]/div[1]/div[2]/div[4]/div[1]/div[2]/div[3]/div[1]/div[2]/div[8]/div[1]/div[1]")
        maya_reports.click()
        time.sleep(3)
        """Double-click on incident-sla-dashboard report"""
        incident_sla_dashboard = self.driver.find_element(By.XPATH,
                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div[2]')
        time.sleep(2)
        action = ActionChains(self.driver)
        action.double_click(incident_sla_dashboard)
        action.perform()
        time.sleep(5)
    
        """Getting the name of the columns"""
        column_list = []
        for i in range(1, 14):
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                                  '/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/div[1]'.format(
                                                                                                      i))))
            column_list.append(self.driver.find_element(By.XPATH,
                                                        '/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/div[1]'.format(
                                                            i)).text)
        column_names = ", ".join(column_list)
        logger.info(column_names)
        self.driver.switch_to.window(window_before)
        matching = True
        if column_names != kwargs['Column_names']:
            matching = False
        return matching

    def upcoming_incident_sla_breach_main1(self, kwargs):
        logger.info("Execuitng smart_reporting()")
        """ Clicking on Application"""
        appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
        appl.click()
    
        """Clicking on Smart Reporting -> Smart Reporting Console"""
        smrtrep = self.driver.find_element_by_link_text('Smart Reporting')
        smrtrep.click()
        smrtrepcon = self.driver.find_element_by_link_text('Smart Reporting Console')
        """Clicking on smart reporting console and switchingg windows"""
        window_before = self.driver.window_handles[0]
        smrtrepcon.click()
        WebDriverWait(self.driver, 10).until(expected_conditions.number_of_windows_to_be(2))
        window_after = self.driver.window_handles[1]
        self.driver.switch_to.window(window_after)
        time.sleep(3)
    
        search_report = self.driver.find_element(By.XPATH,
                                                 '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/input')
        search_report.send_keys(kwargs['Report Name'])
        search_report.send_keys(Keys.ENTER)
        time.sleep(2)
        """opening H3G Folder"""
        h3gopfoler = self.driver.find_element_by_xpath("//div[@title='H3G Operational Reporting']")
        h3gopfoler.click()
        time.sleep(2)
        """Opening rebus reports Folder"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          "/html[1]/body[1]/form[1]/div[12]/div[1]/div[2]/div[4]/div[1]/div[2]/div[3]/div[1]/div[2]/div[8]/div[1]/div[1]")))
        maya_reports = self.driver.find_element(By.XPATH,
                                                "/html[1]/body[1]/form[1]/div[12]/div[1]/div[2]/div[4]/div[1]/div[2]/div[3]/div[1]/div[2]/div[8]/div[1]/div[1]")
        maya_reports.click()
        time.sleep(3)
        """Double-click on incident-sla-dashboard report"""
        incident_sla_dashboard = self.driver.find_element(By.XPATH,
                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div[2]')
        time.sleep(2)
        action = ActionChains(self.driver)
        action.double_click(incident_sla_dashboard)
        action.perform()
        time.sleep(5)
    
        """Checking incident id columns-->descending"""
        sorting = True
        column_count = 1
        for i in range(1, 2):
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                (By.XPATH,
                 "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                     i))))
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                                                                  i))))
            time.sleep(3)
            obj = self.driver.find_element(By.XPATH,
                                           "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                               i))
            obj.click()
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")))
            obj1 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")
            time.sleep(1)
            obj1.click()
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable(
                (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[3]/div[2]")))
            obj2 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[3]/div[2]")
            time.sleep(1)
            obj2.click()
            time.sleep(7)
            column_list = []
            actual_column_list = []
            column_count = 1
            for j in range(1, 21):
                WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH, "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]/a[1]".format(j, column_count))))
                column_list.append(self.driver.find_element(By.XPATH, "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]/a[1]".format(j, column_count)).text)
            for incident in column_list:
                incident = re.findall("INC([\d]*)", incident)[0]
                actual_column_list.append(float(incident))
            print(actual_column_list)
            if float(actual_column_list) != sorted(float(actual_column_list), reverse=True):
                sorting = False
            logger.info("Incident ID descending failed")
            logger.info(float(actual_column_list))
            logger.info(sorted(float(actual_column_list), reverse=True))
            column_count += 1
        
            """Checking priority columns-->descending"""
            column_count = 3
            for i in range(3, 4):
                WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                    (By.XPATH,
                     "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                         i))))
                WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                                  "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                                                                      i))))
                time.sleep(3)
                obj = self.driver.find_element(By.XPATH,
                                               "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                   i))
                obj.click()
                WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                    (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")))
                obj1 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")
                time.sleep(1)
                obj1.click()
                WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable(
                    (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[3]/div[2]")))
                obj2 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[3]/div[2]")
                time.sleep(1)
                obj2.click()
                time.sleep(7)
                column_list = []
            
                for j in range(1, 21):
                    WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                                          "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                                                              j,
                                                                                                              column_count))))
                    column_list.append(self.driver.find_element(By.XPATH,
                                                                "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                    j, column_count)).text)
                if column_list != sorted(column_list, reverse=True):
                    sorting = False
                logger.info("Priority descending failed")
                logger.info(column_list)
                logger.info(sorted(column_list, reverse=True))
                column_count += 1
        
            """Checking time left columns-->descending"""
            column_count = 10
            for i in range(10, 11):
                WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                    (By.XPATH,
                     "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                         i))))
                WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                                  "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                                                                      i))))
                time.sleep(3)
                obj = self.driver.find_element(By.XPATH,
                                               "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                   i))
                obj.click()
                WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                    (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")))
                obj1 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")
                time.sleep(1)
                obj1.click()
                WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable(
                    (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[3]/div[2]")))
                obj2 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[3]/div[2]")
                time.sleep(1)
                obj2.click()
                time.sleep(7)
                column_list = []
                actual_column_list = []
                for j in range(1, 21):
                    WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                                          "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                                                              j,
                                                                                                              column_count))))
                    column_list.append(self.driver.find_element(By.XPATH,
                                                                "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                    j, column_count)).text)
                refined_column_list = re.findall(r"u'([\d,]*)", str(column_list))
                for k in refined_column_list:
                    actual_column_list.append(float(k.replace(",", "")))
                if actual_column_list != sorted(actual_column_list, reverse=True):
                    sorting = False
                logger.info("Time left descending failed")
                logger.info(refined_column_list)
                logger.info(actual_column_list)
                logger.info(sorted(actual_column_list, reverse=True))
                column_count += 1
        
            """Checking time completed columns-->descending"""
            column_count = 11
            for i in range(11, 12):
                WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                    (By.XPATH,
                     "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                         i))))
                WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                                  "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                                                                      i))))
                time.sleep(3)
                obj = self.driver.find_element(By.XPATH,
                                               "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                   i))
                obj.click()
                WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                    (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")))
                obj1 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")
                time.sleep(1)
                obj1.click()
                WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable(
                    (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[3]/div[2]")))
                obj2 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[3]/div[2]")
                time.sleep(1)
                obj2.click()
                time.sleep(7)
                column_list = []
                actual_column_list = []
            
                for j in range(1, 21):
                    WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                                          "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                                                              j,
                                                                                                              column_count))))
                    column_list.append(self.driver.find_element(By.XPATH,
                                                                "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                    j, column_count)).text)
                refined_column_list = re.findall(r'(\d+\s)Days*', str(column_list))
                for k in refined_column_list:
                    actual_column_list.append(float(k.replace(",", "")))
                if actual_column_list != sorted(actual_column_list, reverse=True):
                    sorting = False
                    logger.info("time completed descending failed")
                logger.info(actual_column_list)
                logger.info(sorted(actual_column_list, reverse=True))
                column_count += 1
        
            """Checking %complete columns-->descending"""
            column_count = 12
            for i in range(12, 13):
                WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                    (By.XPATH,
                     "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                         i))))
                WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                                  "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                                                                      i))))
                time.sleep(3)
                obj = self.driver.find_element(By.XPATH,
                                               "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                   i))
                obj.click()
                WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                    (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")))
                obj1 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")
                time.sleep(1)
                obj1.click()
                WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable(
                    (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[3]/div[2]")))
                obj2 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[3]/div[2]")
                time.sleep(1)
                obj2.click()
                time.sleep(7)
                column_list = []
                actual_column_list = []
            
                for j in range(1, 21):
                    WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                                          "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                                                              j,
                                                                                                              column_count))))
                    column_list.append(self.driver.find_element(By.XPATH,
                                                                "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                    j, column_count)).text)
                refined_column_list = re.findall(r'([\d,.]+)%', str(column_list))
                for k in refined_column_list:
                    actual_column_list.append(float(k.replace(",", "")))
                if actual_column_list != sorted(actual_column_list, reverse=True):
                    sorting = False
                    logger.info("% completed descending failed")
                logger.info(actual_column_list)
                logger.info(sorted(actual_column_list, reverse=True))
                column_count += 1
        
            """Checking incident id columns-->ascending"""
            column_count = 1
            for i in range(1, 2):
                WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                    (By.XPATH,
                     "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                         i))))
                WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                                  "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                                                                      i))))
                time.sleep(3)
                obj = self.driver.find_element(By.XPATH,
                                               "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                   i))
                obj.click()
                WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                    (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")))
                obj1 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")
                time.sleep(1)
                obj1.click()
                WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable(
                    (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[2]/div[2]")))
                obj2 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[2]/div[2]")
                time.sleep(1)
                obj2.click()
                time.sleep(7)
                column_list = []
            
                for j in range(1, 21):
                    WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                                          "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                                                              j,
                                                                                                              column_count))))
                    column_list.append(self.driver.find_element(By.XPATH,
                                                                "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                    j, column_count)).text)
                if column_list != sorted(column_list, reverse=False):
                    sorting = False
                    logger.info("Incident ID descending failed")
                logger.info(column_list)
                logger.info(sorted(column_list, reverse=False))
                column_count += 1
            
                """Checking priority columns-->ascending"""
                column_count = 3
                for i in range(3, 4):
                    WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                        (By.XPATH,
                         "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                             i))))
                    WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                                      "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                                                                          i))))
                    time.sleep(3)
                    obj = self.driver.find_element(By.XPATH,
                                                   "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                       i))
                    obj.click()
                    WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                        (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")))
                    obj1 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")
                    time.sleep(1)
                    obj1.click()
                    WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable(
                        (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[2]/div[2]")))
                    obj2 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[2]/div[2]")
                    time.sleep(1)
                    obj2.click()
                    time.sleep(7)
                    column_list = []
                
                    for j in range(1, 21):
                        WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                                              "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                                                                  j,
                                                                                                                  column_count))))
                        column_list.append(self.driver.find_element(By.XPATH,
                                                                    "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                        j, column_count)).text)
                    if column_list != sorted(column_list, reverse=False):
                        sorting = False
                        logger.info("Priority ascending failed")
                    logger.info(column_list)
                    logger.info(sorted(column_list, reverse=False))
                    column_count += 1
            
                """Checking time left columns-->ascending"""
                column_count = 10
                for i in range(10, 11):
                    WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                        (By.XPATH,
                         "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                             i))))
                    WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                                      "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                                                                          i))))
                    time.sleep(3)
                    obj = self.driver.find_element(By.XPATH,
                                                   "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                       i))
                    obj.click()
                    WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                        (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")))
                    obj1 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")
                    time.sleep(1)
                    obj1.click()
                    WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable(
                        (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[2]/div[2]")))
                    obj2 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[2]/div[2]")
                    time.sleep(1)
                    obj2.click()
                    time.sleep(7)
                    column_list = []
                    actual_column_list = []
                    for j in range(1, 21):
                        WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                                              "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                                                                  j,
                                                                                                                  column_count))))
                        column_list.append(self.driver.find_element(By.XPATH,
                                                                    "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                        j, column_count)).text)
                    refined_column_list = re.findall(r"u'([\d,]*)", str(column_list))
                    for k in refined_column_list:
                        actual_column_list.append(float(k.replace(",", "")))
                    if actual_column_list != sorted(actual_column_list, reverse=False):
                        sorting = False
                        logger.info("time left ascending failed")
                    logger.info(sorted(actual_column_list, reverse=False))
                    column_count += 1
            
                """Checking time completed columns-->ascending"""
                column_count = 11
                for i in range(11, 12):
                    WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                        (By.XPATH,
                         "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                             i))))
                    WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                                      "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                                                                          i))))
                    time.sleep(3)
                    obj = self.driver.find_element(By.XPATH,
                                                   "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                       i))
                    obj.click()
                    WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                        (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")))
                    obj1 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")
                    time.sleep(1)
                    obj1.click()
                    WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable(
                        (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[2]/div[2]")))
                    obj2 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[2]/div[2]")
                    time.sleep(1)
                    obj2.click()
                    time.sleep(7)
                    column_list = []
                    actual_column_list = []
                
                    for j in range(1, 21):
                        WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                                              "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                                                                  j,
                                                                                                                  column_count))))
                        column_list.append(self.driver.find_element(By.XPATH,
                                                                    "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                        j, column_count)).text)
                    refined_column_list = re.findall(r'(\d+\s)Days*', str(column_list))
                    for k in refined_column_list:
                        actual_column_list.append(float(k.replace(",", "")))
                    if actual_column_list != sorted(actual_column_list, reverse=False):
                        sorting = False
                    logger.info(actual_column_list)
                    logger.info(sorted(actual_column_list, reverse=False))
                    column_count += 1
            
                """Checking %complete columns-->ascending"""
                column_count = 12
                for i in range(12, 13):
                    WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                        (By.XPATH,
                         "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                             i))))
                    WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                                      "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                                                                          i))))
                    time.sleep(3)
                    obj = self.driver.find_element(By.XPATH,
                                                   "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                       i))
                    obj.click()
                    WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                        (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")))
                    obj1 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")
                    time.sleep(1)
                    obj1.click()
                    WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable(
                        (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[2]/div[2]")))
                    obj2 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[2]/div[2]")
                    time.sleep(1)
                    obj2.click()
                    time.sleep(7)
                    column_list = []
                    actual_column_list = []
                    for j in range(1, 21):
                        WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                                              "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                                                                  j,
                                                                                                                  column_count))))
                        column_list.append(self.driver.find_element(By.XPATH,
                                                                    "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                        j, column_count)).text)
                    refined_column_list = re.findall(r'([\d,.]+)%', str(column_list))
                    for k in refined_column_list:
                        actual_column_list.append(float(k.replace(",", "")))
                    if actual_column_list != sorted(actual_column_list, reverse=False):
                        sorting = False
                        logger.info("%complete ascending failed")
                    logger.info(actual_column_list)
                    logger.info(sorted(actual_column_list, reverse=False))
                    column_count += 1
        self.driver.switch_to.window(window_before)
    
        return sorting

    def breached_incidents_sla_tickets_main1(self, kwargs):
        logger.info("Execuitng smart_reporting()")
        """ Clicking on Application"""
        appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
        appl.click()

        """Clicking on Smart Reporting -> Smart Reporting Console"""
        smrtrep = self.driver.find_element_by_link_text('Smart Reporting')
        smrtrep.click()
        smrtrepcon = self.driver.find_element_by_link_text('Smart Reporting Console')
        """Clicking on smart reporting console and switchingg windows"""
        window_before = self.driver.window_handles[0]
        smrtrepcon.click()
        WebDriverWait(self.driver, 10).until(expected_conditions.number_of_windows_to_be(2))
        window_after = self.driver.window_handles[1]
        self.driver.switch_to.window(window_after)
        time.sleep(3)

        search_report = self.driver.find_element(By.XPATH,
                                                 '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/input')
        search_report.send_keys(kwargs['Report Name'])
        search_report.send_keys(Keys.ENTER)
        time.sleep(2)
        """opening H3G Folder"""
        h3gopfoler = self.driver.find_element_by_xpath("//div[@title='H3G Operational Reporting']")
        h3gopfoler.click()
        time.sleep(2)
        """Opening Rebus reports Folder"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          "/html[1]/body[1]/form[1]/div[12]/div[1]/div[2]/div[4]/div[1]/div[2]/div[3]/div[1]/div[2]/div[8]/div[1]/div[1]")))
        maya_reports = self.driver.find_element(By.XPATH,
                                                "/html[1]/body[1]/form[1]/div[12]/div[1]/div[2]/div[4]/div[1]/div[2]/div[3]/div[1]/div[2]/div[8]/div[1]/div[1]")
        maya_reports.click()
        time.sleep(3)
        """Double-click on incident-sla-dashboard report"""
        incident_sla_dashboard = self.driver.find_element(By.XPATH,
                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div[2]')
        time.sleep(2)
        action = ActionChains(self.driver)
        action.double_click(incident_sla_dashboard)
        action.perform()
        time.sleep(5)

        """Checking incident id columns-->descending"""
        sorting = True
        column_count = 1
        for i in range(1, 2):
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                (By.XPATH,
                 "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                     i))))
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                                                                  i))))
            time.sleep(3)
            obj = self.driver.find_element(By.XPATH,
                                           "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                               i))
            obj.click()
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")))
            obj1 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")
            time.sleep(1)
            obj1.click()
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable(
                (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[3]/div[2]")))
            obj2 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[3]/div[2]")
            time.sleep(1)
            obj2.click()
            time.sleep(7)
            column_list = []

            for j in range(1, 101):
                WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                                      "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[1]/a[1]".format(
                                                                                                          j,
                                                                                                          column_count))))
                column_list.append(self.driver.find_element(By.XPATH,
                                                            "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[1]/a[1]".format(
                                                                j, column_count)).text)
            if column_list != sorted(column_list, reverse=True):
                sorting = False
            logger.info(column_list)
            logger.info(sorted(column_list, reverse=True))
            column_count += 1

            """Checking priority columns-->descending"""
            column_count = 3
            for i in range(3, 4):
                WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                    (By.XPATH,
                     "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                         i))))
                WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                                  "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                                                                      i))))
                time.sleep(3)
                obj = self.driver.find_element(By.XPATH,
                                               "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                   i))
                obj.click()
                WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                    (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")))
                obj1 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")
                time.sleep(1)
                obj1.click()
                WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable(
                    (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[3]/div[2]")))
                obj2 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[3]/div[2]")
                time.sleep(1)
                obj2.click()
                time.sleep(7)
                column_list = []

                for j in range(1, 101):
                    WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                                          "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                                                              j,
                                                                                                              column_count))))
                    column_list.append(self.driver.find_element(By.XPATH,
                                                                "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                    j, column_count)).text)
                if column_list != sorted(column_list, reverse=True):
                    sorting = False
                logger.info(column_list)
                logger.info(sorted(column_list, reverse=True))
                column_count += 1

            """Checking %complete columns-->descending"""
            column_count = 11
            for i in range(11, 12):
                WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                    (By.XPATH,
                     "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                         i))))
                WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                                  "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                                                                      i))))
                time.sleep(3)
                obj = self.driver.find_element(By.XPATH,
                                               "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                   i))
                obj.click()
                WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                    (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")))
                obj1 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")
                time.sleep(1)
                obj1.click()
                WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable(
                    (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[3]/div[2]")))
                obj2 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[3]/div[2]")
                time.sleep(1)
                obj2.click()
                time.sleep(7)
                column_list = []
                actual_column_list = []

                for j in range(1, 101):
                    WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                                          "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                                                              j,
                                                                                                              column_count))))
                    column_list.append(self.driver.find_element(By.XPATH,
                                                                "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                    j, column_count)).text)
                refined_column_list = re.findall(r'([\d,.]+)%', str(column_list))
                for k in refined_column_list:
                    actual_column_list.append(float(k.replace(",", "")))
                if actual_column_list != sorted(actual_column_list, reverse=True):
                    sorting = False
                logger.info(actual_column_list)
                logger.info(sorted(actual_column_list, reverse=True))
                column_count += 1

            """Checking time completed columns-->descending"""
            column_count = 10
            for i in range(10, 11):
                WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                    (By.XPATH,
                     "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                         i))))
                WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                                  "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                                                                      i))))
                time.sleep(3)
                obj = self.driver.find_element(By.XPATH,
                                               "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                   i))
                obj.click()
                WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                    (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")))
                obj1 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")
                time.sleep(1)
                obj1.click()
                WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable(
                    (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[3]/div[2]")))
                obj2 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[3]/div[2]")
                time.sleep(1)
                obj2.click()
                time.sleep(7)
                column_list = []
                actual_column_list = []

                for j in range(1, 101):
                    WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                                          "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                                                              j,
                                                                                                              column_count))))
                    column_list.append(self.driver.find_element(By.XPATH,
                                                                "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                    j, column_count)).text)
                refined_column_list = re.findall(r'(\d+\s)Days*', str(column_list))
                for k in refined_column_list:
                    actual_column_list.append(float(k.replace(",", "")))
                if actual_column_list != sorted(actual_column_list, reverse=True):
                    sorting = False
                logger.info(actual_column_list)
                logger.info(sorted(actual_column_list, reverse=True))
                column_count += 1

            """Checking incident id columns-->ascending"""
            column_count = 1
            for i in range(1, 2):
                WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                    (By.XPATH,
                     "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                         i))))
                WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                                  "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                                                                      i))))
                time.sleep(3)
                obj = self.driver.find_element(By.XPATH,
                                               "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                   i))
                obj.click()
                WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                    (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")))
                obj1 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")
                time.sleep(1)
                obj1.click()
                WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable(
                    (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[2]/div[2]")))
                obj2 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[2]/div[2]")
                time.sleep(1)
                obj2.click()
                time.sleep(7)
                column_list = []

                for j in range(1, 101):
                    WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                                          "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                                                              j,
                                                                                                              column_count))))
                    column_list.append(self.driver.find_element(By.XPATH,
                                                                "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                    j, column_count)).text)
                if column_list != sorted(column_list, reverse=False):
                    sorting = False
                logger.info(column_list)
                logger.info(sorted(column_list, reverse=False))
                column_count += 1

                """Checking priority columns-->ascending"""
                column_count = 3
                for i in range(3, 4):
                    WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                        (By.XPATH,
                         "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                             i))))
                    WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                                      "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                                                                          i))))
                    time.sleep(3)
                    obj = self.driver.find_element(By.XPATH,
                                                   "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                       i))
                    obj.click()
                    WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                        (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")))
                    obj1 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")
                    time.sleep(1)
                    obj1.click()
                    WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable(
                        (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[2]/div[2]")))
                    obj2 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[2]/div[2]")
                    time.sleep(1)
                    obj2.click()
                    time.sleep(7)
                    column_list = []

                    for j in range(1, 101):
                        WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                                              "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                                                                  j,
                                                                                                                  column_count))))
                        column_list.append(self.driver.find_element(By.XPATH,
                                                                    "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                        j, column_count)).text)
                    if column_list != sorted(column_list, reverse=False):
                        sorting = False
                    logger.info(column_list)
                    logger.info(sorted(column_list, reverse=False))
                    column_count += 1

                """Checking time completed columns-->ascending"""
                column_count = 10
                for i in range(10, 11):
                    WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                        (By.XPATH,
                         "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                             i))))
                    WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                                      "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                                                                          i))))
                    time.sleep(3)
                    obj = self.driver.find_element(By.XPATH,
                                                   "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                       i))
                    obj.click()
                    WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                        (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")))
                    obj1 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")
                    time.sleep(1)
                    obj1.click()
                    WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable(
                        (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[2]/div[2]")))
                    obj2 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[2]/div[2]")
                    time.sleep(1)
                    obj2.click()
                    time.sleep(7)
                    column_list = []
                    actual_column_list = []

                    for j in range(1, 101):
                        WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                                              "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                                                                  j,
                                                                                                                  column_count))))
                        column_list.append(self.driver.find_element(By.XPATH,
                                                                    "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                        j, column_count)).text)
                    refined_column_list = re.findall(r'(\d+\s)Days*', str(column_list))
                    for k in refined_column_list:
                        actual_column_list.append(float(k.replace(",", "")))
                    if actual_column_list != sorted(actual_column_list, reverse=False):
                        sorting = False
                    logger.info(actual_column_list)
                    logger.info(sorted(actual_column_list, reverse=False))
                    column_count += 1

                """Checking %complete columns-->ascending"""
                column_count = 11
                for i in range(11, 12):
                    WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                        (By.XPATH,
                         "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                             i))))
                    WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                                      "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                                                                          i))))
                    time.sleep(3)
                    obj = self.driver.find_element(By.XPATH,
                                                   "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                       i))
                    obj.click()
                    WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                        (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")))
                    obj1 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")
                    time.sleep(1)
                    obj1.click()
                    WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable(
                        (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[2]/div[2]")))
                    obj2 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[2]/div[2]")
                    time.sleep(1)
                    obj2.click()
                    time.sleep(7)
                    column_list = []
                    actual_column_list = []
                    for j in range(1, 101):
                        WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                                              "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                                                                  j,
                                                                                                                  column_count))))
                        column_list.append(self.driver.find_element(By.XPATH,
                                                                    "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                        j, column_count)).text)
                    refined_column_list = re.findall(r'([\d,.]+)%', str(column_list))
                    for k in refined_column_list:
                        actual_column_list.append(float(k.replace(",", "")))
                    if column_list != sorted(column_list, reverse=False):
                        sorting = False
                    logger.info(actual_column_list)
                    logger.info(sorted(actual_column_list, reverse=False))
                    column_count += 1

        self.driver.switch_to.window(window_before)

        return sorting

    def listSortedOrNot(self, arr):
        n = len(arr)
    
        if n == 1 or n == 0:
            return True
    
        return arr[0] <= arr[1] and self.listSortedOrNot(arr[1:])

    def dateSortedOrNot(self, arr):
        n = len(arr)
    
        if n == 1 or n == 0:
            return True
    
        return time.strptime(arr[0], "%d/%m/%Y %I:%M %p") <= time.strptime(arr[1],
                                                                           "%d/%m/%Y %I:%M %p") and self.dateSortedOrNot(
            arr[1:])

    def dateSortedOrNotDes(self, arr):
        n = len(arr)
    
        if n == 1 or n == 0:
            return True
    
        return time.strptime(arr[0], "%d/%m/%Y %I:%M %p") >= time.strptime(arr[1],
                                                                           "%d/%m/%Y %I:%M %p") and self.dateSortedOrNotDes(
            arr[1:])

    def completeSortedOrNot(self, arr):
        n = len(arr)
    
        if n == 1 or n == 0:
            return True
        arr[0] = arr[0].replace(',', '')
        arr[1] = arr[1].replace(',', '')
        return float(arr[0].strip("\t\n\r%")) <= float(arr[1].strip("\t\n\r%")) and self.completeSortedOrNot(arr[1:])

    def completeSortedOrNotDes(self, arr):
        n = len(arr)
    
        if n == 1 or n == 0:
            return True
        arr[0] = arr[0].replace(',', '')
        arr[1] = arr[1].replace(',', '')
        return float(arr[0].strip("\t\n\r%")) >= float(arr[1].strip("\t\n\r%")) and self.completeSortedOrNotDes(arr[1:])

    def breached_incidents_sla_tickets_main2(self, kwargs):
        logger.info("Execuitng smart_reporting()")
        """ Clicking on Application"""
        appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
        appl.click()
    
        """Clicking on Smart Reporting -> Smart Reporting Console"""
        smrtrep = self.driver.find_element_by_link_text('Smart Reporting')
        smrtrep.click()
        smrtrepcon = self.driver.find_element_by_link_text('Smart Reporting Console')
        """Clicking on smart reporting console and switchingg windows"""
        window_before = self.driver.window_handles[0]
        smrtrepcon.click()
        WebDriverWait(self.driver, 10).until(expected_conditions.number_of_windows_to_be(2))
        window_after = self.driver.window_handles[1]
        self.driver.switch_to.window(window_after)
        time.sleep(3)
    
        search_report = self.driver.find_element(By.XPATH,
                                                 '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/input')
        search_report.send_keys(kwargs['Report Name'])
        search_report.send_keys(Keys.ENTER)
        """opening H3G Folder"""
        h3gopfoler = self.driver.find_element_by_xpath("//div[@title='H3G Operational Reporting']")
        h3gopfoler.click()
        """Opening rebus reports Folder"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          "/html[1]/body[1]/form[1]/div[12]/div[1]/div[2]/div[4]/div[1]/div[2]/div[3]/div[1]/div[2]/div[8]/div[1]/div[1]")))
        maya_reports = self.driver.find_element(By.XPATH,
                                                "/html[1]/body[1]/form[1]/div[12]/div[1]/div[2]/div[4]/div[1]/div[2]/div[3]/div[1]/div[2]/div[8]/div[1]/div[1]")
        maya_reports.click()
        time.sleep(3)
        """Double-click on incident-sla-dashboard report"""
        incident_sla_dashboard = self.driver.find_element(By.XPATH,
                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div[2]')
        time.sleep(2)
        action = ActionChains(self.driver)
        action.double_click(incident_sla_dashboard)
        action.perform()
        time.sleep(5)
    
        """Getting the list of the columns"""
        column_list = []
        for i in range(1, 14):
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                                  '/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/div[1]'.format(
                                                                                                      i))))
            column_list.append(self.driver.find_element(By.XPATH,
                                                        '/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/div[1]'.format(
                                                            i)).text)
        column_names = ", ".join(column_list)
        logger.info(column_names)
        self.driver.switch_to.window(window_before)
        matching = True
        if column_names != kwargs['Column_names']:
            matching = False
        return matching

    def incident_sla_dashboard_main(self, kwargs):
        logger.info("Execuitng smart_reporting()")
        """ Clicking on Application"""
        appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
        appl.click()

        """Clicking on Smart Reporting -> Smart Reporting Console"""
        smrtrep = self.driver.find_element_by_link_text('Smart Reporting')
        smrtrep.click()
        smrtrepcon = self.driver.find_element_by_link_text('Smart Reporting Console')
        """Clicking on smart reporting console and switchingg windows"""
        window_before = self.driver.window_handles[0]
        smrtrepcon.click()
        WebDriverWait(self.driver, 10).until(expected_conditions.number_of_windows_to_be(2))
        window_after = self.driver.window_handles[1]
        self.driver.switch_to.window(window_after)
        time.sleep(3)

        search_report = self.driver.find_element(By.XPATH,
                                                 '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/input')
        search_report.send_keys(kwargs['Report Name'])
        search_report.send_keys(Keys.ENTER)
        time.sleep(5)
        """opening H3G Folder"""
        h3gopfoler = self.driver.find_element_by_xpath("//div[@title='H3G Operational Reporting']")
        time.sleep(5)
        h3gopfoler.click()
        """Opening Rebus Reports Folder"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          "/html[1]/body[1]/form[1]/div[12]/div[1]/div[2]/div[4]/div[1]/div[2]/div[3]/div[1]/div[2]/div[8]/div[1]/div[1]")))

        maya_reports = self.driver.find_element(By.XPATH,
                                                "/html[1]/body[1]/form[1]/div[12]/div[1]/div[2]/div[4]/div[1]/div[2]/div[3]/div[1]/div[2]/div[8]/div[1]/div[1]")
        maya_reports.click()
        time.sleep(5)
        """Double-click on incident-sla-dashboard report"""
        incident_sla_dashboard = self.driver.find_element(By.XPATH,
                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div[2]')
        time.sleep(2)
        action = ActionChains(self.driver)
        action.double_click(incident_sla_dashboard)
        action.perform()
        time.sleep(5)
        """Getting the text of the table name"""
        WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
            (By.XPATH, '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[1]/table/tbody/tr[1]/td')))
        table_title = self.driver.find_element(By.XPATH, '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[1]/table/tbody/tr[1]/td').text
        logger.info("Table title: {}".format(table_title))
        self.driver.switch_to.window(window_before)
        if table_title != kwargs['Table_title']:
            return False
        else:
            return True

    def breached_incidents_sla_tickets_main(self, kwargs):
        logger.info("Execuitng smart_reporting()")
        """ Clicking on Application"""
        appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
        appl.click()

        """Clicking on Smart Reporting -> Smart Reporting Console"""
        smrtrep = self.driver.find_element_by_link_text('Smart Reporting')
        smrtrep.click()
        smrtrepcon = self.driver.find_element_by_link_text('Smart Reporting Console')
        """Clicking on smart reporting console and switchingg windows"""
        window_before = self.driver.window_handles[0]
        smrtrepcon.click()
        WebDriverWait(self.driver, 10).until(expected_conditions.number_of_windows_to_be(2))
        window_after = self.driver.window_handles[1]
        self.driver.switch_to.window(window_after)
        time.sleep(3)

        search_report = self.driver.find_element(By.XPATH,
                                                 '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/input')
        search_report.send_keys(kwargs['Report Name'])
        search_report.send_keys(Keys.ENTER)
        time.sleep(2)
        """opening H3G Folder"""
        h3gopfoler = self.driver.find_element_by_xpath("//div[@title='H3G Operational Reporting']")
        time.sleep(2)
        h3gopfoler.click()
        """Opening rebus reports Folder"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          "/html[1]/body[1]/form[1]/div[12]/div[1]/div[2]/div[4]/div[1]/div[2]/div[3]/div[1]/div[2]/div[8]/div[1]/div[1]")))
        maya_reports = self.driver.find_element(By.XPATH,
                                                "/html[1]/body[1]/form[1]/div[12]/div[1]/div[2]/div[4]/div[1]/div[2]/div[3]/div[1]/div[2]/div[8]/div[1]/div[1]")
        maya_reports.click()
        time.sleep(3)
        """Double-click on incident-sla-dashboard report"""
        incident_sla_dashboard = self.driver.find_element(By.XPATH,
                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div[2]')
        time.sleep(2)
        action = ActionChains(self.driver)
        action.double_click(incident_sla_dashboard)
        action.perform()
        time.sleep(5)
        """Getting the text of the table name"""
        WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
            (By.XPATH, '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[1]/table[1]/tbody/tr[1]/td')))
        table_title = self.driver.find_element(By.XPATH, '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[1]/table[1]/tbody/tr[1]/td').text
        logger.info("Table title: {}".format(table_title))
        self.driver.switch_to.window(window_before)
        time.sleep(2)
        if table_title != kwargs['Table_title']:
            return False
        else:
            return True

    def breached_incidents_sla_tickets_main1(self, kwargs):
        logger.info("Execuitng smart_reporting()")
        """ Clicking on Application"""
        appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
        appl.click()

        """Clicking on Smart Reporting -> Smart Reporting Console"""
        smrtrep = self.driver.find_element_by_link_text('Smart Reporting')
        smrtrep.click()
        smrtrepcon = self.driver.find_element_by_link_text('Smart Reporting Console')
        """Clicking on smart reporting console and switchingg windows"""
        window_before = self.driver.window_handles[0]
        smrtrepcon.click()
        WebDriverWait(self.driver, 10).until(expected_conditions.number_of_windows_to_be(2))
        window_after = self.driver.window_handles[1]
        self.driver.switch_to.window(window_after)
        time.sleep(3)

        search_report = self.driver.find_element(By.XPATH,
                                                 '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/input')
        search_report.send_keys(kwargs['Report Name'])
        search_report.send_keys(Keys.ENTER)
        time.sleep(2)
        """opening H3G Folder"""
        h3gopfoler = self.driver.find_element_by_xpath("//div[@title='H3G Operational Reporting']")
        h3gopfoler.click()
        time.sleep(2)
        """Opening Rebus reports Folder"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          "/html[1]/body[1]/form[1]/div[12]/div[1]/div[2]/div[4]/div[1]/div[2]/div[3]/div[1]/div[2]/div[8]/div[1]/div[1]")))
        maya_reports = self.driver.find_element(By.XPATH,
                                                "/html[1]/body[1]/form[1]/div[12]/div[1]/div[2]/div[4]/div[1]/div[2]/div[3]/div[1]/div[2]/div[8]/div[1]/div[1]")
        maya_reports.click()
        time.sleep(3)
        """Double-click on incident-sla-dashboard report"""
        incident_sla_dashboard = self.driver.find_element(By.XPATH,
                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div[2]')
        time.sleep(2)
        action = ActionChains(self.driver)
        action.double_click(incident_sla_dashboard)
        action.perform()
        time.sleep(5)

        """Checking incident id columns-->descending"""
        sorting = True
        column_count = 1
        for i in range(1, 2):
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                (By.XPATH,
                 "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                     i))))
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                                                                  i))))
            time.sleep(3)
            obj = self.driver.find_element(By.XPATH,
                                           "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                               i))
            obj.click()
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")))
            obj1 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")
            time.sleep(1)
            obj1.click()
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable(
                (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[3]/div[2]")))
            obj2 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[3]/div[2]")
            time.sleep(1)
            obj2.click()
            time.sleep(7)
            column_list = []

            for j in range(1, 101):
                WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                                      "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[1]/a[1]".format(
                                                                                                          j,
                                                                                                          column_count))))
                column_list.append(self.driver.find_element(By.XPATH,
                                                            "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[1]/a[1]".format(
                                                                j, column_count)).text)
            if column_list != sorted(column_list, reverse=True):
                sorting = False
            logger.info(column_list)
            logger.info(sorted(column_list, reverse=True))
            column_count += 1

            """Checking priority columns-->descending"""
            column_count = 3
            for i in range(3, 4):
                WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                    (By.XPATH,
                     "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                         i))))
                WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                                  "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                                                                      i))))
                time.sleep(3)
                obj = self.driver.find_element(By.XPATH,
                                               "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                   i))
                obj.click()
                WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                    (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")))
                obj1 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")
                time.sleep(1)
                obj1.click()
                WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable(
                    (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[3]/div[2]")))
                obj2 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[3]/div[2]")
                time.sleep(1)
                obj2.click()
                time.sleep(7)
                column_list = []

                for j in range(1, 101):
                    WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                                          "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                                                              j,
                                                                                                              column_count))))
                    column_list.append(self.driver.find_element(By.XPATH,
                                                                "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                    j, column_count)).text)
                if column_list != sorted(column_list, reverse=True):
                    sorting = False
                logger.info(column_list)
                logger.info(sorted(column_list, reverse=True))
                column_count += 1

            """Checking %complete columns-->descending"""
            column_count = 11
            for i in range(11, 12):
                WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                    (By.XPATH,
                     "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                         i))))
                WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                                  "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                                                                      i))))
                time.sleep(3)
                obj = self.driver.find_element(By.XPATH,
                                               "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                   i))
                obj.click()
                WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                    (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")))
                obj1 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")
                time.sleep(1)
                obj1.click()
                WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable(
                    (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[3]/div[2]")))
                obj2 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[3]/div[2]")
                time.sleep(1)
                obj2.click()
                time.sleep(7)
                column_list = []
                actual_column_list = []

                for j in range(1, 101):
                    WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                                          "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                                                              j,
                                                                                                              column_count))))
                    column_list.append(self.driver.find_element(By.XPATH,
                                                                "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                    j, column_count)).text)
                refined_column_list = re.findall(r'([\d,.]+)%', str(column_list))
                for k in refined_column_list:
                    actual_column_list.append(float(k.replace(",", "")))
                if actual_column_list != sorted(actual_column_list, reverse=True):
                    sorting = False
                logger.info(actual_column_list)
                logger.info(sorted(actual_column_list, reverse=True))
                column_count += 1

            """Checking time completed columns-->descending"""
            column_count = 10
            for i in range(10, 11):
                WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                    (By.XPATH,
                     "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                         i))))
                WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                                  "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                                                                      i))))
                time.sleep(3)
                obj = self.driver.find_element(By.XPATH,
                                               "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                   i))
                obj.click()
                WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                    (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")))
                obj1 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")
                time.sleep(1)
                obj1.click()
                WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable(
                    (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[3]/div[2]")))
                obj2 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[3]/div[2]")
                time.sleep(1)
                obj2.click()
                time.sleep(7)
                column_list = []
                actual_column_list = []

                for j in range(1, 101):
                    WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                                          "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                                                              j,
                                                                                                              column_count))))
                    column_list.append(self.driver.find_element(By.XPATH,
                                                                "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                    j, column_count)).text)
                refined_column_list = re.findall(r'(\d+\s)Days*', str(column_list))
                for k in refined_column_list:
                    actual_column_list.append(float(k.replace(",", "")))
                if actual_column_list != sorted(actual_column_list, reverse=True):
                    sorting = False
                logger.info(actual_column_list)
                logger.info(sorted(actual_column_list, reverse=True))
                column_count += 1

            """Checking incident id columns-->ascending"""
            column_count = 1
            for i in range(1, 2):
                WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                    (By.XPATH,
                     "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                         i))))
                WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                                  "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                                                                      i))))
                time.sleep(3)
                obj = self.driver.find_element(By.XPATH,
                                               "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                   i))
                obj.click()
                WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                    (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")))
                obj1 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")
                time.sleep(1)
                obj1.click()
                WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable(
                    (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[2]/div[2]")))
                obj2 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[2]/div[2]")
                time.sleep(1)
                obj2.click()
                time.sleep(7)
                column_list = []

                for j in range(1, 101):
                    WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                                          "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                                                              j,
                                                                                                              column_count))))
                    column_list.append(self.driver.find_element(By.XPATH,
                                                                "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                    j, column_count)).text)
                if column_list != sorted(column_list, reverse=False):
                    sorting = False
                logger.info(column_list)
                logger.info(sorted(column_list, reverse=False))
                column_count += 1

                """Checking priority columns-->ascending"""
                column_count = 3
                for i in range(3, 4):
                    WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                        (By.XPATH,
                         "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                             i))))
                    WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                                      "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                                                                          i))))
                    time.sleep(3)
                    obj = self.driver.find_element(By.XPATH,
                                                   "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                       i))
                    obj.click()
                    WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                        (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")))
                    obj1 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")
                    time.sleep(1)
                    obj1.click()
                    WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable(
                        (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[2]/div[2]")))
                    obj2 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[2]/div[2]")
                    time.sleep(1)
                    obj2.click()
                    time.sleep(7)
                    column_list = []

                    for j in range(1, 101):
                        WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                                              "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                                                                  j,
                                                                                                                  column_count))))
                        column_list.append(self.driver.find_element(By.XPATH,
                                                                    "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                        j, column_count)).text)
                    if column_list != sorted(column_list, reverse=False):
                        sorting = False
                    logger.info(column_list)
                    logger.info(sorted(column_list, reverse=False))
                    column_count += 1

                """Checking time completed columns-->ascending"""
                column_count = 10
                for i in range(10, 11):
                    WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                        (By.XPATH,
                         "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                             i))))
                    WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                                      "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                                                                          i))))
                    time.sleep(3)
                    obj = self.driver.find_element(By.XPATH,
                                                   "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                       i))
                    obj.click()
                    WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                        (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")))
                    obj1 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")
                    time.sleep(1)
                    obj1.click()
                    WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable(
                        (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[2]/div[2]")))
                    obj2 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[2]/div[2]")
                    time.sleep(1)
                    obj2.click()
                    time.sleep(7)
                    column_list = []
                    actual_column_list = []

                    for j in range(1, 101):
                        WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                                              "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                                                                  j,
                                                                                                                  column_count))))
                        column_list.append(self.driver.find_element(By.XPATH,
                                                                    "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                        j, column_count)).text)
                    refined_column_list = re.findall(r'(\d+\s)Days*', str(column_list))
                    for k in refined_column_list:
                        actual_column_list.append(float(k.replace(",", "")))
                    if actual_column_list != sorted(actual_column_list, reverse=False):
                        sorting = False
                    logger.info(actual_column_list)
                    logger.info(sorted(actual_column_list, reverse=False))
                    column_count += 1

                """Checking %complete columns-->ascending"""
                column_count = 11
                for i in range(11, 12):
                    WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                        (By.XPATH,
                         "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                             i))))
                    WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                                      "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                                                                          i))))
                    time.sleep(3)
                    obj = self.driver.find_element(By.XPATH,
                                                   "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                       i))
                    obj.click()
                    WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                        (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")))
                    obj1 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")
                    time.sleep(1)
                    obj1.click()
                    WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable(
                        (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[2]/div[2]")))
                    obj2 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[2]/div[2]")
                    time.sleep(1)
                    obj2.click()
                    time.sleep(7)
                    column_list = []
                    actual_column_list = []
                    for j in range(1, 101):
                        WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                                              "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                                                                  j,
                                                                                                                  column_count))))
                        column_list.append(self.driver.find_element(By.XPATH,
                                                                    "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                        j, column_count)).text)
                    refined_column_list = re.findall(r'([\d,.]+)%', str(column_list))
                    for k in refined_column_list:
                        actual_column_list.append(float(k.replace(",", "")))
                    if column_list != sorted(column_list, reverse=False):
                        sorting = False
                    logger.info(actual_column_list)
                    logger.info(sorted(actual_column_list, reverse=False))
                    column_count += 1

        self.driver.switch_to.window(window_before)

        return sorting

    def incident_sla_dashboard_main1(self, kwargs):
        logger.info("Execuitng smart_reporting()")
        """ Clicking on Application"""
        appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
        appl.click()

        """Clicking on Smart Reporting -> Smart Reporting Console"""
        smrtrep = self.driver.find_element_by_link_text('Smart Reporting')
        smrtrep.click()
        smrtrepcon = self.driver.find_element_by_link_text('Smart Reporting Console')
        """Clicking on smart reporting console and switchingg windows"""
        window_before = self.driver.window_handles[0]
        smrtrepcon.click()
        WebDriverWait(self.driver, 10).until(expected_conditions.number_of_windows_to_be(2))
        window_after = self.driver.window_handles[1]
        self.driver.switch_to.window(window_after)
        time.sleep(3)

        search_report = self.driver.find_element(By.XPATH,
                                                 '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/input')
        search_report.send_keys(kwargs['Report Name'])
        search_report.send_keys(Keys.ENTER)
        time.sleep(2)
        """opening H3G Folder"""
        h3gopfoler = self.driver.find_element_by_xpath("//div[@title='H3G Operational Reporting']")
        h3gopfoler.click()
        time.sleep(2)
        """Opening Rebus Reports Folder"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          "/html[1]/body[1]/form[1]/div[12]/div[1]/div[2]/div[4]/div[1]/div[2]/div[3]/div[1]/div[2]/div[8]/div[1]/div[1]")))
        maya_reports = self.driver.find_element(By.XPATH,
                                                "/html[1]/body[1]/form[1]/div[12]/div[1]/div[2]/div[4]/div[1]/div[2]/div[3]/div[1]/div[2]/div[8]/div[1]/div[1]")
        maya_reports.click()
        time.sleep(3)
        """Double-click on incident-sla-dashboard report"""
        incident_sla_dashboard = self.driver.find_element(By.XPATH,
                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div[2]')
        time.sleep(2)
        action = ActionChains(self.driver)
        action.double_click(incident_sla_dashboard)
        action.perform()
        time.sleep(5)

        """Checking Key-Scope columns-->descending"""
        logger.info("Checking Key-Scope columns-->descending")
        sorting = True
        column_count = 3
        for i in range(3, 4):
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                (By.XPATH,
                 "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                     i))))
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                                                                  i))))
            time.sleep(3)
            obj = self.driver.find_element(By.XPATH,
                                           "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                               i))
            obj.click()
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")))
            obj1 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")
            time.sleep(1)
            obj1.click()
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable(
                (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[3]/div[2]")))
            obj2 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[3]/div[2]")
            time.sleep(1)
            obj2.click()
            time.sleep(7)
            column_list = []
            actual_column_list = []
            for j in range(1, 3):
                WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                                      "//html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]/a[1]".format(
                                                                                                          j,
                                                                                                          column_count))))
                column_list.append(self.driver.find_element(By.XPATH,
                                                            "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]/a[1]".format(
                                                                j, column_count)).text)
            refined_column_list = re.findall(r"(\d+)", str(column_list))
            for k in refined_column_list:
                actual_column_list.append(float(k.replace(",", "")))
            if actual_column_list != sorted(actual_column_list, reverse=True):
                sorting = False
                logger.info("Keyscope descending failed")
            logger.info(actual_column_list)
            logger.info(sorted(actual_column_list, reverse=True))
            column_count += 1

        """Checking target and preference columns-->descending"""
        logger.info("Checking target and preference columns-->descending")
        column_count = 4
        for i in range(4, 6):
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                (By.XPATH,
                 "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                     i))))
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                                                                  i))))
            time.sleep(3)
            obj = self.driver.find_element(By.XPATH,
                                           "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                               i))
            obj.click()
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")))
            obj1 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")
            time.sleep(1)
            obj1.click()
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable(
                (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[3]/div[2]")))
            obj2 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[3]/div[2]")
            time.sleep(1)
            obj2.click()
            time.sleep(7)
            column_list = []
            actual_column_list = []
            for j in range(1, 3):
                WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                                      "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                                                          j,
                                                                                                          column_count))))
                column_list.append(self.driver.find_element(By.XPATH,
                                                            "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                j, column_count)).text)
            refined_column_list = re.findall(r"(\d+)", str(column_list))
            for k in refined_column_list:
                actual_column_list.append(float(k.replace(",", "")))
            if actual_column_list != sorted(actual_column_list, reverse=True):
                sorting = False
                logger.info("target and preference descending failed")
            logger.info(actual_column_list)
            logger.info(sorted(actual_column_list, reverse=True))
            column_count += 1

        """Checking SLA% columns-->descending"""
        logger.info("Checking SLA% columns-->descending")
        column_count = 10
        for i in range(10, 11):
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                (By.XPATH,
                 "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                     i))))
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                                                                  i))))
            time.sleep(3)
            obj = self.driver.find_element(By.XPATH,
                                           "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                               i))
            obj.click()
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")))
            obj1 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")
            time.sleep(1)
            obj1.click()
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable(
                (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[3]/div[2]")))
            obj2 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[3]/div[2]")
            time.sleep(1)
            obj2.click()
            time.sleep(7)
            column_list = []
            actual_column_list = []
            for j in range(1, 3):
                WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                                      "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                                                          j,
                                                                                                          column_count))))
                column_list.append(self.driver.find_element(By.XPATH,
                                                            "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                j, column_count)).text)
            refined_column_list = re.findall(r"(\d+)[.]", str(column_list))
            for k in refined_column_list:
                actual_column_list.append(float(k.replace(",", "")))
            if actual_column_list != sorted(actual_column_list, reverse=True):
                sorting = False
                logger.info("SLA% descending failed")
            logger.info(actual_column_list)
            logger.info(sorted(actual_column_list, reverse=True))
            column_count += 1

        """Checking SLA Ref# columns-->descending"""
        logger.info("Checking SLA Ref# columns-->descending")
        column_count = 1
        for i in range(1, 2):
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                (By.XPATH,
                 "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                     i))))
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                                                                  i))))
            time.sleep(3)
            obj = self.driver.find_element(By.XPATH,
                                           "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                               i))
            obj.click()
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")))
            obj1 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")
            time.sleep(1)
            obj1.click()
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable(
                (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[3]/div[2]")))
            obj2 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[3]/div[2]")
            time.sleep(1)
            obj2.click()
            time.sleep(7)
            column_list = []
            actual_column_list = []
            for j in range(1, 3):
                WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                                      "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                                                          j,
                                                                                                          column_count))))
                column_list.append(self.driver.find_element(By.XPATH,
                                                            "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                j, column_count)).text)
            refined_column_list = re.findall(r"(\d+)", str(column_list))
            for k in refined_column_list:
                actual_column_list.append(float(k.replace(",", "")))
            if actual_column_list != sorted(actual_column_list, reverse=True):
                sorting = False
                logger.info("SLA Ref# descending failed")
            logger.info(actual_column_list)
            logger.info(sorted(actual_column_list, reverse=True))
            column_count += 1

        """Checking pass, fail, total columns-->descending"""
        logger.info("Checking pass, fail, total columns-->descending")
        column_count = 7
        for i in range(7, 10):
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                (By.XPATH,
                 "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                     i))))
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                                                                  i))))
            time.sleep(3)
            obj = self.driver.find_element(By.XPATH,
                                           "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                               i))
            obj.click()
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")))
            obj1 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")
            time.sleep(1)
            obj1.click()
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable(
                (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[3]/div[2]")))
            obj2 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[3]/div[2]")
            time.sleep(1)
            obj2.click()
            time.sleep(7)
            column_list = []
            actual_column_list = []
            for j in range(1, 3):
                WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                                      "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                                                          j,
                                                                                                          column_count))))
                column_list.append(self.driver.find_element(By.XPATH,
                                                            "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                j, column_count)).text)
            logger.info("Column_list pass fail {}".format(column_list))
            refined_column_list = re.findall(r"(\d[,\d]+)", str(column_list))
            logger.info("refined column list: {}".format(refined_column_list))
            for k in refined_column_list:
                actual_column_list.append(float(k.replace(",", "")))
            if actual_column_list != sorted(actual_column_list, reverse=True):
                sorting = False
                logger.info("pass, fail, total descending failed")
            logger.info(actual_column_list)
            logger.info(sorted(actual_column_list, reverse=True))
            column_count += 1

        """Checking priority columns-->ascending"""
        logger.info("Checking priority columns-->ascending")
        column_count = 3
        for i in range(3, 4):
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                (By.XPATH,
                 "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                     i))))
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                                                                  i))))
            time.sleep(3)
            obj = self.driver.find_element(By.XPATH,
                                           "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                               i))
            obj.click()
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")))
            obj1 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")
            time.sleep(1)
            obj1.click()
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable(
                (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[2]/div[2]")))
            obj2 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[2]/div[2]")
            time.sleep(1)
            obj2.click()
            time.sleep(7)
            column_list = []
            actual_column_list = []
            for j in range(1, 3):
                WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                                      "//html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]/a[1]".format(
                                                                                                          j,
                                                                                                          column_count))))
                column_list.append(self.driver.find_element(By.XPATH,
                                                            "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]/a[1]".format(
                                                                j, column_count)).text)
            refined_column_list = re.findall(r"(\d+)", str(column_list))
            for k in refined_column_list:
                actual_column_list.append(float(k.replace(",", "")))
            if actual_column_list != sorted(actual_column_list, reverse=False):
                sorting = False
                logger.info("priority ascending failed")
            logger.info(actual_column_list)
            logger.info(sorted(actual_column_list, reverse=False))
            column_count += 1

        """Checking target and preference columns-->ascending"""
        logger.info("Checking target and preference columns-->ascending")
        column_count = 4
        for i in range(4, 6):
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                (By.XPATH,
                 "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                     i))))
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                                                                  i))))
            time.sleep(3)
            obj = self.driver.find_element(By.XPATH,
                                           "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                               i))
            obj.click()
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")))
            obj1 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")
            time.sleep(1)
            obj1.click()
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable(
                (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[2]/div[2]")))
            obj2 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[2]/div[2]")
            time.sleep(1)
            obj2.click()
            time.sleep(7)
            column_list = []
            actual_column_list = []
            for j in range(1, 3):
                WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                                      "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                                                          j,
                                                                                                          column_count))))
                column_list.append(self.driver.find_element(By.XPATH,
                                                            "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                j, column_count)).text)
            refined_column_list = re.findall(r"(\d+)", str(column_list))
            for k in refined_column_list:
                actual_column_list.append(float(k.replace(",", "")))
            if actual_column_list != sorted(actual_column_list, reverse=False):
                sorting = False
                logger.info("target and preference ascending failed")
            logger.info(actual_column_list)
            logger.info(sorted(actual_column_list, reverse=False))
            column_count += 1

        """Checking SLA% columns-->ascending"""
        logger.info("Checking SLA% columns-->ascending")
        column_count = 10
        for i in range(10, 11):
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                (By.XPATH,
                 "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                     i))))
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                                                                  i))))
            time.sleep(3)
            obj = self.driver.find_element(By.XPATH,
                                           "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                               i))
            obj.click()
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")))
            obj1 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")
            time.sleep(1)
            obj1.click()
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable(
                (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[2]/div[2]")))
            obj2 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[2]/div[2]")
            time.sleep(1)
            obj2.click()
            time.sleep(7)
            column_list = []
            actual_column_list = []
            for j in range(1, 3):
                WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                                      "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                                                          j,
                                                                                                          column_count))))
                column_list.append(self.driver.find_element(By.XPATH,
                                                            "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                j, column_count)).text)
            refined_column_list = re.findall(r"(\d+)[.]", str(column_list))
            for k in refined_column_list:
                actual_column_list.append(float(k.replace(",", "")))
            if actual_column_list != sorted(actual_column_list, reverse=False):
                sorting = False
                logger.info("SLA% ascending failed")
            logger.info(actual_column_list)
            logger.info(sorted(actual_column_list, reverse=False))
            column_count += 1

        """Checking pass, fail, total columns-->ascending"""
        logger.info("Checking pass, fail, total columns-->ascending")
        column_count = 7
        for i in range(7, 10):
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                (By.XPATH,
                 "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                     i))))
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                                                                  i))))
            time.sleep(3)
            obj = self.driver.find_element(By.XPATH,
                                           "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                               i))
            obj.click()
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")))
            obj1 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")
            time.sleep(1)
            obj1.click()
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable(
                (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[2]/div[2]")))
            obj2 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[2]/div[2]")
            time.sleep(1)
            obj2.click()
            time.sleep(7)
            column_list = []
            actual_column_list = []
            for j in range(1, 3):
                WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                                      "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                                                          j,
                                                                                                          column_count))))
                column_list.append(self.driver.find_element(By.XPATH,
                                                            "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                j, column_count)).text)
            refined_column_list = re.findall(r"(\d[,\d]+)", str(column_list))
            for k in refined_column_list:
                actual_column_list.append(float(k.replace(",", "")))
            if actual_column_list != sorted(actual_column_list, reverse=False):
                sorting = False
                logger.info("pass, fail, total ascending failed")
            logger.info(actual_column_list)
            logger.info(sorted(actual_column_list, reverse=False))
            column_count += 1

        """Checking SLA Ref# columns-->ascending"""
        logger.info("Checking SLA Ref# columns-->ascending")
        column_count = 1
        for i in range(1, 2):
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                (By.XPATH,
                 "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                     i))))
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                                                                  i))))
            time.sleep(3)
            obj = self.driver.find_element(By.XPATH,
                                           "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                               i))
            obj.click()
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")))
            obj1 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")
            time.sleep(1)
            obj1.click()
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable(
                (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[2]/div[2]")))
            obj2 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[2]/div[2]")
            time.sleep(1)
            obj2.click()
            time.sleep(7)
            column_list = []
            actual_column_list = []
            for j in range(1, 3):
                WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                                      "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                                                          j,
                                                                                                          column_count))))
                column_list.append(self.driver.find_element(By.XPATH,
                                                            "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                j, column_count)).text)
            refined_column_list = re.findall(r"(\d+)", str(column_list))

            for k in refined_column_list:
                actual_column_list.append(float(k.replace(",", "")))
            if actual_column_list != sorted(actual_column_list, reverse=False):
                sorting = False
                logger.info("SLA# ascending failed")
            logger.info(actual_column_list)
            logger.info(sorted(actual_column_list, reverse=False))
            column_count += 1

        self.driver.switch_to.window(window_before)
        return sorting

    def incident_sla_dashboard_main2(self, kwargs):
        logger.info("Execuitng smart_reporting()")
        """ Clicking on Application"""
        appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
        appl.click()

        """Clicking on Smart Reporting -> Smart Reporting Console"""
        smrtrep = self.driver.find_element_by_link_text('Smart Reporting')
        smrtrep.click()
        smrtrepcon = self.driver.find_element_by_link_text('Smart Reporting Console')
        """Clicking on smart reporting console and switchingg windows"""
        window_before = self.driver.window_handles[0]
        smrtrepcon.click()
        WebDriverWait(self.driver, 10).until(expected_conditions.number_of_windows_to_be(2))
        window_after = self.driver.window_handles[1]
        self.driver.switch_to.window(window_after)
        time.sleep(3)

        search_report = self.driver.find_element(By.XPATH,
                                                 '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/input')
        search_report.send_keys(kwargs['Report Name'])
        search_report.send_keys(Keys.ENTER)
        """opening H3G Folder"""
        h3gopfoler = self.driver.find_element_by_xpath("//div[@title='H3G Operational Reporting']")
        h3gopfoler.click()
        """Opening Rebus Reports Folder"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          "/html[1]/body[1]/form[1]/div[12]/div[1]/div[2]/div[4]/div[1]/div[2]/div[3]/div[1]/div[2]/div[8]/div[1]/div[1]")))
        maya_reports = self.driver.find_element(By.XPATH,
                                                "/html[1]/body[1]/form[1]/div[12]/div[1]/div[2]/div[4]/div[1]/div[2]/div[3]/div[1]/div[2]/div[8]/div[1]/div[1]")
        maya_reports.click()
        time.sleep(3)
        """Double-click on incident-sla-dashboard report"""
        incident_sla_dashboard = self.driver.find_element(By.XPATH,
                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div[2]')
        time.sleep(2)
        action = ActionChains(self.driver)
        action.double_click(incident_sla_dashboard)
        action.perform()
        time.sleep(5)
        """Getting the names of the columns"""
        column_list = []
        for i in range(1, 11):
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                                  '/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/div[1]'.format(
                                                                                                      i))))
            column_list.append(self.driver.find_element(By.XPATH,
                                                        '/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/div[1]'.format(
                                                            i)).text)
        column_names = ", ".join(column_list)
        logger.info(column_names)
        self.driver.switch_to.window(window_before)
        matching = True
        if column_names != kwargs['Column_names']:
            matching = False
        return matching

    def incident_volumes_by_support_group_per_priorities_main(self, kwargs):
        logger.info("Execuitng smart_reporting()")
        """ Clicking on Application"""
        appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
        appl.click()

        """Clicking on Smart Reporting -> Smart Reporting Console"""
        smrtrep = self.driver.find_element_by_link_text('Smart Reporting')
        smrtrep.click()
        smrtrepcon = self.driver.find_element_by_link_text('Smart Reporting Console')
        """Clicking on smart reporting console and switchingg windows"""
        window_before = self.driver.window_handles[0]
        smrtrepcon.click()
        WebDriverWait(self.driver, 10).until(expected_conditions.number_of_windows_to_be(2))
        window_after = self.driver.window_handles[1]
        self.driver.switch_to.window(window_after)
        time.sleep(3)

        search_report = self.driver.find_element(By.XPATH,
                                                 '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/input')
        search_report.send_keys(kwargs['Report Name'])
        search_report.send_keys(Keys.ENTER)
        time.sleep(2)
        """opening H3G Folder"""
        h3gopfoler = self.driver.find_element_by_xpath("//div[@title='H3G Operational Reporting']")
        time.sleep(2)
        h3gopfoler.click()
        time.sleep(3)
        """Opening Rebus Reports Folder"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          "/html[1]/body[1]/form[1]/div[12]/div[1]/div[2]/div[4]/div[1]/div[2]/div[3]/div[1]/div[2]/div[8]/div[1]/div[1]")))
        maya_reports = self.driver.find_element(By.XPATH,
                                                "/html[1]/body[1]/form[1]/div[12]/div[1]/div[2]/div[4]/div[1]/div[2]/div[3]/div[1]/div[2]/div[8]/div[1]/div[1]")
        maya_reports.click()
        time.sleep(3)
        """Taking screen-shot"""
        self.driver.get_screenshot_as_file('C:\GIT\output\ITSM_REBUS Reporting_079_1.png')
        """Double-click on incident-sla-dashboard report"""
        incident_sla_dashboard = self.driver.find_element(By.XPATH,
                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div[2]')
        time.sleep(2)
        action = ActionChains(self.driver)
        action.double_click(incident_sla_dashboard)
        action.perform()
        time.sleep(10)
        self.driver.get_screenshot_as_file('C:\GIT\output\ITSM_REBUS Reporting_079_2.png')
        """Getting the text of the table name"""
        WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
            (By.XPATH, '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[1]/div/div/div/div[1]/table/tbody/tr[1]/td')))
        table_title1 = self.driver.find_element(By.XPATH, '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[1]/div/div/div/div[1]/table/tbody/tr[1]/td').text
        logger.info("Table title1: {}".format(table_title1))
        WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
            (By.XPATH, '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[2]/table/tbody/tr[1]/td/div/div/div/div[1]/table/tbody/tr[1]/td')))
        table_title2 = self.driver.find_element(By.XPATH, '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[2]/table/tbody/tr[1]/td/div/div/div/div[1]/table/tbody/tr[1]/td').text
        logger.info("Table title2: {}".format(table_title2))
        WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
            (By.XPATH, '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[2]/table/tbody/tr[2]/td/div/div/div/div[1]/table/tbody/tr[1]/td')))
        table_title3 = self.driver.find_element(By.XPATH, '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[2]/table/tbody/tr[2]/td/div/div/div/div[1]/table/tbody/tr[1]/td').text
        logger.info("Table title3: {}".format(table_title3))
        self.driver.switch_to.window(window_before)
        Matching = True
        if table_title1 != kwargs['Table_title1']:
            Matching = False
        if table_title2 != kwargs['Table_title2']:
            Matching = False
        if table_title3 != kwargs['Table_title3']:
            Matching = False
        return Matching

    def incident_volumes_by_support_group_per_priorities_main1(self, kwargs):
        logger.info("Execuitng smart_reporting()")
        """ Clicking on Application"""
        appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
        appl.click()

        """Clicking on Smart Reporting -> Smart Reporting Console"""
        smrtrep = self.driver.find_element_by_link_text('Smart Reporting')
        smrtrep.click()
        smrtrepcon = self.driver.find_element_by_link_text('Smart Reporting Console')
        """Clicking on smart reporting console and switchingg windows"""
        window_before = self.driver.window_handles[0]
        smrtrepcon.click()
        WebDriverWait(self.driver, 10).until(expected_conditions.number_of_windows_to_be(2))
        window_after = self.driver.window_handles[1]
        self.driver.switch_to.window(window_after)
        time.sleep(3)

        search_report = self.driver.find_element(By.XPATH,
                                                 '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/input')
        search_report.send_keys(kwargs['Report Name'])
        search_report.send_keys(Keys.ENTER)
        time.sleep(2)
        """opening H3G Folder"""
        h3gopfoler = self.driver.find_element_by_xpath("//div[@title='H3G Operational Reporting']")
        time.sleep(2)
        h3gopfoler.click()
        time.sleep(3)
        """Taking Screen shot"""
        self.driver.get_screenshot_as_file('C:\GIT\output\ITSM_REBUS Reporting_080_1.png')
        """Opening Rebus Reports Folder"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          "/html[1]/body[1]/form[1]/div[12]/div[1]/div[2]/div[4]/div[1]/div[2]/div[3]/div[1]/div[2]/div[8]/div[1]/div[1]")))
        maya_reports = self.driver.find_element(By.XPATH,
                                                "/html[1]/body[1]/form[1]/div[12]/div[1]/div[2]/div[4]/div[1]/div[2]/div[3]/div[1]/div[2]/div[8]/div[1]/div[1]")
        maya_reports.click()
        time.sleep(3)
        """Double-click on incident-sla-dashboard report"""
        incident_sla_dashboard = self.driver.find_element(By.XPATH,
                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div[2]')
        time.sleep(2)
        action = ActionChains(self.driver)
        action.double_click(incident_sla_dashboard)
        action.perform()
        time.sleep(10)
        """Taking Screen Shot"""
        self.driver.get_screenshot_as_file('C:\GIT\output\ITSM_REBUS Reporting_080_2.png')

        """Getting the list of the columns for Incident Volumes (by Support Group per Priorities)"""
        column_list = []
        for i in range(1, 4):
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                (By.XPATH, "//div[@class='rptdata rpt183163f{}']".format(i))))
            column_list.append(self.driver.find_element(By.XPATH, "//div[@class='rptdata rpt183163f{}']".format(i)).text)
        column_names = ", ".join(column_list)
        logger.info(column_names)
        matching = True
        if column_names != kwargs['Table_1_columns']:
            matching = False

        """Getting the list of the columns for Incident Volumes (by Support Group per Priorities) - Resolved"""
        column_list = []
        for i in range(1, 4):
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                (By.XPATH, "//div[@class='rptdata rpt183206f{}']".format(i))))
            column_list.append(self.driver.find_element(By.XPATH, "//div[@class='rptdata rpt183206f{}']".format(i)).text)
        column_names = ", ".join(column_list)
        logger.info(column_names)
        if column_names != kwargs['Table_2_columns']:
            matching = False

        """Getting the list of the columns for Incident Volumes (by Support Group per Priorities) - Backlog"""
        column_list = []
        for i in range(1, 4):
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                (By.XPATH, "//div[@class='rptdata rpt183218f{}']".format(i))))
            column_list.append(self.driver.find_element(By.XPATH, "//div[@class='rptdata rpt183218f{}']".format(i)).text)
        column_names = ", ".join(column_list)
        logger.info(column_names)
        if column_names != kwargs['Table_3_columns']:
            matching = False
        self.driver.switch_to.window(window_before)
        return matching

    def verify_incident_volumes_by_priority_smart_reporting_displays(self, kwargs):
        time.sleep(0)
        logger.info("Executing verify_incident_volumes_by_priority_smart_reporting_displays()")
        """ScreenShot - Taken"""
        self.driver.get_screenshot_as_file('C:/Users/sparsh/Desktop/New folder (2)/screenshot1.png')

        logger.info("Execuitng verify_incident_volumes()")
        window_before = self.driver.window_handles[0]
        """ Clicking on Application"""
        appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
        appl.click()

        """Clicking on Smart Reporting -> Smart Reporting Console"""
        smrtrep = self.driver.find_element_by_link_text('Smart Reporting')
        smrtrep.click()
        smrtrepcon = self.driver.find_element_by_link_text('Smart Reporting Console')
        smrtrepcon.click()

        # WebDriverWait(self.driver, 10).until(expected_conditions.number_of_windows_to_be(2))
        time.sleep(6)
        window_after = self.driver.window_handles[1]
        self.driver.switch_to.window(window_after)

        """ScreenShot - Taken"""
        self.driver.get_screenshot_as_file('C:/Users/sparsh/Desktop/New folder (2)/screenshot2.png')

        # time.sleep(14)
        """All already clicked"""
        """Click H3G"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')))
        obj_h3g = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')
        obj_h3g.click()
        """click on Rebus Reports"""
        obj_rebus = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[2]/div[8]/div/div/div/div[2]')
        obj_rebus.click()

        time.sleep(8)
        """Search content"""
        send_repo = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/input')  # search field
        send_repo.send_keys(kwargs['report_name'])
        time.sleep(5)
        search_icon = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/div[2]/div[2]/img')  # search icon
        search_icon.click()

        time.sleep(10)
        """ScreenShot - Taken"""
        self.driver.get_screenshot_as_file('C:/Users/sparsh/Desktop/New folder (2)/screenshot3.png')

        """Double clicking on report"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div[2]')))
        repo = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div[2]')
        action = ActionChains(self.driver)
        action.double_click(repo).perform()

        time.sleep(10)
        """ScreenShot - Taken"""
        self.driver.get_screenshot_as_file('C:/Users/sparsh/Desktop/New folder (2)/screenshot4.png')

        """Verify if smart reporting displays"""

        """Verify if smart reporting upper displays"""
        report_display_upper = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[1]/table/tbody/tr[1]/td').text
        # logger.info("display up - {}".format(report_display_upper))
        # logger.info("kawrgs up - {}".format(kwargs['report_display_upper']))

        """Verify if smart reporting lower displays"""
        report_display_lower = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[1]/table/tbody/tr[2]/td').text
        # logger.info("display lower - {}".format(report_display_lower))
        # logger.info("kawrgs up - {}".format(kwargs['report_display_lower']))

        smart_reporting_display_status = True

        if report_display_upper != kwargs['report_display_upper']:
            smart_reporting_display_status = False
        elif report_display_lower != kwargs['report_display_lower']:
            smart_reporting_display_status = False

        if smart_reporting_display_status == False:
            logger.info("Failed - Smart reporting displays are Failed to match.")
        else:
            logger.info("Passed - Smart reporting displays are matched.")

        return smart_reporting_display_status

    def verify_problem_Volumetric_smart_reporting_displays(self, kwargs):
        logger.info("Execuitng verify_incident_backlog_smart_reporting_displays()")
        window_before = self.driver.window_handles[0]

        self.driver.get_screenshot_as_file('C:/Users/sparsh/Desktop/New folder (2)/screenshot0.png')
        """ Clicking on Application"""
        appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
        appl.click()
        """Clicking on Smart Reporting -> Smart Reporting Console"""
        smrtrep = self.driver.find_element_by_link_text('Smart Reporting')
        smrtrep.click()
        smrtrepcon = self.driver.find_element_by_link_text('Smart Reporting Console')
        smrtrepcon.click()
        time.sleep(6)
        window_after = self.driver.window_handles[1]
        self.driver.switch_to.window(window_after)

        time.sleep(14)

        """ScreenShot - Taken"""
        self.driver.get_screenshot_as_file('C:/Users/sparsh/Desktop/New folder (2)/screenshot1.png')

        """All already clicked"""
        """Click H3G"""
        obj_h3g = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')
        obj_h3g.click()
        """click on Rebus Reports"""
        obj_rebus = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[2]/div[8]/div/div/div/div[2]')
        obj_rebus.click()

        """Search content"""
        send_repo = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/input')
        send_repo.send_keys(kwargs['Report_name'])

        search_icon = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/div[2]/div[2]/img')
        search_icon.click()

        """ScreenShot - Taken"""
        self.driver.get_screenshot_as_file('C:/Users/sparsh/Desktop/New folder (2)/screenshot2.png')

        time.sleep(2)
        """Double clicking on report"""
        repo = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div[2]')
        action = ActionChains(self.driver)
        action.double_click(repo).perform()

        time.sleep(7)
        """ScreenShot - Taken"""
        self.driver.get_screenshot_as_file('C:/Users/sparsh/Desktop/New folder (2)/screenshot3.png')

        """Verify report name"""
        report_name1 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[1]/table/tbody/tr[1]/td').text
        report_name2 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[1]/table/tbody/tr[1]/td').text
        """Verify if smart reporting upper 1 displays"""
        c1 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[1]/div').text
        c2 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[2]/div').text
        c3 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[3]/div').text
        c4 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[4]/div').text
        c5 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[5]/div').text
        c6 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[6]/div').text
        c7 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[7]/div').text
        c8 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[8]/div').text
        c9 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[9]/div').text
        c10 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[10]/div').text
        c11 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[11]/div').text
        c12 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[2]/div/table/thead/tr/td[1]/div').text
        c13 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[2]/div/table/thead/tr/td[2]/div').text
        c14 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[2]/div/table/thead/tr/td[3]/div').text
        c15 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[2]/div/table/thead/tr/td[4]/div').text
        c16 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[2]/div/table/thead/tr/td[5]/div').text
        c17 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[2]/div/table/thead/tr/td[6]/div').text
        c18 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[2]/div/table/thead/tr/td[7]/div').text
        c19 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[2]/div/table/thead/tr/td[8]/div').text
        c20 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[2]/div/table/thead/tr/td[9]/div').text
        c21 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[2]/div/table/thead/tr/td[10]/div').text
        c22 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[2]/div/table/thead/tr/td[11]/div').text

        """Verify if smart reporting displays the mentioned reports"""
        smart_reporting_display_status = True

        if c1 != kwargs['c1']:
            smart_reporting_display_status = False
        elif c2 != kwargs['c2']:
            smart_reporting_display_status = False
        elif c3 != kwargs['c3']:
            smart_reporting_display_status = False
        elif c4 != kwargs['c4']:
            smart_reporting_display_status = False
        elif c5 != kwargs['c5']:
            smart_reporting_display_status = False
        elif c6 != kwargs['c6']:
            smart_reporting_display_status = False
        elif c7 != kwargs['c7']:
            smart_reporting_display_status = False
        elif c8 != kwargs['c8']:
            smart_reporting_display_status = False
        elif c9 != kwargs['c9']:
            smart_reporting_display_status = False
        elif c10 != kwargs['c10']:
            smart_reporting_display_status = False
        elif c11 != kwargs['c11']:
            smart_reporting_display_status = False
        elif c12 != kwargs['c12']:
            smart_reporting_display_status = False
        elif c13 != kwargs['c13']:
            smart_reporting_display_status = False
        elif c14 != kwargs['c14']:
            smart_reporting_display_status = False
        elif c15 != kwargs['c15']:
            smart_reporting_display_status = False
        elif c16 != kwargs['c16']:
            smart_reporting_display_status = False
        elif c17 != kwargs['c17']:
            smart_reporting_display_status = False
        elif c18 != kwargs['c18']:
            smart_reporting_display_status = False
        elif c19 != kwargs['c19']:
            smart_reporting_display_status = False
        elif c20 != kwargs['c20']:
            smart_reporting_display_status = False
        elif c21 != kwargs['c21']:
            smart_reporting_display_status = False
        elif c22 != kwargs['c22']:
            smart_reporting_display_status = False

        if smart_reporting_display_status == False:
            logger.info("Failed - Smart reporting displays are Failed to match")
        else:
            logger.info("Passed - Smart reporting displays are matched")

        return smart_reporting_display_status

    def verify_change_sla_dashboard(self, kwargs):

        """ScreenShot - Taken"""
        self.driver.get_screenshot_as_file(
            'C:\Users\karsg\Desktop\Automation\screenshots\Reports\changesla\ss1.png')

        logger.info("Execuitng verify_verify_change_sla_dashboard()")
        window_before = self.driver.window_handles[0]
        """ Clicking on Application"""
        appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
        appl.click()

        """Clicking on Smart Reporting -> Smart Reporting Console"""
        smrtrep = self.driver.find_element_by_link_text('Smart Reporting')
        smrtrep.click()
        smrtrepcon = self.driver.find_element_by_link_text('Smart Reporting Console')
        smrtrepcon.click()

        # WebDriverWait(self.driver, 10).until(expected_conditions.number_of_windows_to_be(2))
        time.sleep(6)
        window_after = self.driver.window_handles[1]
        self.driver.switch_to.window(window_after)

        """ScreenShot - Taken"""
        self.driver.get_screenshot_as_file(
            'C:\Users\karsg\Desktop\Automation\screenshots\Reports\changesla\ss2.png')

        # time.sleep(14)
        """All already clicked"""
        """Click H3G"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')))
        obj_h3g = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')
        obj_h3g.click()
        """click on Rebus Reports"""
        obj_rebus = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[2]/div[8]/div/div/div/div[2]')
        obj_rebus.click()

        """Search content"""
        send_repo = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/input')  # search field
        send_repo.send_keys(kwargs['reportname1'])
        time.sleep(2)
        search_icon = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/div[2]/div[2]/img')  # search icon
        search_icon.click()

        time.sleep(5)
        """ScreenShot - Taken"""
        self.driver.get_screenshot_as_file(
            'C:\Users\karsg\Desktop\Automation\screenshots\Reports\changesla\ss3.png')

        """Double clicking on report"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div[2]')))
        repo = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div[2]')
        action = ActionChains(self.driver)
        action.double_click(repo).perform()

        time.sleep(10)
        """ScreenShot - Taken"""
        self.driver.get_screenshot_as_file(
            'C:\Users\karsg\Desktop\Automation\screenshots\Reports\changesla\ss4.png')

        """Verify if the mentioned names & columns are available in the reports as in requirement sheet"""

        WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[1]/table/tbody/tr[1]/td')))

        reportname1 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[1]/table/tbody/tr[1]/td').text
        logger.info("Report Name =  {}".format(reportname1))
        reportname12 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[1]/table/tbody/tr[2]/td').text
        logger.info("Report Name =  {}".format(reportname12))
        slaref = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[2]/div/table/thead/tr/td[1]/div').text
        logger.info("Column01 =  {}".format(slaref))
        slametname = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[2]/div/table/thead/tr/td[2]/div').text
        logger.info("Column02 =  {}".format(slametname))
        perf = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[2]/div/table/thead/tr/td[3]/div').text
        logger.info("Column03 =  {}".format(perf))
        pas = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[2]/div/table/thead/tr/td[4]/div').text
        logger.info("Column04 =  {}".format(pas))
        fail = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[2]/div/table/thead/tr/td[5]/div').text
        logger.info("Column05 =  {}".format(fail))
        total = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[2]/div/table/thead/tr/td[6]/div').text
        logger.info("Column06 =  {}".format(total))
        slapercent = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[2]/div/table/thead/tr/td[7]/div').text
        logger.info("Column07 =  {}".format(slapercent))

        reportname2 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[1]/table/tbody/tr[1]/td').text
        logger.info("Table2 Report Name =  {}".format(reportname2))
        reportname22 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[1]/table/tbody/tr[2]/td').text
        logger.info("Table2 Report Name =  {}".format(reportname22))
        slaref1 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[2]/div/table/thead/tr/td[1]/div').text
        logger.info("Table2 Column01 =  {}".format(slaref1))
        slametname1 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[2]/div/table/thead/tr/td[2]/div').text
        logger.info("Table2 Column02 =  {}".format(slametname1))
        perf1 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[2]/div/table/thead/tr/td[3]/div').text
        logger.info("Table2 Column03 =  {}".format(perf1))
        pas1 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[2]/div/table/thead/tr/td[4]/div').text
        logger.info("Table2 Column04 =  {}".format(pas1))
        fail1 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[2]/div/table/thead/tr/td[5]/div').text
        logger.info("Table2 Column05 =  {}".format(fail1))
        total1 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[2]/div/table/thead/tr/td[6]/div').text
        logger.info("Table2 Column06 =  {}".format(total1))
        slapercent1 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[2]/div/table/thead/tr/td[7]/div').text
        logger.info("Table2 Column07 =  {}".format(slapercent1))

        columns_name_status = True
        if reportname1 != kwargs['reportname1']:
            columns_name_status = False
        elif reportname12 != kwargs['reportname12']:
            columns_name_status = False
        elif reportname2 != kwargs['reportname2']:
            columns_name_status = False
        elif reportname22 != kwargs['reportname22']:
            columns_name_status = False
        elif slaref != kwargs['slaref']:
            columns_name_status = False
        elif slametname != kwargs['slametname']:
            columns_name_status = False
        elif perf != kwargs['perf']:
            columns_name_status = False
        elif pas != kwargs['pas']:
            columns_name_status = False
        elif fail != kwargs['fail']:
            columns_name_status = False
        elif total != kwargs['total']:
            columns_name_status = False
        elif slapercent != kwargs['slapercent']:
            columns_name_status = False
        elif slaref1 != kwargs['slaref1']:
            columns_name_status = False
        elif slametname1 != kwargs['slametname1']:
            columns_name_status = False
        elif perf1 != kwargs['perf1']:
            columns_name_status = False
        elif pas1 != kwargs['pas1']:
            columns_name_status = False
        elif fail1 != kwargs['fail1']:
            columns_name_status = False
        elif total1 != kwargs['total1']:
            columns_name_status = False
        elif slapercent1 != kwargs['slapercent1']:
            columns_name_status = False

        if columns_name_status == False:
            logger.info(
                "Failed - The mentioned Report name & columns are not available in the reports as in requirement")
        else:
            logger.info(
                "Passed - The mentioned Report name & columns are available in the reports as in requirement")

        return columns_name_status

    def verify_active_changes_for_possible_sla_breach(self, kwargs):
        logger.info("Execuitng verify_active_changes_for_possible_sla_breach()")
        time.sleep(0)
        """ScreenShot - Taken"""
        self.driver.get_screenshot_as_file(
            'C:\Users\karsg\Desktop\Automation\screenshots\Reports\Active_changes/ss1.png')

        logger.info("Execuitng verify_active_changes_for_possible_sla_breach()")
        window_before = self.driver.window_handles[0]
        """ Clicking on Application"""
        appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
        appl.click()

        """Clicking on Smart Reporting -> Smart Reporting Console"""
        smrtrep = self.driver.find_element_by_link_text('Smart Reporting')
        smrtrep.click()
        smrtrepcon = self.driver.find_element_by_link_text('Smart Reporting Console')
        smrtrepcon.click()

        # WebDriverWait(self.driver, 10).until(expected_conditions.number_of_windows_to_be(2))
        time.sleep(6)
        window_after = self.driver.window_handles[1]
        self.driver.switch_to.window(window_after)

        """ScreenShot - Taken"""
        self.driver.get_screenshot_as_file(
            'C:\Users\karsg\Desktop\Automation\screenshots\Reports\Active_changes/ss2.png')

        # time.sleep(14)
        """All already clicked"""
        """Click H3G"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')))
        obj_h3g = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')
        obj_h3g.click()
        """click on Rebus Reports"""
        obj_rebus = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[2]/div[8]/div/div/div/div[2]')
        obj_rebus.click()

        """Search content"""
        send_repo = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/input')  # search field
        send_repo.send_keys(kwargs['reportname'])

        search_icon = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/div[2]/div[2]/img')  # search icon
        search_icon.click()

        time.sleep(5)
        """ScreenShot - Taken"""
        self.driver.get_screenshot_as_file(
            'C:\Users\karsg\Desktop\Automation\screenshots\Reports\Active_changes/ss3.png')

        """Double clicking on report"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div[2]')))
        repo = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div[2]')
        action = ActionChains(self.driver)
        action.double_click(repo).perform()

        time.sleep(10)
        """ScreenShot - Taken"""
        self.driver.get_screenshot_as_file(
            'C:\Users\karsg\Desktop\Automation\screenshots\Reports\Active_changes/ss4.png')

        """Verify if the mentioned names & columns are available in the reports as in requirement sheet"""

        WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[1]/table/tbody/tr[1]/td')))

        reportname = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[1]/table/tbody/tr[1]/td').text
        logger.info("Report Name =  {}".format(reportname))
        chg = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[1]/div').text
        logger.info("Column01 =  {}".format(chg))
        slametname = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[2]/div').text
        logger.info("Column02 =  {}".format(slametname))
        hasbreach = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[3]/div').text
        logger.info("Column03 =  {}".format(hasbreach))
        chgstatus = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[4]/div').text
        logger.info("Column04 =  {}".format(chgstatus))
        chgclass = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[5]/div').text
        logger.info("Column05 =  {}".format(chgclass))
        noofp0p3inc = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[6]/div').text
        logger.info("Column06 =  {}".format(noofp0p3inc))
        compdatetime = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[7]/div').text
        logger.info("Column07 =  {}".format(compdatetime))
        targclosedate = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[8]/div').text
        logger.info("Column08 =  {}".format(targclosedate))
        closedatetime = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[9]/div').text
        logger.info("Column09 =  {}".format(closedatetime))
        assigneegrp = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[10]/div').text
        logger.info("Column10 =  {}".format(assigneegrp))
        assignee = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[11]/div').text
        logger.info("Column11 =  {}".format(assignee))
        chgmgr = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[12]/div').text
        logger.info("Column12 =  {}".format(chgmgr))
        chgsummary = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[13]/div').text
        logger.info("Column13 =  {}".format(chgsummary))

        columns_name_status = True
        if reportname != kwargs['reportname']:
            columns_name_status = False
        elif chg != kwargs['chg']:
            columns_name_status = False
        elif slametname != kwargs['slametname']:
            columns_name_status = False
        elif hasbreach != kwargs['hasbreach']:
            columns_name_status = False
        elif chgstatus != kwargs['chgstatus']:
            columns_name_status = False
        elif chgclass != kwargs['chgclass']:
            columns_name_status = False
        elif noofp0p3inc != kwargs['noofp0p3inc']:
            columns_name_status = False
        elif compdatetime != kwargs['compdatetime']:
            columns_name_status = False
        elif targclosedate != kwargs['targclosedate']:
            columns_name_status = False
        elif closedatetime != kwargs['closedatetime']:
            columns_name_status = False
        elif assigneegrp != kwargs['assigneegrp']:
            columns_name_status = False
        elif assignee != kwargs['assignee']:
            columns_name_status = False
        elif chgmgr != kwargs['chgmgr']:
            columns_name_status = False
        elif chgsummary != kwargs['chgsummary']:
            columns_name_status = False

        if columns_name_status == False:
            logger.info(
                "Failed - The mentioned Report name & columns are not available in the reports as in requirement")
        else:
            logger.info("Passed - The mentioned Report name & columns are available in the reports as in requirement")

        return columns_name_status

    def verify_change_sla_dashboard(self, kwargs):

        """ScreenShot - Taken"""
        self.driver.get_screenshot_as_file('C:\Users\karsg\Desktop\Automation\screenshots\Reports\changesla\ss1.png')

        logger.info("Execuitng verify_verify_change_sla_dashboard()")
        window_before = self.driver.window_handles[0]
        """ Clicking on Application"""
        appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
        appl.click()

        """Clicking on Smart Reporting -> Smart Reporting Console"""
        smrtrep = self.driver.find_element_by_link_text('Smart Reporting')
        smrtrep.click()
        smrtrepcon = self.driver.find_element_by_link_text('Smart Reporting Console')
        smrtrepcon.click()

        # WebDriverWait(self.driver, 10).until(expected_conditions.number_of_windows_to_be(2))
        time.sleep(6)
        window_after = self.driver.window_handles[1]
        self.driver.switch_to.window(window_after)

        """ScreenShot - Taken"""
        self.driver.get_screenshot_as_file('C:\Users\karsg\Desktop\Automation\screenshots\Reports\changesla\ss2.png')

        # time.sleep(14)
        """All already clicked"""
        """Click H3G"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')))
        obj_h3g = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')
        obj_h3g.click()
        """click on Rebus Reports"""
        obj_rebus = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[2]/div[8]/div/div/div/div[2]')
        obj_rebus.click()

        """Search content"""
        send_repo = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/input')  # search field
        send_repo.send_keys(kwargs['reportname1'])
        time.sleep(2)
        search_icon = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/div[2]/div[2]/img')  # search icon
        search_icon.click()

        time.sleep(5)
        """ScreenShot - Taken"""
        self.driver.get_screenshot_as_file('C:\Users\karsg\Desktop\Automation\screenshots\Reports\changesla\ss3.png')

        """Double clicking on report"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div[2]')))
        repo = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div[2]')
        action = ActionChains(self.driver)
        action.double_click(repo).perform()

        time.sleep(10)
        """ScreenShot - Taken"""
        self.driver.get_screenshot_as_file('C:\Users\karsg\Desktop\Automation\screenshots\Reports\changesla\ss4.png')

        """Verify if the mentioned names & columns are available in the reports as in requirement sheet"""

        WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[1]/table/tbody/tr[1]/td')))

        reportname1 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[1]/table/tbody/tr[1]/td').text
        logger.info("Report Name =  {}".format(reportname1))
        reportname12 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[1]/table/tbody/tr[2]/td').text
        logger.info("Report Name =  {}".format(reportname12))
        slaref = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[2]/div/table/thead/tr/td[1]/div').text
        logger.info("Column01 =  {}".format(slaref))
        slametname = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[2]/div/table/thead/tr/td[2]/div').text
        logger.info("Column02 =  {}".format(slametname))
        perf = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[2]/div/table/thead/tr/td[3]/div').text
        logger.info("Column03 =  {}".format(perf))
        pas = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[2]/div/table/thead/tr/td[4]/div').text
        logger.info("Column04 =  {}".format(pas))
        fail = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[2]/div/table/thead/tr/td[5]/div').text
        logger.info("Column05 =  {}".format(fail))
        total = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[2]/div/table/thead/tr/td[6]/div').text
        logger.info("Column06 =  {}".format(total))
        slapercent = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[2]/div/table/thead/tr/td[7]/div').text
        logger.info("Column07 =  {}".format(slapercent))

        reportname2 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[1]/table/tbody/tr[1]/td').text
        logger.info("Table2 Report Name =  {}".format(reportname2))
        reportname22 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[1]/table/tbody/tr[2]/td').text
        logger.info("Table2 Report Name =  {}".format(reportname22))
        slaref1 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[2]/div/table/thead/tr/td[1]/div').text
        logger.info("Table2 Column01 =  {}".format(slaref1))
        slametname1 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[2]/div/table/thead/tr/td[2]/div').text
        logger.info("Table2 Column02 =  {}".format(slametname1))
        perf1 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[2]/div/table/thead/tr/td[3]/div').text
        logger.info("Table2 Column03 =  {}".format(perf1))
        pas1 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[2]/div/table/thead/tr/td[4]/div').text
        logger.info("Table2 Column04 =  {}".format(pas1))
        fail1 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[2]/div/table/thead/tr/td[5]/div').text
        logger.info("Table2 Column05 =  {}".format(fail1))
        total1 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[2]/div/table/thead/tr/td[6]/div').text
        logger.info("Table2 Column06 =  {}".format(total1))
        slapercent1 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[2]/div/table/thead/tr/td[7]/div').text
        logger.info("Table2 Column07 =  {}".format(slapercent1))

        columns_name_status = True
        if reportname1 != kwargs['reportname1']:
            columns_name_status = False
        elif reportname12 != kwargs['reportname12']:
            columns_name_status = False
        elif reportname2 != kwargs['reportname2']:
            columns_name_status = False
        elif reportname22 != kwargs['reportname22']:
            columns_name_status = False
        elif slaref != kwargs['slaref']:
            columns_name_status = False
        elif slametname != kwargs['slametname']:
            columns_name_status = False
        elif perf != kwargs['perf']:
            columns_name_status = False
        elif pas != kwargs['pas']:
            columns_name_status = False
        elif fail != kwargs['fail']:
            columns_name_status = False
        elif total != kwargs['total']:
            columns_name_status = False
        elif slapercent != kwargs['slapercent']:
            columns_name_status = False
        elif slaref1 != kwargs['slaref1']:
            columns_name_status = False
        elif slametname1 != kwargs['slametname1']:
            columns_name_status = False
        elif perf1 != kwargs['perf1']:
            columns_name_status = False
        elif pas1 != kwargs['pas1']:
            columns_name_status = False
        elif fail1 != kwargs['fail1']:
            columns_name_status = False
        elif total1 != kwargs['total1']:
            columns_name_status = False
        elif slapercent1 != kwargs['slapercent1']:
            columns_name_status = False

        if columns_name_status == False:
            logger.info(
                "Failed - The mentioned Report name & columns are not available in the reports as in requirement")
        else:
            logger.info("Passed - The mentioned Report name & columns are available in the reports as in requirement")

        return columns_name_status

    def verify_breached_change_sla_tickets(self, kwargs):
        """ScreenShot - Taken"""
        self.driver.get_screenshot_as_file(
            'C:\Users\karsg\Desktop\Automation\screenshots\Reports\Breachedchange\ss1.png')

        logger.info("Execuitng verify_breached_change_sla_tickets()")
        window_before = self.driver.window_handles[0]
        """ Clicking on Application"""
        appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
        appl.click()

        """Clicking on Smart Reporting -> Smart Reporting Console"""
        smrtrep = self.driver.find_element_by_link_text('Smart Reporting')
        smrtrep.click()
        smrtrepcon = self.driver.find_element_by_link_text('Smart Reporting Console')
        smrtrepcon.click()

        # WebDriverWait(self.driver, 10).until(expected_conditions.number_of_windows_to_be(2))
        time.sleep(6)
        window_after = self.driver.window_handles[1]
        self.driver.switch_to.window(window_after)

        """ScreenShot - Taken"""
        self.driver.get_screenshot_as_file(
            'C:\Users\karsg\Desktop\Automation\screenshots\Reports\Breachedchange\ss2.png')

        # time.sleep(14)
        """All already clicked"""
        """Click H3G"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')))
        obj_h3g = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')
        obj_h3g.click()
        """click on Rebus Reports"""
        obj_rebus = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[2]/div[8]/div/div/div/div[2]')
        obj_rebus.click()

        """Search content"""
        send_repo = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/input')  # search field
        send_repo.send_keys(kwargs['reportname1'])

        search_icon = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/div[2]/div[2]/img')  # search icon
        search_icon.click()

        time.sleep(5)
        """ScreenShot - Taken"""
        self.driver.get_screenshot_as_file(
            'C:\Users\karsg\Desktop\Automation\screenshots\Reports\Breachedchange\ss3.png')

        """Double clicking on report"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div[2]')))
        repo = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div[2]')
        action = ActionChains(self.driver)
        action.double_click(repo).perform()

        time.sleep(10)
        """ScreenShot - Taken"""
        self.driver.get_screenshot_as_file(
            'C:\Users\karsg\Desktop\Automation\screenshots\Reports\Breachedchange\ss4.png')

        """Verify if the mentioned names & columns are available in the reports as in requirement sheet"""

        WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[1]/table/tbody/tr[1]/td')))

        reportname1 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[1]/table/tbody/tr[1]/td').text
        logger.info("Report Name =  {}".format(reportname1))
        chg = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[1]/div').text
        logger.info("Column01 =  {}".format(chg))
        slametname = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[2]/div').text
        logger.info("Column02 =  {}".format(slametname))
        hasbreach = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[3]/div').text
        logger.info("Column03 =  {}".format(hasbreach))
        chgstatus = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[4]/div').text
        logger.info("Column04 =  {}".format(chgstatus))
        chgclass = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[5]/div').text
        logger.info("Column05 =  {}".format(chgclass))
        noofp0p3inc = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[6]/div').text
        logger.info("Column06 =  {}".format(noofp0p3inc))
        compdatetime = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[7]/div').text
        logger.info("Column07 =  {}".format(compdatetime))
        targclosedate = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[8]/div').text
        logger.info("Column08 =  {}".format(targclosedate))
        closedatetime = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[9]/div').text
        logger.info("Column09 =  {}".format(closedatetime))
        assigneegrp = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[10]/div').text
        logger.info("Column10 =  {}".format(assigneegrp))
        assignee = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[11]/div').text
        logger.info("Column11 =  {}".format(assignee))
        chgmgr = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[12]/div').text
        logger.info("Column12 =  {}".format(chgmgr))
        chgsummary = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[13]/div').text
        logger.info("Column13 =  {}".format(chgsummary))

        reportname2 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[1]/table/tbody/tr[1]/td').text
        logger.info("Table2 Report Name =  {}".format(reportname2))
        chg1 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[2]/div/table/thead/tr/td[1]/div').text
        logger.info("Table2 Column01 =  {}".format(chg1))
        slametname1 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[2]/div/table/thead/tr/td[2]/div').text
        logger.info("Table2 Column02 =  {}".format(slametname1))
        hasbreach1 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[2]/div/table/thead/tr/td[3]/div').text
        logger.info("Table2 Column03 =  {}".format(hasbreach1))
        chgstatus1 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[2]/div/table/thead/tr/td[4]/div').text
        logger.info("Table2 Column04 =  {}".format(chgstatus1))
        chgclass1 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[2]/div/table/thead/tr/td[5]/div').text
        logger.info("Table2 Column05 =  {}".format(chgclass1))
        closestatsreason1 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[2]/div/table/thead/tr/td[6]/div').text
        logger.info("Table2 Column06 =  {}".format(closestatsreason1))
        compdate1 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[2]/div/table/thead/tr/td[7]/div').text
        logger.info("Table2 Column07 =  {}".format(compdate1))
        actualstart1 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[2]/div/table/thead/tr/td[8]/div').text
        logger.info("Table2 Column08 =  {}".format(actualstart1))
        actualend1 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[2]/div/table/thead/tr/td[9]/div').text
        logger.info("Table2 Column09 =  {}".format(actualend1))
        assigneegrp1 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[2]/div/table/thead/tr/td[10]/div').text
        logger.info("Table2 Column10 =  {}".format(assigneegrp1))
        assignee1 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[2]/div/table/thead/tr/td[11]/div').text
        logger.info("Table2 Column11 =  {}".format(assignee1))
        chgmgr1 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[2]/div/table/thead/tr/td[12]/div').text
        logger.info("Table2 Column12 =  {}".format(chgmgr1))
        chgsummary1 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[2]/div/table/thead/tr/td[13]/div').text
        logger.info("Table2 Column13 =  {}".format(chgsummary1))

        columns_name_status = True
        if reportname1 != kwargs['reportname1']:
            columns_name_status = False
        elif reportname2 != kwargs['reportname2']:
            columns_name_status = False
        elif chg != kwargs['chg']:
            columns_name_status = False
        elif slametname != kwargs['slametname']:
            columns_name_status = False
        elif hasbreach != kwargs['hasbreach']:
            columns_name_status = False
        elif chgstatus != kwargs['chgstatus']:
            columns_name_status = False
        elif chgclass != kwargs['chgclass']:
            columns_name_status = False
        elif noofp0p3inc != kwargs['noofp0p3inc']:
            columns_name_status = False
        elif compdatetime != kwargs['compdatetime']:
            columns_name_status = False
        elif targclosedate != kwargs['targclosedate']:
            columns_name_status = False
        elif closedatetime != kwargs['closedatetime']:
            columns_name_status = False
        elif assigneegrp != kwargs['assigneegrp']:
            columns_name_status = False
        elif assignee != kwargs['assignee']:
            columns_name_status = False
        elif chgmgr != kwargs['chgmgr']:
            columns_name_status = False
        elif chgsummary != kwargs['chgsummary']:
            columns_name_status = False
        elif chg1 != kwargs['chg1']:
            columns_name_status = False
        elif slametname1 != kwargs['slametname1']:
            columns_name_status = False
        elif hasbreach1 != kwargs['hasbreach1']:
            columns_name_status = False
        elif chgstatus1 != kwargs['chgstatus1']:
            columns_name_status = False
        elif chgclass1 != kwargs['chgclass1']:
            columns_name_status = False
        elif closestatsreason1 != kwargs['closestatsreason1']:
            columns_name_status = False
        elif compdate1 != kwargs['compdate1']:
            columns_name_status = False
        elif actualstart1 != kwargs['actualstart1']:
            columns_name_status = False
        elif actualend1 != kwargs['actualend1']:
            columns_name_status = False
        elif assigneegrp1 != kwargs['assigneegrp1']:
            columns_name_status = False
        elif assignee1 != kwargs['assignee1']:
            columns_name_status = False
        elif chgmgr1 != kwargs['chgmgr1']:
            columns_name_status = False
        elif chgsummary1 != kwargs['chgsummary1']:
            columns_name_status = False

        if columns_name_status == False:
            logger.info(
                "Failed - The mentioned Report name & columns are not available in the reports as in requirement")
        else:
            logger.info("Passed - The mentioned Report name & columns are available in the reports as in requirement")
        return columns_name_status

    def incident_response_sla_data_main(self, kwargs):
        logger.info("Execuitng smart_reporting()")
        """ Clicking on Application"""
        appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
        appl.click()

        """Clicking on Smart Reporting -> Smart Reporting Console"""
        smrtrep = self.driver.find_element_by_link_text('Smart Reporting')
        smrtrep.click()
        smrtrepcon = self.driver.find_element_by_link_text('Smart Reporting Console')
        """Clicking on smart reporting console and switchingg windows"""
        window_before = self.driver.window_handles[0]
        smrtrepcon.click()
        WebDriverWait(self.driver, 10).until(expected_conditions.number_of_windows_to_be(2))
        window_after = self.driver.window_handles[1]
        self.driver.switch_to.window(window_after)
        time.sleep(3)

        search_report = self.driver.find_element(By.XPATH,
                                                 '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/input')
        search_report.send_keys(kwargs['Report Name'])
        search_report.send_keys(Keys.ENTER)
        time.sleep(2)
        """opening H3G Folder"""
        h3gopfoler = self.driver.find_element_by_xpath("//div[@title='H3G Operational Reporting']")
        time.sleep(2)
        h3gopfoler.click()
        """Opening Rebus Reports Folder"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          "/html[1]/body[1]/form[1]/div[12]/div[1]/div[2]/div[4]/div[1]/div[2]/div[3]/div[1]/div[2]/div[8]/div[1]/div[1]")))
        maya_reports = self.driver.find_element(By.XPATH,
                                                "/html[1]/body[1]/form[1]/div[12]/div[1]/div[2]/div[4]/div[1]/div[2]/div[3]/div[1]/div[2]/div[8]/div[1]/div[1]")
        maya_reports.click()
        time.sleep(3)
        """Taking Screen shot"""
        self.driver.get_screenshot_as_file('C:\GIT\output\ITSM_REBUS Reporting_070_1.png')
        """Double-click on incident-sla-dashboard report"""
        incident_sla_dashboard = self.driver.find_element(By.XPATH,
                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div[2]')
        time.sleep(2)
        action = ActionChains(self.driver)
        action.double_click(incident_sla_dashboard)
        action.perform()
        time.sleep(10)

        """Taking Screen shot"""
        self.driver.get_screenshot_as_file('C:\GIT\output\ITSM_REBUS Reporting_031_1.png')

        """Getting the text of the table name"""
        WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
            (By.XPATH, "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[1]/table[1]/tbody[1]/tr[1]/td[1]")))
        table_title = self.driver.find_element(By.XPATH, "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[1]/table[1]/tbody[1]/tr[1]/td[1]").text
        logger.info("Table title1: {}".format(table_title))
        self.driver.switch_to.window(window_before)
        Matching = True
        if table_title != kwargs['Table_title']:
            Matching = False
        return Matching

    def incident_response_sla_data_main1(self, kwargs):
        logger.info("Execuitng smart_reporting()")
        """ Clicking on Application"""
        appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
        appl.click()

        """Clicking on Smart Reporting -> Smart Reporting Console"""
        smrtrep = self.driver.find_element_by_link_text('Smart Reporting')
        smrtrep.click()
        smrtrepcon = self.driver.find_element_by_link_text('Smart Reporting Console')
        """Clicking on smart reporting console and switchingg windows"""
        window_before = self.driver.window_handles[0]
        smrtrepcon.click()
        WebDriverWait(self.driver, 10).until(expected_conditions.number_of_windows_to_be(2))
        window_after = self.driver.window_handles[1]
        self.driver.switch_to.window(window_after)
        time.sleep(3)
        search_report = self.driver.find_element(By.XPATH,
                                                 '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/input')
        search_report.send_keys(kwargs['Report Name'])
        search_report.send_keys(Keys.ENTER)
        time.sleep(2)
        """opening H3G Folder"""
        h3gopfoler = self.driver.find_element_by_xpath("//div[@title='H3G Operational Reporting']")
        time.sleep(2)
        h3gopfoler.click()
        """Opening Rebus Reports Folder"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          "/html[1]/body[1]/form[1]/div[12]/div[1]/div[2]/div[4]/div[1]/div[2]/div[3]/div[1]/div[2]/div[8]/div[1]/div[1]")))
        maya_reports = self.driver.find_element(By.XPATH,
                                                "/html[1]/body[1]/form[1]/div[12]/div[1]/div[2]/div[4]/div[1]/div[2]/div[3]/div[1]/div[2]/div[8]/div[1]/div[1]")
        maya_reports.click()
        time.sleep(3)

        """Taking Screen shot"""
        self.driver.get_screenshot_as_file('C:\GIT\output\ITSM_REBUS Reporting_032_1.png')
        """Double-click on incident-sla-dashboard report"""
        incident_sla_dashboard = self.driver.find_element(By.XPATH,
                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div[2]')
        time.sleep(2)
        action = ActionChains(self.driver)
        action.double_click(incident_sla_dashboard)
        action.perform()
        time.sleep(10)
        """Taking Screen shot"""
        self.driver.get_screenshot_as_file('C:\GIT\output\ITSM_REBUS Reporting_032_1.png')

        """Getting the list of the columns"""
        column_list = []
        for i in range(1, 14):
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                                  '/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/div[1]'.format(
                                                                                                      i))))
            column_list.append(self.driver.find_element(By.XPATH,
                                                        '/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/div[1]'.format(
                                                            i)).text)
        column_names = ", ".join(column_list)
        logger.info(column_names)
        self.driver.switch_to.window(window_before)
        matching = True
        if column_names != kwargs['Column_names']:
            matching = False
        return matching

    def incident_response_sla_data_main2(self, kwargs):
        logger.info("Execuitng smart_reporting()")
        """ Clicking on Application"""
        appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
        appl.click()

        """Clicking on Smart Reporting -> Smart Reporting Console"""
        smrtrep = self.driver.find_element_by_link_text('Smart Reporting')
        smrtrep.click()
        smrtrepcon = self.driver.find_element_by_link_text('Smart Reporting Console')
        """Clicking on smart reporting console and switchingg windows"""
        window_before = self.driver.window_handles[0]
        smrtrepcon.click()
        WebDriverWait(self.driver, 10).until(expected_conditions.number_of_windows_to_be(2))
        window_after = self.driver.window_handles[1]
        self.driver.switch_to.window(window_after)
        time.sleep(3)

        search_report = self.driver.find_element(By.XPATH,
                                                 '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/input')
        search_report.send_keys(kwargs['Report Name'])
        search_report.send_keys(Keys.ENTER)
        time.sleep(2)
        """opening H3G Folder"""
        h3gopfoler = self.driver.find_element_by_xpath("//div[@title='H3G Operational Reporting']")

        time.sleep(2)
        h3gopfoler.click()
        """Opening Rebus Reports Folder"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          "/html[1]/body[1]/form[1]/div[12]/div[1]/div[2]/div[4]/div[1]/div[2]/div[3]/div[1]/div[2]/div[8]/div[1]/div[1]")))
        maya_reports = self.driver.find_element(By.XPATH,
                                                "/html[1]/body[1]/form[1]/div[12]/div[1]/div[2]/div[4]/div[1]/div[2]/div[3]/div[1]/div[2]/div[8]/div[1]/div[1]")
        maya_reports.click()
        time.sleep(3)

        """Taking Screen shot"""
        self.driver.get_screenshot_as_file('C:\GIT\output\ITSM_REBUS Reporting_035_1.png')
        """Double-click on incident-sla-dashboard report"""
        incident_sla_dashboard = self.driver.find_element(By.XPATH,
                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div[2]')
        time.sleep(2)
        action = ActionChains(self.driver)
        action.double_click(incident_sla_dashboard)
        action.perform()
        time.sleep(10)
        """Taking Screen shot"""
        self.driver.get_screenshot_as_file('C:\GIT\output\ITSM_REBUS Reporting_035_2.png')

        """Checking Incident ID columns-->descending"""
        sorting = True
        column_count = 1
        for i in range(1, 2):
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                (By.XPATH,
                 "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                     i))))
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                                                                  i))))
            time.sleep(3)
            obj = self.driver.find_element(By.XPATH,
                                           "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                               i))
            obj.click()
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")))
            obj1 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")
            time.sleep(1)
            obj1.click()
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable(
                (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[3]/div[2]")))
            obj2 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[3]/div[2]")
            time.sleep(1)
            obj2.click()
            time.sleep(7)
            column_list = []
            actual_column_list = []
            for j in range(1, 101):
                WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                                      "//html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]/a[1]".format(
                                                                                                          j,
                                                                                                          column_count))))
                column_list.append(self.driver.find_element(By.XPATH,
                                                            "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]/a[1]".format(
                                                                j, column_count)).text)
            refined_column_list = re.findall(r"(\d+)", str(column_list))
            for k in refined_column_list:
                actual_column_list.append(float(k.replace(",", "")))
            if actual_column_list != sorted(actual_column_list, reverse=True):
                sorting = False
                logger.info("Incident ID descending failed")
            logger.info(actual_column_list)
            logger.info(sorted(actual_column_list, reverse=True))
            column_count += 1

        """Taking Screen shot"""
        self.driver.get_screenshot_as_file('C:\GIT\output\ITSM_REBUS Reporting_035_3.png')

        """Checking for Priority and Target time-->Descending"""
        column_count = 3
        for i in range(3, 5):
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                (By.XPATH,
                 "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                     i))))
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                                                                  i))))
            time.sleep(3)
            obj = self.driver.find_element(By.XPATH,
                                           "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                               i))
            obj.click()
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")))
            obj1 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")
            time.sleep(1)
            obj1.click()
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable(
                (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[3]/div[2]")))
            obj2 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[3]/div[2]")
            time.sleep(1)
            obj2.click()
            time.sleep(7)
            column_list = []
            actual_column_list = []
            for j in range(1, 101):
                WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                                      "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                                                          j,
                                                                                                          column_count))))
                column_list.append(self.driver.find_element(By.XPATH,
                                                            "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                j, column_count)).text)
            refined_column_list = re.findall(r"(\d+)", str(column_list))
            for k in refined_column_list:
                actual_column_list.append(float(k.replace(",", "")))
            if actual_column_list != sorted(actual_column_list, reverse=True):
                sorting = False
                logger.info("priority and target time descending failed")
            logger.info(actual_column_list)
            logger.info(sorted(actual_column_list, reverse=True))
            column_count += 1

        """Taking Screen shot"""
        self.driver.get_screenshot_as_file('C:\GIT\output\ITSM_REBUS Reporting_035_4.png')

        """Checking for Actual time-->Descending"""
        column_count = 5
        for i in range(5, 6):
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                (By.XPATH,
                 "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                     i))))
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                                                                  i))))
            time.sleep(3)
            obj = self.driver.find_element(By.XPATH,
                                           "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                               i))
            obj.click()
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")))
            obj1 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")
            time.sleep(1)
            obj1.click()
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable(
                (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[3]/div[2]")))
            obj2 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[3]/div[2]")
            time.sleep(1)
            obj2.click()
            time.sleep(7)
            column_list = []
            actual_column_list = []
            for j in range(1, 101):
                WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                                      "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                                                          j,
                                                                                                          column_count))))
                column_list.append(self.driver.find_element(By.XPATH,
                                                            "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                j, column_count)).text)
            refined_column_list = re.findall(r'(\d+\s)Days*', str(column_list))
            for k in refined_column_list:
                actual_column_list.append(float(k.replace(",", "")))
            if actual_column_list != sorted(actual_column_list, reverse=True):
                sorting = False
                logger.info("Actual time descending failed")
            logger.info(actual_column_list)
            logger.info(sorted(actual_column_list, reverse=True))
            column_count += 1

        """Taking Screen shot"""
        self.driver.get_screenshot_as_file('C:\GIT\output\ITSM_REBUS Reporting_035_5.png')

        """Checking Incident ID columns-->ascending"""
        column_count = 1
        for i in range(1, 2):
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                (By.XPATH,
                 "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                     i))))
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                                                                  i))))
            time.sleep(3)
            obj = self.driver.find_element(By.XPATH,
                                           "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                               i))
            obj.click()
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")))
            obj1 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")
            time.sleep(1)
            obj1.click()
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable(
                (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[2]/div[2]")))
            obj2 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[2]/div[2]")
            time.sleep(1)
            obj2.click()
            time.sleep(7)
            column_list = []
            actual_column_list = []
            for j in range(1, 101):
                WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                                      "//html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]/a[1]".format(
                                                                                                          j,
                                                                                                          column_count))))
                column_list.append(self.driver.find_element(By.XPATH,
                                                            "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]/a[1]".format(
                                                                j, column_count)).text)
            refined_column_list = re.findall(r"(\d+)", str(column_list))
            for k in refined_column_list:
                actual_column_list.append(float(k.replace(",", "")))
            if actual_column_list != sorted(actual_column_list, reverse=False):
                sorting = False
                logger.info("Incident ID ascending failed")
            logger.info(actual_column_list)
            logger.info(sorted(actual_column_list, reverse=False))
            column_count += 1

        """Taking Screen shot"""
        self.driver.get_screenshot_as_file('C:\GIT\output\ITSM_REBUS Reporting_035_6.png')

        """Checking for Priority and Target time-->Ascending"""
        column_count = 3
        for i in range(3, 5):
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                (By.XPATH,
                 "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                     i))))
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                                                                  i))))
            time.sleep(3)
            obj = self.driver.find_element(By.XPATH,"/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                               i))
            obj.click()
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")))
            obj1 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")
            time.sleep(1)
            obj1.click()
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable(
                (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[2]/div[2]")))
            obj2 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[2]/div[2]")
            time.sleep(1)
            obj2.click()
            time.sleep(7)
            column_list = []
            actual_column_list = []
            for j in range(1, 101):
                WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                                      "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                                                          j,
                                                                                                          column_count))))
                column_list.append(self.driver.find_element(By.XPATH,
                                                            "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                j, column_count)).text)
            refined_column_list = re.findall(r"(\d+)", str(column_list))
            for k in refined_column_list:
                actual_column_list.append(float(k.replace(",", "")))
            if actual_column_list != sorted(actual_column_list, reverse=False):
                sorting = False
                logger.info("priority and target time ascending failed")
            logger.info(actual_column_list)
            logger.info(sorted(actual_column_list, reverse=False))
            column_count += 1

        """Taking Screen shot"""
        self.driver.get_screenshot_as_file('C:\GIT\output\ITSM_REBUS Reporting_035_7.png')

        """Checking for Actual time-->ascending"""
        column_count = 5
        for i in range(5, 6):
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                (By.XPATH,
                 "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                     i))))
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                                                                  i))))
            time.sleep(3)
            obj = self.driver.find_element(By.XPATH,
                                           "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                               i))
            obj.click()
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")))
            obj1 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")
            time.sleep(1)
            obj1.click()
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable(
                (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[2]/div[2]")))
            obj2 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[2]/div[2]")
            time.sleep(1)
            obj2.click()
            time.sleep(7)
            column_list = []
            actual_column_list = []
            for j in range(1, 101):
                WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                                      "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                                                          j,
                                                                                                          column_count))))
                column_list.append(self.driver.find_element(By.XPATH,
                                                            "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                j, column_count)).text)
            refined_column_list = re.findall(r'(\d+\s)Days*', str(column_list))
            for k in refined_column_list:
                actual_column_list.append(float(k.replace(",", "")))
            if actual_column_list != sorted(actual_column_list, reverse=False):
                sorting = False
                logger.info("Actual time ascending failed")
            logger.info(actual_column_list)
            logger.info(sorted(actual_column_list, reverse=False))
            column_count += 1

        self.driver.switch_to.window(window_before)

        return sorting

    def incident_restore_sla_data_main(self, kwargs):
        logger.info("Execuitng smart_reporting()")
        """ Clicking on Application"""
        appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
        appl.click()

        """Clicking on Smart Reporting -> Smart Reporting Console"""
        smrtrep = self.driver.find_element_by_link_text('Smart Reporting')
        smrtrep.click()
        smrtrepcon = self.driver.find_element_by_link_text('Smart Reporting Console')
        """Clicking on smart reporting console and switchingg windows"""
        window_before = self.driver.window_handles[0]
        smrtrepcon.click()
        WebDriverWait(self.driver, 10).until(expected_conditions.number_of_windows_to_be(2))
        window_after = self.driver.window_handles[1]
        self.driver.switch_to.window(window_after)
        time.sleep(3)

        search_report = self.driver.find_element(By.XPATH,
                                                 '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/input')
        search_report.send_keys(kwargs['Report Name'])
        search_report.send_keys(Keys.ENTER)
        time.sleep(2)
        """opening H3G Folder"""
        h3gopfoler = self.driver.find_element_by_xpath("//div[@title='H3G Operational Reporting']")
        time.sleep(2)
        h3gopfoler.click()
        """Opening Rebus Reports Folder"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          "/html[1]/body[1]/form[1]/div[12]/div[1]/div[2]/div[4]/div[1]/div[2]/div[3]/div[1]/div[2]/div[8]/div[1]/div[1]")))
        maya_reports = self.driver.find_element(By.XPATH,
                                                "/html[1]/body[1]/form[1]/div[12]/div[1]/div[2]/div[4]/div[1]/div[2]/div[3]/div[1]/div[2]/div[8]/div[1]/div[1]")
        maya_reports.click()
        time.sleep(3)
        """Taking Screen shot"""
        self.driver.get_screenshot_as_file('C:\GIT\output\ITSM_REBUS Reporting_070_1.png')
        """Double-click on incident-sla-dashboard report"""
        incident_sla_dashboard = self.driver.find_element(By.XPATH,
                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div[2]')
        time.sleep(2)
        action = ActionChains(self.driver)
        action.double_click(incident_sla_dashboard)
        action.perform()
        time.sleep(10)

        """Taking Screen shot"""
        self.driver.get_screenshot_as_file('C:\GIT\output\ITSM_REBUS Reporting_040_1.png')

        """Getting the text of the table name"""
        WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
            (By.XPATH, '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[1]/table[1]/tbody/tr[1]/td')))
        table_title = self.driver.find_element(By.XPATH, '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[1]/table[1]/tbody/tr[1]/td').text
        logger.info("Table title1: {}".format(table_title))
        self.driver.switch_to.window(window_before)
        Matching = True
        if table_title != kwargs['Table_title']:
            Matching = False
        return Matching

    def incident_restore_sla_data_main1(self, kwargs):
        logger.info("Execuitng smart_reporting()")
        """ Clicking on Application"""
        appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
        appl.click()

        """Clicking on Smart Reporting -> Smart Reporting Console"""
        smrtrep = self.driver.find_element_by_link_text('Smart Reporting')
        smrtrep.click()
        smrtrepcon = self.driver.find_element_by_link_text('Smart Reporting Console')
        """Clicking on smart reporting console and switchingg windows"""
        window_before = self.driver.window_handles[0]
        smrtrepcon.click()
        WebDriverWait(self.driver, 10).until(expected_conditions.number_of_windows_to_be(2))
        window_after = self.driver.window_handles[1]
        self.driver.switch_to.window(window_after)
        time.sleep(3)

        search_report = self.driver.find_element(By.XPATH,
                                                 '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/input')
        search_report.send_keys(kwargs['Report Name'])
        search_report.send_keys(Keys.ENTER)
        time.sleep(2)
        """opening H3G Folder"""
        h3gopfoler = self.driver.find_element_by_xpath("//div[@title='H3G Operational Reporting']")
        time.sleep(2)
        h3gopfoler.click()
        """Opening Rebus Reports Folder"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          "/html[1]/body[1]/form[1]/div[12]/div[1]/div[2]/div[4]/div[1]/div[2]/div[3]/div[1]/div[2]/div[8]/div[1]/div[1]")))
        maya_reports = self.driver.find_element(By.XPATH,
                                                "/html[1]/body[1]/form[1]/div[12]/div[1]/div[2]/div[4]/div[1]/div[2]/div[3]/div[1]/div[2]/div[8]/div[1]/div[1]")
        maya_reports.click()
        time.sleep(3)
        """Taking Screen shot"""
        self.driver.get_screenshot_as_file('C:\GIT\output\ITSM_REBUS Reporting_070_1.png')
        """Double-click on incident-sla-dashboard report"""
        incident_sla_dashboard = self.driver.find_element(By.XPATH,
                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div[2]')
        time.sleep(2)
        action = ActionChains(self.driver)
        action.double_click(incident_sla_dashboard)
        action.perform()
        time.sleep(10)

        """Taking Screen shot"""
        self.driver.get_screenshot_as_file('C:\GIT\output\ITSM_REBUS Reporting_041_1.png')

        """Getting the list of the columns"""
        column_list = []
        for i in range(1, 14):
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                                  '/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/div[1]'.format(
                                                                                                      i))))
            column_list.append(self.driver.find_element(By.XPATH,
                                                        '/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/div[1]'.format(
                                                            i)).text)
        column_names = ", ".join(column_list)
        logger.info(column_names)
        self.driver.switch_to.window(window_before)
        matching = True
        if column_names != kwargs['Column_names']:
            matching = False
        return matching

    def incident_restore_sla_data_main2(self, kwargs):
        logger.info("Execuitng smart_reporting()")
        """ Clicking on Application"""
        appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
        appl.click()

        """Clicking on Smart Reporting -> Smart Reporting Console"""
        smrtrep = self.driver.find_element_by_link_text('Smart Reporting')
        smrtrep.click()
        smrtrepcon = self.driver.find_element_by_link_text('Smart Reporting Console')
        """Clicking on smart reporting console and switchingg windows"""
        window_before = self.driver.window_handles[0]
        smrtrepcon.click()
        WebDriverWait(self.driver, 10).until(expected_conditions.number_of_windows_to_be(2))
        window_after = self.driver.window_handles[1]
        self.driver.switch_to.window(window_after)
        time.sleep(3)

        search_report = self.driver.find_element(By.XPATH,
                                                 '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/input')
        search_report.send_keys(kwargs['Report Name'])
        search_report.send_keys(Keys.ENTER)
        time.sleep(2)
        """opening H3G Folder"""
        h3gopfoler = self.driver.find_element_by_xpath("//div[@title='H3G Operational Reporting']")
        time.sleep(2)
        h3gopfoler.click()
        """Opening Rebus Reports Folder"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          "/html[1]/body[1]/form[1]/div[12]/div[1]/div[2]/div[4]/div[1]/div[2]/div[3]/div[1]/div[2]/div[8]/div[1]/div[1]")))
        maya_reports = self.driver.find_element(By.XPATH,
                                                "/html[1]/body[1]/form[1]/div[12]/div[1]/div[2]/div[4]/div[1]/div[2]/div[3]/div[1]/div[2]/div[8]/div[1]/div[1]")
        maya_reports.click()
        time.sleep(3)

        """Taking Screen shot"""
        self.driver.get_screenshot_as_file('C:\GIT\output\ITSM_REBUS Reporting_044_1.png')

        """Double-click on incident-sla-dashboard report"""
        incident_sla_dashboard = self.driver.find_element(By.XPATH,
                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div[2]')
        time.sleep(2)
        action = ActionChains(self.driver)
        action.double_click(incident_sla_dashboard)
        action.perform()
        time.sleep(10)

        """Taking Screen shot"""
        self.driver.get_screenshot_as_file('C:\GIT\output\ITSM_REBUS Reporting_044_2.png')

        """Checking Incident ID columns-->descending"""
        sorting = True
        column_count = 1
        for i in range(1, 2):
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                (By.XPATH,
                 "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                     i))))
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                                                                  i))))
            time.sleep(3)
            obj = self.driver.find_element(By.XPATH,
                                           "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                               i))
            obj.click()
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")))
            obj1 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")
            time.sleep(1)
            obj1.click()
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable(
                (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[3]/div[2]")))
            obj2 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[3]/div[2]")
            time.sleep(1)
            obj2.click()
            time.sleep(7)
            column_list = []
            actual_column_list = []
            for j in range(1, 101):
                WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                                      "//html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]/a[1]".format(
                                                                                                          j,
                                                                                                          column_count))))
                column_list.append(self.driver.find_element(By.XPATH,
                                                            "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]/a[1]".format(
                                                                j, column_count)).text)
            refined_column_list = re.findall(r"(\d+)", str(column_list))
            for k in refined_column_list:
                actual_column_list.append(float(k.replace(",", "")))
            if actual_column_list != sorted(actual_column_list, reverse=True):
                sorting = False
                logger.info("Incident ID descending failed")
            logger.info(actual_column_list)
            logger.info(sorted(actual_column_list, reverse=True))
            column_count += 1

        """Taking Screen shot"""
        self.driver.get_screenshot_as_file('C:\GIT\output\ITSM_REBUS Reporting_044_3.png')

        """Checking for Priority and Target time-->Descending"""
        column_count = 3
        for i in range(3, 5):
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                (By.XPATH,
                 "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                     i))))
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                                                                  i))))
            time.sleep(3)
            obj = self.driver.find_element(By.XPATH,
                                           "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                               i))
            obj.click()
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")))
            obj1 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")
            time.sleep(1)
            obj1.click()
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable(
                (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[3]/div[2]")))
            obj2 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[3]/div[2]")
            time.sleep(1)
            obj2.click()
            time.sleep(7)
            column_list = []
            actual_column_list = []
            for j in range(1, 101):
                WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                                      "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                                                          j,
                                                                                                          column_count))))
                column_list.append(self.driver.find_element(By.XPATH,
                                                            "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                j, column_count)).text)
            refined_column_list = re.findall(r"(\d+)", str(column_list))
            for k in refined_column_list:
                actual_column_list.append(float(k.replace(",", "")))
            if actual_column_list != sorted(actual_column_list, reverse=True):
                sorting = False
                logger.info("priority and target time descending failed")
            logger.info(actual_column_list)
            logger.info(sorted(actual_column_list, reverse=True))
            column_count += 1

        """Taking Screen shot"""
        self.driver.get_screenshot_as_file('C:\GIT\output\ITSM_REBUS Reporting_044_4.png')

        """Checking for Actual time-->Descending"""
        column_count = 5
        for i in range(5, 6):
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                (By.XPATH,
                 "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                     i))))
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                                                                  i))))
            time.sleep(3)
            obj = self.driver.find_element(By.XPATH,
                                           "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                               i))
            obj.click()
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")))
            obj1 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")
            time.sleep(1)
            obj1.click()
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable(
                (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[3]/div[2]")))
            obj2 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[3]/div[2]")
            time.sleep(1)
            obj2.click()
            time.sleep(7)
            column_list = []
            actual_column_list = []
            for j in range(1, 101):
                WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                                      "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                                                          j,
                                                                                                          column_count))))
                column_list.append(self.driver.find_element(By.XPATH,
                                                            "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                j, column_count)).text)
            refined_column_list = re.findall(r'(\d+\s)Days*', str(column_list))
            for k in refined_column_list:
                actual_column_list.append(float(k.replace(",", "")))
            if actual_column_list != sorted(actual_column_list, reverse=True):
                sorting = False
                logger.info("Actual time descending failed")
            logger.info(actual_column_list)
            logger.info(sorted(actual_column_list, reverse=True))
            column_count += 1

        """Taking Screen shot"""
        self.driver.get_screenshot_as_file('C:\GIT\output\ITSM_REBUS Reporting_044_5.png')

        """Checking Incident ID columns-->ascending"""
        column_count = 1
        for i in range(1, 2):
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                (By.XPATH,
                 "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                     i))))
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                                                                  i))))
            time.sleep(3)
            obj = self.driver.find_element(By.XPATH,
                                           "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                               i))
            obj.click()
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")))
            obj1 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")
            time.sleep(1)
            obj1.click()
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable(
                (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[2]/div[2]")))
            obj2 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[2]/div[2]")
            time.sleep(1)
            obj2.click()
            time.sleep(7)
            column_list = []
            actual_column_list = []
            for j in range(1, 101):
                WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                                      "//html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]/a[1]".format(
                                                                                                          j,
                                                                                                          column_count))))
                column_list.append(self.driver.find_element(By.XPATH,
                                                            "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]/a[1]".format(
                                                                j, column_count)).text)
            refined_column_list = re.findall(r"(\d+)", str(column_list))
            for k in refined_column_list:
                actual_column_list.append(float(k.replace(",", "")))
            if actual_column_list != sorted(actual_column_list, reverse=False):
                sorting = False
                logger.info("Incident ID ascending failed")
            logger.info(actual_column_list)
            logger.info(sorted(actual_column_list, reverse=False))
            column_count += 1

        """Taking Screen shot"""
        self.driver.get_screenshot_as_file('C:\GIT\output\ITSM_REBUS Reporting_044_6.png')

        """Checking for Priority and Target time-->Ascending"""
        column_count = 3
        for i in range(3, 5):
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                (By.XPATH,
                 "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                     i))))
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                                                                  i))))
            time.sleep(3)
            obj = self.driver.find_element(By.XPATH,
                                           "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                               i))
            obj.click()
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")))
            obj1 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")
            time.sleep(1)
            obj1.click()
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable(
                (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[2]/div[2]")))
            obj2 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[2]/div[2]")
            time.sleep(1)
            obj2.click()
            time.sleep(7)
            column_list = []
            actual_column_list = []
            for j in range(1, 101):
                WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                                      "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                                                          j,
                                                                                                          column_count))))
                column_list.append(self.driver.find_element(By.XPATH,
                                                            "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                j, column_count)).text)
            refined_column_list = re.findall(r"(\d+)", str(column_list))
            for k in refined_column_list:
                actual_column_list.append(float(k.replace(",", "")))
            if actual_column_list != sorted(actual_column_list, reverse=False):
                sorting = False
                logger.info("priority and target time ascending failed")
            logger.info(actual_column_list)
            logger.info(sorted(actual_column_list, reverse=False))
            column_count += 1

        """Taking Screen shot"""
        self.driver.get_screenshot_as_file('C:\GIT\output\ITSM_REBUS Reporting_044_7.png')

        """Checking for Actual time-->ascending"""
        column_count = 5
        for i in range(5, 6):
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                (By.XPATH,
                 "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                     i))))
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                                                                  i))))
            time.sleep(3)
            obj = self.driver.find_element(By.XPATH,
                                           "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                               i))
            obj.click()
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")))
            obj1 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")
            time.sleep(1)
            obj1.click()
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable(
                (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[2]/div[2]")))
            obj2 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[2]/div[2]")
            time.sleep(1)
            obj2.click()
            time.sleep(7)
            column_list = []
            actual_column_list = []
            for j in range(1, 101):
                WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                                      "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                                                          j,
                                                                                                          column_count))))
                column_list.append(self.driver.find_element(By.XPATH,
                                                            "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                j, column_count)).text)
            refined_column_list = re.findall(r'(\d+\s)Days*', str(column_list))
            for k in refined_column_list:
                actual_column_list.append(float(k.replace(",", "")))
            if actual_column_list != sorted(actual_column_list, reverse=False):
                sorting = False
                logger.info("Actual time ascending failed")
            logger.info(actual_column_list)
            logger.info(sorted(actual_column_list, reverse=False))
            column_count += 1

        self.driver.switch_to.window(window_before)

        return sorting

    def work_order_priority(self, kwargs):
        logger.info("Execuitng work_order_priority()")
        window_before = self.driver.window_handles[0]

        self.driver.get_screenshot_as_file('C:/Users/sparsh/Desktop/New folder (2)/screenshot0.png')
        """ Clicking on Application"""
        appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
        appl.click()

        """Clicking on Smart Reporting -> Smart Reporting Console"""
        smrtrep = self.driver.find_element_by_link_text('Smart Reporting')
        smrtrep.click()
        smrtrepcon = self.driver.find_element_by_link_text('Smart Reporting Console')
        smrtrepcon.click()
        time.sleep(20)
        WebDriverWait(self.driver, 30).until(
            expected_conditions.number_of_windows_to_be(2))
        window_after = self.driver.window_handles[1]
        self.driver.switch_to.window(window_after)

        """ScreenShot - Taken"""
        self.driver.get_screenshot_as_file('C:/Users/sparsh/Desktop/New folder (2)/screenshot1.png')

        """All already clicked"""
        """Click H3G"""
        obj_h3g = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')
        obj_h3g.click()
        """click on Rebus Reports"""
        obj_rebus = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[2]/div[8]/div/div/div/div[2]')
        obj_rebus.click()

        """Search content"""
        send_repo = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/input')
        send_repo.send_keys(kwargs['Report_name'])

        search_icon = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/div[2]/div[2]/img')
        search_icon.click()

        """ScreenShot - Taken"""
        self.driver.get_screenshot_as_file('C:/Users/sparsh/Desktop/New folder (2)/screenshot2.png')

        time.sleep(2)
        """Double clicking on report"""
        repo = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div[2]')
        action = ActionChains(self.driver)
        action.double_click(repo).perform()

        time.sleep(7)
        """ScreenShot - Taken"""
        self.driver.get_screenshot_as_file('C:/Users/sparsh/Desktop/New folder (2)/screenshot3.png')
        self.driver.save_screenshot("ReportNamePriority.png")
        report_display_1_upper = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[1]/table/tbody/tr[1]/td').text

        """Verify if smart reporting lower 1 displays"""
        report_display_1_lower = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[1]/table/tbody/tr[2]/td').text

        """Verify if smart reporting displays the mentioned reports"""
        smart_reporting_display_status = True

        if report_display_1_upper != kwargs['Report_display_1_upper']:
            smart_reporting_display_status = False
        elif report_display_1_lower != kwargs['Report_display_1_lower']:
            smart_reporting_display_status = False

        if smart_reporting_display_status == False:
            logger.info("Failed - Smart reporting displays are Failed to match")
        else:
            logger.info("Passed - Smart reporting displays are matched")

        return smart_reporting_display_status

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


    def work_order_priority_names_columns(self, kwargs):
        logger.info("Execuitng work_order_priority_names_columns()")
        window_before = self.driver.window_handles[0]
        self.driver.get_screenshot_as_file('C:/Users/sparsh/Desktop/New folder (2)/screenshot0.png')
        """ Clicking on Application"""
        appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
        appl.click()

        """Clicking on Smart Reporting -> Smart Reporting Console"""
        smrtrep = self.driver.find_element_by_link_text('Smart Reporting')
        smrtrep.click()
        smrtrepcon = self.driver.find_element_by_link_text('Smart Reporting Console')
        smrtrepcon.click()
        time.sleep(20)
        WebDriverWait(self.driver, 30).until(
            expected_conditions.number_of_windows_to_be(2))
        window_after = self.driver.window_handles[1]
        self.driver.switch_to.window(window_after)

        """ScreenShot - Taken"""
        self.driver.get_screenshot_as_file('C:/Users/sparsh/Desktop/New folder (2)/screenshot1.png')

        """All already clicked"""
        """Click H3G"""
        obj_h3g = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')
        obj_h3g.click()
        """click on Rebus Reports"""
        obj_rebus = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[2]/div[8]/div/div/div/div[2]')
        obj_rebus.click()

        """Search content"""
        send_repo = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/input')
        send_repo.send_keys(kwargs['Report_name'])

        search_icon = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/div[2]/div[2]/img')
        search_icon.click()

        """ScreenShot - Taken"""
        self.driver.get_screenshot_as_file('C:/Users/sparsh/Desktop/New folder (2)/screenshot2.png')

        time.sleep(2)
        """Double clicking on report"""
        repo = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div[2]')
        action = ActionChains(self.driver)
        action.double_click(repo).perform()

        time.sleep(7)
        """ScreenShot - Taken"""
        self.driver.get_screenshot_as_file('C:/Users/sparsh/Desktop/New folder (2)/screenshot3.png')

        """Verify column"""
        self.driver.save_screenshot("ColumnNamePriority.png")
        period = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/table/tbody/tr/td[1]/div/table/thead/tr/td[1]/div').text

        priority = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/table/tbody/tr/td[1]/div/table/thead/tr/td[2]/div').text

        incoming = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/table/tbody/tr/td[1]/div/table/thead/tr/td[3]/div').text

        resolved = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/table/tbody/tr/td[1]/div/table/thead/tr/td[4]/div').text

        backlogs = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/table/tbody/tr/td[1]/div/table/thead/tr/td[5]/div').text

        time.sleep(2)
        """Verify if the mentioned names & columns are available in the reports as in requirement sheet"""
        names_columns_status = True

        if period != kwargs['column1']:
            names_columns_status = False
        elif priority != kwargs['column2']:
            names_columns_status = False
        elif incoming != kwargs['column3']:
            names_columns_status = False
        elif resolved != kwargs['column4']:
            names_columns_status = False
        elif backlogs != kwargs['column5']:
            names_columns_status = False

        if names_columns_status == False:
            logger.info("Failed - The mentioned names & columns are not available in the report as in requirement")
        else:
            logger.info("Passed - The mentioned names & columns are available in the report as in requirement")

        return names_columns_status

    def work_order_status(self, kwargs):
        logger.info("Execuitng work_order_status()")
        window_before = self.driver.window_handles[0]

        self.driver.get_screenshot_as_file('C:/Users/sparsh/Desktop/New folder (2)/screenshot0.png')
        """ Clicking on Application"""
        appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
        appl.click()

        """Clicking on Smart Reporting -> Smart Reporting Console"""
        smrtrep = self.driver.find_element_by_link_text('Smart Reporting')
        smrtrep.click()
        smrtrepcon = self.driver.find_element_by_link_text('Smart Reporting Console')
        smrtrepcon.click()

        WebDriverWait(self.driver, 30).until(
            expected_conditions.number_of_windows_to_be(2))
        window_after = self.driver.window_handles[1]
        self.driver.switch_to.window(window_after)

        """ScreenShot - Taken"""
        self.driver.get_screenshot_as_file('C:/Users/sparsh/Desktop/New folder (2)/screenshot1.png')

        time.sleep(20)

        """All already clicked"""
        """Click H3G"""
        obj_h3g = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')
        obj_h3g.click()
        """click on Rebus Reports"""
        obj_rebus = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[2]/div[8]/div/div/div/div[2]')
        obj_rebus.click()

        """Search content"""
        send_repo = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/input')
        send_repo.send_keys(kwargs['Report_name'])

        search_icon = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/div[2]/div[2]/img')
        search_icon.click()

        """ScreenShot - Taken"""
        self.driver.get_screenshot_as_file('C:/Users/sparsh/Desktop/New folder (2)/screenshot2.png')

        time.sleep(2)
        """Double clicking on report"""
        repo = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div[2]')
        action = ActionChains(self.driver)
        action.double_click(repo).perform()

        time.sleep(7)
        """ScreenShot - Taken"""
        self.driver.get_screenshot_as_file('C:/Users/sparsh/Desktop/New folder (2)/screenshot3.png')
        self.driver.save_screenshot("ReportNameStatus.png")
        report_display_1_upper = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[1]/table/tbody/tr[1]/td').text

        """Verify if smart reporting lower 1 displays"""
        report_display_1_lower = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[1]/table/tbody/tr[2]/td').text

        """Verify if smart reporting upper 2 display"""
        report_display_2_upper = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[1]/table/tbody/tr[1]/td').text

        """Verify if smart reporting lower 2 display"""
        report_display_2_lower = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[1]/table/tbody/tr[2]/td').text

        """Verify if smart reporting displays the mentioned reports"""
        smart_reporting_display_status = True

        if report_display_1_upper != kwargs['Report_display_1_upper']:
            smart_reporting_display_status = False
        elif report_display_1_lower != kwargs['Report_display_1_lower']:
            smart_reporting_display_status = False
        elif report_display_2_upper != kwargs['Report_display_2_upper']:
            smart_reporting_display_status = False
        elif report_display_2_lower != kwargs['Report_display_2_lower']:
            smart_reporting_display_status = False

        if smart_reporting_display_status == False:
            logger.info("Failed - Smart reporting displays are Failed to match")
        else:
            logger.info("Passed - Smart reporting displays are matched")

        return smart_reporting_display_status

    def work_order_status_names_columns(self, kwargs):
        logger.info("Execuitng work_order_status_names_columns()")
        window_before = self.driver.window_handles[0]
        self.driver.get_screenshot_as_file('C:/Users/sparsh/Desktop/New folder (2)/screenshot0.png')
        """ Clicking on Application"""
        appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
        appl.click()

        """Clicking on Smart Reporting -> Smart Reporting Console"""
        smrtrep = self.driver.find_element_by_link_text('Smart Reporting')
        smrtrep.click()
        smrtrepcon = self.driver.find_element_by_link_text('Smart Reporting Console')
        smrtrepcon.click()

        WebDriverWait(self.driver, 30).until(
            expected_conditions.number_of_windows_to_be(2))
        window_after = self.driver.window_handles[1]
        self.driver.switch_to.window(window_after)

        """ScreenShot - Taken"""
        self.driver.get_screenshot_as_file('C:/Users/sparsh/Desktop/New folder (2)/screenshot1.png')

        time.sleep(20)

        """All already clicked"""
        """Click H3G"""
        obj_h3g = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')
        obj_h3g.click()
        """click on Rebus Reports"""
        obj_rebus = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[2]/div[8]/div/div/div/div[2]')
        obj_rebus.click()

        """Search content"""
        send_repo = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/input')
        send_repo.send_keys(kwargs['Report_name'])

        search_icon = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/div[2]/div[2]/img')
        search_icon.click()

        """ScreenShot - Taken"""
        self.driver.get_screenshot_as_file('C:/Users/sparsh/Desktop/New folder (2)/screenshot2.png')

        time.sleep(2)
        """Double clicking on report"""
        repo = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div[2]')
        action = ActionChains(self.driver)
        action.double_click(repo).perform()

        time.sleep(7)
        """ScreenShot - Taken"""
        self.driver.get_screenshot_as_file('C:/Users/sparsh/Desktop/New folder (2)/screenshot3.png')
        self.driver.save_screenshot("ColumnNameStatus.png")
        """Verify coloumn for upper table"""
        priority1 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[1]/div').text

        total = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[2]/div').text

        assign = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[3]/div').text

        pending = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[4]/div').text

        waiting_approval = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[5]/div').text

        planning = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[6]/div').text

        in_progress = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[7]/div').text

        completed = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[8]/div').text

        cancelled = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[9]/div').text

        rejected = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[10]/div').text

        closed = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[11]/div').text

        """Verify coloumn for lower table"""
        support_org = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[2]/div/table/thead/tr/td[1]/div').text

        total2 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[2]/div/table/thead/tr/td[2]/div').text

        assign2 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[2]/div/table/thead/tr/td[3]/div').text

        pending2 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[2]/div/table/thead/tr/td[4]/div').text

        waiting_approval2 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[2]/div/table/thead/tr/td[5]/div').text

        planning2 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[2]/div/table/thead/tr/td[6]/div').text

        in_progress2 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[2]/div/table/thead/tr/td[7]/div').text

        completed2 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[2]/div/table/thead/tr/td[8]/div').text

        cancelled2 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[2]/div/table/thead/tr/td[9]/div').text

        rejected2 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[2]/div/table/thead/tr/td[10]/div').text

        closed2 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[2]/div/table/thead/tr/td[11]/div').text

        time.sleep(2)
        """Verify if the mentioned names & columns are available in the reports as in requirement sheet"""
        names_columns_status = True

        if priority1 != kwargs['column1']:
            names_columns_status = False
        elif total != kwargs['column2']:
            names_columns_status = False
        elif assign != kwargs['column3']:
            names_columns_status = False
        elif pending != kwargs['column4']:
            names_columns_status = False
        elif waiting_approval != kwargs['column5']:
            names_columns_status = False
        elif planning != kwargs['column6']:
            names_columns_status = False
        elif in_progress != kwargs['column7']:
            names_columns_status = False
        elif completed != kwargs['column8']:
            names_columns_status = False
        elif cancelled != kwargs['column9']:
            names_columns_status = False
        elif rejected != kwargs['column10']:
            names_columns_status = False
        elif closed != kwargs['column11']:
            names_columns_status = False
        elif support_org != kwargs['column2.1']:
            names_columns_status = False
        elif total2 != kwargs['column2.2']:
            names_columns_status = False
        elif assign2 != kwargs['column2.3']:
            names_columns_status = False
        elif pending2 != kwargs['column2.4']:
            names_columns_status = False
        elif waiting_approval2 != kwargs['column2.5']:
            names_columns_status = False
        elif planning2 != kwargs['column2.6']:
            names_columns_status = False
        elif in_progress2 != kwargs['column2.7']:
            names_columns_status = False
        elif completed2 != kwargs['column2.8']:
            names_columns_status = False
        elif cancelled2 != kwargs['column2.9']:
            names_columns_status = False
        elif rejected2 != kwargs['column2.10']:
            names_columns_status = False
        elif closed2 != kwargs['column2.11']:
            names_columns_status = False

        if names_columns_status == False:
            logger.info("Failed - The mentioned names & columns are not available in the report as in requirement")
        else:
            logger.info("Passed - The mentioned names & columns are available in the report as in requirement")

        return names_columns_status

    def work_order_priority_sorting_of_data(self, kwargs):
        logger.info("Execuitng work_order_priority_sorting_of_data()")
        window_before = self.driver.window_handles[0]
        """ Clicking on Application"""
        appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
        appl.click()

        """Clicking on Smart Reporting -> Smart Reporting Console"""
        smrtrep = self.driver.find_element_by_link_text('Smart Reporting')
        smrtrep.click()
        smrtrepcon = self.driver.find_element_by_link_text('Smart Reporting Console')
        smrtrepcon.click()

        WebDriverWait(self.driver, 10).until(expected_conditions.number_of_windows_to_be(2))
        time.sleep(10)
        window_after = self.driver.window_handles[1]
        self.driver.switch_to.window(window_after)

        time.sleep(20)
        """All already clicked"""
        """Click H3G"""
        obj_h3g = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')
        obj_h3g.click()
        """click on Rebus Reports"""
        obj_rebus = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[2]/div[8]/div/div/div/div[2]')
        obj_rebus.click()

        """Search content"""
        send_repo = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/input')  # search field
        send_repo.send_keys(kwargs['report_name'])
        time.sleep(2)
        send_repo.send_keys(Keys.ENTER)

        time.sleep(3)

        """Double clicking on report"""
        repo = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div[2]')
        action = ActionChains(self.driver)
        action.double_click(repo).perform()

        time.sleep(5)

        """Verify the sorting of data in the reports mentioned"""

        """Creating Python List"""
        List = []

        time.sleep(2)
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN1.png")
        """Getting table xpath"""
        table = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/table/tbody/tr/td[1]/div/table')

        """counting number of rows in table"""
        count = 0
        for i in table.find_elements_by_tag_name('tr'):
            count += 1

        logger.info("Number of row in table = {}".format(count))

        logger.info("started executing period")
        time.sleep(5)
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/table/tbody/tr/td[1]/div/table/thead/tr/td[1]/img')))
        """ascending"""
        self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/table/tbody/tr/td[1]/div/table/thead/tr/td[1]/img').click()  # priority image
        self.driver.find_element_by_xpath('html/body/ul/li[2]/div').click()  # sort

        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN2.png")

        self.driver.find_element_by_xpath('html/body/ul/li[2]/ul/li[2]/div[2]').click()  # ascending

        time.sleep(3)
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN3.png")

        for i in range(1, count):
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/table/tbody/tr/td[1]/div/table/tbody/tr[{}]/td[1]'.format(
                                                                                                  i))))
            List.append(self.driver.find_element_by_xpath(
                '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/table/tbody/tr/td[1]/div/table/tbody/tr[{}]/td[1]'.format(
                    i)).text)
        List.pop()
        logger.info("List = {}".format(List))
        """Checking whether list is ascending order or not"""
        period_colm_asc_status = False

        """Converting list's element in integer"""
        List = list(filter(None, List))  # Using filter to remove NULL values

        for i in range(len(List)):
            List[i] = List[i].encode('ASCII')

        if self.listSortedOrNot(List):
            period_colm_asc_status = True

        del List[0:len(List)]

        """descending"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/table/tbody/tr/td[1]/div/table/thead/tr/td[1]/img')))
        self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/table/tbody/tr/td[1]/div/table/thead/tr/td[1]/img').click()  # priority image
        self.driver.find_element_by_xpath('html/body/ul/li[2]/div[2]').click()  # sort
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN4.png")

        self.driver.find_element_by_xpath('html/body/ul/li[2]/ul/li[3]/div[2]').click()  # Descending

        time.sleep(3)
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN5.png")
        for i in range(1, count):
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/table/tbody/tr/td[1]/div/table/tbody/tr[{}]/td[1]'.format(
                                                                                                  i))))
            List.append(self.driver.find_element_by_xpath(
                '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/table/tbody/tr/td[1]/div/table/tbody/tr[{}]/td[1]'.format(
                    i)).text)
        List.pop()
        logger.info("List decending = {}".format(List))

        """Checking whether list is descending order or not"""
        List.sort()
        period_colm_desc_status = False

        logger.info("List = {}".format(List))

        """Converting list's element in integer"""
        List = list(filter(None, List))  # Using filter to remove NULL values

        logger.info("List = {}".format(List))

        for i in range(len(List)):
            List[i] = List[i].encode('ASCII')

        if self.listSortedOrNot(List):
            period_colm_desc_status = True

        del List[0:len(List)]

        logger.info("finished executing period")

        logger.info("started executing priority")

        """ascending"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/table/tbody/tr/td[1]/div/table/thead/tr/td[2]/img')))
        self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/table/tbody/tr/td[1]/div/table/thead/tr/td[2]/img').click()  # total image
        self.driver.find_element_by_xpath('html/body/ul/li[2]/div').click()  # sort
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN6.png")
        self.driver.find_element_by_xpath('html/body/ul/li[2]/ul/li[2]/div[2]').click()  # ascending

        time.sleep(3)
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN7.png")
        for i in range(1, count):
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/table/tbody/tr/td[1]/div/table/tbody/tr[{}]/td[2]'.format(
                                                                                                  i))))
            List.append(self.driver.find_element_by_xpath(
                '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/table/tbody/tr/td[1]/div/table/tbody/tr[{}]/td[2]'.format(
                    i)).text)
        List.pop()
        logger.info("list - {}".format(List))

        """Checking whether list is ascending order or not"""
        priority_colm_asc_status = False

        """Converting list's element in integer"""
        List = list(filter(None, List))  # Using filter to remove NULL values

        for i in range(len(List)):
            List[i] = List[i].encode('ASCII')

        if self.listSortedOrNot(List):
            priority_colm_asc_status = True
        logger.info(" status - {}".format(priority_colm_asc_status))

        del List[0:len(List)]

        """descending"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/table/tbody/tr/td[1]/div/table/thead/tr/td[2]/img')))
        self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/table/tbody/tr/td[1]/div/table/thead/tr/td[2]/img').click()  # total image

        self.driver.find_element_by_xpath('html/body/ul/li[2]/div[2]').click()  # sort
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN8.png")
        self.driver.find_element_by_xpath('html/body/ul/li[2]/ul/li[3]/div[2]').click()  # descending

        time.sleep(3)
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN9.png")
        for i in range(1, count):
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/table/tbody/tr/td[1]/div/table/tbody/tr[{}]/td[2]'.format(
                                                                                                  i))))
            List.append(self.driver.find_element_by_xpath(
                '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/table/tbody/tr/td[1]/div/table/tbody/tr[{}]/td[2]'.format(
                    i)).text)
        List.pop()
        """Checking whether list is ascending order or not"""
        List.sort()
        priority_colm_desc_status = False

        """Encoded list's element from unicode to string"""
        List = list(filter(None, List))  # Using filter to remove NULL values

        for i in range(len(List)):
            List[i] = List[i].encode('ASCII')

        if self.listSortedOrNot(List):
            priority_colm_desc_status = True

        del List[0:len(List)]

        logger.info("finished executing priority")

        logger.info("started executing incoming")

        """ascending"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/table/tbody/tr/td[1]/div/table/thead/tr/td[3]/img')))
        self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/table/tbody/tr/td[1]/div/table/thead/tr/td[3]/img').click()  # system mgmt image

        self.driver.find_element_by_xpath('html/body/ul/li[2]/div').click()  # sort

        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN10.png")
        assign2 = self.driver.find_element_by_xpath('html/body/ul/li[2]/ul/li[2]/div[2]')
        assign2.click()  # ascending

        time.sleep(3)
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN11.png")
        for i in range(1, count):
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/table/tbody/tr/td[1]/div/table/tbody/tr[{}]/td[3]'.format(
                                                                                                  i))))
            List.append(self.driver.find_element_by_xpath(
                '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/table/tbody/tr/td[1]/div/table/tbody/tr[{}]/td[3]'.format(
                    i)).text)
        List.pop()
        """Checking whether list is ascending order or not"""
        incoming_colm_asc_status = False

        """Converting list's element in integer"""
        List = list(filter(None, List))  # Using filter to remove NULL values

        for i in range(len(List)):
            List[i] = List[i].encode('ASCII')
            # List[i] = str(List[i])
            List[i] = int(List[i])

        if self.listSortedOrNot(List):
            incoming_colm_asc_status = True
        logger.info("List = {}".format(List))
        del List[0:len(List)]

        """descending"""
        time.sleep(5)
        self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/table/tbody/tr/td[1]/div/table/thead/tr/td[3]/img').click()  # system mgmt image

        self.driver.find_element_by_xpath('html/body/ul/li[2]/div[2]').click()  # sort

        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN12.png")
        self.driver.find_element_by_xpath('html/body/ul/li[2]/ul/li[3]/div[2]').click()  # decending

        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN13.png")

        for i in range(1, count):
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/table/tbody/tr/td[1]/div/table/tbody/tr[{}]/td[3]'.format(
                                                                                                  i))))
            List.append(self.driver.find_element_by_xpath(
                './/*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/table/tbody/tr/td[1]/div/table/tbody/tr[{}]/td[3]'.format(
                    i)).text)
        List.pop()
        """Checking whether list is ascending order or not"""
        List.sort()

        incoming_colm_desc_status = False

        """Converting list's element in integer"""
        List = list(filter(None, List))  # Using filter to remove NULL values
        for i in range(len(List)):
            List[i] = List[i].encode('ASCII')

        if self.listSortedOrNot(List):
            incoming_colm_desc_status = True
        logger.info("List = {}".format(List))
        del List[0:len(List)]

        logger.info("finished executing incoming")

        logger.info("started executing resolved")
        """ascending"""
        time.sleep(5)
        self.driver.find_element_by_xpath(
            './/*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/table/tbody/tr/td[1]/div/table/thead/tr/td[4]/img').click()  # self service and web image
        self.driver.find_element_by_xpath('html/body/ul/li[2]/div').click()  # sort
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN14.png")

        assign1 = self.driver.find_element_by_xpath('html/body/ul/li[2]/ul/li[2]/div[2]')
        assign1.click()  # ascending

        time.sleep(3)
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN15.png")

        for i in range(1, count):
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/table/tbody/tr/td[1]/div/table/tbody/tr[{}]/td[4]'.format(
                                                                                                  i))))
            List.append(self.driver.find_element_by_xpath(
                './/*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/table/tbody/tr/td[1]/div/table/tbody/tr[{}]/td[4]'.format(
                    i)).text)

        """Checking whether list is ascending order or not"""
        resolved_colm_asc_status = False

        List.pop()
        """Converting list's element in integer"""
        List = list(filter(None, List))  # Using filter to remove NULL values

        for i in range(len(List)):
            List[i] = List[i].encode('ASCII')
            # List[i] = str(List[i])
            List[i] = int(List[i])
        if self.listSortedOrNot(List):
            resolved_colm_asc_status = True
        logger.info("List = {}".format(List))
        del List[0:len(List)]

        """descending"""
        time.sleep(5)
        self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/table/tbody/tr/td[1]/div/table/thead/tr/td[4]/img').click()  # self service and web image
        self.driver.find_element_by_xpath('/html/body/ul/li[2]/div[2]').click()  # sort
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN16.png")

        self.driver.find_element_by_xpath('/html/body/ul/li[2]/ul/li[3]/div[2]').click()  # decending

        time.sleep(3)
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN17.png")

        for i in range(1, count):
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              './/*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/table/tbody/tr/td[1]/div/table/tbody/tr[{}]/td[4]'.format(
                                                                                                  i))))
            List.append(self.driver.find_element_by_xpath(
                './/*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/table/tbody/tr/td[1]/div/table/tbody/tr[{}]/td[4]'.format(
                    i)).text)

        """Checking whether list is ascending order or not"""
        List.pop()
        List.sort()
        resolved_colm_desc_status = False

        """Converting list's element in integer"""
        List = list(filter(None, List))  # Using filter to remove NULL values

        for i in range(len(List)):
            List[i] = List[i].encode('ASCII')

        if self.listSortedOrNot(List):
            resolved_colm_desc_status = True
        logger.info("List = {}".format(List))
        del List[0:len(List)]

        logger.info("finished executing resloved")

        logger.info("started executing lacklogs")
        time.sleep(5)
        """ascending"""
        self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/table/tbody/tr/td[1]/div/table/thead/tr/td[5]/img').click()  # total image
        self.driver.find_element_by_xpath('/html/body/ul/li[2]/div').click()  # sort
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN18.png")

        self.driver.find_element_by_xpath('/html/body/ul/li[2]/ul/li[2]/div[2]').click()  # ascending

        time.sleep(3)
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN19.png")

        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/table/tbody/tr/td[1]/div/table/tbody/tr[{}]/td[5]'.format(
                                                                                              i))))
        List.append(self.driver.find_element_by_xpath(
            './/*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/table/tbody/tr/td[1]/div/table/tbody/tr[{}]/td[5]'.format(
                i)).text)
        List.pop()
        """Checking whether list is ascending order or not"""

        backlogs_colm_asc_status = False
        """Converting list's element in integer"""
        List = list(filter(None, List))  # Using filter to remove NULL values

        for i in range(len(List)):
            List[i] = List[i].encode('ASCII')
            List[i] = str(List[i])
            List[i] = int(List[i])

        if self.listSortedOrNot(List):
            backlogs_colm_asc_status = True

        del List[0:len(List)]

        """descending"""
        time.sleep(5)
        self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/table/tbody/tr/td[1]/div/table/thead/tr/td[5]/img').click()
        self.driver.find_element_by_xpath('/html/body/ul/li[2]/div[2]').click()  # sort
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN20.png")

        self.driver.find_element_by_xpath('/html/body/ul/li[2]/ul/li[3]/div[2]').click()

        time.sleep(3)
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN21.png")

        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/table/tbody/tr/td[1]/div/table/tbody/tr[{}]/td[5]'.format(
                                                                                              i))))
        List.append(self.driver.find_element_by_xpath(
            './/*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/table/tbody/tr/td[1]/div/table/tbody/tr[{}]/td[5]'.format(
                i)).text)
        List.pop()
        """Checking whether list is ascending order or not"""
        List.sort()
        backlogs_colm_desc_status = False

        """Converting list's element in integer"""
        List = list(filter(None, List))  # Using filter to remove NULL values

        for i in range(len(List)):
            List[i] = List[i].encode('ASCII')

        if self.listSortedOrNot(List):
            backlogs_colm_desc_status = True

        del List[0:len(List)]

        logger.info("finished executing backlogs")

        """Printing status messages on Logger.info()"""

        tables_sorting_data_status = False

        if period_colm_asc_status and period_colm_desc_status and priority_colm_asc_status and priority_colm_desc_status and incoming_colm_asc_status and incoming_colm_desc_status and resolved_colm_asc_status and resolved_colm_desc_status and backlogs_colm_asc_status and backlogs_colm_desc_status:
            tables_sorting_data_status = True
            logger.info("Passed - The sorting of data in the reports mentioned are verified")
        else:
            logger.info("Failed - The sorting of data in the reports mentioned are not verified")
            if period_colm_asc_status == False:
                logger.info("Failed - Period column is not in Ascending order")
            if period_colm_desc_status == False:
                logger.info("Failed - Period column is not in Descending order")
            if priority_colm_asc_status == False:
                logger.info("Failed - Priority column is not in Ascending order")
            if priority_colm_desc_status == False:
                logger.info("Failed - Priority column is not in Descending order")
            if incoming_colm_asc_status == False:
                logger.info("Failed - Incoming column is not in Ascending order")
            if incoming_colm_desc_status == False:
                logger.info("Failed - Incoming column is not in Descending order")
            if resolved_colm_asc_status == False:
                logger.info("Failed - Resolved column is not in Ascending order")
            if resolved_colm_desc_status == False:
                logger.info("Failed - Resolved  column is not in Descending order")
            if backlogs_colm_asc_status == False:
                logger.info("Failed - Backlogs column is not in Ascending order")
            if backlogs_colm_desc_status == False:
                logger.info("Failed - Backlogs column is not in Descending order")

        return tables_sorting_data_status

    def work_order_status_sorting_of_data(self, kwargs):
        logger.info("Execuitng work_order_status_sorting_of_data()")
        window_before = self.driver.window_handles[0]
        """ Clicking on Application"""
        appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
        appl.click()
        """Clicking on Smart Reporting -> Smart Reporting Console"""
        smrtrep = self.driver.find_element_by_link_text('Smart Reporting')
        smrtrep.click()
        smrtrepcon = self.driver.find_element_by_link_text('Smart Reporting Console')
        smrtrepcon.click()

        WebDriverWait(self.driver, 30).until(
            expected_conditions.number_of_windows_to_be(2))
        window_after = self.driver.window_handles[1]
        self.driver.switch_to.window(window_after)

        time.sleep(20)

        """Click H3G"""
        obj_h3g = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')
        obj_h3g.click()
        """click on Rebus Reports"""
        obj_rebus = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[2]/div[8]/div/div/div/div[2]')
        obj_rebus.click()

        """Search content"""
        send_repo = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/input')  # search field
        send_repo.send_keys(kwargs['report_name'])
        time.sleep(2)
        send_repo.send_keys(Keys.ENTER)
        time.sleep(2)
        """ScreenShot"""
        self.driver.save_screenshot("VPN1.png")

        """Double clicking on report"""
        repo = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div[2]')
        action = ActionChains(self.driver)
        action.double_click(repo).perform()

        time.sleep(6)
        """ScreenShot"""
        self.driver.save_screenshot("VPN2.png")

        """Creating Python List"""
        List = []

        time.sleep(7)
        """Getting table xpath"""
        table = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table')

        """counting number of rows in table"""
        count = 0
        for i in table.find_elements_by_tag_name('tr'):
            count += 1

        logger.info("Number of row in table = {}".format(count))

        logger.info("started executing Priority")

        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[1]/img')))
        """ascending"""
        self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[1]/img').click()  # priority image
        self.driver.find_element_by_xpath('html/body/ul/li[2]/div').click()  # sort

        """ScreenShot"""
        self.driver.save_screenshot("VPN3.png")

        self.driver.find_element_by_xpath('html/body/ul/li[2]/ul/li[2]/div[2]').click()  # ascending

        time.sleep(3)
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN4.png")

        for i in range(1, count):
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[1]'.format(
                                                                                                  i))))
            List.append(self.driver.find_element_by_xpath(
                '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[1]'.format(
                    i)).text)
        List.pop()
        logger.info("List = {}".format(List))
        """Checking whether list is ascending order or not"""
        priority_colm_asc_status = False

        """Converting list's element in integer"""
        List = list(filter(None, List))  # Using filter to remove NULL values

        for i in range(len(List)):
            List[i] = List[i].encode('ASCII')

        if self.listSortedOrNot(List):
            priority_colm_asc_status = True

        del List[0:len(List)]

        """descending"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[1]/img')))
        self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[1]/img').click()  # priority image
        self.driver.find_element_by_xpath('html/body/ul/li[2]/div[2]').click()  # sort
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN5.png")

        self.driver.find_element_by_xpath('html/body/ul/li[2]/ul/li[3]/div[2]').click()  # Descending

        time.sleep(3)
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN6.png")

        for i in range(1, count):
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[1]'.format(
                                                                                                  i))))
            List.append(self.driver.find_element_by_xpath(
                '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[1]'.format(
                    i)).text)
        List.pop()

        """Checking whether list is descending order or not"""
        List.sort()
        priority_colm_desc_status = False

        logger.info("List = {}".format(List))

        """Converting list's element in integer"""
        List = list(filter(None, List))  # Using filter to remove NULL values

        logger.info("List = {}".format(List))

        for i in range(len(List)):
            List[i] = List[i].encode('ASCII')

        if self.listSortedOrNot(List):
            priority_colm_desc_status = True

        del List[0:len(List)]

        logger.info("finished executing priority")

        logger.info("started executing total")

        """ascending"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[2]/img')))
        self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[2]/img').click()  # total image
        self.driver.find_element_by_xpath('html/body/ul/li[2]/div').click()  # sort
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN7.png")
        self.driver.find_element_by_xpath('html/body/ul/li[2]/ul/li[2]/div[2]').click()  # ascending

        time.sleep(3)
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN8.png")
        for i in range(1, count):
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[2]'.format(
                                                                                                  i))))
            List.append(self.driver.find_element_by_xpath(
                '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[2]'.format(
                    i)).text)
        List.pop()

        """Checking whether list is ascending order or not"""
        total_colm_asc_status = False

        """Converting list's element in integer"""
        List = list(filter(None, List))  # Using filter to remove NULL values

        for i in range(len(List)):
            List[i] = List[i].encode('ASCII')
            List[i] = int(List[i])

        if self.listSortedOrNot(List):
            total_colm_asc_status = True

        del List[0:len(List)]

        """descending"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[2]/img')))
        self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[2]/img').click()  # total image

        self.driver.find_element_by_xpath('html/body/ul/li[2]/div[2]').click()  # sort
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN9.png")
        self.driver.find_element_by_xpath('html/body/ul/li[2]/ul/li[3]/div[2]').click()  # descending

        time.sleep(3)
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN10.png")
        for i in range(1, count):
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[2]'.format(
                                                                                                  i))))
            List.append(self.driver.find_element_by_xpath(
                '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[2]'.format(
                    i)).text)
        List.pop()
        logger.info("List = {}".format(List))
        """Checking whether list is ascending order or not"""
        List.sort()
        total_colm_desc_status = False

        """Encoded list's element from unicode to string"""
        List = list(filter(None, List))  # Using filter to remove NULL values

        for i in range(len(List)):
            List[i] = List[i].encode('ASCII')

        if self.listSortedOrNot(List):
            total_colm_desc_status = True

        del List[0:len(List)]

        logger.info("finished executing total")

        logger.info("started executing assigned")

        """ascending"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[3]/img')))
        self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[3]/img').click()  # system mgmt image

        self.driver.find_element_by_xpath('html/body/ul/li[2]/div').click()  # sort

        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN11.png")
        ass = self.driver.find_element_by_xpath('html/body/ul/li[2]/ul/li[2]/div[2]')
        ass.click()  # ascending
        time.sleep(4)
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN12.png")
        for i in range(1, count):
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[3]'.format(
                                                                                                  i))))
            List.append(self.driver.find_element_by_xpath(
                '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[3]'.format(
                    i)).text)
        List.pop()
        """Checking whether list is ascending order or not"""
        assigned_colm_asc_status = False

        """Converting list's element in integer"""
        List = list(filter(None, List))  # Using filter to remove NULL values

        for i in range(len(List)):
            List[i] = List[i].encode('ASCII')
            List[i] = str(List[i])
            List[i] = int(List[i])

        if self.listSortedOrNot(List):
            assigned_colm_asc_status = True
        logger.info("List = {}".format(List))
        del List[0:len(List)]

        """descending"""
        time.sleep(5)
        self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[3]/img').click()  # system mgmt image

        self.driver.find_element_by_xpath('html/body/ul/li[2]/div[2]').click()  # sort

        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN13.png")
        self.driver.find_element_by_xpath('html/body/ul/li[2]/ul/li[3]/div[2]').click()  # decending
        time.sleep(3)
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN14.png")

        for i in range(1, count):
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[3]'.format(
                                                                                                  i))))
            List.append(self.driver.find_element_by_xpath(
                '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[3]'.format(
                    i)).text)
        List.pop()
        logger.info("List = {}".format(List))
        """Checking whether list is ascending order or not"""
        List.sort()

        assigned_colm_desc_status = False

        """Converting list's element in integer"""
        List = list(filter(None, List))  # Using filter to remove NULL values
        for i in range(len(List)):
            List[i] = List[i].encode('ASCII')

        if self.listSortedOrNot(List):
            assigned_colm_desc_status = True
        del List[0:len(List)]

        logger.info("finished executing assigned")

        logger.info("started executing pending")

        """ascending"""
        time.sleep(5)
        self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[4]/img').click()  # self service and web image
        self.driver.find_element_by_xpath('html/body/ul/li[2]/div').click()  # sort
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN15.png")

        self.driver.find_element_by_xpath('html/body/ul/li[2]/ul/li[2]/div[2]').click()  # ascending

        time.sleep(3)
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN16.png")

        for i in range(1, count):
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[4]'.format(
                                                                                                  i))))
            List.append(self.driver.find_element_by_xpath(
                '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[4]'.format(
                    i)).text)

        """Checking whether list is ascending order or not"""
        pending_colm_asc_status = False

        List.pop()
        """Converting list's element in integer"""
        List = list(filter(None, List))  # Using filter to remove NULL values

        for i in range(len(List)):
            List[i] = List[i].encode('ASCII')
            List[i] = str(List[i])
            List[i] = int(List[i])

        if self.listSortedOrNot(List):
            pending_colm_asc_status = True
        logger.info("List = {}".format(List))
        del List[0:len(List)]

        """descending"""
        time.sleep(5)
        self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[4]/img').click()  # self service and web image
        self.driver.find_element_by_xpath('/html/body/ul/li[2]/div[2]').click()  # sort
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN17.png")

        self.driver.find_element_by_xpath('/html/body/ul/li[2]/ul/li[3]/div[2]').click()  # decending

        time.sleep(3)
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN18.png")
        for i in range(1, count):
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[4]'.format(
                                                                                                  i))))
            List.append(self.driver.find_element_by_xpath(
                '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[4]'.format(
                    i)).text)

        """Checking whether list is ascending order or not"""
        List.pop()
        List.sort()
        pending_colm_desc_status = False

        """Converting list's element in integer"""
        List = list(filter(None, List))  # Using filter to remove NULL values

        for i in range(len(List)):
            List[i] = List[i].encode('ASCII')

        if self.listSortedOrNot(List):
            pending_colm_desc_status = True
        logger.info("List = {}".format(List))
        del List[0:len(List)]

        logger.info("finished executing pending")

        logger.info("started executing waiting approval")
        time.sleep(5)
        """ascending"""
        self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[5]/img').click()  # total image
        self.driver.find_element_by_xpath('/html/body/ul/li[2]/div').click()  # sort
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN19.png")

        self.driver.find_element_by_xpath('/html/body/ul/li[2]/ul/li[2]/div[2]').click()  # ascending

        time.sleep(3)
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN20.png")

        for i in range(1, count):
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[5]'.format(
                                                                                                  i))))
            List.append(self.driver.find_element_by_xpath(
                '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[1]/td[5]'.format(
                    i)).text)
        List.pop()
        """Checking whether list is ascending order or not"""

        waiting_approval_colm_asc_status = False
        """Converting list's element in integer"""
        List = list(filter(None, List))  # Using filter to remove NULL values

        for i in range(len(List)):
            List[i] = List[i].encode('ASCII')
            List[i] = str(List[i])
            List[i] = int(List[i])

        if self.listSortedOrNot(List):
            waiting_approval_colm_asc_status = True

        del List[0:len(List)]

        """descending"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[5]/img')))
        self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[5]/img').click()  # total image
        self.driver.find_element_by_xpath('/html/body/ul/li[2]/div[2]').click()  # sort
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN21.png")
        self.driver.find_element_by_xpath('/html/body/ul/li[2]/ul/li[3]/div[2]').click()  # ascending

        time.sleep(3)
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN22.png")

        for i in range(1, count):
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[5]'.format(
                                                                                                  i))))
            List.append(self.driver.find_element_by_xpath(
                '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[5]'.format(
                    i)).text)
        List.pop()
        """Checking whether list is ascending order or not"""
        List.sort()
        waiting_approval_colm_desc_status = False

        """Converting list's element in integer"""
        List = list(filter(None, List))  # Using filter to remove NULL values

        for i in range(len(List)):
            List[i] = List[i].encode('ASCII')

        if self.listSortedOrNot(List):
            waiting_approval_colm_desc_status = True

        del List[0:len(List)]

        logger.info("finished executing waiting approval")

        logger.info("started executing planning")

        """ascending"""
        time.sleep(5)
        self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[6]/img').click()  # self service and web image
        self.driver.find_element_by_xpath('html/body/ul/li[2]/div').click()  # sort
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN23.png")

        self.driver.find_element_by_xpath('html/body/ul/li[2]/ul/li[2]/div[2]').click()  # ascending

        time.sleep(5)
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN24.png")

        for i in range(1, count):
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[6]'.format(
                                                                                                  i))))
            List.append(self.driver.find_element_by_xpath(
                '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[6]'.format(
                    i)).text)

        """Checking whether list is ascending order or not"""
        planning_colm_asc_status = False

        List.pop()

        """Converting list's element in integer"""
        List = list(filter(None, List))  # Using filter to remove NULL values

        for i in range(len(List)):
            List[i] = List[i].encode('ASCII')
            # List[i] = str(List[i])
            List[i] = int(List[i])

        if self.listSortedOrNot(List):
            planning_colm_asc_status = True
        logger.info("List = {}".format(List))
        del List[0:len(List)]

        """descending"""
        time.sleep(5)
        self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[6]/img').click()  # self service and web image
        self.driver.find_element_by_xpath('/html/body/ul/li[2]/div[2]').click()  # sort
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN25.png")

        self.driver.find_element_by_xpath('/html/body/ul/li[2]/ul/li[3]/div[2]').click()  # decending

        time.sleep(3)
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN26.png")

        for i in range(1, count):
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[6]'.format(
                                                                                                  i))))
            List.append(self.driver.find_element_by_xpath(
                '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[6]'.format(
                    i)).text)

        """Checking whether list is ascending order or not"""
        List.pop()
        List.sort()
        planning_colm_desc_status = False

        """Converting list's element in integer"""
        List = list(filter(None, List))  # Using filter to remove NULL values

        for i in range(len(List)):
            List[i] = List[i].encode('ASCII')

        if self.listSortedOrNot(List):
            planning_colm_desc_status = True
        logger.info("List = {}".format(List))
        del List[0:len(List)]

        logger.info("finished executing planning")

        logger.info("started executing in progress")

        """ascending"""
        time.sleep(5)
        self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[7]/img').click()  # self service and web image
        self.driver.find_element_by_xpath('html/body/ul/li[2]/div').click()  # sort
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN27.png")

        self.driver.find_element_by_xpath('html/body/ul/li[2]/ul/li[2]/div[2]').click()  # ascending

        time.sleep(3)
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN28.png")

        for i in range(1, count):
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[7]'.format(
                                                                                                  i))))
            List.append(self.driver.find_element_by_xpath(
                '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[7]'.format(
                    i)).text)

        """Checking whether list is ascending order or not"""
        in_progress_colm_asc_status = False

        List.pop()

        """Converting list's element in integer"""
        List = list(filter(None, List))  # Using filter to remove NULL values

        for i in range(len(List)):
            List[i] = List[i].encode('ASCII')
            # List[i] = str(List[i])
            List[i] = int(List[i])

        if self.listSortedOrNot(List):
            in_progress_colm_asc_status = True
        logger.info("List = {}".format(List))
        del List[0:len(List)]

        """descending"""
        time.sleep(5)
        self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[7]/img').click()  # self service and web image
        self.driver.find_element_by_xpath('/html/body/ul/li[2]/div[2]').click()  # sort
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN29.png")

        self.driver.find_element_by_xpath('/html/body/ul/li[2]/ul/li[3]/div[2]').click()  # decending

        time.sleep(3)
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN30.png")

        for i in range(1, count):
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[7]'.format(
                                                                                                  i))))
            List.append(self.driver.find_element_by_xpath(
                '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[7]'.format(
                    i)).text)

        """Checking whether list is ascending order or not"""
        List.pop()
        List.sort()
        in_progress_colm_desc_status = False

        """Converting list's element in integer"""
        List = list(filter(None, List))  # Using filter to remove NULL values

        for i in range(len(List)):
            List[i] = List[i].encode('ASCII')

        if self.listSortedOrNot(List):
            in_progress_colm_desc_status = True
        logger.info("List = {}".format(List))
        del List[0:len(List)]

        logger.info("finished executing in progress")

        logger.info("started executing completed")
        """ascending"""
        time.sleep(5)
        self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[8]/img').click()  # self service and web image
        self.driver.find_element_by_xpath('html/body/ul/li[2]/div').click()  # sort
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN31.png")

        assign1 = self.driver.find_element_by_xpath('html/body/ul/li[2]/ul/li[2]/div[2]')
        assign1.click()  # ascending

        time.sleep(4)
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN32.png")
        for i in range(1, count):
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[8]'.format(
                                                                                                  i))))
            List.append(self.driver.find_element_by_xpath(
                '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[8]'.format(
                    i)).text)

        """Checking whether list is ascending order or not"""
        completed_colm_asc_status = False

        List.pop()

        """Converting list's element in integer"""
        List = list(filter(None, List))  # Using filter to remove NULL values

        for i in range(len(List)):
            List[i] = List[i].encode('ASCII')
            # List[i] = str(List[i])
            List[i] = int(List[i])

        if self.listSortedOrNot(List):
            completed_colm_asc_status = True
        logger.info("List = {}".format(List))
        del List[0:len(List)]

        """descending"""
        time.sleep(5)
        self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[8]/img').click()  # self service and web image
        self.driver.find_element_by_xpath('/html/body/ul/li[2]/div[2]').click()  # sort
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN33.png")
        self.driver.find_element_by_xpath('/html/body/ul/li[2]/ul/li[3]/div[2]').click()  # decending

        time.sleep(3)
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN34.png")
        for i in range(1, count):
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[8]'.format(
                                                                                                  i))))
            List.append(self.driver.find_element_by_xpath(
                '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[8]'.format(
                    i)).text)

        """Checking whether list is ascending order or not"""
        List.pop()
        List.sort()
        completed_colm_desc_status = False

        """Converting list's element in integer"""
        List = list(filter(None, List))  # Using filter to remove NULL values

        for i in range(len(List)):
            List[i] = List[i].encode('ASCII')

        if self.listSortedOrNot(List):
            completed_colm_desc_status = True
        logger.info("List = {}".format(List))
        del List[0:len(List)]

        logger.info("finished executing completed")

        logger.info("started executing cancelled")

        """ascending"""
        time.sleep(5)
        self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[9]/img').click()  # self service and web image
        self.driver.find_element_by_xpath('html/body/ul/li[2]/div').click()  # sort
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN35.png")

        self.driver.find_element_by_xpath('html/body/ul/li[2]/ul/li[2]/div[2]').click()  # ascending

        time.sleep(3)
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN36.png")
        for i in range(1, count):
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[9]'.format(
                                                                                                  i))))
            List.append(self.driver.find_element_by_xpath(
                '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[9]'.format(
                    i)).text)

        """Checking whether list is ascending order or not"""
        cancelled_colm_asc_status = False

        List.pop()

        """Converting list's element in integer"""
        List = list(filter(None, List))  # Using filter to remove NULL values

        for i in range(len(List)):
            List[i] = List[i].encode('ASCII')
            # List[i] = str(List[i])
            List[i] = int(List[i])

        if self.listSortedOrNot(List):
            cancelled_colm_asc_status = True
        logger.info("List = {}".format(List))
        del List[0:len(List)]

        """descending"""
        time.sleep(5)
        self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[9]/img').click()  # self service and web image
        self.driver.find_element_by_xpath('/html/body/ul/li[2]/div[2]').click()  # sort
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN37.png")

        self.driver.find_element_by_xpath('/html/body/ul/li[2]/ul/li[3]/div[2]').click()  # decending

        time.sleep(3)
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN38.png")
        for i in range(1, count):
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[9]'.format(
                                                                                                  i))))
            List.append(self.driver.find_element_by_xpath(
                '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[9]'.format(
                    i)).text)

        """Checking whether list is ascending order or not"""
        List.pop()
        List.sort()
        cancelled_colm_desc_status = False

        """Converting list's element in integer"""
        List = list(filter(None, List))  # Using filter to remove NULL values

        for i in range(len(List)):
            List[i] = List[i].encode('ASCII')

        if self.listSortedOrNot(List):
            cancelled_colm_desc_status = True
        logger.info("List = {}".format(List))
        del List[0:len(List)]

        logger.info("finished executing cancelled")

        logger.info("started executing rejected")

        """ascending"""
        time.sleep(5)
        self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[10]/img').click()  # self service and web image
        self.driver.find_element_by_xpath('html/body/ul/li[2]/div').click()  # sort
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN39.png")
        assign2 = self.driver.find_element_by_xpath('html/body/ul/li[2]/ul/li[2]/div[2]')
        assign2.click()  # ascending

        time.sleep(4)
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN40.png")
        for i in range(1, count):
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[10]'.format(
                                                                                                  i))))
            List.append(self.driver.find_element_by_xpath(
                '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[10]'.format(
                    i)).text)

        """Checking whether list is ascending order or not"""
        rejected_colm_asc_status = False

        List.pop()

        """Converting list's element in integer"""
        List = list(filter(None, List))  # Using filter to remove NULL values

        for i in range(len(List)):
            List[i] = List[i].encode('ASCII')
            # List[i] = str(List[i])
            List[i] = int(List[i])
        if self.listSortedOrNot(List):
            rejected_colm_asc_status = True
        logger.info("List = {}".format(List))
        del List[0:len(List)]

        """descending"""
        time.sleep(5)
        self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[10]/img').click()  # self service and web image
        self.driver.find_element_by_xpath('/html/body/ul/li[2]/div[2]').click()  # sort
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN41.png")

        self.driver.find_element_by_xpath('/html/body/ul/li[2]/ul/li[3]/div[2]').click()  # decending

        time.sleep(3)
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN42.png")
        for i in range(1, count):
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[10]'.format(
                                                                                                  i))))
            List.append(self.driver.find_element_by_xpath(
                '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[10]'.format(
                    i)).text)

        """Checking whether list is ascending order or not"""
        List.pop()
        List.sort()
        rejected_colm_desc_status = False

        """Converting list's element in integer"""
        List = list(filter(None, List))  # Using filter to remove NULL values

        for i in range(len(List)):
            List[i] = List[i].encode('ASCII')

        if self.listSortedOrNot(List):
            rejected_colm_desc_status = True
        logger.info("List = {}".format(List))
        del List[0:len(List)]

        logger.info("finished executing rejected")

        logger.info("started executing closed")
        """ascending"""
        time.sleep(5)
        self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[11]/img').click()  # self service and web image
        self.driver.find_element_by_xpath('html/body/ul/li[2]/div').click()  # sort
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN43.png")

        self.driver.find_element_by_xpath('html/body/ul/li[2]/ul/li[2]/div[2]').click()  # ascending

        time.sleep(3)
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN44.png")
        for i in range(1, count):
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[11]'.format(
                                                                                                  i))))
            List.append(self.driver.find_element_by_xpath(
                '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[11]'.format(
                    i)).text)

        """Checking whether list is ascending order or not"""
        closed_colm_asc_status = False

        List.pop()

        """Converting list's element in integer"""
        List = list(filter(None, List))  # Using filter to remove NULL values

        for i in range(len(List)):
            List[i] = List[i].encode('ASCII')
            # List[i] = str(List[i])
            List[i] = int(List[i])

        if self.listSortedOrNot(List):
            closed_colm_asc_status = True
        logger.info("List = {}".format(List))
        del List[0:len(List)]

        """descending"""
        time.sleep(5)
        self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[11]/img').click()  # self service and web image
        self.driver.find_element_by_xpath('/html/body/ul/li[2]/div[2]').click()  # sort
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN45.png")

        self.driver.find_element_by_xpath('/html/body/ul/li[2]/ul/li[3]/div[2]').click()  # decending

        time.sleep(3)
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN46.png")

        for i in range(1, count):
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[11]'.format(
                                                                                                  i))))
            List.append(self.driver.find_element_by_xpath(
                '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[11]'.format(
                    i)).text)

        """Checking whether list is ascending order or not"""
        List.pop()
        List.sort()
        closed_colm_desc_status = False

        """Converting list's element in integer"""
        List = list(filter(None, List))  # Using filter to remove NULL values

        for i in range(len(List)):
            List[i] = List[i].encode('ASCII')

        if self.listSortedOrNot(List):
            closed_colm_desc_status = True
        logger.info("List = {}".format(List))
        del List[0:len(List)]

        logger.info("finished executing pending")

        """Printing status messages on Logger.info()"""

        tables_sorting_data_status = False

        if priority_colm_asc_status and priority_colm_desc_status and total_colm_asc_status and total_colm_desc_status and assigned_colm_asc_status and assigned_colm_desc_status and pending_colm_asc_status and pending_colm_desc_status and waiting_approval_colm_asc_status and waiting_approval_colm_desc_status and planning_colm_asc_status and planning_colm_desc_status and in_progress_colm_asc_status and in_progress_colm_desc_status and completed_colm_asc_status and completed_colm_desc_status and cancelled_colm_asc_status and cancelled_colm_desc_status and rejected_colm_asc_status and rejected_colm_desc_status and closed_colm_asc_status and closed_colm_desc_status:
            tables_sorting_data_status = True
            logger.info("Passed - The sorting of data in the reports mentioned are verified")
        else:
            logger.info("Failed - The sorting of data in the reports mentioned are not verified")
            if priority_colm_asc_status == False:
                logger.info("Failed - Priority column is not in Ascending order")
            if priority_colm_desc_status == False:
                logger.info("Failed - Priority column is not in Descending order")
            if total_colm_asc_status == False:
                logger.info("Failed - Total column is not in Ascending order")
            if total_colm_desc_status == False:
                logger.info("Failed - Total column is not in Descending order")
            if assigned_colm_asc_status == False:
                logger.info("Failed - Assigned column is not in Ascending order")
            if assigned_colm_desc_status == False:
                logger.info("Failed - Assigned column is not in Descending order")
            if pending_colm_asc_status == False:
                logger.info("Failed - Pending column is not in Ascending order")
            if pending_colm_desc_status == False:
                logger.info("Failed - Pending  column is not in Descending order")
            if waiting_approval_colm_asc_status == False:
                logger.info("Failed - Waiting Approval column is not in Ascending order")
            if waiting_approval_colm_desc_status == False:
                logger.info("Failed - waiting approval column is not in Descending order")
            if planning_colm_asc_status == False:
                logger.info("Failed - planning column is not in Ascending order")
            if planning_colm_desc_status == False:
                logger.info("Failed - planning column is not in Descending order")
            if in_progress_colm_asc_status == False:
                logger.info("Failed - in progess column is not in Ascending order")
            if in_progress_colm_desc_status == False:
                logger.info("Failed - in progess column is not in Descending order")
            if completed_colm_asc_status == False:
                logger.info("Failed - completed column is not in Ascending order")
            if completed_colm_desc_status == False:
                logger.info("Failed - completed column is not in Descending order")
            if cancelled_colm_asc_status == False:
                logger.info("Failed - cancelled column is not in Ascending order")
            if cancelled_colm_desc_status == False:
                logger.info("Failed - cancelled column is not in Descending order")
            if rejected_colm_asc_status == False:
                logger.info("Failed - rejected column is not in Ascending order")
            if rejected_colm_desc_status == False:
                logger.info("Failed - rejected column is not in Descending order")
            if closed_colm_asc_status == False:
                logger.info("Failed - cloesd column is not in Ascending order")
            if closed_colm_desc_status == False:
                logger.info("Failed - closed column is not in Descending order")

        return tables_sorting_data_status

    def verify_filter_condition(self, kwargs):
        """ScreenShot - Taken"""
        self.driver.save_screenshot('Ss1.png')

        logger.info("Execuitng filter_condition_for_breached_incident_sla_tickets()")
        window_before = self.driver.window_handles[0]
        """ Clicking on Application"""
        appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
        appl.click()

        """Clicking on Smart Reporting -> Smart Reporting Console"""
        smrtrep = self.driver.find_element_by_link_text('Smart Reporting')
        smrtrep.click()
        smrtrepcon = self.driver.find_element_by_link_text('Smart Reporting Console')
        smrtrepcon.click()

        # WebDriverWait(self.driver, 10).until(expected_conditions.number_of_windows_to_be(2))

        window_after = self.driver.window_handles[1]
        self.driver.switch_to.window(window_after)
        time.sleep(2)
        """ScreenShot - Taken"""
        self.driver.save_screenshot('Ss2.png')

        time.sleep(20)
        """All already clicked"""
        """Click H3G"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')))
        obj_h3g = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')
        obj_h3g.click()
        """click on Rebus Reports"""
        obj_rebus = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[2]/div[8]/div/div/div/div[2]')
        obj_rebus.click()

        """Search content"""
        send_repo = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/input')  # search field
        send_repo.send_keys(kwargs['reportname1'])

        time.sleep(2)
        search_icon = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/div[2]/div[2]/img')  # search icon
        search_icon.click()
        time.sleep(5)
        """ScreenShot - Taken"""
        self.driver.save_screenshot('Ss3.png')

        """Double clicking on report"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div[2]')))
        repo = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div[2]')
        action = ActionChains(self.driver)
        action.double_click(repo).perform()

        time.sleep(20)
        """ScreenShot - Taken"""
        self.driver.save_screenshot('Ss4.png')

        "Clicking on reset"
        self.driver.find_element_by_xpath(
            "//*[@id='pagecontent']/div[2]/div[3]/div[1]/div/div/div[3]/div[2]/table/tbody/tr/td/div/table/tbody/tr/td[2]/span").click()

        "clicking on time"
        time.sleep(10)
        if (kwargs['reportname1'] == "Breached Incident SLA Tickets"):
            self.driver.find_element_by_xpath("//*[@id='143771']/div/div[4]/div/div/div/div[1]/img").click()
        if (kwargs['reportname1'] == "Upcoming Incident SLAs Breach Details"):
            self.driver.find_element_by_xpath("//*[@id='143801']/div/div[4]/div/div/div/div[1]/img").click()
        time.sleep(4)
        window_after = self.driver.window_handles[1]
        self.driver.switch_to.window(window_after)
        showtime1 = strftime("%Y_%m_%d", gmtime())
        logger.info(showtime1)
        showtime2 = strftime("%d/%m/%Y %H:%M:%S", gmtime())
        logger.info(showtime2)
        theday = datetime.date(*map(int, showtime1.split('_')))
        prevday = theday - datetime.timedelta(days=7)
        pre = prevday.strftime('%Y/%m/%d')
        self.driver.find_element_by_xpath("html/body/div[8]/div[2]/div[2]/div[1]/div[1]/input").send_keys(pre)
        self.driver.find_element_by_xpath("html/body/div[8]/div[2]/div[2]/div[1]/div[2]/input").send_keys(showtime2)
        time.sleep(5)
        self.driver.find_element_by_xpath(
            "html/body/div[8]/div[2]/div[2]/div[2]/div[2]/table/tbody/tr/td/div/table/tbody/tr/td[2]/span").click()
        time.sleep(2)
        # self.driver.switch_to.window(window_before)
        "Clicking on Support Organization"
        time.sleep(3)
        if (kwargs['reportname1'] == "Upcoming Incident SLAs Breach Details"):
            self.driver.find_element_by_xpath("//*[@id='143803']/div/div[4]/div/div/div/div[2]/img").click()
            self.driver.find_element_by_xpath("//*[@id='143803']/div/div[4]/div/div/div/div[3]/img").click()
            self.driver.find_element_by_xpath("//*[@id='143803']/div/div[4]/div/div/div/div[4]/img").click()
            self.driver.find_element_by_xpath("//*[@id='143803']/div/div[4]/div/div/div/div[7]/img").click()
        if (kwargs['reportname1'] == "Breached Incident SLA Tickets"):
            self.driver.find_element_by_xpath("//*[@id='143773']/div/div[4]/div/div/div/div[1]/img").click()
            self.driver.find_element_by_xpath("//*[@id='143773']/div/div[4]/div/div/div/div[2]/img").click()
            self.driver.find_element_by_xpath("//*[@id='143773']/div/div[4]/div/div/div/div[3]/img").click()
            self.driver.find_element_by_xpath("//*[@id='143773']/div/div[4]/div/div/div/div[4]/img").click()
            self.driver.find_element_by_xpath("//*[@id='143773']/div/div[4]/div/div/div/div[5]/img").click()
            self.driver.find_element_by_xpath("//*[@id='143773']/div/div[4]/div/div/div/div[9]/img").click()

        "Clicking on Support Group"
        time.sleep(10)
        if (kwargs['reportname1'] == "Upcoming Incident SLAs Breach Details"):
            self.driver.find_element_by_xpath("//*[@id='143802']/div/div[4]/div/div/div/div[1]/img").click()
            self.driver.find_element_by_xpath("//*[@id='143802']/div/div[4]/div/div/div/div[2]/img").click()
            self.driver.find_element_by_xpath("//*[@id='143802']/div/div[4]/div/div/div/div[3]/img").click()
            self.driver.find_element_by_xpath("//*[@id='143802']/div/div[4]/div/div/div/div[4]/img").click()
            self.driver.find_element_by_xpath("//*[@id='143802']/div/div[4]/div/div/div/div[7]/img").click()

        if (kwargs['reportname1'] == "Breached Incident SLA Tickets"):
            self.driver.find_element_by_xpath("//*[@id='143767']/div/div[4]/div/div/div/div[1]/img").click()
            self.driver.find_element_by_xpath("//*[@id='143767']/div/div[4]/div/div/div/div[2]/img").click()
            self.driver.find_element_by_xpath("//*[@id='143767']/div/div[4]/div/div/div/div[5]/img").click()
            self.driver.find_element_by_xpath("//*[@id='143767']/div/div[4]/div/div/div/div[6]/img").click()

        "Clicking on GO"
        time.sleep(3)
        self.driver.find_element_by_xpath(
            "//*[@id='pagecontent']/div[2]/div[3]/div[1]/div/div/div[3]/div[1]/table/tbody/tr/td/div/table/tbody/tr/td[2]/span").click()
        time.sleep(5)
        self.driver.execute_script("window.scrollTo(0, 10)")
        time.sleep(5)
        self.driver.execute_script("document.body.style.zoom='50%'")
        self.driver.save_screenshot('Ss5.png')
        self.driver.execute_script("document.body.style.zoom='100%'")
        found = True
        time.sleep(5)
        "Getting values from table"
        table = self.driver.find_element_by_xpath(
            "//*[@id='pagecontent']/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table")
        tablelist = []
        for tr in table.find_elements_by_tag_name("tr"):
            tablelist.append(tr.text)
        logger.info(tablelist)

        if not tablelist:
            found = False
            logger.info("There is no data in Report")

        """Verifying data in table are present"""
        if (kwargs['reportname1'] == "Breached Incident SLA Tickets"):
            for elem in tablelist:
                if "No" in elem:
                    found = False
                    break
        if (kwargs['reportname1'] == "Upcoming Incident SLAs Breach Details"):
            for elem in tablelist:
                if "Yes" in elem:
                    found = False
                    break
        return found

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

    def problem_volumes_priority(self, kwargs):
        logger.info("Execuitng problem_volumes_priority()")
        window_before = self.driver.window_handles[0]

        self.driver.save_screenshot("ss1.png")
        """ Clicking on Application"""
        appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
        appl.click()

        """Clicking on Smart Reporting -> Smart Reporting Console"""
        smrtrep = self.driver.find_element_by_link_text('Smart Reporting')
        smrtrep.click()
        smrtrepcon = self.driver.find_element_by_link_text('Smart Reporting Console')
        smrtrepcon.click()

        time.sleep(20)
        WebDriverWait(self.driver, 30).until(
            expected_conditions.number_of_windows_to_be(2))
        window_after = self.driver.window_handles[1]
        self.driver.switch_to.window(window_after)

        """ScreenShot - Taken"""
        self.driver.save_screenshot("ss2.png")

        """All already clicked"""
        """Click H3G"""
        obj_h3g = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')
        obj_h3g.click()
        """click on Rebus Reports"""
        obj_rebus = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[2]/div[8]/div/div/div/div[2]')
        obj_rebus.click()

        """Search content"""
        send_repo = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/input')
        send_repo.send_keys(kwargs['Report_name'])

        time.sleep(2)
        search_icon = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/div[2]/div[2]/img')
        search_icon.click()

        """ScreenShot - Taken"""
        self.driver.save_screenshot("ss3.png")

        time.sleep(2)
        """Double clicking on report"""
        repo = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div[2]')
        action = ActionChains(self.driver)
        action.double_click(repo).perform()

        time.sleep(7)
        """ScreenShot - Taken"""
        self.driver.save_screenshot("ss4.png")
        report_display_1_upper = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[1]/table/tbody/tr[1]/td').text

        """Verify if smart reporting lower 1 displays"""
        report_display_1_lower = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[1]/table/tbody/tr[2]/td').text

        """Verify if smart reporting displays the mentioned reports"""
        smart_reporting_display_status = True

        if report_display_1_upper != kwargs['Report_display_1_upper']:
            smart_reporting_display_status = False
        elif report_display_1_lower != kwargs['Report_display_1_lower']:
            smart_reporting_display_status = False

        if smart_reporting_display_status == False:
            logger.info("Failed - Smart reporting displays are Failed to match")
        else:
            logger.info("Passed - Smart reporting displays are matched")

        return smart_reporting_display_status

    def problem_volumes_priority_names_columns(self, kwargs):
        logger.info("Execuitng problem_volumes_priority_names_columns()")
        window_before = self.driver.window_handles[0]
        self.driver.save_screenshot("Column_ss1.png")
        """ Clicking on Application"""
        appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
        appl.click()

        """Clicking on Smart Reporting -> Smart Reporting Console"""
        smrtrep = self.driver.find_element_by_link_text('Smart Reporting')
        smrtrep.click()
        smrtrepcon = self.driver.find_element_by_link_text('Smart Reporting Console')
        smrtrepcon.click()

        time.sleep(20)
        WebDriverWait(self.driver, 30).until(
            expected_conditions.number_of_windows_to_be(2))
        window_after = self.driver.window_handles[1]
        self.driver.switch_to.window(window_after)

        """ScreenShot - Taken"""
        self.driver.save_screenshot("Column_ss2.png")

        """All already clicked"""
        """Click H3G"""
        obj_h3g = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')
        obj_h3g.click()
        """click on Rebus Reports"""
        obj_rebus = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[2]/div[8]/div/div/div/div[2]')
        obj_rebus.click()

        """Search content"""
        send_repo = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/input')
        send_repo.send_keys(kwargs['Report_name'])

        time.sleep(2)

        search_icon = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/div[2]/div[2]/img')
        search_icon.click()

        """ScreenShot - Taken"""
        self.driver.save_screenshot("Column_ss3.png")

        time.sleep(2)
        """Double clicking on report"""
        repo = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div[2]')
        action = ActionChains(self.driver)
        action.double_click(repo).perform()

        time.sleep(7)
        """ScreenShot - Taken"""
        self.driver.save_screenshot("Column_ss4.png")
        """Verify coloumn for upper table"""

        period = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/table/tbody/tr/td[1]/div/table/thead/tr/td[1]/div').text

        priority = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/table/tbody/tr/td[1]/div/table/thead/tr/td[2]/div').text

        incoming = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/table/tbody/tr/td[1]/div/table/thead/tr/td[3]/div').text

        resolved = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/table/tbody/tr/td[1]/div/table/thead/tr/td[4]/div').text

        backlog = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/table/tbody/tr/td[1]/div/table/thead/tr/td[5]/div').text

        time.sleep(2)
        """Verify if the mentioned names & columns are available in the reports as in requirement sheet"""
        names_columns_status = True

        if period != kwargs['column1']:
            names_columns_status = False
        elif priority != kwargs['column2']:
            names_columns_status = False
        elif incoming != kwargs['column3']:
            names_columns_status = False
        elif resolved != kwargs['column4']:
            names_columns_status = False
        elif backlog != kwargs['column5']:
            names_columns_status = False

        if names_columns_status == False:
            logger.info("Failed - The mentioned names & columns are not available in the report as in requirement")
        else:
            logger.info("Passed - The mentioned names & columns are available in the report as in requirement")

        return names_columns_status

    def sorting_upcoming_problems_sla_breach_details_main(self, kwargs):
        logger.info("Execuitng smart_reporting()")
        """ Clicking on Application"""
        appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
        appl.click()

        """Clicking on Smart Reporting -> Smart Reporting Console"""
        smrtrep = self.driver.find_element_by_link_text('Smart Reporting')
        smrtrep.click()
        smrtrepcon = self.driver.find_element_by_link_text('Smart Reporting Console')
        """Clicking on smart reporting console and switchingg windows"""
        window_before = self.driver.window_handles[0]
        smrtrepcon.click()
        WebDriverWait(self.driver, 10).until(expected_conditions.number_of_windows_to_be(2))
        window_after = self.driver.window_handles[1]
        self.driver.switch_to.window(window_after)
        time.sleep(3)
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')))
        time.sleep(3)
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')))
        search_report = self.driver.find_element(By.XPATH,
                                                 '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/input')
        search_report.send_keys(kwargs['Report Name'])
        search_report.send_keys(Keys.ENTER)
        time.sleep(2)
        """opening H3G Folder"""
        h3gopfoler = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')
        time.sleep(2)
        h3gopfoler.click()
        """Opening Rebus Reports Folder"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          "/html[1]/body[1]/form[1]/div[12]/div[1]/div[2]/div[4]/div[1]/div[2]/div[3]/div[1]/div[2]/div[8]/div[1]/div[1]")))
        maya_reports = self.driver.find_element(By.XPATH,
                                                "/html[1]/body[1]/form[1]/div[12]/div[1]/div[2]/div[4]/div[1]/div[2]/div[3]/div[1]/div[2]/div[8]/div[1]/div[1]")
        maya_reports.click()
        time.sleep(3)

        """Taking Screen shot"""
        self.driver.get_screenshot_as_file('C:\GIT\output\ITSM_REBUS Reporting_178_1.png')
        """Double-click on incident-sla-dashboard report"""
        incident_sla_dashboard = self.driver.find_element(By.XPATH,
                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div[2]')
        time.sleep(2)
        action = ActionChains(self.driver)
        action.double_click(incident_sla_dashboard)
        action.perform()
        time.sleep(10)
        """Taking Screen shot"""
        self.driver.get_screenshot_as_file('C:\GIT\output\ITSM_REBUS Reporting_178_2.png')

        """Checking Problem ID columns-->descending"""
        sorting = True
        column_count = 1
        for i in range(1, 2):
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                (By.XPATH,
                 "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                     i))))
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                                                                  i))))
            time.sleep(3)
            obj = self.driver.find_element(By.XPATH,
                                           "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                               i))
            obj.click()
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")))
            obj1 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")
            time.sleep(1)
            obj1.click()
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable(
                (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[3]/div[2]")))
            obj2 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[3]/div[2]")
            time.sleep(1)
            obj2.click()
            time.sleep(7)

            column_list = []
            actual_column_list = []
            for j in range(1, 31):
                WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                                      "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                                                          j,
                                                                                                          column_count))))
                column_list.append(self.driver.find_element(By.XPATH,
                                                            "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                j, column_count)).text)
            logger.info("Problem ID retrieved after sorting in descending order")
            logger.info(column_list)
            refined_column_list = re.findall(r"PBI(\d*)", str(column_list))
            for k in refined_column_list:
                actual_column_list.append(float(k.replace(",", "")))
            if actual_column_list != sorted(actual_column_list, reverse=True):
                sorting = False
                logger.info("Problem ID descending failed")
            logger.info("Problem IDs after refining:")
            logger.info(actual_column_list)

        """Taking Screen shot"""
        self.driver.get_screenshot_as_file('C:\GIT\output\ITSM_REBUS Reporting_178_3.png')

        """Checking Priority columns-->descending"""
        column_count = 3
        for i in range(3, 4):
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                (By.XPATH,
                 "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                     i))))
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                                                                  i))))
            time.sleep(3)
            obj = self.driver.find_element(By.XPATH,
                                           "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                               i))
            obj.click()
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")))
            obj1 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")
            time.sleep(1)
            obj1.click()
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable(
                (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[3]/div[2]")))
            obj2 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[3]/div[2]")
            time.sleep(1)
            obj2.click()
            time.sleep(7)
            column_list = []
            actual_column_list = []
            for j in range(1, 31):
                WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                                      "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                                                          j,
                                                                                                          column_count))))
                column_list.append(self.driver.find_element(By.XPATH,
                                                            "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                j, column_count)).text)
            logger.info("Priorities retrieved after sorting in descending order")
            logger.info(column_list)
            refined_column_list = re.findall(r"P(\d*)", str(column_list))
            logger.info(refined_column_list)
            for k in refined_column_list:
                actual_column_list.append(float(k.replace(",", "")))
            if actual_column_list != sorted(actual_column_list, reverse=True):
                sorting = False
                logger.info("Priority descending failed")
            logger.info("Priorities after refining:")
            logger.info(actual_column_list)

        """Taking Screen shot"""
        self.driver.get_screenshot_as_file('C:\GIT\output\ITSM_REBUS Reporting_178_4.png')

        """Checking % Complete columns-->descending"""
        column_count = 11
        for i in range(11, 12):
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                (By.XPATH,
                 "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                     i))))
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                                                                  i))))
            time.sleep(3)
            obj = self.driver.find_element(By.XPATH,
                                           "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                               i))
            obj.click()
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")))
            obj1 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")
            time.sleep(1)
            obj1.click()
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable(
                (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[3]/div[2]")))
            obj2 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[3]/div[2]")
            time.sleep(1)
            obj2.click()
            time.sleep(7)
            column_list = []
            actual_column_list = []
            for j in range(1, 31):
                WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                                      "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                                                          j,
                                                                                                          column_count))))
                column_list.append(self.driver.find_element(By.XPATH,
                                                            "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                j, column_count)).text)
            logger.info("% complete data retrieved after sorting in descending order")
            logger.info(column_list)
            refined_column_list = re.findall(r"([\d,.]+)%", str(column_list))
            for k in refined_column_list:
                actual_column_list.append(float(k.replace(",", "")))
            if actual_column_list != sorted(actual_column_list, reverse=True):
                sorting = False
                logger.info("%complete descending failed")
            logger.info("% complete after refining:")
            logger.info(actual_column_list)

        """Taking Screen shot"""
        self.driver.get_screenshot_as_file('C:\GIT\output\ITSM_REBUS Reporting_178_5.png')

        """Checking Problem ID columns-->ascending"""
        column_count = 1
        for i in range(1, 2):
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                (By.XPATH,
                 "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                     i))))
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                                                                  i))))
            time.sleep(3)
            obj = self.driver.find_element(By.XPATH,
                                           "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                               i))
            obj.click()
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")))
            obj1 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")
            time.sleep(1)
            obj1.click()
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable(
                (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[2]/div[2]")))
            obj2 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[2]/div[2]")
            time.sleep(1)
            obj2.click()
            time.sleep(7)
            column_list = []
            actual_column_list = []
            for j in range(1, 31):
                WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                                      "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                                                          j,
                                                                                                          column_count))))
                column_list.append(self.driver.find_element(By.XPATH,
                                                            "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                j, column_count)).text)
            logger.info("Problem ID retrieved after sorting in ascending order")
            logger.info(column_list)
            refined_column_list = re.findall(r"PBI(\d*)", str(column_list))
            for k in refined_column_list:
                actual_column_list.append(float(k.replace(",", "")))
            if actual_column_list != sorted(actual_column_list, reverse=False):
                sorting = False
                logger.info("Problem ID ascending failed")
            logger.info("Problem IDs after refining:")
            logger.info(actual_column_list)

        """Taking Screen shot"""
        self.driver.get_screenshot_as_file('C:\GIT\output\ITSM_REBUS Reporting_178_6.png')

        """Checking Priority columns-->ascending"""
        column_count = 3
        for i in range(3, 4):
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                (By.XPATH,
                 "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                     i))))
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                                                                  i))))
            time.sleep(3)
            obj = self.driver.find_element(By.XPATH,
                                           "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                               i))
            obj.click()
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")))
            obj1 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")
            time.sleep(1)
            obj1.click()
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable(
                (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[2]/div[2]")))
            obj2 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[2]/div[2]")
            time.sleep(1)
            obj2.click()
            time.sleep(7)
            column_list = []
            actual_column_list = []
            for j in range(1, 31):
                WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                                      "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                                                          j,
                                                                                                          column_count))))
                column_list.append(self.driver.find_element(By.XPATH,
                                                            "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                j, column_count)).text)
            logger.info("Priorities retrieved after sorting in ascending order")
            logger.info(column_list)
            refined_column_list = re.findall(r"P(\d*)", str(column_list))
            for k in refined_column_list:
                actual_column_list.append(float(k.replace(",", "")))
            if actual_column_list != sorted(actual_column_list, reverse=False):
                sorting = False
                logger.info("Priorities ascending failed")
            logger.info("Priorities after refining:")
            logger.info(actual_column_list)

        """Taking Screen shot"""
        self.driver.get_screenshot_as_file('C:\GIT\output\ITSM_REBUS Reporting_178_7.png')

        """Checking % Complete columns-->ascending"""
        column_count = 11
        for i in range(11, 12):
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                (By.XPATH,
                 "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                     i))))
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                                                                  i))))
            time.sleep(3)
            obj = self.driver.find_element(By.XPATH,
                                           "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                               i))
            obj.click()
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")))
            obj1 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")
            time.sleep(1)
            obj1.click()
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable(
                (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[2]/div[2]")))
            obj2 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[2]/div[2]")
            time.sleep(1)
            obj2.click()
            time.sleep(7)
            column_list = []
            actual_column_list = []
            for j in range(1, 31):
                WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                                      "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                                                          j,
                                                                                                          column_count))))
                column_list.append(self.driver.find_element(By.XPATH,
                                                            "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[{}]".format(
                                                                j, column_count)).text)
            logger.info("% complete data retrieved after sorting in ascending order")
            logger.info(column_list)
            refined_column_list = re.findall(r"([\d,.]+)%", str(column_list))
            for k in refined_column_list:
                actual_column_list.append(float(k.replace(",", "")))
            if actual_column_list != sorted(actual_column_list, reverse=False):
                sorting = False
                logger.info("%complete ascending failed")
            logger.info("% complete after refining:")
            logger.info(actual_column_list)

        return sorting

    def open_smart_reporting_mbnl_all_main(self, kwargs):
        logger.info("Execuitng smart_reporting()")
        """ Clicking on Application"""
        time.sleep(3)
        appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
        appl.click()
        time.sleep(5)
    
        """Clicking on Smart Reporting -> Smart Reporting Console"""
        smrtrep = self.driver.find_element_by_link_text('Smart Reporting')
        smrtrep.click()
        smrtrepcon = self.driver.find_element_by_link_text('Smart Reporting Console')
    
        window_before = self.driver.window_handles[0]
        smrtrepcon.click()
        WebDriverWait(self.driver, 10).until(expected_conditions.number_of_windows_to_be(2))
        window_after = self.driver.window_handles[1]
        self.driver.switch_to.window(window_after)
        time.sleep(3)
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')))
        h3gopfoler = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')
        h3gopfoler.click()
        time.sleep(10)
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[2]/div[2]/div/div/div/div[2]')))
        mbnlsubfolder = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[2]/div[2]/div/div/div/div[2]')
        mbnlsubfolder.click()
        time.sleep(5)
        mbnlalltickets = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div[2]')
        action = ActionChains(self.driver)
        action.double_click(mbnlalltickets)
        action.perform()
        time.sleep(2)
        time.sleep(7)
        WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
            (By.XPATH,
             "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[1]/img[1]")))
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[1]/img[1]")))
        time.sleep(3)
        obj = self.driver.find_element(By.XPATH,
                                       "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[1]/img[1]")
        obj.click()
        WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
            (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")))
        obj1 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")
        time.sleep(1)
        obj1.click()
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable(
            (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[3]/div[2]")))
        obj2 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[3]/div[2]")
        time.sleep(1)
        obj2.click()
        time.sleep(10)
        row_details = []
        for i in range(1, 10):
            row_details.append(self.driver.find_element(By.XPATH,
                                                        '/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[1]/td[{}]'.format(
                                                            i)).text)
    
        logger.info("Row details before updation: {}".format(row_details))
        logger.info("Owner group before updation: {}".format(row_details[5]))
    
        self.driver.switch_to.window(window_before)
    
        return row_details[5]

    def status_change_verification_smart_report_main(self, kwargs):
        """Searching incident by ID"""
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
        inciid.send_keys(kwargs['incident_id'])
        inciid.send_keys(Keys.ENTER)
        time.sleep(2)
    
        date_system_tab = self.driver.find_element(By.XPATH,
                                                   '//*[@id="WIN_3_1000000200"]/div[2]/div[2]/div/dl/dd[5]/span[2]/a')
        date_system_tab.click()
        time.sleep(3)
        owner_group = self.driver.find_element(By.XPATH, '//*[@id="WIN_3_1000000422"]/a')
    
        owner_group.click()
        time.sleep(1)
        company_name = self.driver.find_element(By.XPATH, '/html/body/div[4]/div[2]/table/tbody/tr/td[1]')
        time.sleep(3)
        company_name.click()
        company_sub = self.driver.find_element(By.XPATH, '/html/body/div[5]/div[2]/table/tbody/tr[4]/td[1]')
        time.sleep(3)
        company_sub.click()
        time.sleep(3)
        second_line = self.driver.find_element(By.XPATH, '/html/body/div[6]/div[2]/table/tbody/tr/td[1]')
        time.sleep(3)
        second_line.click()
        owner_group.send_keys("2nd Line Technical Support")
        time.sleep(3)
        saveinc = self.driver.find_element_by_xpath(
            '//a[@id="WIN_3_301614800"]/div[@class="btntextdiv"]/div[@class="f1"]')
        saveinc.click()
        time.sleep(10)
        logger.info("Execuitng smart_reporting()")
    
        """ Clicking on Application"""
        time.sleep(3)
        appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
        appl.click()
        time.sleep(5)
    
        """Clicking on Smart Reporting -> Smart Reporting Console"""
        smrtrep = self.driver.find_element_by_link_text('Smart Reporting')
        smrtrep.click()
        smrtrepcon = self.driver.find_element_by_link_text('Smart Reporting Console')
    
        window_before = self.driver.window_handles[0]
        smrtrepcon.click()
        WebDriverWait(self.driver, 10).until(expected_conditions.number_of_windows_to_be(2))
        window_after = self.driver.window_handles[1]
        self.driver.switch_to.window(window_after)
        time.sleep(3)
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')))
        h3gopfoler = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')
        h3gopfoler.click()
        time.sleep(10)
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[2]/div[2]/div/div/div/div[2]')))
        mbnlsubfolder = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[2]/div[2]/div/div/div/div[2]')
        mbnlsubfolder.click()
        time.sleep(5)
        mbnlalltickets = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div[2]')
        action = ActionChains(self.driver)
        action.double_click(mbnlalltickets)
        action.perform()
        time.sleep(2)
        time.sleep(7)
        WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
            (By.XPATH,
             "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[1]/img[1]")))
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[1]/img[1]")))
        time.sleep(3)
        obj = self.driver.find_element(By.XPATH,
                                       "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[1]/img[1]")
        obj.click()
        WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
            (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")))
        obj1 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")
        time.sleep(1)
        obj1.click()
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable(
            (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[3]/div[2]")))
        obj2 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[3]/div[2]")
        time.sleep(1)
        obj2.click()
        time.sleep(10)
    
        row_details = []
        for i in range(1, 10):
            row_details.append(self.driver.find_element(By.XPATH,
                                                        '/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[1]/td[{}]'.format(
                                                            i)).text)
        logger.info("Row details after updation: {}".format(row_details))
        logger.info("Ownner group after updation:{}".format(row_details[5]))
        self.driver.switch_to.window(window_before)
    
        """Validation"""
        Matching = True
        if row_details[5] == kwargs['Owner_group']:
            Matching = False
        return Matching

    def verify_incident_volumes_by_priority_names_columns(self, kwargs):
        logger.info("Execuitng verify_incident_volumes_by_priority_names_columns()")
        time.sleep(0)
        """ScreenShot - Taken"""
        self.driver.get_screenshot_as_file('C:/Users/sparsh/Desktop/New folder (2)/screenshot1.png')

        logger.info("Execuitng verify_incident_volumes_by_priority_names_columns()")
        window_before = self.driver.window_handles[0]
        """ Clicking on Application"""
        appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
        appl.click()

        """Clicking on Smart Reporting -> Smart Reporting Console"""
        smrtrep = self.driver.find_element_by_link_text('Smart Reporting')
        smrtrep.click()
        smrtrepcon = self.driver.find_element_by_link_text('Smart Reporting Console')
        smrtrepcon.click()

        # WebDriverWait(self.driver, 10).until(expected_conditions.number_of_windows_to_be(2))
        time.sleep(6)
        window_after = self.driver.window_handles[1]
        self.driver.switch_to.window(window_after)

        self.verify_popup()

        """ScreenShot - Taken"""
        self.driver\
            .get_screenshot_as_file('C:/Users/sparsh/Desktop/New folder (2)/screenshot2.png')

        # time.sleep(14)
        """All already clicked"""
        """Click H3G"""
        WebDriverWait(self.driver, 100).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')))
        obj_h3g = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')
        obj_h3g.click()
        """click on Rebus Reports"""
        obj_rebus = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[2]/div[8]/div/div/div/div[2]')
        obj_rebus.click()

        """Search content"""

        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,'//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/input')))

        send_repo = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/input')  # search field
        send_repo.send_keys(kwargs['report_name'])

        time.sleep(5)
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable(
            (By.XPATH, '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/div[2]/div[2]/img')))

        search_icon = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/div[2]/div[2]/img')  # search icon
        search_icon.click()

        #time.sleep(20)
        """ScreenShot - Taken"""
        self.driver.get_screenshot_as_file('C:/Users/sparsh/Desktop/New folder (2)/screenshot3.png')

        """Double clicking on report"""

        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div[2]')))
        repo = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div[2]')
        action = ActionChains(self.driver)
        action.double_click(repo).perform()

        time.sleep(10)
        """ScreenShot - Taken"""
        self.driver.get_screenshot_as_file('C:/Users/sparsh/Desktop/New folder (2)/screenshot4.png')

        """Verify if the mentioned names & columns are available in the reports as in requirement sheet"""

        WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                              '//div[@class="rptdata rpt98713f1"]')))

        clm_period = self.driver.find_element_by_xpath(
            '//div[@class="rptdata rpt98713f1"]').text
        clm_priority = self.driver.find_element_by_xpath(
            '//td[@class="rpt98713hdr rpt98713hdrf5 rpthdrcol"]').text
        clm_incoming = self.driver.find_element_by_xpath(
            '//td[@class="rpt98713hdr rpt98713hdrf6 rpthdrcol"]').text
        clm_resolved = self.driver.find_element_by_xpath(
            '//td[@class="rpt98713hdr rpt98713hdrf7 rpthdrcol"]').text
        clm_backlogs = self.driver.find_element_by_xpath(
            '//td[@class="rpt98713hdr rpt98713hdrf8 rpthdrcol"]').text

        columns_name_status = True

        if clm_period != kwargs['period']:
            columns_name_status = False
        elif clm_priority != kwargs['priority']:
            columns_name_status = False
        elif clm_incoming != kwargs['incoming']:
            columns_name_status = False
        elif clm_resolved != kwargs['resolved']:
            columns_name_status = False
        elif clm_backlogs != kwargs['backlogs']:
            columns_name_status = False

        if columns_name_status == False:
            logger.info("Failed - The mentioned names & columns are not available in the reports as in requirement")
        else:
            logger.info("Passed - The mentioned names & columns are available in the reports as in requirement")

        return columns_name_status



    def incident_sla_dashboard(self, kwargs):
        try:
            self.login_bmc()
            status = self.incident_sla_dashboard_main(kwargs)
        except BaseException as be:
            logger.fatal('Fatal exception occured in incident_sla_dashboard_lib() in {}'.format(self.name))
            logger.error(traceback.print_exc())
        finally:
            self.bmc_logout()
            return status

    def smart_reporting_gui(self, kwargs):
        try:
            for k in kwargs.keys():
                logger.info("arguments are {}{}".format(k, kwargs[k]))
            self.login_bmc()
            rep = False
            rep = self.smart_reporting(kwargs)
        except BaseException as be:
            logger.fatal("Fatal exception occured in smart_reporting_gui() in {}".format(self.name))
            logger.error(traceback.print_exc())
        finally:
            self.bmc_logout()
            return rep

    def search_incident_verify_b2b_integration_info_gui(self, kwargs):
        try:
            for k in kwargs.keys():
                logger.info("arguments are {}{}".format(k, kwargs[k]))
            self.login_bmc()
            ongrp = False
            ongrp = self.search_incident_verify_b2b_integration_info(kwargs)
        except BaseException as be:
            logger.fatal(
                "Fatal exception occured in search_incident_verify_b2b_integration_info_gui() in {}".format(
                    self.name))
            logger.error(traceback.print_exc())
        finally:
            self.bmc_logout()
            return ongrp

    def verify_smart_reporting_status(self, kwargs):
        try:
            for k in kwargs.keys():
                logger.info("arguments are {}{}".format(k, kwargs[k]))
            self.login_bmc()
            rep = False
            rep = self.verify_status(kwargs)
        except BaseException as be:
            logger.fatal("Fatal exception occured in verify_smart_reporting_status() in {}".format(self.name))
            logger.error(traceback.print_exc())
        finally:
            self.bmc_logout()

            return rep

    def smart_reporting_sorting_gui(self, kwargs):
        try:
            for k in kwargs.keys():
                logger.info("arguments are {}{}".format(k, kwargs[k]))
            self.login_bmc()
            rep = False
            rep = self.smart_reporting_sorting(kwargs)
        except BaseException as be:
            logger.fatal("Fatal exception occured in search_incident_verify_slm_gui() in {}".format(self.name))
            logger.error(traceback.print_exc())
        finally:
            self.bmc_logout()
            return rep

    def smart_reporting_criteria_gui(self, kwargs):
        try:
            for k in kwargs.keys():
                logger.info("arguments are {}{}".format(k, kwargs[k]))
            self.login_bmc()
            rep = False
            rep = self.smart_reporting_criteria(kwargs)
        except BaseException as be:
            logger.fatal("Fatal exception occured in smart_reporting_criteria_gui() in {}".format(self.name))
            logger.error(traceback.print_exc())
        finally:
            self.bmc_logout()
            return rep

    def smart_reporting_b2b_verification_gui(self, kwargs):
        try:
            for k in kwargs.keys():
                logger.info("arguments are {}{}".format(k, kwargs[k]))
            self.login_bmc()
            rep = False
            rep = self.smart_reporting_b2b_verification(kwargs)
        except BaseException as be:
            logger.fatal("Fatal exception occured in smart_reporting_criteria_gui() in {}".format(self.name))
            logger.error(traceback.print_exc())
        finally:
            self.bmc_logout()
            return rep

    def smart_reporting_b2b_verification_gui(self, kwargs):
        try:
            for k in kwargs.keys():
                logger.info("arguments are {}{}".format(k, kwargs[k]))
            self.login_bmc()
            rep = False
            rep = self.smart_reporting_b2b_verification(kwargs)
        except BaseException as be:
            logger.fatal("Fatal exception occured in smart_reporting_criteria_gui() in {}".format(self.name))
            logger.error(traceback.print_exc())
        finally:
            self.bmc_logout()
            return rep

    def upcoming_incident_sla_breach(self, kwargs):
        try:
            self.login_bmc()
            status = self.upcoming_incident_sla_breach_main(kwargs)
        except BaseException as be:
            logger.fatal('Fatal exception occured in upcoming_incident_sla_breach_details) in {}'.format(self.name))
            logger.error(traceback.print_exc())
        finally:
            self.bmc_logout()
            return status

    def breached_incidents_sla_tickets(self, kwargs):
        try:
            self.login_bmc()
            status = self.breached_incidents_sla_tickets_main(kwargs)
        except BaseException as be:
            logger.fatal('Fatal exception occured in breached_incidents_sla_tickets_lib) in {}'.format(self.name))
            logger.error(traceback.print_exc())
        finally:
            self.bmc_logout()
            return status

    def breached_incidents_sla_tickets1(self, kwargs):
        try:
            self.login_bmc()
            status = self.breached_incidents_sla_tickets_main1(kwargs)
        except BaseException as be:
            logger.fatal('Fatal exception occured in breached_incidents_sla_tickets_lib1 in {}'.format(self.name))
            logger.error(traceback.print_exc())
        finally:
            self.bmc_logout()
            return status

    def breached_incidents_sla_tickets2(self, kwargs):
        try:
            self.login_bmc()
            status = self.breached_incidents_sla_tickets_main2(kwargs)
        except BaseException as be:
            logger.fatal('Fatal exception occured in breached_incidents_sla_tickets_lib2 in {}'.format(self.name))
            logger.error(traceback.print_exc())
        finally:
            self.bmc_logout()
            return status

    def incident_sla_dashboard(self, kwargs):
        try:
            self.login_bmc()
            status = self.incident_sla_dashboard_main(kwargs)
        except BaseException as be:
            logger.fatal('Fatal exception occured in incident_sla_dashboard_lib() in {}'.format(self.name))
            logger.error(traceback.print_exc())
        finally:
            self.bmc_logout()
            return status

    def upcoming_incident_sla_breach1(self, kwargs):
        try:
            self.login_bmc()
            status = self.upcoming_incident_sla_breach_main1(kwargs)
        except BaseException as be:
            logger.fatal('Fatal exception occured in upcoming_incident_sla_breach_details1 in {}'.format(self.name))
            logger.error(traceback.print_exc())
        finally:

            self.bmc_logout()
            return status

    def upcoming_incident_sla_breach2(self, kwargs):
        try:
            self.login_bmc()
            status = self.upcoming_incident_sla_breach_main2(kwargs)
        except BaseException as be:
            logger.fatal('Fatal exception occured in upcoming_incident_sla_breach_details2 in {}'.format(self.name))
            logger.error(traceback.print_exc())
        finally:
            self.bmc_logout()
            return status

    def incident_sla_dashboard1(self, kwargs):
        try:
            self.login_bmc()
            status = self.incident_sla_dashboard_main1(kwargs)
        except BaseException as be:
            logger.fatal('Fatal exception occured in incident_sla_dashboard_lib1 in {}'.format(self.name))
            logger.error(traceback.print_exc())
        finally:
            self.bmc_logout()
            return status

    def incident_sla_dashboard2(self, kwargs):
        try:
            self.login_bmc()
            status = self.incident_sla_dashboard_main2(kwargs)
        except BaseException as be:
            logger.fatal('Fatal exception occured in incident_sla_dashboard_lib1 in {}'.format(self.name))
            logger.error(traceback.print_exc())
        finally:
            self.bmc_logout()
            return status

    def incident_volumes_by_support_group_per_priorities(self, kwargs):
        try:
            self.login_bmc()
            status = self.incident_volumes_by_support_group_per_priorities_main(kwargs)
        except BaseException as be:
            logger.fatal('Fatal exception occured in incident_volumes_by_support_group_per_priorities_lib in {}'.format(
                self.name))
            logger.error(traceback.print_exc())
        finally:
            self.bmc_logout()
            return status

    def incident_volumes_by_support_group_per_priorities_1(self, kwargs):
        try:
            self.login_bmc()
            status = self.incident_volumes_by_support_group_per_priorities_main1(kwargs)
        except BaseException as be:
            logger.fatal(
                'Fatal exception occured in incident_volumes_by_support_group_per_priorities_lib1 in {}'.format(
                    self.name))
            logger.error(traceback.print_exc())
        finally:
            self.bmc_logout()
            return status

    def incident_volumes_by_priority_smart_reporting_displays(self, kwargs):
        try:
            self.login_bmc()
            status = False
            status = self.verify_incident_volumes_by_priority_smart_reporting_displays(kwargs)
        except BaseException as be:
            logger.fatal(
                'Fatal exception occured in incident_volumes_by_priority_smart_reporting_displays() in {}'.format(
                    self.name))
            logger.error(traceback.print_exc())
        finally:
            self.bmc_logout()
            return status

    def Problem_Volumetric_smart_reporting_displays(self, kwargs):
        try:
            self.login_bmc()
            status = False
            status = self.verify_problem_Volumetric_smart_reporting_displays(kwargs)
        except BaseException as be:
            logger.fatal(
                'Fatal exception occured in incident_backlog_and_backlog_age_by_priority_smart_reporting_displays() in {}'.format(
                    self.name))
            logger.error(traceback.print_exc())
        finally:
            self.bmc_logout()
            return status

    def verify_active_changes_for_possible_sla_breach_gui(self, kwargs):
        try:
            self.login_bmc()
            status = False
            status = self.verify_active_changes_for_possible_sla_breach(kwargs)
        except BaseException as be:
            logger.fatal('Fatal exception occured in verify_active_changes_for_possible_sla_breach_gui() in {}'.format(
                self.name))
            logger.error(traceback.print_exc())
        finally:
            self.bmc_logout()
            return status

    def verify_change_sla_dashboard_gui(self, kwargs):
        try:
            self.login_bmc()
            status = False
            status = self.verify_change_sla_dashboard(kwargs)
        except BaseException as be:
            logger.fatal(
                'Fatal exception occured in verify_verify_verify_change_sla_dashboard_gui() in {}'.format(self.name))
            logger.error(traceback.print_exc())
        finally:
            self.bmc_logout()
            return status

    def verify_breached_change_sla_tickets_gui(self, kwargs):
        try:
            self.login_bmc()
            status = False
            status = self.verify_breached_change_sla_tickets(kwargs)
        except BaseException as be:
            logger.fatal('Fatal exception occured in verify_breached_change_sla_tickets_gui() in {}'.format(self.name))
            logger.error(traceback.print_exc())
        finally:
            self.bmc_logout()
            return status

    def report_refresh_and_data_sync_up_main(self, kwargs):
        logger.info("Execuitng smart_reporting()")
        """ Clicking on Application"""
        appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
        appl.click()

        """Clicking on Smart Reporting -> Smart Reporting Console"""
        smrtrep = self.driver.find_element_by_link_text('Smart Reporting')
        smrtrep.click()
        smrtrepcon = self.driver.find_element_by_link_text('Smart Reporting Console')
        """Clicking on smart reporting console and switchingg windows"""
        window_zero = self.driver.window_handles[0]
        smrtrepcon.click()
        WebDriverWait(self.driver, 10).until(expected_conditions.number_of_windows_to_be(2))
        window_one = self.driver.window_handles[1]
        self.driver.switch_to.window(window_one)
        time.sleep(3)
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')))
        time.sleep(3)
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')))
        search_report = self.driver.find_element(By.XPATH,
                                                 '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/input')
        search_report.send_keys(kwargs['Report Name'])
        search_report.send_keys(Keys.ENTER)
        time.sleep(2)
        """opening H3G Folder"""
        h3gopfoler = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')
        time.sleep(2)
        h3gopfoler.click()
        """Opening Rebus Reports Folder"""


        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//body[@id="browsePageBody"]/form[@name="MIForm"]/div[@class="browsePageContainer"]/div[@class="browsePage"]/div[@class="browseLeft"]/div[@class="browseFolders browseToggleSearch"]/div[@class="browseFolder"]/div[@class="subFolders"]/div[3]/div[1]/div[2]/div[8]/div[1]/div[1]')))
        rebus_reports = self.driver.find_element(By.XPATH,
                                                 '//body[@id="browsePageBody"]/form[@name="MIForm"]/div[@class="browsePageContainer"]/div[@class="browsePage"]/div[@class="browseLeft"]/div[@class="browseFolders browseToggleSearch"]/div[@class="browseFolder"]/div[@class="subFolders"]/div[3]/div[1]/div[2]/div[8]/div[1]/div[1]')

        # WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
        #                                                                                   "/html[1]/body[1]/form[1]/div[12]/div[1]/div[2]/div[4]/div[1]/div[2]/div[3]/div[1]/div[2]/div[8]/div[1]/div[1]")))
        # rebus_reports = self.driver.find_element(By.XPATH,
        #                                          "/html[1]/body[1]/form[1]/div[12]/div[1]/div[2]/div[4]/div[1]/div[2]/div[3]/div[1]/div[2]/div[8]/div[1]/div[1]")
        rebus_reports.click()
        time.sleep(3)
        """Taking Screen shot"""
        self.driver.get_screenshot_as_file('C:\GIT\output\ITSM_REBUS Reporting_233_1.png')
        """Double-click on incident-sla-dashboard report"""
        incident_sla_dashboard = self.driver.find_element(By.XPATH,
                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div[2]')
        time.sleep(2)
        action = ActionChains(self.driver)
        action.double_click(incident_sla_dashboard)
        action.perform()
        time.sleep(10)

        for i in range(1, 2):
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                (By.XPATH,
                 "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                     i))))
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                                                                  i))))
            time.sleep(3)
            obj = self.driver.find_element(By.XPATH,
                                           "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                               i))
            obj.click()
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")))
            obj1 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")
            time.sleep(1)
            obj1.click()
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable(
                (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[3]/div[2]")))
            obj2 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[3]/div[2]")
            time.sleep(1)
            obj2.click()
            time.sleep(7)

        """Taking Screen shot"""
        self.driver.get_screenshot_as_file('C:\GIT\output\ITSM_REBUS Reporting_233_2.png')

        """Extracting the incident incident id"""
        recent_ten_incidents = []
        for i in range(1, 10):
            recent_ten_incidents.append(self.driver.find_element(By.XPATH,
                                                                 "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[1]/a[1]".format(
                                                                     i)).text)
        logger.info("The recent ten incidents are: {}".format(recent_ten_incidents))

        """Getting the details of the first row in the report before updation"""
        incident_before = self.driver.find_element(By.XPATH,
                                                   "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[1]/td[1]/a[1]").text
        logger.info("Incdent ID before updation: {}".format(incident_before))
        priority_before = self.driver.find_element(By.XPATH,
                                                   "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[1]/td[3]").text
        logger.info("Priority before updation: {}".format(priority_before))
        status_before = self.driver.find_element(By.XPATH,
                                                 "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[1]/td[4]").text
        logger.info("Status before updation: {}".format(status_before))
        support_group_before = self.driver.find_element(By.XPATH,
                                                        "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[1]/td[5]").text
        logger.info("Support group before updation: {}".format(support_group_before))
        summary_before = self.driver.find_element(By.XPATH,
                                                  "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[1]/td[14]").text
        logger.info("Summary before updation: {}".format(summary_before))

        column_values_before = []
        column_values_before.extend([priority_before, status_before, support_group_before, summary_before])
        logger.info("Column values before updation: {}".format(column_values_before))

        """Switching the incident window"""
        incident_before_clickable = self.driver.find_element(By.XPATH,
                                                             "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[1]/td[1]/a[1]")

        incident_before_clickable.click()
        window_two = self.driver.window_handles[2]

        WebDriverWait(self.driver, 10).until(expected_conditions.number_of_windows_to_be(3))
        self.driver.switch_to.window(window_two)
        time.sleep(7)

        """Taking Screen shot"""
        self.driver.get_screenshot_as_file('C:\GIT\output\ITSM_REBUS Reporting_233_3.png')

        WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
            (By.XPATH, "//textarea[@id='arid_WIN_1_1000000000']")))
        summary = self.driver.find_element_by_xpath("//textarea[@id='arid_WIN_1_1000000000']")
        summary.click()
        time.sleep(1)
        summary.clear()
        # summary.send_keys(kwargs['Summary'])
        summary.send_keys(random.randint(1, 10000))

        WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
            (By.XPATH, "//div[@id='WIN_1_1000000163']//a[@class='btn btn3d selectionbtn']")))
        impact = self.driver.find_element_by_xpath("//div[@id='WIN_1_1000000163']//a[@class='btn btn3d selectionbtn']")
        impact.click()
        impact.send_keys(Keys.DOWN)
        impact.send_keys(kwargs['Impact'])
        impact.send_keys(Keys.ENTER)

        urgency = self.driver.find_element_by_xpath("//div[@id='WIN_1_1000000162']//a[@class='btn btn3d selectionbtn']")
        urgency.click()
        urgency.send_keys(Keys.DOWN)
        urgency.send_keys(kwargs['Urgency'])
        urgency.send_keys(Keys.ENTER)

        assignedgroup = self.driver.find_element_by_xpath("//textarea[@id='arid_WIN_1_1000000217']")
        assignedgroup.click()
        assignedgroup.clear()
        assignedgroup.send_keys(kwargs['Assigned_group'])
        time.sleep(3)
        assignedgroup.send_keys(Keys.DOWN)
        assignedgroup.send_keys(Keys.ENTER)

        assignee = self.driver.find_element_by_xpath("//textarea[@id='arid_WIN_1_1000000218']")
        assignee.click()
        assignee.clear()
        assignee.send_keys(kwargs['Assignee'])
        assignee.send_keys(Keys.DOWN)
        assignee.send_keys(Keys.ENTER)

        status = self.driver.find_element_by_xpath("//div[@id='WIN_1_7']//a[@class='btn btn3d selectionbtn']")
        status.click()
        status.send_keys(Keys.DOWN)
        status.send_keys(kwargs['Status'])
        time.sleep(2)
        status.send_keys(Keys.DOWN)
        time.sleep(2)
        status.send_keys(Keys.ENTER)
        

        """Taking Screen shot"""
        self.driver.get_screenshot_as_file('C:\GIT\output\ITSM_REBUS Reporting_233_4.png')

        saveinc = self.driver.find_element_by_xpath(
            "//a[@id='WIN_1_301614800']//div[@class='f1'][contains(text(),'Save')]")
        saveinc.click()
        time.sleep(10)
        """Taking Screen shot"""
        self.driver.get_screenshot_as_file('C:\GIT\output\ITSM_REBUS Reporting_233_5.png')

        """Repeating the above two steps"""
        status = self.driver.find_element_by_xpath("//div[@id='WIN_1_7']//a[@class='btn btn3d selectionbtn']")
        status.click()
        status.send_keys(Keys.DOWN)
        status.send_keys(kwargs['Status'])
        time.sleep(2)
        status.send_keys(Keys.DOWN)
        time.sleep(2)
        status.send_keys(Keys.DOWN)
        time.sleep(2)
        status.send_keys(Keys.ENTER)
        time.sleep(2)
        time.sleep(2)
        status.send_keys(Keys.ENTER)

        saveinc = self.driver.find_element_by_xpath(
            "//a[@id='WIN_1_301614800']//div[@class='f1'][contains(text(),'Save')]")
        saveinc.click()
        time.sleep(3)

        """Switching to report window"""
        self.driver.switch_to.window(window_one)

        """refreshing the data"""
        self.driver.refresh()
        time.sleep(7)

        """Taking Screen shot"""
        self.driver.get_screenshot_as_file('C:\GIT\output\ITSM_REBUS Reporting_233_6.png')

        """Getting the details of the first row in the report after updation"""
        incident_after = self.driver.find_element(By.XPATH,
                                                  "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[1]/td[1]/a[1]").text
        if incident_before != incident_after:
            incident_after = self.driver.find_element(By.XPATH,
                                                      "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[2]/td[1]/a[1]").text
            logger.info("Incdent ID after updation: {}".format(incident_after))
            priority_after = self.driver.find_element(By.XPATH,
                                                      "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[2]/td[3]").text
            logger.info("Priority after updation: {}".format(priority_after))
            status_after = self.driver.find_element(By.XPATH,
                                                    "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[2]/td[4]").text
            logger.info("Status after updation: {}".format(status_after))
            support_group_after = self.driver.find_element(By.XPATH,
                                                           "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[2]/td[5]").text
            logger.info("Support group after updation: {}".format(support_group_after))
            summary_after = self.driver.find_element(By.XPATH,
                                                     "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[2]/td[14]").text
            logger.info("Summary after updation: {}".format(summary_after))

        else:
            incident_after = self.driver.find_element(By.XPATH,
                                                      "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[1]/td[1]/a[1]").text
            logger.info("Incdent ID after updation: {}".format(incident_after))
            priority_after = self.driver.find_element(By.XPATH,
                                                      "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[1]/td[3]").text
            logger.info("Priority after updation: {}".format(priority_after))
            status_after = self.driver.find_element(By.XPATH,
                                                    "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[1]/td[4]").text
            logger.info("Status after updation: {}".format(status_after))
            support_group_after = self.driver.find_element(By.XPATH,
                                                           "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[1]/td[5]").text
            logger.info("Support group after updation: {}".format(support_group_after))
            summary_after = self.driver.find_element(By.XPATH,
                                                     "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[1]/td[14]").text
            logger.info("Summary after updation: {}".format(summary_after))

        column_values_after = []
        column_values_after.extend([priority_after, status_after, support_group_after, summary_after])
        logger.info("Column values after updation: {}".format(column_values_after))

        self.driver.switch_to.window(window_zero)

        matching = True

        if column_values_before == column_values_after:
            matching = False
        return matching

    def report_refresh_and_data_sync_up_breach_details_main(self, kwargs):
        logger.info("Execuitng smart_reporting()")
        """ Clicking on Application"""
        appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
        appl.click()

        """Clicking on Smart Reporting -> Smart Reporting Console"""
        smrtrep = self.driver.find_element_by_link_text('Smart Reporting')
        smrtrep.click()
        smrtrepcon = self.driver.find_element_by_link_text('Smart Reporting Console')
        """Clicking on smart reporting console and switchingg windows"""
        window_zero = self.driver.window_handles[0]
        smrtrepcon.click()
        WebDriverWait(self.driver, 10).until(expected_conditions.number_of_windows_to_be(2))
        window_one = self.driver.window_handles[1]
        self.driver.switch_to.window(window_one)
        time.sleep(3)
        WebDriverWait(self.driver, 100).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                           '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')))
        time.sleep(3)
        WebDriverWait(self.driver, 100).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                           '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')))
        search_report = self.driver.find_element(By.XPATH,
                                                 '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/input')
        search_report.send_keys(kwargs['Report Name'])
        search_report.send_keys(Keys.ENTER)
        time.sleep(2)
        """opening H3G Folder"""
        h3gopfoler = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')
        time.sleep(2)
        h3gopfoler.click()
        """Opening Rebus Reports Folder"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          "/html[1]/body[1]/form[1]/div[12]/div[1]/div[2]/div[4]/div[1]/div[2]/div[3]/div[1]/div[2]/div[8]/div[1]/div[1]")))
        rebus_reports = self.driver.find_element(By.XPATH,
                                                 "/html[1]/body[1]/form[1]/div[12]/div[1]/div[2]/div[4]/div[1]/div[2]/div[3]/div[1]/div[2]/div[8]/div[1]/div[1]")
        rebus_reports.click()
        time.sleep(3)
        """Taking Screen shot"""
        self.driver.get_screenshot_as_file('C:\GIT\output\ITSM_REBUS Reporting_224_1.png')
        """Double-click on incident-sla-dashboard report"""
        incident_sla_dashboard = self.driver.find_element(By.XPATH,
                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div[2]')
        time.sleep(2)
        action = ActionChains(self.driver)
        action.double_click(incident_sla_dashboard)
        action.perform()
        time.sleep(10)

        for i in range(1, 2):
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                (By.XPATH,
                 "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                     i))))
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                                                                  i))))
            time.sleep(3)
            obj = self.driver.find_element(By.XPATH,
                                           "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                               i))
            obj.click()
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")))
            obj1 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")
            time.sleep(1)
            obj1.click()
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable(
                (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[3]/div[2]")))
            obj2 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[3]/div[2]")
            time.sleep(1)
            obj2.click()
            time.sleep(7)

        """Taking Screen shot"""
        self.driver.get_screenshot_as_file('C:\GIT\output\ITSM_REBUS Reporting_224_2.png')

        """Getting the details of the first row in the report before updation"""
        incident_before = self.driver.find_element(By.XPATH,
                                                   "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[1]/td[1]/a[1]").text
        logger.info("Incdent ID before updation: {}".format(incident_before))
        priority_before = self.driver.find_element(By.XPATH,
                                                   "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[1]/td[3]").text
        logger.info("Priority before updation: {}".format(priority_before))
        status_before = self.driver.find_element(By.XPATH,
                                                 "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[1]/td[4]").text
        logger.info("Status before updation: {}".format(status_before))
        support_group_before = self.driver.find_element(By.XPATH,
                                                        "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[1]/td[5]").text
        logger.info("Support group before updation: {}".format(support_group_before))
        summary_before = self.driver.find_element(By.XPATH,
                                                  "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[1]/td[13]").text
        logger.info("Summary before updation: {}".format(summary_before))

        column_values_before = []
        column_values_before.extend([priority_before, status_before, support_group_before, summary_before])
        logger.info("Column values before updation: {}".format(column_values_before))

        """Switching the incident window"""
        incident_before_clickable = self.driver.find_element(By.XPATH,
                                                             "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[1]/td[1]/a[1]")
        incident_before_clickable.click()
        window_two = self.driver.window_handles[2]

        WebDriverWait(self.driver, 10).until(expected_conditions.number_of_windows_to_be(3))
        self.driver.switch_to.window(window_two)
        time.sleep(5)

        """Taking Screen shot"""
        self.driver.get_screenshot_as_file('C:\GIT\output\ITSM_REBUS Reporting_224_3.png')

        WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
            (By.XPATH, "//textarea[@id='arid_WIN_1_1000000000']")))
        summary = self.driver.find_element_by_xpath("//textarea[@id='arid_WIN_1_1000000000']")
        summary.click()
        time.sleep(1)
        summary.clear()
        summary.send_keys(kwargs['Summary'])

        WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
            (By.XPATH, "//div[@id='WIN_1_1000000163']//a[@class='btn btn3d selectionbtn']")))
        impact = self.driver.find_element_by_xpath("//div[@id='WIN_1_1000000163']//a[@class='btn btn3d selectionbtn']")
        impact.click()
        impact.send_keys(Keys.DOWN)
        impact.send_keys(kwargs['Impact'])
        impact.send_keys(Keys.ENTER)

        urgency = self.driver.find_element_by_xpath("//div[@id='WIN_1_1000000162']//a[@class='btn btn3d selectionbtn']")
        urgency.click()
        urgency.send_keys(Keys.DOWN)
        urgency.send_keys(kwargs['Urgency'])
        urgency.send_keys(Keys.ENTER)

        assignedgroup = self.driver.find_element_by_xpath("//textarea[@id='arid_WIN_1_1000000217']")
        assignedgroup.click()
        assignedgroup.clear()
        assignedgroup.send_keys(kwargs['Assigned_group'])
        time.sleep(3)
        assignedgroup.send_keys(Keys.DOWN)
        assignedgroup.send_keys(Keys.ENTER)

        assignee = self.driver.find_element_by_xpath("//textarea[@id='arid_WIN_1_1000000218']")
        assignee.click()
        assignee.clear()
        assignee.send_keys(kwargs['Assignee'])
        assignee.send_keys(Keys.DOWN)
        assignee.send_keys(Keys.ENTER)

        status = self.driver.find_element_by_xpath("//div[@id='WIN_1_7']//a[@class='btn btn3d selectionbtn']")
        status.click()
        status.send_keys(Keys.DOWN)
        status.send_keys(kwargs['Status'])
        time.sleep(2)
        status.send_keys(Keys.DOWN)
        time.sleep(2)
        status.send_keys(Keys.ENTER)

        """Taking Screen shot"""
        self.driver.get_screenshot_as_file('C:\GIT\output\ITSM_REBUS Reporting_224_4.png')

        saveinc = self.driver.find_element_by_xpath(
            "//a[@id='WIN_1_301614800']//div[@class='f1'][contains(text(),'Save')]")
        saveinc.click()
        time.sleep(6)
        """Taking Screen shot"""
        self.driver.get_screenshot_as_file('C:\GIT\output\ITSM_REBUS Reporting_224_5.png')

        """Repeating the above two steps"""
        status = self.driver.find_element_by_xpath("//div[@id='WIN_1_7']//a[@class='btn btn3d selectionbtn']")
        status.click()
        status.send_keys(Keys.DOWN)
        status.send_keys(kwargs['Status'])
        time.sleep(2)
        status.send_keys(Keys.DOWN)
        time.sleep(2)
        status.send_keys(Keys.DOWN)
        time.sleep(2)
        status.send_keys(Keys.ENTER)
        time.sleep(2)

        saveinc = self.driver.find_element_by_xpath(
            "//a[@id='WIN_1_301614800']//div[@class='f1'][contains(text(),'Save')]")
        saveinc.click()
        time.sleep(3)

        """Switching to report window"""
        self.driver.switch_to.window(window_one)

        """refreshing the data"""
        self.driver.refresh()
        time.sleep(7)

        """Taking Screen shot"""
        self.driver.get_screenshot_as_file('C:\GIT\output\ITSM_REBUS Reporting_224_6.png')

        """Getting the details of the first row in the report after updation"""
        incident_after = self.driver.find_element(By.XPATH,
                                                  "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[1]/td[1]/a[1]").text
        if incident_before != incident_after:
            incident_after = self.driver.find_element(By.XPATH,
                                                      "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[2]/td[1]/a[1]").text
            logger.info("Incdent ID after updation: {}".format(incident_after))
            priority_after = self.driver.find_element(By.XPATH,
                                                      "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[2]/td[3]").text
            logger.info("Priority after updation: {}".format(priority_after))
            status_after = self.driver.find_element(By.XPATH,
                                                    "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[2]/td[4]").text
            logger.info("Status after updation: {}".format(status_after))
            support_group_after = self.driver.find_element(By.XPATH,
                                                           "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[2]/td[5]").text
            logger.info("Support group after updation: {}".format(support_group_after))
            summary_after = self.driver.find_element(By.XPATH,
                                                     "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[2]/td[13]").text
            logger.info("Summary after updation: {}".format(summary_after))

        else:
            incident_after = self.driver.find_element(By.XPATH,
                                                      "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[1]/td[1]/a[1]").text
            logger.info("Incdent ID after updation: {}".format(incident_after))
            priority_after = self.driver.find_element(By.XPATH,
                                                      "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[1]/td[3]").text
            logger.info("Priority after updation: {}".format(priority_after))
            status_after = self.driver.find_element(By.XPATH,
                                                    "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[1]/td[4]").text
            logger.info("Status after updation: {}".format(status_after))
            support_group_after = self.driver.find_element(By.XPATH,
                                                           "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[1]/td[5]").text
            logger.info("Support group after updation: {}".format(support_group_after))
            summary_after = self.driver.find_element(By.XPATH,
                                                     "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[1]/td[13]").text
            logger.info("Summary after updation: {}".format(summary_after))

        column_values_after = []
        column_values_after.extend([priority_after, status_after, support_group_after, summary_after])
        logger.info("Column values after updation:{}".format(column_values_after))

        self.driver.switch_to.window(window_zero)

        matching = True

        if column_values_before == column_values_after:
            matching = False
        return matching

    def report_refresh_and_sync_up_upcoming_problems_main(self, kwargs):
        logger.info("Executing_Create_Problem_by_priority()")
        '''application xpath'''
        app = self.driver.find_element_by_xpath('.//*[@id="reg_img_304316340"]')
        app.click()
        time.sleep(3)
        '''Clicking on Problem Management -> Search Problem'''
        prbmgmt = self.driver.find_element_by_link_text('Problem Management')
        prbmgmt.click()
        search_problem = self.driver.find_element_by_link_text('Search Problem')
        search_problem.click()
        time.sleep(4)

        '''Passing the valu of the problem ID in the search bar'''
        search_problem_field = self.driver.find_element(By.XPATH, "//textarea[@id='arid_WIN_3_1000000232']")
        search_problem_field.send_keys(kwargs['Problem_id'])
        time.sleep(1)
        search_problem_field.send_keys(Keys.ENTER)
        time.sleep(2)

        """Taking Screen shot"""
        self.driver.get_screenshot_as_file('C:\GIT\output\ITSM_REBUS Reporting_179_1.png')

        """Going to reporting page"""
        logger.info("Execuitng smart_reporting()")
        """ Clicking on Application"""
        appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
        appl.click()

        """Clicking on Smart Reporting -> Smart Reporting Console"""
        smrtrep = self.driver.find_element_by_link_text('Smart Reporting')
        smrtrep.click()
        smrtrepcon = self.driver.find_element_by_link_text('Smart Reporting Console')
        """Clicking on smart reporting console and switchingg windows"""
        window_zero = self.driver.window_handles[0]
        smrtrepcon.click()
        WebDriverWait(self.driver, 10).until(expected_conditions.number_of_windows_to_be(2))
        window_one = self.driver.window_handles[1]
        self.driver.switch_to.window(window_one)
        time.sleep(3)
        WebDriverWait(self.driver, 100).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                           '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')))
        time.sleep(3)
        WebDriverWait(self.driver, 100).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                           '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')))
        search_report = self.driver.find_element(By.XPATH,
                                                 '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/input')
        search_report.send_keys(kwargs['Report Name'])
        search_report.send_keys(Keys.ENTER)
        time.sleep(2)
        """opening H3G Folder"""
        h3gopfoler = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')
        time.sleep(2)
        h3gopfoler.click()
        """Opening Rebus Reports Folder"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          "/html[1]/body[1]/form[1]/div[12]/div[1]/div[2]/div[4]/div[1]/div[2]/div[3]/div[1]/div[2]/div[8]/div[1]/div[1]")))
        rebus_reports = self.driver.find_element(By.XPATH,
                                                 "/html[1]/body[1]/form[1]/div[12]/div[1]/div[2]/div[4]/div[1]/div[2]/div[3]/div[1]/div[2]/div[8]/div[1]/div[1]")
        rebus_reports.click()
        time.sleep(3)
        """Taking Screen shot"""
        self.driver.get_screenshot_as_file('C:\GIT\output\ITSM_REBUS Reporting_179_2.png')
        """Double-click on incident-sla-dashboard report"""
        incident_sla_dashboard = self.driver.find_element(By.XPATH,
                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div[2]')
        time.sleep(2)
        action = ActionChains(self.driver)
        action.double_click(incident_sla_dashboard)
        action.perform()
        time.sleep(10)

        logger.info("Sorting in descending order")
        for i in range(1, 2):
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                (By.XPATH,
                 "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                     i))))
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                                                                  i))))
            time.sleep(3)
            obj = self.driver.find_element(By.XPATH,
                                           "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                               i))
            obj.click()
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")))
            obj1 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")
            time.sleep(1)
            obj1.click()
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable(
                (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[3]/div[2]")))
            obj2 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[3]/div[2]")
            time.sleep(1)
            obj2.click()
            time.sleep(7)

        """Taking Screen shot"""
        self.driver.get_screenshot_as_file('C:\GIT\output\ITSM_REBUS Reporting_179_3.png')

        logger.info("Clicking on the reset button")
        reset = self.driver.find_element(By.XPATH,
                                         '//*[@id="pagecontent"]/div[2]/div[3]/div[1]/div/div/div[3]/div[2]/table/tbody/tr/td/div/table/tbody/tr/td[2]/span')
        reset.click()
        time.sleep(5)
        '''Taking details before updation'''
        problem_id_before = self.driver.find_element(By.XPATH,
                                                     "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[1]/td[1]").text
        logger.info("Problem ID before: {}".format(problem_id_before))
        priority_before = self.driver.find_element(By.XPATH,
                                                   "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[1]/td[3]").text
        logger.info("Priority before: {}".format(priority_before))
        status_before = self.driver.find_element(By.XPATH,
                                                 "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[1]/td[4]").text
        logger.info("Status before: {}".format(status_before))
        support_group_before = self.driver.find_element(By.XPATH,
                                                        "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[1]/td[5]").text
        logger.info("Support group before: {}".format(support_group_before))
        assignee_before = self.driver.find_element(By.XPATH,
                                                   "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[1]/td[6]").text
        logger.info("Assignee before: {}".format(assignee_before))
        summary_before = self.driver.find_element(By.XPATH,
                                                  "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[12]/div[1]").text
        logger.info("Summary before: {}".format(summary_before))

        column_values_before = []
        column_values_before.extend(
            [priority_before, status_before, support_group_before, assignee_before, summary_before])
        logger.info("Column values before updation: {}".format(column_values_before))

        logger.info("Switching to previous window to change the parameters of the corresponding problem")
        self.driver.switch_to.window(window_zero)

        WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
            (By.XPATH, "//textarea[@id='arid_WIN_3_1000000000']")))
        summary = self.driver.find_element_by_xpath("//textarea[@id='arid_WIN_3_1000000000']")
        summary.click()
        time.sleep(1)
        summary.clear()
        summary.send_keys(kwargs['Summary_after'])
        summary.send_keys(Keys.ENTER)
        # time.sleep(3)

        urgencies = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_1000000162"]')
        urgencies.click()
        urgencies.send_keys(Keys.DOWN)
        urgencies.send_keys(kwargs['Urgency_after'])
        time.sleep(3)
        urgencies.send_keys(Keys.ENTER)
        # time.sleep(3)

        impact = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_1000000163"]')
        impact.click()
        impact.send_keys(Keys.DOWN)
        impact.send_keys(kwargs['Impact_after'])
        time.sleep(3)
        impact.send_keys(Keys.ENTER)

        assignedgroup = self.driver.find_element_by_xpath("//textarea[@id='arid_WIN_3_1000000217']")
        assignedgroup.click()
        assignedgroup.clear()
        assignedgroup.send_keys(kwargs['Assigned_group_after'])
        time.sleep(3)
        assignedgroup.send_keys(Keys.DOWN)
        assignedgroup.send_keys(Keys.ENTER)

        """Taking Screen shot"""
        self.driver.get_screenshot_as_file('C:\GIT\output\ITSM_REBUS Reporting_179_4.png')

        assignee = self.driver.find_element_by_xpath("//textarea[@id='arid_WIN_3_1000000218']")
        assignee.click()
        time.sleep(1)
        assignee.clear()
        assignee.send_keys(kwargs['Assignee_after'])
        assignee.send_keys(Keys.DOWN)
        assignee.send_keys(Keys.ENTER)

        status = self.driver.find_element_by_xpath("//div[@id='WIN_3_7']//a[@class='btn btn3d selectionbtn']")
        status.click()
        time.sleep(2)
        status.send_keys(Keys.DOWN)
        time.sleep(2)
        status.send_keys(Keys.DOWN)
        time.sleep(2)
        status.send_keys(Keys.DOWN)
        time.sleep(2)
        status.send_keys(Keys.DOWN)
        time.sleep(2)
        status.send_keys(Keys.DOWN)
        time.sleep(2)
        status.send_keys(Keys.ENTER)

        """"Save buton click"""
        self.driver.find_element_by_xpath(
            "//a[@id='WIN_3_301614800']//div[@class='f1'][contains(text(),'Save')]").click()
        time.sleep(3)

        logger.info("Going back to reporting page")
        self.driver.switch_to.window(window_one)
        logger.info("Reseting the data after updation")

        logger.info("refreshing the browser")
        self.driver.refresh()
        time.sleep(5)

        """Taking Screen shot"""
        self.driver.get_screenshot_as_file('C:\GIT\output\ITSM_REBUS Reporting_179_5.png')

        '''Taking details after updation'''
        problem_id_after = self.driver.find_element(By.XPATH,
                                                    "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[1]/td[1]").text
        logger.info("Problem ID after: {}".format(problem_id_after))
        if problem_id_after == problem_id_before:
            priority_after = self.driver.find_element(By.XPATH,
                                                      "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[1]/td[3]").text
            logger.info("Priority after: {}".format(priority_after))
            status_after = self.driver.find_element(By.XPATH,
                                                    "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[1]/td[4]").text
            logger.info("Status after: {}".format(status_after))
            support_group_after = self.driver.find_element(By.XPATH,
                                                           "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[1]/td[5]").text
            logger.info("Support group after: {}".format(support_group_after))
            assignee_after = self.driver.find_element(By.XPATH,
                                                      "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[1]/td[6]").text
            logger.info("Assignee after: {}".format(assignee_after))
            summary_after = self.driver.find_element(By.XPATH,
                                                     "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[2]/td[12]").text
            logger.info("Summary after: {}".format(summary_after))
        else:
            priority_after = self.driver.find_element(By.XPATH,
                                                      "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[2]/td[3]").text
            logger.info("Priority after: {}".format(priority_after))
            status_after = self.driver.find_element(By.XPATH,
                                                    "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[2]/td[4]").text
            logger.info("Status after: {}".format(status_after))
            support_group_after = self.driver.find_element(By.XPATH,
                                                           "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[2]/tr[1]/td[5]").text
            logger.info("Support after: {}".format(support_group_after))
            assignee_after = self.driver.find_element(By.XPATH,
                                                      "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[2]/td[6]").text
            logger.info("Assignee after: {}".format(assignee_after))
            summary_after = self.driver.find_element(By.XPATH,
                                                     "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[2]/td[12]").text
            logger.info("Summary after: {}".format(summary_after))

        column_values_after = []
        column_values_after.extend([priority_after, status_after, support_group_after, assignee_after, summary_after])
        logger.info("Column values after updation:{}".format(column_values_after))

        logger.info("Switching back to previous window and exiting")
        self.driver.switch_to.window(window_zero)

        matching = True
        if column_values_before == column_values_after:
            matching = False

        return matching

    def upcoming_problems_sla_breach_details_column_name_verification_main(self, kwargs):
        logger.info("Execuitng smart_reporting()")
        """ Clicking on Application"""
        appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
        appl.click()

        """Clicking on Smart Reporting -> Smart Reporting Console"""
        smrtrep = self.driver.find_element_by_link_text('Smart Reporting')
        smrtrep.click()
        smrtrepcon = self.driver.find_element_by_link_text('Smart Reporting Console')
        """Clicking on smart reporting console and switchingg windows"""
        window_before = self.driver.window_handles[0]
        smrtrepcon.click()
        WebDriverWait(self.driver, 10).until(expected_conditions.number_of_windows_to_be(2))
        window_after = self.driver.window_handles[1]
        self.driver.switch_to.window(window_after)
        time.sleep(3)
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')))
        time.sleep(3)
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')))
        search_report = self.driver.find_element(By.XPATH,
                                                 '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/input')
        search_report.send_keys(kwargs['Report Name'])
        search_report.send_keys(Keys.ENTER)
        """opening H3G Folder"""
        h3gopfoler = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')
        h3gopfoler.click()
        """Opening rebus reports Folder"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          "/html[1]/body[1]/form[1]/div[12]/div[1]/div[2]/div[4]/div[1]/div[2]/div[3]/div[1]/div[2]/div[8]/div[1]/div[1]")))
        maya_reports = self.driver.find_element(By.XPATH,
                                                "/html[1]/body[1]/form[1]/div[12]/div[1]/div[2]/div[4]/div[1]/div[2]/div[3]/div[1]/div[2]/div[8]/div[1]/div[1]")
        maya_reports.click()
        time.sleep(3)

        """Taking Screen shot"""
        self.driver.get_screenshot_as_file('C:\GIT\output\ITSM_REBUS Reporting_175_1.png')

        """Double-click on Upcoming Problem SLA Breach Details report"""
        incident_sla_dashboard = self.driver.find_element(By.XPATH,
                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div[2]')
        time.sleep(2)
        action = ActionChains(self.driver)
        action.double_click(incident_sla_dashboard)
        action.perform()
        time.sleep(5)

        """Taking Screen shot"""
        self.driver.get_screenshot_as_file('C:\GIT\output\ITSM_REBUS Reporting_175_2.png')

        """Getting the list of the columns"""
        column_list = []
        for i in range(1, 13):
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                                  '/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/div[1]'.format(
                                                                                                      i))))
            column_list.append(self.driver.find_element(By.XPATH,
                                                        '/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/div[1]'.format(
                                                            i)).text)
        column_names = ", ".join(column_list)
        logger.info("Following columns are present in the report:")
        count = 1
        for i in column_list:
            logger.info("COLUMN {}: {}".format(count, i))
            count += 1
        self.driver.switch_to.window(window_before)
        matching = True
        if column_names != kwargs['Column_names']:
            matching = False
        return matching

    def breached_problems_SLA_tickets_by_names(self, kwargs):
        logger.info(" Executing breached_problems_SLA_tickets_by_names()")
        window_before = self.driver.window_handles[0]

        self.driver.get_screenshot_as_file('D:\git\November192018\Screenshots\screenshot0.png')
        """ Clicking on Application"""
        appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
        appl.click()
        logger.info("clicked on application")

        """Clicking on Smart Reporting -> Smart Reporting Console"""
        smrtrep = self.driver.find_element_by_link_text('Smart Reporting')
        smrtrep.click()
        smrtrepcon = self.driver.find_element_by_link_text('Smart Reporting Console')
        smrtrepcon.click()
        time.sleep(20)
        WebDriverWait(self.driver, 50).until(
            expected_conditions.number_of_windows_to_be(2))
        window_after = self.driver.window_handles[1]
        self.driver.switch_to.window(window_after)

        """ScreenShot - Taken"""
        self.driver.get_screenshot_as_file('D:\git\November192018\Screenshots\screenshot1.png')

        """All already clicked"""
        """Click H3G"""
        obj_h3g = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[1]')
        obj_h3g.click()
        """click on Rebus Reports"""
        obj_rebus = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[2]/div[8]/div/div/div/div[2]')
        obj_rebus.click()

        """Search content"""
        send_repo = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/input')
        send_repo.send_keys(kwargs['Report_name'])

        search_icon = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/div[2]/div[2]/img')
        search_icon.click()

        """ScreenShot - Taken"""
        self.driver.get_screenshot_as_file('D:\git\November192018\Screenshots\screenshot2.png')

        time.sleep(10)
        """Double clicking on report"""
        repo = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[2]/div/div[1]/div[2]')
        action = ActionChains(self.driver)
        action.double_click(repo).perform()

        time.sleep(7)
        """ScreenShot - Taken"""
        self.driver.get_screenshot_as_file('D:\git\November192018\Screenshots\screenshot3.png')
        self.driver.save_screenshot("ReportNamePriority.png")
        report_display_1_upper = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[1]/table/tbody/tr[1]/td').text
        logger.info("The upper display=  {}".format(report_display_1_upper))

        """Verify if smart reporting lower 1 displays"""
        report_display_1_lower = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[1]/table/tbody/tr[2]/td').text
        logger.info("The lower display=  {}".format(report_display_1_lower))

        """Verify if smart reporting displays the mentioned reports"""
        string = list()

        if report_display_1_upper != kwargs['Report_display_1_upper']:
            string.append('uppername')
        if report_display_1_lower != kwargs['Report_display_1_lower']:
            string.append('lowername')

        if len(string) == 0:
            logger.info("Passed - The mentioned report names are available in the report as in requirement")
            return True
        else:
            logger.info(
                "Failed - The mentioned report names are not available in the report as in requirement, The incorrect report names are =  {} ".format(
                    string))
        return False

    def breached_problems_SLA_tickets_by_names_columns_gui(self, kwargs):
        logger.info(" Executing breached_problems_SLA_tickets_by_names_columns_gui()")
        window_before = self.driver.window_handles[0]
        self.driver.get_screenshot_as_file('D:\git\November192018\Screenshots\ss1.png')
        """ Clicking on Application"""
        appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
        appl.click()

        """Clicking on Smart Reporting -> Smart Reporting Console"""
        smrtrep = self.driver.find_element_by_link_text('Smart Reporting')
        smrtrep.click()
        smrtrepcon = self.driver.find_element_by_link_text('Smart Reporting Console')
        smrtrepcon.click()
        time.sleep(20)
        WebDriverWait(self.driver, 30).until(
            expected_conditions.number_of_windows_to_be(2))
        window_after = self.driver.window_handles[1]
        self.driver.switch_to.window(window_after)

        """ScreenShot - Taken"""
        self.driver.get_screenshot_as_file('D:\git\November192018\Screenshots\ss2.png')

        """All already clicked"""
        """Click H3G"""
        obj_h3g = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[1]')
        obj_h3g.click()
        """click on Rebus Reports"""
        obj_rebus = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[2]/div[8]/div/div/div/div[2]')
        obj_rebus.click()

        """Search content"""
        send_repo = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/input')
        send_repo.send_keys(kwargs['Report_name'])

        search_icon = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/div[2]/div[2]/img')
        search_icon.click()

        """ScreenShot - Taken"""
        self.driver.get_screenshot_as_file('D:\git\November192018\Screenshots\ss3.png')

        time.sleep(10)
        """Double clicking on report"""
        repo = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[2]/div/div[1]/div[2]')
        action = ActionChains(self.driver)
        action.double_click(repo).perform()

        time.sleep(7)
        """ScreenShot - Taken"""
        self.driver.get_screenshot_as_file('D:\git\November192018\Screenshots\ss4.png')

        """Verify column"""
        self.driver.save_screenshot("ColumnNamePriority.png")
        prb = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[1]/div').text
        logger.info("The upper display=  {}".format(prb))

        sla = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[2]/div').text
        logger.info("The upper display=  {}".format(sla))

        priority = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[3]/div').text
        logger.info("The upper display=  {}".format(priority))

        status = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[4]/div').text
        logger.info("The upper display=  {}".format(status))

        support_group = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[5]/div').text
        logger.info("The upper display=  {}".format(support_group))

        assignee = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[6]/div').text
        logger.info("The upper display=  {}".format(assignee))

        has_breached = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[7]/div').text
        logger.info("The upper display=  {}".format(has_breached))

        submit_date = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[8]/div').text
        logger.info("The upper display=  {}".format(submit_date))

        complete = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[9]/div').text
        logger.info("The upper display=  {}".format(complete))

        actual = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[10]/div').text
        logger.info("The upper display=  {}".format(actual))

        problem = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[11]/div').text
        logger.info("The upper display=  {}".format(problem))

        summary = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[12]/div').text
        logger.info("The upper display=  {}".format(summary))

        time.sleep(2)
        """Verify if the mentioned names & columns are available in the reports as in requirement sheet"""
        string = list()

        if prb != kwargs['column1']:
            string.append('prb')
        if sla != kwargs['column2']:
            string.append('sla')
        if priority != kwargs['column3']:
            string.append('priority')
        if status != kwargs['column4']:
            string.append('status')
        if support_group != kwargs['column5']:
            string.append('support_group')
        if assignee != kwargs['column6']:
            string.append('assignee')
        if has_breached != kwargs['column7']:
            string.append('has_breached')
        if submit_date != kwargs['column8']:
            string.append('submit_date')
        if complete != kwargs['column9']:
            string.append('complete')
        if actual != kwargs['column10']:
            string.append('actual')
        if problem != kwargs['column11']:
            string.append('problem')
        if summary != kwargs['column12']:
            string.append('summary')

        if len(string) == 0:
            logger.info("Passed - The mentioned names & columns are available in the report as in requirement")
            return True
        else:
            logger.info(
                "Failed - The mentioned names & columns are not available in the report as in requirement, The incorrect column names are =  {} ".format(
                    string))
        return False

    def breached_problem_sorting_of_data(self, kwargs):
        logger.info("Executing breached_problem_sorting_of_data()")
        window_before = self.driver.window_handles[0]
        """ Clicking on Application"""
        appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
        appl.click()
        """Clicking on Smart Reporting -> Smart Reporting Console"""
        smrtrep = self.driver.find_element_by_link_text('Smart Reporting')
        smrtrep.click()
        smrtrepcon = self.driver.find_element_by_link_text('Smart Reporting Console')
        smrtrepcon.click()
        time.sleep(20)
        WebDriverWait(self.driver, 30).until(
            expected_conditions.number_of_windows_to_be(2))
        window_after = self.driver.window_handles[1]
        self.driver.switch_to.window(window_after)

        time.sleep(30)
        """Click H3G"""
        obj_h3g = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[1]')
        obj_h3g.click()
        """click on Rebus Reports"""
        obj_rebus = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[2]/div[8]/div/div/div/div[2]')
        obj_rebus.click()

        """Search content"""
        send_repo = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/input')  # search field
        send_repo.send_keys(kwargs['report_name'])
        time.sleep(2)
        send_repo.send_keys(Keys.ENTER)
        time.sleep(10)
        """ScreenShot"""
        self.driver.save_screenshot("VPN1.png")

        """Double clicking on report"""
        repo = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div[2]/div[2]/div/div/div[2]')
        action = ActionChains(self.driver)
        action.double_click(repo).perform()

        time.sleep(6)
        """ScreenShot"""
        self.driver.save_screenshot("VPN2.png")

        """Creating Python List"""
        List = []

        time.sleep(7)
        """Getting table xpath"""
        table = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table')

        """counting number of rows in table"""
        count = 0
        for i in table.find_elements_by_tag_name('tr'):
            count += 1

        logger.info("Number of row in table = {}".format(count))

        logger.info("started executing Prb asc operation")

        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[1]/img')))
        """ascending"""
        self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[1]/img').click()  # prb image
        logger.info("clicked on priority")
        self.driver.find_element_by_xpath('/html/body/ul/li[2]/div').click()  # sort
        logger.info("clicked on sorting")

        """ScreenShot"""
        self.driver.save_screenshot("VPN3.png")

        self.driver.find_element_by_xpath('/html/body/ul/li[2]/ul/li[2]/div[2]').click()  # ascending
        logger.info("clicked on ascending")

        time.sleep(3)
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN4.png")

        for i in range(1, count):
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[1]'.format(
                                                                                                  i))))
            List.append(self.driver.find_element_by_xpath(
                '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[1]'.format(
                    i)).text)
        logger.info("collected the values")
        logger.info("List = {}".format(List))
        """Checking whether list is ascending order or not"""
        prb_colm_asc_status = False

        """Converting list's element in integer"""
        List = list(filter(None, List))  # Using filter to remove NULL values

        for i in range(len(List)):
            List[i] = List[i].encode('ASCII')

        if self.listSortedOrNot(List):
            prb_colm_asc_status = True
        logger.info("function called")

        del List[0:len(List)]

        logger.info("finished executing asc operation of prb")

        logger.info("started executing SLA Metric name asc operation")

        """ascending"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[2]/img')))
        self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[2]/img').click()  # sla image
        self.driver.find_element_by_xpath('/html/body/ul/li[2]/div').click()  # sort
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN7.png")
        self.driver.find_element_by_xpath('/html/body/ul/li[2]/ul/li[2]/div[2]').click()  # ascending

        time.sleep(3)
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN8.png")
        for i in range(1, count):
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[2]'.format(
                                                                                                  i))))
            List.append(self.driver.find_element_by_xpath(
                '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[2]'.format(
                    i)).text)
        logger.info("List = {}".format(List))

        """Checking whether list is ascending order or not"""
        sla_colm_asc_status = False

        """Converting list's element in integer"""
        List = list(filter(None, List))  # Using filter to remove NULL values

        for i in range(len(List)):
            List[i] = List[i].encode('ASCII')

        if self.listSortedOrNot(List):
            sla_colm_asc_status = True

        del List[0:len(List)]

        logger.info("finished executing SLA Metric name asc operation")

        logger.info("started executing priority asc operation")

        """ascending"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[3]/img')))
        self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[3]/img').click()  # priority image

        self.driver.find_element_by_xpath('/html/body/ul/li[2]/div').click()  # sort

        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN11.png")
        ass = self.driver.find_element_by_xpath('/html/body/ul/li[2]/ul/li[2]/div[2]')
        ass.click()  # ascending
        time.sleep(4)
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN12.png")
        for i in range(1, count):
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[3]'.format(
                                                                                                  i))))
            List.append(self.driver.find_element_by_xpath(
                '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[3]'.format(
                    i)).text)
        """Checking whether list is ascending order or not"""
        priority_colm_asc_status = False

        """Converting list's element in integer"""
        List = list(filter(None, List))  # Using filter to remove NULL values

        for i in range(len(List)):
            List[i] = List[i].encode('ASCII')

        if self.listSortedOrNot(List):
            priority_colm_asc_status = True
        logger.info("List = {}".format(List))
        del List[0:len(List)]

        logger.info("finished executing priority asc operation")

        logger.info("started executing status asc operation")

        """ascending"""
        time.sleep(5)
        self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[4]/img').click()  # status image
        self.driver.find_element_by_xpath('/html/body/ul/li[2]/div').click()  # sort
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN15.png")

        self.driver.find_element_by_xpath('/html/body/ul/li[2]/ul/li[2]/div[2]').click()  # ascending

        time.sleep(3)
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN16.png")

        for i in range(1, count):
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[4]'.format(
                                                                                                  i))))
            List.append(self.driver.find_element_by_xpath(
                '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[4]'.format(
                    i)).text)

        """Checking whether list is ascending order or not"""
        status_colm_asc_status = False

        """Converting list's element in integer"""
        List = list(filter(None, List))  # Using filter to remove NULL values

        for i in range(len(List)):
            List[i] = List[i].encode('ASCII')

        if self.listSortedOrNot(List):
            status_colm_asc_status = True
        logger.info("List = {}".format(List))
        del List[0:len(List)]

        logger.info("finished executing status asc operation")

        logger.info("started executing support group asc operation")
        time.sleep(5)
        """ascending"""
        self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[5]/img').click()  # support group image
        self.driver.find_element_by_xpath('/html/body/ul/li[2]/div').click()  # sort
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN19.png")

        self.driver.find_element_by_xpath('/html/body/ul/li[2]/ul/li[2]/div[2]').click()  # ascending

        time.sleep(3)
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN20.png")

        for i in range(1, count):
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[5]'.format(
                                                                                                  i))))
            List.append(self.driver.find_element_by_xpath(
                '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[1]/td[5]'.format(
                    i)).text)
        logger.info("List = {}".format(List))
        """Checking whether list is ascending order or not"""

        support_colm_asc_status = False
        """Converting list's element in integer"""
        List = list(filter(None, List))  # Using filter to remove NULL values

        for i in range(len(List)):
            List[i] = List[i].encode('ASCII')

        if self.listSortedOrNot(List):
            support_colm_asc_status = True

        del List[0:len(List)]

        logger.info("finished executing waiting support group asc operation")

        logger.info("started executing Assignee asc operation")

        """ascending"""
        time.sleep(5)
        self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[6]/img').click()  # assignee image
        self.driver.find_element_by_xpath('/html/body/ul/li[2]/div').click()  # sort
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN23.png")

        self.driver.find_element_by_xpath('/html/body/ul/li[2]/ul/li[2]/div[2]').click()  # ascending

        time.sleep(5)
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN24.png")

        for i in range(1, count):
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[6]'.format(
                                                                                                  i))))
            List.append(self.driver.find_element_by_xpath(
                '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[6]'.format(
                    i)).text)

        """Checking whether list is ascending order or not"""
        assignee_colm_asc_status = False

        """Converting list's element in integer"""
        List = list(filter(None, List))  # Using filter to remove NULL values

        for i in range(len(List)):
            List[i] = List[i].encode('ASCII')

        if self.listSortedOrNot(List):
            assignee_colm_asc_status = True
        logger.info("List = {}".format(List))
        del List[0:len(List)]

        logger.info("finished executing Assignee asc operation")

        logger.info("started executing in Has Breached asc operation")

        """ascending"""
        time.sleep(5)
        self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[7]/img').click()  # has breached image
        self.driver.find_element_by_xpath('/html/body/ul/li[2]/div').click()  # sort
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN27.png")

        self.driver.find_element_by_xpath('/html/body/ul/li[2]/ul/li[2]/div[2]').click()  # ascending

        time.sleep(3)
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN28.png")

        for i in range(1, count):
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[7]'.format(
                                                                                                  i))))
            List.append(self.driver.find_element_by_xpath(
                '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[7]'.format(
                    i)).text)

        """Checking whether list is ascending order or not"""
        has_colm_asc_status = False

        """Converting list's element in integer"""
        List = list(filter(None, List))  # Using filter to remove NULL values

        for i in range(len(List)):
            List[i] = List[i].encode('ASCII')

        if self.listSortedOrNot(List):
            has_colm_asc_status = True
        logger.info("List = {}".format(List))
        del List[0:len(List)]

        logger.info("finished executing Has breached asc operation")

        logger.info("started executing submit date asc operation")
        """ascending"""
        time.sleep(5)
        self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[8]/img').click()  # submitdate image
        self.driver.find_element_by_xpath('/html/body/ul/li[2]/div').click()  # sort
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN31.png")

        assign1 = self.driver.find_element_by_xpath('/html/body/ul/li[2]/ul/li[2]/div[2]')
        assign1.click()  # ascending

        time.sleep(4)
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN32.png")
        for i in range(1, count):
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[8]'.format(
                                                                                                  i))))
            List.append(self.driver.find_element_by_xpath(
                '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[8]'.format(
                    i)).text)

        """Checking whether list is ascending order or not"""
        submit_colm_asc_status = False

        """Converting list's element in integer"""
        List = list(filter(None, List))  # Using filter to remove NULL values

        for i in range(len(List)):
            List[i] = List[i].encode('ASCII')

        if self.dateSortedOrNot(List):
            submit_colm_asc_status = True
        logger.info("List = {}".format(List))
        del List[0:len(List)]

        logger.info("finished executing submit date asc operation")

        logger.info("started executing complete asc operation")

        """ascending"""
        time.sleep(5)
        self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[9]/img').click()  # complete image
        self.driver.find_element_by_xpath('/html/body/ul/li[2]/div').click()  # sort
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN35.png")

        self.driver.find_element_by_xpath('/html/body/ul/li[2]/ul/li[2]/div[2]').click()  # ascending

        time.sleep(3)
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN36.png")
        for i in range(1, count):
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[9]'.format(
                                                                                                  i))))
            List.append(self.driver.find_element_by_xpath(
                '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[9]'.format(
                    i)).text)

        """Checking whether list is ascending order or not"""
        complete_colm_asc_status = False

        """Converting list's element in integer"""
        List = list(filter(None, List))  # Using filter to remove NULL values

        for i in range(len(List)):
            List[i] = List[i].encode('ASCII')

        if self.completeSortedOrNot(List):
            complete_colm_asc_status = True
        logger.info("List = {}".format(List))
        del List[0:len(List)]

        logger.info("finished executing complete asc operation")

        logger.info("started executing actual time asc operation")

        """ascending"""
        time.sleep(5)
        self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[10]/img').click()  # actual image
        self.driver.find_element_by_xpath('/html/body/ul/li[2]/div').click()  # sort
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN39.png")
        assign2 = self.driver.find_element_by_xpath('/html/body/ul/li[2]/ul/li[2]/div[2]')
        assign2.click()  # ascending

        time.sleep(4)
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN40.png")
        for i in range(1, count):
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[10]'.format(
                                                                                                  i))))
            List.append(self.driver.find_element_by_xpath(
                '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[10]'.format(
                    i)).text)

        """Checking whether list is ascending order or not"""
        actual_colm_asc_status = False

        """Converting list's element in integer"""
        List = list(filter(None, List))  # Using filter to remove NULL values

        for i in range(len(List)):
            List[i] = List[i].encode('ASCII')
        if self.listSortedOrNot(List):
            actual_colm_asc_status = True
        logger.info("List = {}".format(List))
        del List[0:len(List)]

        logger.info("finished executing actual time asc operation")

        logger.info("started executing problem manager asc operation")
        """ascending"""
        time.sleep(5)
        self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[11]/img').click()  # problem manager image
        self.driver.find_element_by_xpath('/html/body/ul/li[2]/div').click()  # sort
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN43.png")

        self.driver.find_element_by_xpath('/html/body/ul/li[2]/ul/li[2]/div[2]').click()  # ascending

        time.sleep(3)
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN44.png")
        for i in range(1, count):
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[11]'.format(
                                                                                                  i))))
            List.append(self.driver.find_element_by_xpath(
                '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[11]'.format(
                    i)).text)

        """Checking whether list is ascending order or not"""
        problem_colm_asc_status = False

        """Converting list's element in integer"""
        List = list(filter(None, List))  # Using filter to remove NULL values

        for i in range(len(List)):
            List[i] = List[i].encode('ASCII')

        if self.listSortedOrNot(List):
            problem_colm_asc_status = True
        logger.info("List = {}".format(List))
        del List[0:len(List)]

        logger.info("finished executing problem manager asc operation")

        logger.info("started executing summary asc operation")
        """ascending"""
        time.sleep(5)
        self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[12]/img').click()  # summary image
        self.driver.find_element_by_xpath('/html/body/ul/li[2]/div').click()  # sort
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN43.png")

        self.driver.find_element_by_xpath('/html/body/ul/li[2]/ul/li[2]/div[2]').click()  # ascending

        time.sleep(3)
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN44.png")
        for i in range(1, count):
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[12]'.format(
                                                                                                  i))))
            List.append(self.driver.find_element_by_xpath(
                '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[12]'.format(
                    i)).text)

        """Checking whether list is ascending order or not"""
        summary_colm_asc_status = False

        """Converting list's element in integer"""
        List = list(filter(None, List))  # Using filter to remove NULL values

        for i in range(len(List)):
            List[i] = List[i].encode('ASCII')

        if self.listSortedOrNot(List):
            summary_colm_asc_status = True
        logger.info("List = {}".format(List))
        del List[0:len(List)]
        logger.info("finsihed executing summary asc operation")

        logger.info("started executing prb desc operation")
        """descending"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[1]/img')))
        self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[1]/img').click()  # prb image
        logger.info("clicked on image")
        self.driver.find_element_by_xpath('/html/body/ul/li[2]/div').click()  # sort
        logger.info("clicked on Sort")
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN5.png")
        logger.info("clicking on Descending")

        self.driver.find_element_by_xpath('/html/body/ul/li[2]/ul/li[3]/div[2]').click()  # Descending
        logger.info("clicked on Descending")

        time.sleep(3)
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN6.png")

        for i in range(1, count):
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[1]'.format(
                                                                                                  i))))
            List.append(self.driver.find_element_by_xpath(
                '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[1]'.format(
                    i)).text)

        """Checking whether list is descending order or not"""
        List.sort()
        prb_colm_desc_status = False
        """Converting list's element in integer"""
        List = list(filter(None, List))  # Using filter to remove NULL values

        logger.info("List = {}".format(List))

        for i in range(len(List)):
            List[i] = List[i].encode('ASCII')

        if self.listSortedOrNot(List):
            prb_colm_desc_status = True

        del List[0:len(List)]

        logger.info("finished executing prb desc operation")

        logger.info("started executing SLA Metric name desc operation")
        """descending"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[2]/img')))
        self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[2]/img').click()  # sla image

        self.driver.find_element_by_xpath('/html/body/ul/li[2]/div').click()  # sort
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN9.png")
        self.driver.find_element_by_xpath('/html/body/ul/li[2]/ul/li[3]/div[2]').click()  # descending

        time.sleep(3)
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN10.png")
        for i in range(1, count):
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[2]'.format(
                                                                                                  i))))
            List.append(self.driver.find_element_by_xpath(
                '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[2]'.format(
                    i)).text)
        logger.info("List = {}".format(List))
        """Checking whether list is descending order or not"""
        List.sort()
        sla_colm_desc_status = False

        """Encoded list's element from unicode to string"""
        List = list(filter(None, List))  # Using filter to remove NULL values

        for i in range(len(List)):
            List[i] = List[i].encode('ASCII')

        if self.listSortedOrNot(List):
            sla_colm_desc_status = True

        del List[0:len(List)]

        logger.info("finished executing SLA Metric name desc operation")

        logger.info("started executing priority desc operation")
        """descending"""
        time.sleep(5)
        self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[3]/img').click()  # priority image

        self.driver.find_element_by_xpath('/html/body/ul/li[2]/div').click()  # sort

        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN13.png")
        self.driver.find_element_by_xpath('/html/body/ul/li[2]/ul/li[3]/div[2]').click()  # decending
        time.sleep(3)
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN14.png")

        for i in range(1, count):
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[3]'.format(
                                                                                                  i))))
            List.append(self.driver.find_element_by_xpath(
                '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[3]'.format(
                    i)).text)
        logger.info("List = {}".format(List))
        """Checking whether list is ascending order or not"""
        List.sort()

        priority_colm_desc_status = False

        """Converting list's element in integer"""
        List = list(filter(None, List))  # Using filter to remove NULL values
        for i in range(len(List)):
            List[i] = List[i].encode('ASCII')

        if self.listSortedOrNot(List):
            priority_colm_desc_status = True
        del List[0:len(List)]

        logger.info("finished executing priority desc operation")

        logger.info("started executing status desc operation")

        """descending"""
        time.sleep(5)
        self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[4]/img').click()  # status image
        self.driver.find_element_by_xpath('/html/body/ul/li[2]/div').click()  # sort
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN17.png")

        self.driver.find_element_by_xpath('/html/body/ul/li[2]/ul/li[3]/div[2]').click()  # decending

        time.sleep(3)
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN18.png")
        for i in range(1, count):
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[4]'.format(
                                                                                                  i))))
            List.append(self.driver.find_element_by_xpath(
                '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[4]'.format(
                    i)).text)

        """Checking whether list is ascending order or not"""
        List.sort()
        status_colm_desc_status = False

        """Converting list's element in integer"""
        List = list(filter(None, List))  # Using filter to remove NULL values

        for i in range(len(List)):
            List[i] = List[i].encode('ASCII')

        if self.listSortedOrNot(List):
            status_colm_desc_status = True
        logger.info("List = {}".format(List))
        del List[0:len(List)]

        logger.info("finished executing status desc operation")

        logger.info("started executing support group desc operation")

        """descending"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[5]/img')))
        self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[5]/img').click()  # support group image
        self.driver.find_element_by_xpath('/html/body/ul/li[2]/div').click()  # sort
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN21.png")
        self.driver.find_element_by_xpath('/html/body/ul/li[2]/ul/li[2]/div[2]').click()  # ascending

        time.sleep(3)
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN22.png")

        for i in range(1, count):
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[5]'.format(
                                                                                                  i))))
            List.append(self.driver.find_element_by_xpath(
                '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[5]'.format(
                    i)).text)
        logger.info("List = {}".format(List))
        """Checking whether list is ascending order or not"""
        List.sort()
        support_colm_desc_status = False

        """Converting list's element in integer"""
        List = list(filter(None, List))  # Using filter to remove NULL values

        for i in range(len(List)):
            List[i] = List[i].encode('ASCII')

        if self.listSortedOrNot(List):
            suppport_colm_desc_status = True

        del List[0:len(List)]

        logger.info("finished executing support group desc operation")

        logger.info("started executing Assignee desc operation")
        """descending"""
        time.sleep(5)
        self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[6]/img').click()  # assignee image
        self.driver.find_element_by_xpath('/html/body/ul/li[2]/div').click()  # sort
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN25.png")

        self.driver.find_element_by_xpath('/html/body/ul/li[2]/ul/li[3]/div[2]').click()  # decending

        time.sleep(3)
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN26.png")

        for i in range(1, count):
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[6]'.format(
                                                                                                  i))))
            List.append(self.driver.find_element_by_xpath(
                '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[6]'.format(
                    i)).text)

        """Checking whether list is ascending order or not"""
        List.sort()
        assignee_colm_desc_status = False

        """Converting list's element in integer"""
        List = list(filter(None, List))  # Using filter to remove NULL values

        for i in range(len(List)):
            List[i] = List[i].encode('ASCII')

        if self.listSortedOrNot(List):
            assignee_colm_desc_status = True
        logger.info("List = {}".format(List))
        del List[0:len(List)]

        logger.info("finished executing Assignee desc operation")

        logger.info("started executing Has breached desc operation")
        """descending"""
        time.sleep(5)
        self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[7]/img').click()  # has breached image
        self.driver.find_element_by_xpath('/html/body/ul/li[2]/div').click()  # sort
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN29.png")

        self.driver.find_element_by_xpath('/html/body/ul/li[2]/ul/li[3]/div[2]').click()  # decending

        time.sleep(3)
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN30.png")

        for i in range(1, count):
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[7]'.format(
                                                                                                  i))))
            List.append(self.driver.find_element_by_xpath(
                '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[7]'.format(
                    i)).text)

        """Checking whether list is ascending order or not"""
        List.sort()
        has_colm_desc_status = False

        """Converting list's element in integer"""
        List = list(filter(None, List))  # Using filter to remove NULL values

        for i in range(len(List)):
            List[i] = List[i].encode('ASCII')

        if self.listSortedOrNot(List):
            has_colm_desc_status = True
        logger.info("List = {}".format(List))
        del List[0:len(List)]

        logger.info("finished executing Has breached desc operation")

        logger.info("started executing submit date desc operation")
        """descending"""
        time.sleep(5)
        self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[8]/img').click()  # submit date image
        self.driver.find_element_by_xpath('/html/body/ul/li[2]/div').click()  # sort
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN33.png")
        self.driver.find_element_by_xpath('/html/body/ul/li[2]/ul/li[3]/div[2]').click()  # decending

        time.sleep(3)
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN34.png")
        for i in range(1, count):
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[8]'.format(
                                                                                                  i))))
            List.append(self.driver.find_element_by_xpath(
                '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[8]'.format(
                    i)).text)

        """Checking whether list is ascending order or not"""
        submit_colm_desc_status = False

        """Converting list's element in integer"""
        List = list(filter(None, List))  # Using filter to remove NULL values

        for i in range(len(List)):
            List[i] = List[i].encode('ASCII')

        if self.dateSortedOrNotDes(List):
            submit_colm_desc_status = True
        logger.info("List = {}".format(List))
        del List[0:len(List)]

        logger.info("finished executing submit date desc operation")

        logger.info("started executing complete desc operation")
        """descending"""
        time.sleep(5)
        self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[9]/img').click()  # complete image
        self.driver.find_element_by_xpath('/html/body/ul/li[2]/div').click()  # sort
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN37.png")

        self.driver.find_element_by_xpath('/html/body/ul/li[2]/ul/li[3]/div[2]').click()  # decending

        time.sleep(3)
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN38.png")
        for i in range(1, count):
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[9]'.format(
                                                                                                  i))))
            List.append(self.driver.find_element_by_xpath(
                '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[9]'.format(
                    i)).text)

        """Checking whether list is ascending order or not"""
        complete_colm_desc_status = False

        """Converting list's element in integer"""
        List = list(filter(None, List))  # Using filter to remove NULL values

        for i in range(len(List)):
            List[i] = List[i].encode('ASCII')

        if self.completeSortedOrNotDes(List):
            complete_colm_desc_status = True
        logger.info("List = {}".format(List))
        del List[0:len(List)]

        logger.info("finished executing complete desc operation")

        logger.info("started executing actual time desc operation")
        """descending"""
        time.sleep(5)
        self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[10]/img').click()  # actual time image
        self.driver.find_element_by_xpath('/html/body/ul/li[2]/div').click()  # sort
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN41.png")

        self.driver.find_element_by_xpath('/html/body/ul/li[2]/ul/li[3]/div[2]').click()  # decending

        time.sleep(3)
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN42.png")
        for i in range(1, count):
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[10]'.format(
                                                                                                  i))))
            List.append(self.driver.find_element_by_xpath(
                '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[10]'.format(
                    i)).text)

        """Checking whether list is ascending order or not"""
        List.sort()
        actual_colm_desc_status = False

        """Converting list's element in integer"""
        List = list(filter(None, List))  # Using filter to remove NULL values

        for i in range(len(List)):
            List[i] = List[i].encode('ASCII')

        if self.listSortedOrNot(List):
            actual_colm_desc_status = True
        logger.info("List = {}".format(List))
        del List[0:len(List)]

        logger.info("finished executing actual time desc operation")

        logger.info("started executing problem manager desc operation")
        """descending"""
        time.sleep(5)
        self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[11]/img').click()  # prb manager image
        self.driver.find_element_by_xpath('/html/body/ul/li[2]/div').click()  # sort
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN45.png")

        self.driver.find_element_by_xpath('/html/body/ul/li[2]/ul/li[3]/div[2]').click()  # decending

        time.sleep(3)
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN46.png")

        for i in range(1, count):
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[11]'.format(
                                                                                                  i))))
            List.append(self.driver.find_element_by_xpath(
                '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[11]'.format(
                    i)).text)

        """Checking whether list is ascending order or not"""
        List.sort()
        problem_colm_desc_status = False

        """Converting list's element in integer"""
        List = list(filter(None, List))  # Using filter to remove NULL values

        for i in range(len(List)):
            List[i] = List[i].encode('ASCII')

        if self.listSortedOrNot(List):
            problem_colm_desc_status = True
        logger.info("List = {}".format(List))
        del List[0:len(List)]

        logger.info("finished executing problem manager desc operation")

        logger.info("started executing summary desc operation")
        """descending"""
        time.sleep(5)
        self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[12]/img').click()  # summary image
        self.driver.find_element_by_xpath('/html/body/ul/li[2]/div').click()  # sort
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN45.png")

        self.driver.find_element_by_xpath('/html/body/ul/li[2]/ul/li[3]/div[2]').click()  # decending

        time.sleep(3)
        """ScreenShot - Taken"""
        self.driver.save_screenshot("VPN46.png")

        for i in range(1, count):
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[12]'.format(
                                                                                                  i))))
            List.append(self.driver.find_element_by_xpath(
                '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[12]'.format(
                    i)).text)

        """Checking whether list is ascending order or not"""
        List.sort()
        summary_colm_desc_status = False

        """Converting list's element in integer"""
        List = list(filter(None, List))  # Using filter to remove NULL values

        for i in range(len(List)):
            List[i] = List[i].encode('ASCII')

        if self.listSortedOrNot(List):
            summary_colm_desc_status = True
        logger.info("List = {}".format(List))
        del List[0:len(List)]

        logger.info("finished executing summary desc operation")

        """Printing status messages on Logger.info()"""

        tables_sorting_data_status = False

        if prb_colm_asc_status and prb_colm_desc_status and sla_colm_asc_status and sla_colm_desc_status and priority_colm_asc_status and priority_colm_desc_status and status_colm_asc_status and status_colm_desc_status and assignee_colm_asc_status and assignee_colm_desc_status and has_colm_asc_status and has_colm_desc_status and submit_colm_asc_status and submit_colm_desc_status and complete_colm_asc_status and complete_colm_desc_status and problem_colm_asc_status and problem_colm_desc_status:
            tables_sorting_data_status = True
            logger.info("Passed - The sorting of data in the reports mentioned are verified")
        else:
            logger.info("Failed - The sorting of data in the reports mentioned are not verified")
            if prb_colm_asc_status == False:
                logger.info("Failed - Prb column is not in Ascending order")
            if prb_colm_desc_status == False:
                logger.info("Failed - prb column is not in Descending order")
            if sla_colm_asc_status == False:
                logger.info("Failed - sla column is not in Ascending order")
            if sla_colm_desc_status == False:
                logger.info("Failed - sla column is not in Descending order")
            if priority_colm_asc_status == False:
                logger.info("Failed - priority column is not in Ascending order")
            if priority_colm_desc_status == False:
                logger.info("Failed - priority column is not in Descending order")
            if status_colm_asc_status == False:
                logger.info("Failed - status column is not in Ascending order")
            if status_colm_desc_status == False:
                logger.info("Failed - status  column is not in Descending order")
            if assignee_colm_asc_status == False:
                logger.info("Failed - assignee column is not in Ascending order")
            if assignee_colm_desc_status == False:
                logger.info("Failed - assignee column is not in Descending order")
            if has_colm_asc_status == False:
                logger.info("Failed - hasbreached column is not in Ascending order")
            if has_colm_desc_status == False:
                logger.info("Failed - hasbreached column is not in Descending order")
            if submit_colm_asc_status == False:
                logger.info("Failed - submit column is not in Ascending order")
            if submit_colm_desc_status == False:
                logger.info("Failed - submit column is not in Descending order")
            if complete_colm_asc_status == False:
                logger.info("Failed - complete column is not in Ascending order")
            if complete_colm_desc_status == False:
                logger.info("Failed - complete column is not in Descending order")
            if problem_colm_asc_status == False:
                logger.info("Failed - problem column is not in Ascending order")
            if problem_colm_desc_status == False:
                logger.info("Failed - problem column is not in Descending order")

        return tables_sorting_data_status

    def breached_problems_verification_of_status_gui(self, kwargs):
        logger.info("Executing breached_problems_verification_of_status()")
        window_before = self.driver.window_handles[0]
        """ Clicking on Application"""
        appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
        appl.click()
        """Clicking on Smart Reporting -> Smart Reporting Console"""
        smrtrep = self.driver.find_element_by_link_text('Smart Reporting')
        smrtrep.click()
        smrtrepcon = self.driver.find_element_by_link_text('Smart Reporting Console')
        smrtrepcon.click()
        time.sleep(20)
        WebDriverWait(self.driver, 30).until(
            expected_conditions.number_of_windows_to_be(2))
        window_after = self.driver.window_handles[1]
        self.driver.switch_to.window(window_after)

        time.sleep(30)
        """Click H3G"""
        obj_h3g = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[1]')
        obj_h3g.click()
        """click on Rebus Reports"""
        obj_rebus = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[2]/div[8]/div/div/div/div[2]')
        obj_rebus.click()

        """Search content"""
        send_repo = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/input')  # search field
        send_repo.send_keys(kwargs['report_name'])
        time.sleep(2)
        send_repo.send_keys(Keys.ENTER)
        time.sleep(10)
        """ScreenShot"""
        self.driver.save_screenshot("srs1.png")

        """Double clicking on report"""
        repo = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div[2]/div[2]/div/div/div[2]')
        action = ActionChains(self.driver)
        action.double_click(repo).perform()

        time.sleep(6)
        """ScreenShot"""
        self.driver.save_screenshot("VPN2.png")

        """Creating Python List"""

        time.sleep(7)
        """Getting table xpath"""
        table = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table')

        """counting number of rows in table"""
        count = 0
        for i in table.find_elements_by_tag_name('tr'):
            count += 1
        applicationticket = ''

        logger.info("Number of row in table = {}".format(count))
        logger.info("Loop is to get the ticket number of draft application")
        self.driver.save_screenshot("srs2.png")
        stat = kwargs['stat']
        for i in range(1, count):
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[4]'.format(
                                                                                                  i))))
            statusofapplication = self.driver.find_element_by_xpath(
                '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[4]'.format(
                    i)).text
            if statusofapplication == stat:
                applicationticket = self.driver.find_element_by_xpath(
                    '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[1]'.format(
                        i)).text
                break
        if applicationticket == '':
            logger.info("None of the tickets are in" + stat + "status")
            return False
        logger.info("Status of ticket:{}".format(statusofapplication))
        logger.info("Draft ticket number:{}".format(applicationticket))

        logger.info("Closing the Breached problem SLA tickets window")
        self.driver.find_element_by_xpath('//*[@id="logoffBtn"]').click()
        self.driver.switch_to.window(window_before)
        self.driver.refresh()
        time.sleep(15)
        window_before = self.driver.window_handles[0]
        """ Clicking on Application"""
        appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
        appl.click()

        """Clicking on Problem Mangement -> Search Problem"""
        self.driver.find_element_by_link_text('Problem Management').click()
        self.driver.find_element_by_link_text('Search Problem').click()
        time.sleep(5)
        prbid = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_1000000232"]')  # problem id field
        prbid.send_keys(applicationticket)
        self.driver.save_screenshot("VPN1.png")
        time.sleep(2)
        logger.info("Problem id entered in prb_id input")
        logger.info("Clicking on search button")
        self.driver.find_element_by_xpath('//*[@id="WIN_3_1002"]/div/div').click()
        time.sleep(5)
        logger.info("Filling target date")
        target_date = self.driver.find_element_by_xpath('//*[@id="arid_WIN_3_1000001571"]')
        target_value = target_date.get_attribute('value')
        if not target_value:
            target_date.send_keys(kwargs['target_date'])
        self.driver.find_element_by_xpath('//*[@id="WIN_3_7"]/div/a/img').click()
        time.sleep(2)
        logger.info("Selecting status")
        status = "'" + kwargs['status'] + "'"
        statusb = kwargs['status']
        self.driver.find_element_by_xpath("//td[@class='MenuEntryNoSub' and @arvalue=" + status + "]").click()
        time.sleep(2)
        logger.info("Clicking on save button")
        self.driver.find_element_by_xpath('//*[@id="WIN_3_301614800"]').click()
        time.sleep(5)

        logger.info("Clicking on application image")
        appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
        appl.click()
        """Clicking on Smart Reporting -> Smart Reporting Console"""
        smrtrep = self.driver.find_element_by_link_text('Smart Reporting')
        smrtrep.click()
        smrtrepcon = self.driver.find_element_by_link_text('Smart Reporting Console')
        smrtrepcon.click()
        time.sleep(20)
        WebDriverWait(self.driver, 30).until(
            expected_conditions.number_of_windows_to_be(2))
        window_after = self.driver.window_handles[1]
        self.driver.switch_to.window(window_after)

        time.sleep(10)
        """Click H3G"""
        obj_h3g = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[1]')
        obj_h3g.click()
        """click on Rebus Reports"""
        obj_rebus = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[2]/div[8]/div/div/div/div[2]')
        obj_rebus.click()

        """Search content"""
        send_repo = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/input')  # search field
        send_repo.send_keys(kwargs['report_name'])
        time.sleep(2)
        send_repo.send_keys(Keys.ENTER)
        time.sleep(10)
        """ScreenShot"""
        self.driver.save_screenshot("VPN1.png")

        """Double clicking on report"""
        repo = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div[2]/div[2]/div/div/div[2]')
        action = ActionChains(self.driver)
        action.double_click(repo).perform()

        time.sleep(6)
        """ScreenShot"""
        self.driver.save_screenshot("VPN2.png")

        time.sleep(7)
        """Getting table xpath"""
        table = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table')

        """counting number of rows in table"""
        count = 0
        for i in table.find_elements_by_tag_name('tr'):
            count += 1

        logger.info("Number of row in table = {}".format(count))
        logger.info("Loop is to get the status of ticket number")
        self.driver.save_screenshot("srs3.png")
        for i in range(1, count):
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[4]'.format(
                                                                                                  i))))
            getticketnumber = self.driver.find_element_by_xpath(
                '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[1]'.format(
                    i)).text
            if getticketnumber == applicationticket:
                newstatusofticket = self.driver.find_element_by_xpath(
                    '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[4]'.format(
                        i)).text
                break
        logger.info("Ticket number:{}".format(getticketnumber))
        logger.info("New Status of ticket:{}".format(newstatusofticket))
        if newstatusofticket == statusb:
            return True
        else:
            return False

    def verify_incident_backlog_smart_reporting_displays(self, kwargs):
        logger.info("Execuitng verify_incident_backlog_smart_reporting_displays()")
        window_before = self.driver.window_handles[0]

        self.driver.get_screenshot_as_file('C:/Users/sparsh/Desktop/New folder (2)/screenshot0.png')
        """ Clicking on Application"""
        appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
        appl.click()

        """Clicking on Smart Reporting -> Smart Reporting Console"""
        smrtrep = self.driver.find_element_by_link_text('Smart Reporting')
        smrtrep.click()
        smrtrepcon = self.driver.find_element_by_link_text('Smart Reporting Console')
        smrtrepcon.click()

        # WebDriverWait(self.driver, 10).until(expected_conditions.number_of_windows_to_be(2))
        time.sleep(6)
        window_after = self.driver.window_handles[1]
        self.driver.switch_to.window(window_after)

        time.sleep(14)

        """ScreenShot - Taken"""
        self.driver.get_screenshot_as_file('C:/Users/sparsh/Desktop/New folder (2)/screenshot1.png')

        """All already clicked"""
        """Click H3G"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')))
        obj_h3g = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')
        obj_h3g.click()
        """click on Rebus Reports"""
        obj_rebus = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[2]/div[8]/div/div/div/div[2]')
        obj_rebus.click()

        """Search content"""
        send_repo = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/input')
        send_repo.send_keys(kwargs['Report_name'])

        search_icon = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/div[2]/div[2]/img')
        search_icon.click()

        """ScreenShot - Taken"""
        self.driver.get_screenshot_as_file('C:/Users/sparsh/Desktop/New folder (2)/screenshot2.png')

        time.sleep(2)
        """Double clicking on report"""
        repo = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div[2]')
        action = ActionChains(self.driver)
        action.double_click(repo).perform()

        time.sleep(7)
        """ScreenShot - Taken"""
        self.driver.get_screenshot_as_file('C:/Users/sparsh/Desktop/New folder (2)/screenshot3.png')

        """Verify if smart reporting upper 1 displays"""
        # WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located((By.XPATH,'/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/div[1]'.format(i))))

        WebDriverWait(self.driver, 50).until(expected_conditions.visibility_of_element_located((By.XPATH,
                                                                                                '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[1]/div/div/div/div[1]/table/tbody/tr[1]/td')))
        report_display_1_upper = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[1]/div/div/div/div[1]/table/tbody/tr[1]/td').text

        """Verify if smart reporting lower 1 displays"""
        report_display_1_lower = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[1]/div/div/div/div[1]/table/tbody/tr[2]/td').text

        """Verify if smart reporting upper 2 display"""
        WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[2]/table/tbody/tr/td/div/div/div/div[1]/table/tbody/tr[1]/td')))
        report_display_2_upper = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[2]/table/tbody/tr/td/div/div/div/div[1]/table/tbody/tr[1]/td').text

        """Verify if smart reporting lower 2 display"""
        report_display_2_lower = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[2]/table/tbody/tr/td/div/div/div/div[1]/table/tbody/tr[2]/td').text

        """Verify if smart reporting displays the mentioned reports"""
        smart_reporting_display_status = True

        if report_display_1_upper != kwargs['Report_display_1_upper']:
            smart_reporting_display_status = False
        elif report_display_1_lower != kwargs['Report_display_1_lower']:
            smart_reporting_display_status = False
        elif report_display_2_upper != kwargs['Report_display_2_upper']:
            smart_reporting_display_status = False
        elif report_display_2_lower != kwargs['Report_display_2_lower']:
            smart_reporting_display_status = False

        if smart_reporting_display_status == False:
            logger.info("Failed - Smart reporting displays are Failed to match")
        else:
            logger.info("Passed - Smart reporting displays are matched")

        return smart_reporting_display_status

    def verify_monitoring_efficiency_smart_reporting_displays(self, kwargs):
        logger.info("Execuitng verify_monitoring_efficiency_smart_reporting_displays()")
        time.sleep(0)
        """ScreenShot - Taken"""
        self.driver.get_screenshot_as_file('C:/Users/sparsh/Desktop/New folder (2)/screenshot1.png')

        logger.info("Execuitng verify_monitoring_efficiency()")
        window_before = self.driver.window_handles[0]
        """ Clicking on Application"""
        appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
        appl.click()

        """Clicking on Smart Reporting -> Smart Reporting Console"""
        smrtrep = self.driver.find_element_by_link_text('Smart Reporting')
        smrtrep.click()
        smrtrepcon = self.driver.find_element_by_link_text('Smart Reporting Console')
        smrtrepcon.click()

        # WebDriverWait(self.driver, 10).until(expected_conditions.number_of_windows_to_be(2))
        time.sleep(6)
        window_after = self.driver.window_handles[1]
        self.driver.switch_to.window(window_after)

        time.sleep(14)
        """ScreenShot - Taken"""
        self.driver.get_screenshot_as_file('C:/Users/sparsh/Desktop/New folder (2)/screenshot2.png')

        """All already clicked"""
        """Click H3G"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')))

        obj_h3g = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')
        obj_h3g.click()

        """click on Rebus Reports"""
        obj_rebus = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[2]/div[8]/div/div/div/div[2]')
        obj_rebus.click()

        """Search content"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/input')))
        send_repo = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/input')  # search field
        send_repo.send_keys(kwargs['report_name'])

        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/div[2]/div[2]/img')))
        search_icon = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/div[2]/div[2]/img')  # search icon
        search_icon.click()

        time.sleep(5)
        """ScreenShot - Taken"""
        self.driver.get_screenshot_as_file('C:/Users/sparsh/Desktop/New folder (2)/screenshot3.png')

        """Double clicking on report"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div[2]')))

        repo = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div[2]')
        action = ActionChains(self.driver)
        action.double_click(repo).perform()

        time.sleep(10)
        """ScreenShot - Taken"""
        self.driver.get_screenshot_as_file('C:/Users/sparsh/Desktop/New folder (2)/screenshot4.png')

        """Verify if smart reporting displays"""

        """Verify if smart reporting upper displays"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[1]/table/tbody/tr[1]/td')))

        report_display_upper = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[1]/table/tbody/tr[1]/td').text
        # logger.info("display up - {}".format(report_display_upper))

        """Verify if smart reporting lower displays"""
        report_display_lower = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[1]/table/tbody/tr[2]/td').text
        # logger.info("display up - {}".format(report_display_lower))

        smart_reporting_display_status = True

        if report_display_upper != kwargs['report_display_upper']:
            smart_reporting_display_status = False
        elif report_display_lower != kwargs['report_display_lower']:
            smart_reporting_display_status = False

        if smart_reporting_display_status == False:
            logger.info("Failed - Smart reporting displays are Failed to match.")
        else:
            logger.info("Passed - Smart reporting displays are matched.")

        return smart_reporting_display_status

    def verify_incident_monitoring_efficiency_names_columns(self, kwargs):
        logger.info("Execuitng verify_incident_monitoring_efficiency_names_columns()")
        time.sleep(0)

        """ScreenShot - Taken"""
        self.driver.get_screenshot_as_file('C:/Users/sparsh/Desktop/New folder (2)/screenshot1.png')
        # self.driver.get_screenshot_as_file('C:/Users/sparsh/Desktop/Vashu (007)/screenshot1.png')
        # self.driver.save_screenshot("screenshot.png")

        logger.info("Execuitng verify_monitoring_efficiency()")
        window_before = self.driver.window_handles[0]
        """ Clicking on Application"""
        appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
        appl.click()

        """Clicking on Smart Reporting -> Smart Reporting Console"""
        smrtrep = self.driver.find_element_by_link_text('Smart Reporting')
        smrtrep.click()
        smrtrepcon = self.driver.find_element_by_link_text('Smart Reporting Console')
        smrtrepcon.click()

        # WebDriverWait(self.driver, 10).until(expected_conditions.number_of_windows_to_be(2))
        time.sleep(6)
        window_after = self.driver.window_handles[1]
        self.driver.switch_to.window(window_after)

        time.sleep(14)
        """ScreenShot - Taken"""
        self.driver.get_screenshot_as_file('C:/Users/sparsh/Desktop/New folder (2)/screenshot2.png')
        # self.driver.save_screenshot("screenshot.png")

        """All already clicked"""
        """Click H3G"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')))

        obj_h3g = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')
        obj_h3g.click()

        """click on Rebus Reports"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[2]/div[8]/div/div/div/div[2]')))

        obj_rebus = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[2]/div[8]/div/div/div/div[2]')
        obj_rebus.click()

        time.sleep(6)
        """Search content"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/input')))

        send_repo = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/input')  # search field
        send_repo.send_keys(kwargs['report_name'])

        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/div[2]/div[2]/img')))
        search_icon = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/div[2]/div[2]/img')  # search icon
        search_icon.click()

        time.sleep(10)
        """ScreenShot - Taken"""
        self.driver.get_screenshot_as_file('C:/Users/sparsh/Desktop/New folder (2)/screenshot3.png')
        # self.driver.save_screenshot("screenshot.png")

        """Double clicking on report"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div[2]')))

        repo = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div[2]')
        action = ActionChains(self.driver)
        action.double_click(repo).perform()

        time.sleep(10)
        """ScreenShot - Taken"""
        self.driver.get_screenshot_as_file('C:/Users/sparsh/Desktop/New folder (2)/screenshot4.png')
        # self.driver.save_screenshot("screenshot.png")

        """Verify if the mentioned names & columns are available in the reports as in requirement sheet"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[1]/div')))

        clm_priority = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[1]/div').text
        clm_total_up = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[2]/div').text
        clm_systems_mgmt_up = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[3]/div').text
        clm_self_service_web_up = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[4]/div').text
        clm_other_up = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[5]/div').text
        clm_monitoring_eff_up = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[6]/div').text
        clm_support_org = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[2]/div/table/thead/tr/td[1]/div').text
        clm_total_down = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[2]/div/table/thead/tr/td[2]/div').text
        clm_systems_mgmt_down = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[2]/div/table/thead/tr/td[3]/div').text
        clm_self_service_web_down = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[2]/div/table/thead/tr/td[4]/div').text
        clm_others_down = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[2]/div/table/thead/tr/td[5]/div').text
        clm_monitoring_eff_down = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td/div/div/div/div[2]/div/table/thead/tr/td[6]/div').text

        names_columns_status = True

        if clm_priority != kwargs['priority']:
            names_columns_status = False
        elif clm_total_up != kwargs['total_up']:
            names_columns_status = False
        elif clm_systems_mgmt_up != kwargs['systems_mgmt_up']:
            names_columns_status = False
        elif clm_self_service_web_up != kwargs['self_service_web_up']:
            names_columns_status = False
        elif clm_other_up != kwargs['others_up']:
            names_columns_status = False
        elif clm_monitoring_eff_up != kwargs['monitoring_eff_up']:
            names_columns_status = False
        elif clm_support_org != kwargs['support_org']:
            names_columns_status = False
        elif clm_total_down != kwargs['total_down']:
            names_columns_status = False
        elif clm_systems_mgmt_down != kwargs['systems_mgmt_down']:
            names_columns_status = False
        elif clm_self_service_web_down != kwargs['self_service_web_down']:
            names_columns_status = False
        elif clm_others_down != kwargs['others_down']:
            names_columns_status = False
        elif clm_monitoring_eff_down != kwargs['monitoring_eff_down']:
            names_columns_status = False

        """Printing status messages on Logger.info()"""

        if names_columns_status == False:
            logger.info("Failed - The mentioned names & columns are not available in the reports as in requirement")
        else:
            logger.info("Passed - The mentioned names & columns are available in the reports as in requirement")

        return names_columns_status

    def verify_monitoring_efficiency_sorting_of_data(self, kwargs):
        logger.info("Execuitng verify_monitoring_efficiency_sorting_of_data()")

        window_before = self.driver.window_handles[0]

        """ScreenShot - Taken"""
        self.driver.save_screenshot('scr1.png')

        """ Clicking on Application"""
        appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
        appl.click()

        """Clicking on Smart Reporting -> Smart Reporting Console"""
        smrtrep = self.driver.find_element_by_link_text('Smart Reporting')
        smrtrep.click()
        smrtrepcon = self.driver.find_element_by_link_text('Smart Reporting Console')
        smrtrepcon.click()

        # WebDriverWait(self.driver, 10).until(expected_conditions.number_of_windows_to_be(2))
        time.sleep(6)
        window_after = self.driver.window_handles[1]
        self.driver.switch_to.window(window_after)

        time.sleep(14)
        """ScreenShot - Taken"""
        self.driver.save_screenshot('scr2.png')

        """All already clicked"""
        """Click H3G"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')))

        obj_h3g = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')
        obj_h3g.click()

        """click on Rebus Reports"""
        time.sleep(3)
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[2]/div[8]/div/div/div/div[2]')))

        obj_rebus = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[2]/div[8]/div/div/div/div[2]')
        obj_rebus.click()

        """Search content"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/input')))

        send_repo = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/input')  # search field
        send_repo.send_keys(kwargs['report_name'])

        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/div[2]/div[2]/img')))

        search_icon = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/div[2]/div[2]/img')  # search icon
        search_icon.click()

        time.sleep(5)
        """ScreenShot - Taken"""
        self.driver.save_screenshot('scr3.png')

        """Double clicking on report"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div[2]')))

        repo = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div[2]')
        action = ActionChains(self.driver)
        action.double_click(repo).perform()

        time.sleep(10)
        """ScreenShot - Taken"""
        self.driver.save_screenshot('scr4.png')

        """3. Verify the sorting of data in the reports mentioned"""

        """Creating Python List"""
        List = []

        time.sleep(2)
        """Getting table xpath"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody')))

        table = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody')

        """counting number of rows in table"""
        count = 0
        for i in table.find_elements_by_tag_name('tr'):
            count += 1

        """checking for priority"""

        """ScreenShot - Taken"""
        self.driver.save_screenshot('scr5.png')

        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[1]/img')))
        """ascending"""
        obj = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[1]/img')  # priority image
        obj = obj.click()

        obj = self.driver.find_element_by_xpath('.//div[text()="Sort"]')  # sort
        obj = obj.click()

        """ScreenShot - Taken"""
        self.driver.save_screenshot('scr6.png')

        self.driver.find_element_by_xpath('/html/body/ul/li[2]/ul/li[2]/div[2]').click()  # ascending

        time.sleep(3)
        """ScreenShot - Taken"""
        self.driver.save_screenshot('scr7.png')

        time.sleep(2)
        for i in range(1, count):
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[1]'.format(
                                                                                                  i))))
            List.append(self.driver.find_element_by_xpath(
                '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[1]'.format(
                    i)).text)

        """Checking whether list is ascending order or not"""
        priority_colm_asc_status = False

        # logger.info("my list hai ye -  -  - {}".format(List))
        """Converting list's element in integer"""
        List = list(filter(None, List))  # Using filter to remove NULL values

        for i in range(len(List)):
            List[i] = List[i].encode('ASCII')

        if self.listSortedOrNot(List):
            priority_colm_asc_status = True

        #logger.info("pri asc --  {}".format(List))

        del List[0:len(List)]

        """descending"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[1]/img')))
        self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[1]/img').click()  # priority image
        self.driver.find_element_by_xpath('/html/body/ul/li[2]/div[2]').click()  # sort
        """ScreenShot - Taken"""
        self.driver.get_screenshot_as_file('C:/Users/sparsh/Desktop/New folder (2)/screenshot8.png')

        self.driver.find_element_by_xpath('/html/body/ul/li[2]/ul/li[3]/div[2]').click()  # Descending

        time.sleep(3)
        """ScreenShot - Taken"""
        self.driver.save_screenshot('scr8.png')

        time.sleep(2)
        for i in range(1, count):
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[1]'.format(
                                                                                                  i))))
            List.append(self.driver.find_element_by_xpath(
                '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[1]'.format(
                    i)).text)

        """Checking whether list is descending order or not"""
        priority_colm_desc_status = False

        """Converting list's element in integer"""
        List = list(filter(None, List))  # Using filter to remove NULL values

        for i in range(len(List)):
            List[i] = List[i].encode('ASCII')

        List.reverse()
        if self.listSortedOrNot(List):
            priority_colm_desc_status = True

        #logger.info("Pri - desc   {}".format(List))

        del List[0:len(List)]

        """checking for total"""

        """ascending"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[2]/img')))
        self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[2]/img').click()  # total image
        self.driver.find_element_by_xpath('.//div[text()="Sort"]').click()  # sort
        """ScreenShot - Taken"""
        self.driver.save_screenshot('scr9.png')
        self.driver.find_element_by_xpath('/html/body/ul/li[2]/ul/li[2]/div[2]').click()  # ascending

        time.sleep(3)
        """ScreenShot - Taken"""
        self.driver.save_screenshot('scr10.png')

        time.sleep(2)
        for i in range(1, count):
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[2]'.format(
                                                                                                  i))))
            List.append(self.driver.find_element_by_xpath(
                '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[2]'.format(
                    i)).text)

        # logger.info("total list - {}".format(List))
        """Checking whether list is ascending order or not"""
        total_colm_asc_status = False

        """Converting list's element in integer"""
        List = list(filter(None, List))  # Using filter to remove NULL values

        for i in range(len(List)):
            List[i] = List[i].encode('ASCII')
            List[i] = List[i].replace(',', '')
            List[i] = int(List[i])

        if self.listSortedOrNot(List):
            total_colm_asc_status = True
            logger.info("total status - {}".format(total_colm_asc_status))

       # logger.info("total - asc List -  {}".format(List))

        del List[0:len(List)]

        """descending"""
        self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[2]/img').click()  # total image
        self.driver.find_element_by_xpath('/html/body/ul/li[2]/div[2]').click()  # sort
        """ScreenShot - Taken"""
        self.driver.save_screenshot('scr11.png')
        self.driver.find_element_by_xpath('/html/body/ul/li[2]/ul/li[3]/div[2]').click()  # ascending

        time.sleep(3)
        """ScreenShot - Taken"""
        self.driver.save_screenshot('scr12.png')

        time.sleep(4)
        for i in range(1, count):
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[2]'.format(
                                                                                                  i))))
            List.append(self.driver.find_element_by_xpath(
                '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[2]'.format(
                    i)).text)

        """Checking whether list is ascending order or not"""
        total_colm_desc_status = False

        """Encoded list's element from unicode to string"""
        List = list(filter(None, List))  # Using filter to remove NULL values

        for i in range(len(List)):
            List[i] = List[i].encode('ASCII')
            List[i] = List[i].replace(',', '')
            List[i] = int(List[i])

        List.reverse()

        if self.listSortedOrNot(List):
            total_colm_desc_status = True

        #logger.info("Total -  desc   - {}   ,  {}".format(List, total_colm_desc_status))

        del List[0:len(List)]

        """checking for system mgmt"""

        """ascending"""
        WebDriverWait(self.driver, 100).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                           '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[3]/img')))
        obj = self.driver.find_element_by_xpath('//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[3]/img')# system mgmt image
        obj.click()

        obj = self.driver.find_element_by_xpath('.//div[text()="Sort"]')# sort
        obj.click()

        """ScreenShot - Taken"""
        self.driver.save_screenshot('scr13.png')
        obj = self.driver.find_element_by_xpath('/html/body/ul/li[2]/ul/li[2]/div[2]')# ascending
        obj.click()

        """ScreenShot - Taken"""
        self.driver.save_screenshot('scr14.png')

        time.sleep(4)
        for i in range(1, count):
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[3]'.format(
                                                                                                  i))))
            obj = self.driver.find_element_by_xpath('//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[3]'.format(i))
            obj = obj.text

            List.append(obj)


        # logger.info("system mgmt LIST -  - - --> {}".format(List))
        """Checking whether list is ascending order or not"""
        system_mgmt_colm_asc_status = False

        """Converting list's element in integer"""
        List = list(filter(None, List))  # Using filter to remove NULL values

        #logger.info("List  --  {}".format(List))

        for i in range(len(List)):
            List[i] = List[i].encode('ASCII')
            List[i] = List[i].replace(',', '')
            List[i] = int(List[i])

        if self.listSortedOrNot(List):
            system_mgmt_colm_asc_status = True

       # logger.info("System - asc  -   {}".format(List))
        del List[0:len(List)]

        """descending"""
        # WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,'//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[3]/img')))
        time.sleep(5)
        obj = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[3]/img')  # system mgmt image
        # time.sleep(3)
        WebDriverWait(self.driver, 100).until(expected_conditions.element_to_be_clickable)
        obj.click()

        # WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located((By.XPATH,'/html/body/ul/li[2]/div[2]')))
        # WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,'/html/body/ul/li[2]/div[2]')))
        self.driver.find_element_by_xpath('/html/body/ul/li[2]/div[2]').click()  # sort
        """ScreenShot - Taken"""
        self.driver.save_screenshot('scr15.png')
        self.driver.find_element_by_xpath('/html/body/ul/li[2]/ul/li[3]/div[2]').click()  # ascending

        time.sleep(3)
        """ScreenShot - Taken"""
        self.driver.save_screenshot('scr16.png')

        time.sleep(4)
        for i in range(1, count):
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[3]'.format(
                                                                                                  i))))
            List.append(self.driver.find_element_by_xpath(
                '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[3]'.format(
                    i)).text)

        """Checking whether list is ascending order or not"""
        system_mgmt_colm_desc_status = False

        """Converting list's element in integer"""
        List = list(filter(None, List))  # Using filter to remove NULL values
        for i in range(len(List)):
            List[i] = List[i].encode('ASCII')
            List[i] = List[i].replace(',', '')
            List[i] = int(List[i])

        List.reverse()
        if self.listSortedOrNot(List):
            system_mgmt_colm_desc_status = True

        #logger.info("System - dasc  -   {}".format(List))

        del List[0:len(List)]

        """checking for self service and web"""

        """ascending"""
        self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[4]/img').click()  # self service and web image
        self.driver.find_element_by_xpath('.//div[text()="Sort"]').click()  # sort
        """ScreenShot - Taken"""
        self.driver.save_screenshot('scr17.png')

        self.driver.find_element_by_xpath('/html/body/ul/li[2]/ul/li[2]/div[2]').click()  # ascending

        time.sleep(3)
        """ScreenShot - Taken"""
        self.driver.save_screenshot('scr18.png')

        time.sleep(4)
        for i in range(1, count):
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[4]'.format(
                                                                                                  i))))
            List.append(self.driver.find_element_by_xpath(
                '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[4]'.format(
                    i)).text)

        """Checking whether list is ascending order or not"""
        self_service_colm_asc_status = False

        # logger.info("self service increasing - - - > {}".format(List))
        """Converting list's element in integer"""
        List = list(filter(None, List))  # Using filter to remove NULL values
        time.sleep(4)
        for i in range(len(List)):
            List[i] = List[i].encode('ASCII')
            List[i] = List[i].replace(',', '')
            List[i] = int(List[i])

        # logger.info("self service increasing - - - > {}".format(List))

        if self.listSortedOrNot(List):
            self_service_colm_asc_status = True

        #logger.info("self serv asc - {}".format(List))
        del List[0:len(List)]

        """descending"""
        self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[4]/img').click()  # self service and web image
        self.driver.find_element_by_xpath('/html/body/ul/li[2]/div[2]').click()  # sort
        """ScreenShot - Taken"""
        self.driver.save_screenshot('scr19.png')

        self.driver.find_element_by_xpath('/html/body/ul/li[2]/ul/li[3]/div[2]').click()  # ascending

        time.sleep(3)
        """ScreenShot - Taken"""
        self.driver.save_screenshot('scr20.png')

        time.sleep(4)
        for i in range(1, count):
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[4]'.format(
                                                                                                  i))))
            List.append(self.driver.find_element_by_xpath(
                '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[4]'.format(
                    i)).text)

        """Checking whether list is ascending order or not"""
        self_service_colm_desc_status = False

        """Converting list's element in integer"""
        List = list(filter(None, List))  # Using filter to remove NULL values

        for i in range(len(List)):
            List[i] = List[i].encode('ASCII')
            List[i] = List[i].replace(',', '')
            List[i] = int(List[i])

        List.reverse()
        if self.listSortedOrNot(List):
            self_service_colm_desc_status = True

        #logger.info("self serv desc - {}".format(List))
        del List[0:len(List)]

        """checking for others(manual)"""

        """ascending"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[5]/img')))
        self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[5]/img').click()  # total image
        self.driver.find_element_by_xpath('/html/body/ul/li[2]/div').click()  # sort
        """ScreenShot - Taken"""
        self.driver.save_screenshot('scr21.png')

        self.driver.find_element_by_xpath('/html/body/ul/li[2]/ul/li[2]/div[2]').click()  # ascending

        time.sleep(3)
        """ScreenShot - Taken"""
        self.driver.save_screenshot('scr22.png')

        time.sleep(4)
        for i in range(1, count):
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[5]'.format(
                                                                                                  i))))
            List.append(self.driver.find_element_by_xpath(
                '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[5]'.format(
                    i)).text)

        """Checking whether list is ascending order or not"""

        others_colm_asc_status = False
        # logger.info(" --- --   {}    -- -- ".format(List))
        """Converting list's element in integer"""
        List = list(filter(None, List))  # Using filter to remove NULL values

        for i in range(len(List)):
            List[i] = List[i].encode('ASCII')
            List[i] = List[i].replace(',', '')
            List[i] = int(List[i])

        if self.listSortedOrNot(List):
            others_colm_asc_status = True

        #logger.info("Others asc  - {}".format(List))
        del List[0:len(List)]

        """descending"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[5]/img')))
        self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[5]/img').click()  # total image
        self.driver.find_element_by_xpath('/html/body/ul/li[2]/div[2]').click()  # sort
        """ScreenShot - Taken"""
        self.driver.save_screenshot('scr23.png')

        self.driver.find_element_by_xpath('/html/body/ul/li[2]/ul/li[3]/div[2]').click()  # ascending

        time.sleep(3)
        """ScreenShot - Taken"""
        self.driver.save_screenshot('scr24.png')

        time.sleep(4)
        for i in range(1, count):
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[5]'.format(
                                                                                                  i))))
            List.append(self.driver.find_element_by_xpath(
                '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[5]'.format(
                    i)).text)

        """Checking whether list is ascending order or not"""
        others_colm_desc_status = False

        """Converting list's element in integer"""
        List = list(filter(None, List))  # Using filter to remove NULL values

        for i in range(len(List)):
            List[i] = List[i].encode('ASCII')
            List[i] = List[i].replace(',', '')
            List[i] = int(List[i])

        List.reverse()
        if self.listSortedOrNot(List):
            others_colm_desc_status = True

        #logger.info("Others desc - {}".format(List))
        del List[0:len(List)]

        """checking for monitoring eff"""

        """ascending"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[6]/img')))
        self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[6]/img').click()  # monitoring eff image
        self.driver.find_element_by_xpath('.//div[text()="Sort"]').click()  # sort
        """ScreenShot - Taken"""
        self.driver.get_screenshot_as_file('C:/Users/sparsh/Desktop/New folder (2)/screenshot26.png')

        self.driver.find_element_by_xpath('/html/body/ul/li[2]/ul/li[2]/div[2]').click()  # ascending

        time.sleep(3)
        """ScreenShot - Taken"""
        self.driver.save_screenshot('scr25.png')

        time.sleep(4)
        for i in range(1, count):
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[6]'.format(
                                                                                                  i))))
            List.append(self.driver.find_element_by_xpath(
                '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[6]'.format(
                    i)).text)

        """Checking whether list is ascending order or not"""
        monitor_eff_colm_asc_status = False

        """Converting list's element in integer"""
        List = list(filter(None, List))  # Using filter to remove NULL values

        for i in range(len(List)):
            List[i] = List[i].encode('ASCII')
            List[i] = List[i].replace(',', '')

        if self.listSortedOrNot(List):
            monitor_eff_colm_asc_status = True

        #logger.info("monitoring - asc List - {}".format(List))
        del List[0:len(List)]

        """descending"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[6]/img')))
        self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/thead/tr/td[6]/img').click()  # monitoring eff image

        WebDriverWait(self.driver, 50).until(
            expected_conditions.element_to_be_clickable((By.XPATH, '/html/body/ul/li[2]/div[2]')))
        self.driver.find_element_by_xpath('/html/body/ul/li[2]/div[2]').click()  # sort

        """ScreenShot - Taken"""
        self.driver.save_screenshot('scr26.png')

        WebDriverWait(self.driver, 50).until(
            expected_conditions.element_to_be_clickable((By.XPATH, '/html/body/ul/li[2]/ul/li[3]/div[2]')))

        self.driver.find_element_by_xpath('/html/body/ul/li[2]/ul/li[3]/div[2]').click()  # ascending

        time.sleep(3)
        """ScreenShot - Taken"""
        self.driver.save_screenshot('scr27.png')

        time.sleep(4)
        for i in range(1, count):
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[6]'.format(
                                                                                                  i))))
            List.append(self.driver.find_element_by_xpath(
                '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[6]'.format(
                    i)).text)

        """Checking whether list is ascending order or not"""

        monitor_eff_colm_desc_status = False

        """Converting list's element in integer"""
        List = list(filter(None, List))  # Using filter to remove NULL values

        for i in range(len(List)):
            List[i] = List[i].encode('ASCII')
            List[i] = List[i].replace(',', '')

        List.reverse()
        if self.listSortedOrNot(List):
            monitor_eff_colm_desc_status = True

        #logger.info("monitoring - desc List - {}".format(List))
        del List[0:len(List)]

        """Printing status messages on Logger.info()"""

        tables_sorting_data_status = False

        if priority_colm_asc_status and priority_colm_desc_status and total_colm_asc_status and total_colm_desc_status and system_mgmt_colm_asc_status and system_mgmt_colm_desc_status and self_service_colm_asc_status and self_service_colm_desc_status and others_colm_asc_status and others_colm_desc_status and monitor_eff_colm_asc_status and monitor_eff_colm_desc_status:
            tables_sorting_data_status = True
            logger.info("Passed - The sorting of data in the reports mentioned are verified")
        else:
            logger.info("Failed - The sorting of data in the reports mentioned are not verified")
            if priority_colm_asc_status == False:
                logger.info("Failed - Priority column is not in Ascending order")
            if priority_colm_desc_status == False:
                logger.info("Failed - Priority column is not in Descending order")
            if total_colm_asc_status == False:
                logger.info("Failed - Total column is not in Ascending order")
            if total_colm_desc_status == False:
                logger.info("Failed - Total column is not in Descending order")
            if system_mgmt_colm_asc_status == False:
                logger.info("Failed - System Mgmmt column is not in Ascending order")
            if system_mgmt_colm_desc_status == False:
                logger.info("Failed - System Mgmmt column is not in Descending order")
            if self_service_colm_asc_status == False:
                logger.info("Failed - Self Service & Web column is not in Ascending order")
            if self_service_colm_desc_status == False:
                logger.info("Failed - Self Service & Web  column is not in Descending order")
            if others_colm_asc_status == False:
                logger.info("Failed - Others(Manual) column is not in Ascending order")
            if others_colm_desc_status == False:
                logger.info("Failed - Others(Manual) column is not in Descending order")
            if monitor_eff_colm_asc_status == False:
                logger.info("Failed - Monitoring Eff % column is not in Ascending order")
            if monitor_eff_colm_desc_status == False:
                logger.info("Failed - Monitoring Eff % column is not in descending order")

        return tables_sorting_data_status

    def verify_filter_condition_problem(self, kwargs):
        """ScreenShot - Taken"""
        self.driver.save_screenshot('Ss1.png')

        logger.info("Execuitng filter_condition_for_breached_incident_sla_tickets()")
        window_before = self.driver.window_handles[0]
        """ Clicking on Application"""
        appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
        appl.click()

        """Clicking on Smart Reporting -> Smart Reporting Console"""
        smrtrep = self.driver.find_element_by_link_text('Smart Reporting')
        smrtrep.click()
        smrtrepcon = self.driver.find_element_by_link_text('Smart Reporting Console')
        smrtrepcon.click()

        # WebDriverWait(self.driver, 10).until(expected_conditions.number_of_windows_to_be(2))
        window_after = self.driver.window_handles[1]
        self.driver.switch_to.window(window_after)
        time.sleep(2)
        """ScreenShot - Taken"""
        self.driver.save_screenshot('Ss2.png')

        time.sleep(20)
        """All already clicked"""
        """Click H3G"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')))
        obj_h3g = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')
        obj_h3g.click()
        """click on Rebus Reports"""
        obj_rebus = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[2]/div[8]/div/div/div/div[2]')
        obj_rebus.click()

        """Search content"""
        send_repo = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/input')  # search field
        send_repo.send_keys(kwargs['reportname1'])

        time.sleep(2)
        search_icon = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/div[2]/div[2]/img')  # search icon
        search_icon.click()
        time.sleep(5)
        """ScreenShot - Taken"""
        self.driver.save_screenshot('Ss3.png')

        """Double clicking on report"""
        if (kwargs['reportname1'] == "Breached Problem SLA Tickets"):
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[2]/div/div[1]/div[2]/div[2]')))
            repo = self.driver.find_element_by_xpath(
                '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[2]/div/div[1]/div[2]/div[2]')
            action = ActionChains(self.driver)
            action.double_click(repo).perform()
        if (kwargs['reportname1'] == "Upcoming Problem SLAs Breach Details"):
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div[2]')))
            repo = self.driver.find_element_by_xpath(
                '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div[2]')
            action = ActionChains(self.driver)
            action.double_click(repo).perform()

        time.sleep(20)
        """ScreenShot - Taken"""
        self.driver.save_screenshot('Ss4.png')

        "Clicking on reset"
        self.driver.find_element_by_xpath(
            "//*[@id='pagecontent']/div[2]/div[3]/div[1]/div/div/div[3]/div[2]/table/tbody/tr/td/div/table/tbody/tr/td[2]/span").click()

        "clicking on time"
        time.sleep(6)
        if (kwargs['reportname1'] == "Breached Problem SLA Tickets"):
            self.driver.find_element_by_xpath("//*[@id='99167']/div/div[4]/div/div/div/div[1]/img").click()
        if (kwargs['reportname1'] == "Upcoming Problem SLAs Breach Details"):
            self.driver.find_element_by_xpath("//*[@id='99103']/div/div[4]/div/div/div/div[1]/img").click()
        time.sleep(4)
        window_after = self.driver.window_handles[1]
        self.driver.switch_to.window(window_after)
        showtime1 = strftime("%Y_%m_%d", gmtime())
        logger.info(showtime1)
        showtime2 = strftime("%d/%m/%Y %H:%M:%S", gmtime())
        logger.info(showtime2)
        theday = datetime.date(*map(int, showtime1.split('_')))
        prevday = theday - datetime.timedelta(days=30)
        pre = prevday.strftime('%Y/%m/%d')
        self.driver.find_element_by_xpath("html/body/div[8]/div[2]/div[2]/div[1]/div[1]/input").send_keys(pre)
        self.driver.find_element_by_xpath("html/body/div[8]/div[2]/div[2]/div[1]/div[2]/input").send_keys(showtime2)
        time.sleep(5)
        self.driver.find_element_by_xpath(
            "html/body/div[8]/div[2]/div[2]/div[2]/div[2]/table/tbody/tr/td/div/table/tbody/tr/td[2]/span").click()
        time.sleep(5)

        "clicking on priority"
        # if (kwargs['reportname1'] == "Upcoming Problem SLAs Breach Details"):
        # 	self.driver.find_element_by_xpath("//*[@id='99105']/div/div[4]/div/div/div/div[1]/img").click()
        # 	self.driver.find_element_by_xpath("//*[@id='99105']/div/div[4]/div/div/div/div[2]/img").click()
        # 	self.driver.find_element_by_xpath("//*[@id='99105']/div/div[4]/div/div/div/div[3]/img").click()
        # if (kwargs['reportname1'] == "Breached Problem SLA Tickets"):
        # 	self.driver.find_element_by_xpath("//*[@id='83309']/div/div[4]/div/div/div/div[1]/img").click()
        # 	self.driver.find_element_by_xpath("//*[@id='83309']/div/div[4]/div/div/div/div[2]/img").click()
        # 	self.driver.find_element_by_xpath("//*[@id='83309']/div/div[4]/div/div/div/div[3]/img").click()
        # self.driver.switch_to.window(window_before)

        "Clicking on Support Organization"
        time.sleep(3)
        if (kwargs['reportname1'] == "Upcoming Problem SLAs Breach Details"):
            self.driver.find_element_by_xpath("//*[@id='99104']/div/div[4]/div/div/div/div[2]/img").click()
        # if (kwargs['reportname1'] == "Breached Problem SLA Tickets"):
        # 	self.driver.find_element_by_xpath("//*[@id='99161']/div/div[4]/div/div/div/div[1]/img").click()

        "Clicking on Support Group"
        time.sleep(10)
        if (kwargs['reportname1'] == "Upcoming Problem SLAs Breach Details"):
            self.driver.find_element_by_xpath("//*[@id='99107']/div/div[4]/div/div/div/div[1]/img").click()

        if (kwargs['reportname1'] == "Breached Problem SLA Tickets"):
            self.driver.find_element_by_xpath("//*[@id='99166']/div/div[4]/div/div/div/div[1]/img").click()

        "Clicking on GO"
        time.sleep(3)
        self.driver.find_element_by_xpath(
            "//*[@id='pagecontent']/div[2]/div[3]/div[1]/div/div/div[3]/div[1]/table/tbody/tr/td/div/table/tbody/tr/td[2]/span").click()
        time.sleep(5)
        self.driver.execute_script("window.scrollTo(0, 10)")
        time.sleep(5)
        self.driver.execute_script("document.body.style.zoom='50%'")
        self.driver.save_screenshot('Ss5.png')
        self.driver.execute_script("document.body.style.zoom='100%'")
        found = True
        time.sleep(5)
        "Getting values from table"
        table = self.driver.find_element_by_xpath(
            "//*[@id='pagecontent']/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table")
        tablelist = []
        for tr in table.find_elements_by_tag_name("tr"):
            tablelist.append(tr.text)
        logger.info(tablelist)

        if not tablelist:
            found = False
            logger.info("There is no data in Report")

        """Verifying data in table are present"""
        if (kwargs['reportname1'] == "Breached Problem SLA Tickets"):
            for elem in tablelist:
                if "No" in elem:
                    found = False
                    break
        if (kwargs['reportname1'] == "Upcoming Problem SLAs Breach Details"):
            for elem in tablelist:
                if "Yes" in elem:
                    found = False
                    break
        return found

    def check_for_unique_id_and_hyper_link(self, kwargs):
        logger.info("Execuitng check_for_unique_id_and_hyper_link()")
        time.sleep(0)
        """ScreenShot - Taken"""
        self.driver.save_screenshot('scr1.png')

        window_before = self.driver.window_handles[0]
        """ Clicking on Application"""
        appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
        appl.click()

        """Clicking on Smart Reporting -> Smart Reporting Console"""
        smrtrep = self.driver.find_element_by_link_text('Smart Reporting')
        smrtrep.click()
        smrtrepcon = self.driver.find_element_by_link_text('Smart Reporting Console')
        smrtrepcon.click()

        # WebDriverWait(self.driver, 10).until(expected_conditions.number_of_windows_to_be(2))
        time.sleep(6)
        window_after = self.driver.window_handles[1]
        self.driver.switch_to.window(window_after)

        """ScreenShot - Taken"""
        self.driver.save_screenshot('scr2.png')

        # time.sleep(14)
        """All already clicked"""
        """Click H3G"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')))
        obj_h3g = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')
        obj_h3g.click()
        """click on Rebus Reports"""
        obj_rebus = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[2]/div[8]/div/div/div/div[2]')
        obj_rebus.click()

        """Search content"""
        send_repo = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/input')  # search field
        send_repo.send_keys(kwargs['report_name'])

        search_icon = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/div[2]/div[2]/img')  # search icon
        search_icon.click()

        time.sleep(5)
        """ScreenShot - Taken"""
        self.driver.save_screenshot('scr3.png')

        """Double clicking on report"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div[2]')))
        repo = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div[2]')
        action = ActionChains(self.driver)
        action.double_click(repo).perform()

        time.sleep(10)
        """ScreenShot - Taken"""
        self.driver.save_screenshot('scr4.png')

        """1. Verify no duplicate incident id available in the reports"""
        """creating python list"""
        incident_id_list = []

        dup_list_status = False
        """counting number of rows in table for single page"""
        WebDriverWait(self.driver, 10).until(expected_conditions.presence_of_element_located(
            (By.XPATH, '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody')))

        table = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody')

        count = 0
        for i in table.find_elements_by_tag_name('tr'):
            count += 1

        # logger.info("Rows -  {}".format(count))

        for i in range(1, count + 1):
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[1]'.format(
                                                                                                  i))))

            incident_id_list.append(self.driver.find_element_by_xpath(
                '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[{}]/td[1]'.format(
                    i)).text)

            """Changing list element from UNICODE to string"""
            incident_id_list[i - 1] = incident_id_list[i - 1].encode('ASCII')

            """Checking for NULL value in list"""
            if incident_id_list[-1] == '':
                dup_list_status = False

        # logger.info("First -  {}".format(incident_id_list[0]))
        # logger.info("Last -  {}".format(incident_id_list[-1]))

        """Checking for duplicate incident IDs in list"""
        dup_list_status = False

        if len(incident_id_list) == len(set(incident_id_list)):
            dup_list_status = True

        if dup_list_status == True:
            logger.info('In incident column Unique incident IDs are present - Passed')
        else:
            logger.info('In incident column Duplicate incident IDs are present - Failed')

        # logger.info(incident_id_list)

        """2. Verify the incident id available on console or not"""
        """Click on first incident ID"""
        inc1 = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[1]/td[1]')
        incident_id1 = inc1.text
        # logger.info('This is incidentID 1 -- {}'.format(incident_id1))

        """Double click on the incident"""

        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[1]/td[1]')))
        inci = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[1]/td[1]')
        action = ActionChains(self.driver)
        action.double_click(inci).perform()

        """Switch window"""
        time.sleep(8)
        WebDriverWait(self.driver, 10).until(expected_conditions.number_of_windows_to_be(3))

        window_third = self.driver.window_handles[2]
        self.driver.switch_to.window(window_third)

        """ScreenShot - Taken"""
        self.driver.save_screenshot('scr5.png')

        # time.sleep(5)
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="arid_WIN_1_1000000161"]')))

        inc2 = self.driver.find_element_by_xpath('//*[@id="arid_WIN_1_1000000161"]')
        incident_id2 = inc2.get_attribute('value')

        # logger.info("Thisis Incident id2 =    {}".format(incident_id2))

        incident_id_console_status = False
        if incident_id1 == incident_id2:
            incident_id_console_status = True

        if incident_id_console_status == True:
            logger.info('Incident ID matched with incident ID present on console - Passed')
        else:
            logger.info('Incident ID does not match with incident ID present on console - Failed')

        if dup_list_status and incident_id_console_status:
            return True
        else:
            return False

    def verify_smart_reporting_status_for_report_problem_volumes_by_support(self, kwargs):
        logger.info("Execuitng verify_smart_reporting_status_for_report_problem_volumes_by_support()")
        window_before = self.driver.window_handles[0]

        self.driver.get_screenshot_as_file('C:/Users/sparsh/Desktop/New folder (2)/screenshot0.png')
        """ Clicking on Application"""
        appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
        appl.click()

        """Clicking on Smart Reporting -> Smart Reporting Console"""
        smrtrep = self.driver.find_element_by_link_text('Smart Reporting')
        smrtrep.click()
        smrtrepcon = self.driver.find_element_by_link_text('Smart Reporting Console')
        smrtrepcon.click()

        # WebDriverWait(self.driver, 10).until(expected_conditions.number_of_windows_to_be(2))
        time.sleep(6)
        window_after = self.driver.window_handles[1]
        self.driver.switch_to.window(window_after)

        time.sleep(14)

        """ScreenShot - Taken"""
        self.driver.save_screenshot('scr1.png')

        """All already clicked"""
        """Click H3G"""
        obj_h3g = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')
        obj_h3g.click()
        """click on Rebus Reports"""
        obj_rebus = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[2]/div[8]/div/div/div/div[2]')
        obj_rebus.click()

        """Search content"""
        send_repo = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/input')
        send_repo.send_keys(kwargs['Report_name'])

        search_icon = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/div[2]/div[2]/img')
        search_icon.click()

        """ScreenShot - Taken"""
        self.driver.save_screenshot('scr2.png')

        time.sleep(2)
        """Double clicking on report"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[3]/div/div[1]/div[2]/div[2]')))

        repo = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[3]/div/div[1]/div[2]/div[2]')
        action = ActionChains(self.driver)
        action.double_click(repo).perform()

        time.sleep(7)
        """ScreenShot - Taken"""
        self.driver.save_screenshot('scr3.png')

        """Verify if smart reporting upper 1 displays"""
        report_display_1_upper = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[1]/div/div/div/div[1]/table/tbody/tr[1]/td').text

        """Verify if smart reporting upper 2 display"""
        WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[2]/table/tbody/tr[1]/td/div/div/div/div[1]/table/tbody/tr[1]/td')))
        report_display_2_upper = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[2]/table/tbody/tr[1]/td/div/div/div/div[1]/table/tbody/tr[1]/td').text

        """Verify if smart reporting upper 3 display"""
        WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[2]/table/tbody/tr[2]/td/div/div/div/div[1]/table/tbody/tr[1]/td')))
        report_display_3_upper = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[2]/table/tbody/tr[2]/td/div/div/div/div[1]/table/tbody/tr[1]/td').text

        """Verify if smart reporting displays the mentioned reports"""
        smart_reporting_display_status = True

        if report_display_1_upper != kwargs['Report_display_1_upper']:
            smart_reporting_display_status = False

        elif report_display_2_upper != kwargs['Report_display_2_upper']:
            smart_reporting_display_status = False
        elif report_display_3_upper != kwargs['Report_display_3_upper']:
            smart_reporting_display_status = False

        if smart_reporting_display_status == False:
            logger.info("Failed - Smart reporting displays are Failed to match")
        else:
            logger.info("Passed - Smart reporting displays are matched")

        return smart_reporting_display_status

    def verify_problem_volumes_by_support_group_per_priority_names_columns(self, kwargs):
        logger.info("Execuitng verify_problem_volumes_by_support_group_per_priority_names_columns()")
        window_before = self.driver.window_handles[0]

        self.driver.get_screenshot_as_file('C:/Users/sparsh/Desktop/New folder (2)/screenshot0.png')
        """ Clicking on Application"""
        appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
        appl.click()

        """Clicking on Smart Reporting -> Smart Reporting Console"""
        smrtrep = self.driver.find_element_by_link_text('Smart Reporting')
        smrtrep.click()
        smrtrepcon = self.driver.find_element_by_link_text('Smart Reporting Console')
        smrtrepcon.click()

        # WebDriverWait(self.driver, 10).until(expected_conditions.number_of_windows_to_be(2))
        time.sleep(6)
        window_after = self.driver.window_handles[1]
        self.driver.switch_to.window(window_after)

        time.sleep(14)

        """ScreenShot - Taken"""
        self.driver.save_screenshot('scr1.png')

        """All already clicked"""
        """Click H3G"""
        obj_h3g = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')
        obj_h3g.click()
        """click on Rebus Reports"""
        obj_rebus = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[2]/div[8]/div/div/div/div[2]')
        obj_rebus.click()

        """Search content"""
        send_repo = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/input')
        send_repo.send_keys(kwargs['Report_name'])

        search_icon = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/div[2]/div[2]/img')
        search_icon.click()

        """ScreenShot - Taken"""
        self.driver.save_screenshot('scr2.png')

        time.sleep(2)
        """Double clicking on report"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[3]/div/div[1]/div[2]/div[2]')))

        repo = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[3]/div/div[1]/div[2]/div[2]')
        action = ActionChains(self.driver)
        action.double_click(repo).perform()

        time.sleep(7)
        """ScreenShot - Taken"""
        self.driver.save_screenshot('scr3.png')

        """Verify table_1 column"""
        t1_c1_incoming = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[1]/div/div/div/div[2]/div/table/thead/tr[1]/td[1]/div').text
        t1_c2_problems = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[1]/div/div/div/div[2]/div/table/thead/tr[1]/td[2]/div').text

        """Verify table_2 column"""
        t2_c1_resolved = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[2]/table/tbody/tr[1]/td/div/div/div/div[2]/div/table/thead/tr[1]/td[1]/div').text
        t2_c2_problems = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[2]/table/tbody/tr[1]/td/div/div/div/div[2]/div/table/thead/tr[1]/td[2]/div').text

        """Verify table_3 column"""
        t3_c1_backlog = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[2]/table/tbody/tr[2]/td/div/div/div/div[2]/div/table/thead/tr[1]/td[1]/div').text
        t3_c2_problems = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[2]/table/tbody/tr[2]/td/div/div/div/div[2]/div/table/thead/tr[1]/td[2]/div').text

        """Verify if smart reporting displays the mentioned reports"""
        smart_reporting_display_status = True

        if t1_c1_incoming != kwargs['incoming']:
            smart_reporting_display_status = False
        elif t1_c2_problems != kwargs['problems']:
            smart_reporting_display_status = False
        elif t2_c1_resolved != kwargs['resolved']:
            smart_reporting_display_status = False
        elif t2_c2_problems != kwargs['problems']:
            smart_reporting_display_status = False
        elif t3_c1_backlog != kwargs['backlog']:
            smart_reporting_display_status = False
        elif t3_c2_problems != kwargs['problems']:
            smart_reporting_display_status = False

        if smart_reporting_display_status == False:
            logger.info("Failed - The mentioned names & columns are not available in the report as in requirement")
        else:
            logger.info("Passed - The mentioned names & columns are available in the report as in requirement")

        return smart_reporting_display_status

    def verify_created_incident_and_change_of_status_is_reflected_in_report(self, kwargs):

        logger.info("Execuitng verify_created_incident_and_change_of_status_is_reflected_in_report()")

        window_before = self.driver.window_handles[0]

        self.driver.get_screenshot_as_file('C:/Users/sparsh/Desktop/New folder (2)/screenshot0.png')

        """ Clicking on Application"""
        appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
        appl.click()

        page = self.driver.find_element_by_tag_name("html")
        page.send_keys(Keys.END)

        time.sleep(2)

        """Clicking on Smart Reporting -> Smart Reporting Console"""
        time.sleep(3)
        smrtrep = self.driver.find_element_by_link_text('Smart Reporting')
        smrtrep.click()

        page = self.driver.find_element_by_tag_name("html")
        page.send_keys(Keys.END)

        WebDriverWait(self.driver, 100).until(
            expected_conditions.element_to_be_clickable((By.LINK_TEXT, 'Smart Reporting Console')))
        smrtrepcon = self.driver.find_element_by_link_text('Smart Reporting Console')

        page = self.driver.find_element_by_tag_name("html")
        page.send_keys(Keys.END)

        time.sleep(10)

        smrtrepcon.click()

        time.sleep(6)
        window_after = self.driver.window_handles[1]
        self.driver.switch_to.window(window_after)

        time.sleep(14)

        """ScreenShot - Taken"""
        self.driver.save_screenshot('scr1.png')

        """Search content"""
        WebDriverWait(self.driver, 200).until(expected_conditions.element_to_be_clickable(
            (By.XPATH, '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/input')))
        send_repo = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/input')
        send_repo.send_keys(kwargs['Report_name'])

        WebDriverWait(self.driver, 200).until(expected_conditions.element_to_be_clickable(
            (By.XPATH, '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/div[2]/div[2]/img')))
        search_icon = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/div[2]/div[2]/img')
        search_icon.click()

        """All already clicked"""
        """Click H3G"""

        WebDriverWait(self.driver, 100).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                           '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')))
        obj_h3g = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')
        obj_h3g.click()

        """click on Rebus Reports"""
        obj_rebus = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[2]/div[8]/div/div/div/div[2]')
        obj_rebus.click()

        """ScreenShot - Taken"""
        self.driver.save_screenshot('scr2.png')

        time.sleep(10)
        """Double clicking on report"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[3]/div/div[1]/div[2]/div[2]')))

        repo = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[3]/div/div[1]/div[2]/div[2]')
        action = ActionChains(self.driver)
        action.double_click(repo).perform()

        time.sleep(7)

        """ScreenShot - Taken"""
        self.driver.save_screenshot('mera_screen_new1.png')

        """Getting values of priorities for 1st Table"""
        p0, p1, p2, p3, p4 = 0, 0, 0, 0, 0
        WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[1]/div/div/div/div[2]/div/table/tbody')))
        table = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[1]/div/div/div/div[2]/div/table/tbody')

        count = 0
        for i in table.find_elements_by_tag_name('tr'):
            count += 1

        status_list = []

        if count != 0:

            for i in range(1, count):

                support_group = self.driver.find_element_by_xpath(
                    '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[1]/div/div/div/div[2]/div/table/tbody/tr[{}]/td[1]'.format(
                        i))

                if support_group.text == kwargs['support_group']:

                    total = self.driver.find_element_by_xpath(
                        '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[1]/div/div/div/div[2]/div/table/tbody/tr[{}]/td[2]'.format(
                            i))

                    if kwargs['priority'] == 'Critical':
                        "So take data of p0 and p1"
                        p0 = self.driver.find_element_by_xpath(
                            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[1]/div/div/div/div[2]/div/table/tbody/tr[{}]/td[2]'.format(
                                i))

                        p1 = self.driver.find_element_by_xpath(
                            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[1]/div/div/div/div[2]/div/table/tbody/tr[{}]/td[3]'.format(
                                i))

                        p0 = p0.text
                        p1 = p1.text

                        p0 = p0.encode('ASCII')
                        p0 = int(p0)

                        p1 = p1.encode('ASCII')
                        p1 = int(p1)

                        break
                    elif kwargs['priority'] == 'High':
                        "So take data of p2"
                        p2 = self.driver.find_element_by_xpath(
                            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[1]/div/div/div/div[2]/div/table/tbody/tr[{}]/td[4]'.format(
                                i))
                        p2 = p2.text
                        p2 = p2.encode('ASCII')
                        p2 = int(p2)

                        break
                    elif kwargs['priority'] == 'Medium':
                        "So take data of p3"
                        p3 = self.driver.find_element_by_xpath(
                            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[1]/div/div/div/div[2]/div/table/tbody/tr[{}]/td[5]'.format(
                                i))
                        p3 = p3.text

                        p3 = p3.encode('ASCII')
                        p3 = int(p3)

                        break
                    elif kwargs['priority'] == 'Low':
                        "So take data of p4"
                        p4 = self.driver.find_element_by_xpath(
                            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[1]/div/div/div/div[2]/div/table/tbody/tr[{}]/td[6]'.format(
                                i))
                        p4 = p4.text

                        p4 = p4.encode('ASCII')
                        p4 = int(p4)

                        break

        table1_prio_list = [p0, p1, p2, p3, p4]

        """Getting values of priorities for 2nd Table"""
        p0, p1, p2, p3, p4 = 0, 0, 0, 0, 0
        WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[2]/table/tbody/tr[1]/td/div/div/div/div[2]/div/table/tbody')))
        table = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[2]/table/tbody/tr[1]/td/div/div/div/div[2]/div/table/tbody')

        count = 0
        for i in table.find_elements_by_tag_name('tr'):
            count += 1

        status_list = []

        if count != 0:

            for i in range(1, count):
                support_group = self.driver.find_element_by_xpath(
                    '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[2]/table/tbody/tr[1]/td/div/div/div/div[2]/div/table/tbody/tr[{}]/td[1]'.format(
                        i))

                if support_group.text == kwargs['support_group']:

                    if kwargs['priority'] == 'Critical':
                        "So take data of p0 and p1"
                        p0 = self.driver.find_element_by_xpath(
                            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[2]/table/tbody/tr[1]/td/div/div/div/div[2]/div/table/tbody/tr[{}]/td[2]'.format(
                                i))

                        p1 = self.driver.find_element_by_xpath(
                            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[2]/table/tbody/tr[1]/td/div/div/div/div[2]/div/table/tbody/tr[{}]/td[3]'.format(
                                i))

                        p0 = p0.text
                        p1 = p1.text

                        p0 = p0.encode('ASCII')
                        p0 = int(p0)

                        p1 = p1.encode('ASCII')
                        p1 = int(p1)
                        break

                    elif kwargs['priority'] == 'High':
                        "So take data of p2"
                        p2 = self.driver.find_element_by_xpath(
                            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[2]/table/tbody/tr[1]/td/div/div/div/div[2]/div/table/tbody/tr[{}]/td[4]'.format(
                                i))

                        p2 = p2.text
                        p2 = int(p2)

                        break

                    elif kwargs['priority'] == 'Medium':
                        "So take data of p3"
                        p3 = self.driver.find_element_by_xpath(
                            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[2]/table/tbody/tr[1]/td/div/div/div/div[2]/div/table/tbody/tr[{}]/td[5]'.format(
                                i))
                        p3 = p3.encode('ASCII')
                        p3 = int(p3)
                        p3 = p3.text
                        break

                    elif kwargs['priority'] == 'Low':
                        "So take data of p4"
                        p4 = self.driver.find_element_by_xpath(
                            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[2]/table/tbody/tr[1]/td/div/div/div/div[2]/div/table/tbody/tr[{}]/td[6]'.format(
                                i))
                        p4 = p4.encode('ASCII')
                        p4 = int(p4)

                        p4 = p4.text
                        break

        table2_prio_list = [p0, p1, p2, p3, p4]

        """Getting values of priorities for 3rd Table"""
        p0, p1, p2, p3, p4 = 0, 0, 0, 0, 0

        WebDriverWait(self.driver, 100).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                               '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[2]/table/tbody/tr[2]/td/div/div/div/div[2]/div/table/tbody')))
        table = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[2]/table/tbody/tr[2]/td/div/div/div/div[2]/div/table/tbody')

        count = 0
        for i in table.find_elements_by_tag_name('tr'):
            count += 1

        status_list = []

        if count != 0:

            for i in range(1, count):
                support_group = self.driver.find_element_by_xpath(
                    '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[2]/table/tbody/tr[2]/td/div/div/div/div[2]/div/table/tbody/tr[{}]/td[1]'.format(
                        i))
                logger.info("i - {}".format(support_group.text))

                if support_group.text == kwargs['support_group']:
                    """logger.info("Its met")"""

                    if kwargs['priority'] == 'Critical':
                        "So take data of p0 and p1"
                        p0 = self.driver.find_element_by_xpath(
                            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[2]/table/tbody/tr[2]/td/div/div/div/div[2]/div/table/tbody/tr[{}]/td[2]'.format(
                                i))

                        p1 = self.driver.find_element_by_xpath(
                            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[2]/table/tbody/tr[2]/td/div/div/div/div[2]/div/table/tbody/tr[{}]/td[3]'.format(
                                i))

                        p0 = p0.text
                        p1 = p1.text
                        p0 = p0.encode('ASCII')
                        p0 = int(p0)

                        p1 = p1.encode('ASCII')
                        p1 = int(p1)

                        """Count of this must be inc."""
                        break
                    elif kwargs['priority'] == 'High':
                        "So take data of p2"
                        p2 = self.driver.find_element_by_xpath(
                            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[2]/table/tbody/tr[2]/td/div/div/div/div[2]/div/table/tbody/tr[{}]/td[4]'.format(
                                i))
                        p2 = p2.text
                        p2 = int(p2)

                        break
                    elif kwargs['priority'] == 'Medium':
                        "So take data of p3"
                        p3 = self.driver.find_element_by_xpath(
                            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[2]/table/tbody/tr[2]/td/div/div/div/div[2]/div/table/tbody/tr[{}]/td[5]'.format(
                                i))
                        p3 = p3.text
                        break
                    elif kwargs['priority'] == 'Low':
                        "So take data of p4"
                        p4 = self.driver.find_element_by_xpath(
                            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[2]/table/tbody/tr[2]/td/div/div/div/div[2]/div/table/tbody/tr[{}]/td[6]'.format(
                                i))
                        p4 = p4.text
                        break

            table3_prio_list = [p0, p1, p2, p3, p4]

            temp_2d_list = [True, table1_prio_list, table2_prio_list, table3_prio_list]

        self.driver.switch_to.window(window_before)

        '''application xpath'''
        time.sleep(3)
        '''Clicking on Problem Management -> New Problem'''
        prbmgmt = self.driver.find_element_by_link_text('Problem Management')
        prbmgmt.click()
        newprb = self.driver.find_element_by_link_text('New Problem')
        newprb.click()
        time.sleep(3)

        """Populating the mandatory areas"""
        WebDriverWait(self.driver, 100).until(
            expected_conditions.element_to_be_clickable((By.XPATH, '//*[@id="arid_WIN_4_303497300"]')))
        service = self.driver.find_element_by_xpath('//*[@id="arid_WIN_4_303497300"]')
        service.click()
        service.send_keys(kwargs['sval'])

        time.sleep(3)
        self.driver.find_element_by_xpath('//*[@id="arid_WIN_4_1000000000"]').send_keys(kwargs['Notes'])

        time.sleep(4)
        urgencies = self.driver.find_element_by_xpath('//*[@id="arid_WIN_4_1000000162"]')
        urgencies.click()
        urgencies.send_keys(Keys.DOWN)
        urgencies.send_keys(kwargs['value'])

        time.sleep(3)
        urgencies.send_keys(Keys.ENTER)

        time.sleep(3)
        impact = self.driver.find_element_by_xpath('//*[@id="arid_WIN_4_1000000163"]')
        impact.click()
        impact.send_keys(Keys.DOWN)
        impact.send_keys(kwargs['val'])

        time.sleep(3)
        impact.send_keys(Keys.ENTER)
        time.sleep(3)

        date = self.driver.find_element_by_xpath('//*[@id="arid_WIN_4_1000001571"]')
        date.send_keys(kwargs['date'])

        prob_id = self.driver.find_element_by_xpath('//*[@id="arid_WIN_4_1000000232"]')
        prob_id_val = prob_id.get_attribute('value')

        priority = self.driver.find_element_by_xpath('//*[@id="arid_WIN_4_1000000164"]')
        pri_val = priority.get_attribute('value')

        assigned_group = self.driver.find_element_by_xpath('//*[@id="arid_WIN_4_1000000217"]')
        assigned_group.click()
        assigned_group.send_keys(kwargs['assigned_group'])
        time.sleep(5)
        assigned_group.send_keys(Keys.DOWN)
        assigned_group.send_keys(Keys.ENTER)

        """"Save buton click"""
        self.driver.find_element_by_xpath('//*[@id="WIN_4_301614800"]/div/div').click()
        logger.info("Exiting create_problem_for_report()")

        temp_list = [True, pri_val, prob_id_val]

        """Now go for report """

        self.driver.switch_to.window(window_after)
        time.sleep(4)
        self.driver.refresh()

        """Verifying the created problem displayed and status change reflected in report"""

        WebDriverWait(self.driver, 100).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                               '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[1]/div/div/div/div[2]/div/table/tbody')))
        table = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[1]/div/div/div/div[2]/div/table/tbody')

        count = 0
        for i in table.find_elements_by_tag_name('tr'):
            count += 1

        priority_status = False

        if count != 0:

            for i in range(1, count):
                support_group = self.driver.find_element_by_xpath(
                    '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[1]/div/div/div/div[2]/div/table/tbody/tr[{}]/td[1]'.format(
                        i))

                if support_group.text == kwargs['support_group']:

                    if kwargs['priority'] == 'Critical':

                        p0 = self.driver.find_element_by_xpath(
                            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[1]/div/div/div/div[2]/div/table/tbody/tr[{}]/td[2]'.format(
                                i))

                        p1 = self.driver.find_element_by_xpath(
                            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[1]/div/div/div/div[2]/div/table/tbody/tr[{}]/td[3]'.format(
                                i))

                        p0 = p0.text
                        p1 = p1.text

                        p0 = int(p0)
                        p1 = int(p1)

                        if (p0 + p1) > (int(temp_2d_list[1][0]) + int(temp_2d_list[1][1])):
                            priority_status = True
                            break

                    elif kwargs['priority'] == 'High':
                        p2 = self.driver.find_element_by_xpath(
                            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[1]/div/div/div/div[2]/div/table/tbody/tr[{}]/td[4]'.format(
                                i))

                        p2 = p2.text
                        p2 = int(p2)

                        if (p2) > (int(temp_2d_list[1][2])):
                            priority_status = True
                            break

                    elif kwargs['priority'] == 'Medium':
                        p3 = self.driver.find_element_by_xpath(
                            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[1]/div/div/div/div[2]/div/table/tbody/tr[{}]/td[5]'.format(
                                i))
                        p3 = int(p3.text)
                        p3 = int(p3)

                        if (p3) > (int(temp_2d_list[1][3])):
                            priority_status = True
                            break

                    elif kwargs['priority'] == 'Low':

                        p4 = self.driver.find_element_by_xpath(
                            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[1]/div/div/div/div[2]/div/table/tbody/tr[{}]/td[6]'.format(
                                i))
                        p4 = p4.text
                        p4 = int(p4)

                        if (p4) > (int(temp_2d_list[1][4])):
                            priority_status = True
                            break

        time.sleep(3)
        """Going back to problem to update it - """

        self.driver.switch_to.window(window_before)

        """ Clicking on Application"""
        WebDriverWait(self.driver, 50).until(
            expected_conditions.element_to_be_clickable((By.XPATH, '//img[@id="reg_img_304316340"]')))
        appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
        appl.click()

        '''Clicking on Problem Management -> Search Problem'''
        WebDriverWait(self.driver, 50).until(
            expected_conditions.element_to_be_clickable((By.LINK_TEXT, 'Problem Management')))
        prbmgmt = self.driver.find_element_by_link_text('Problem Management')
        prbmgmt.click()
        newprb = self.driver.find_element_by_link_text('Search Problem')
        newprb.click()
        time.sleep(3)

        """Searching the problem based on the problem ID"""
        """Problem ID"""

        prob_id_field = self.driver.find_element_by_xpath('//*[@id="arid_WIN_5_1000000232"]')
        prob_id_field.send_keys(temp_list[2])

        """click on search"""
        search_button = self.driver.find_element_by_xpath('//*[@id="WIN_5_1002"]/div/div')
        search_button.click()

        """status"""
        status_field = self.driver.find_element_by_xpath('//*[@id="arid_WIN_5_7"]')
        time.sleep(2)
        status_field.click()
        time.sleep(2)
        status_field.send_keys(kwargs['status'])
        status_field.send_keys(Keys.ENTER)

        """status reason"""
        status_rsn = self.driver.find_element_by_xpath('//*[@id="arid_WIN_5_1000000881"]')
        time.sleep(2)
        status_rsn.click()
        time.sleep(2)
        status_rsn.send_keys(kwargs['status_reason'])
        status_rsn.send_keys(Keys.ENTER)

        """Assignee"""
        status_rsn = self.driver.find_element_by_xpath('//*[@id="arid_WIN_5_1000000218"]')
        status_rsn.send_keys(kwargs['assignee'])
        time.sleep(4)
        status_rsn.send_keys(Keys.DOWN)
        status_rsn.send_keys(Keys.ENTER)

        """CI+"""
        ci = self.driver.find_element_by_xpath('//*[@id="arid_WIN_5_303497400"]')
        ci.send_keys(kwargs['ci_value'])

        """"Save button click"""

        page = self.driver.find_element_by_tag_name("html")
        page.send_keys(Keys.END)

        # WebDriverWait(self.driver, 10).until(expected_conditions.visibility_of_element_located((By.XPATH, '//*[@id="WIN_4_301614800"]/div/div')))

        time.sleep(2)
        save = self.driver.find_element_by_xpath('//*[@id="WIN_5_301614800"]/div/div')
        save.click()

        """switch to report - and refresh the report"""
        self.driver.switch_to.window(window_after)
        """refresh the page"""
        self.driver.refresh()

        time.sleep(3)
        time.sleep(7)
        """ScreenShot - Taken"""
        self.driver.save_screenshot('scr3.png')

        """Verifying the created problem displayed and status change reflected in report"""

        """Table 1st already varified"""
        """Verifying Table 2nd and 3rd"""

        """table 2nd"""
        WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                              '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[2]/table/tbody')))
        table = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[2]/table/tbody')

        count = 0
        for i in table.find_elements_by_tag_name('tr'):
            count += 1

        priority_status = False

        if count != 0:

            for i in range(1, count):
                support_group = self.driver.find_element_by_xpath(
                    '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[2]/table/tbody/tr[1]/td/div/div/div/div[2]/div/table/tbody/tr[{}]/td[1]'.format(
                        i))
                # logger.info("i - {}".format(support_group.text))

                if support_group.text == kwargs['support_group']:

                    if kwargs['priority'] == 'Critical':

                        p0 = self.driver.find_element_by_xpath(
                            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[2]/table/tbody/tr[1]/td/div/div/div/div[2]/div/table/tbody/tr[{}]/td[2]'.format(
                                i))

                        p1 = self.driver.find_element_by_xpath(
                            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[2]/table/tbody/tr[1]/td/div/div/div/div[2]/div/table/tbody/tr[{}]/td[3]'.format(
                                i))

                        p0 = int(p0.text)
                        p1 = int(p1.text)

                        if (p0 + p1) > (int(temp_2d_list[2][0]) + int(temp_2d_list[2][1])):
                            priority_status = True
                            break


                    elif kwargs['priority'] == 'High':

                        p2 = self.driver.find_element_by_xpath(
                            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[2]/table/tbody/tr[1]/td/div/div/div/div[2]/div/table/tbody/tr[{}]/td[4]'.format(
                                i))

                        p2 = int(p2.text)

                        if (p2) > (int(temp_2d_list[2][2])):
                            priority_status = True
                            break

                    elif kwargs['priority'] == 'Medium':

                        p3 = self.driver.find_element_by_xpath(
                            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[2]/table/tbody/tr[1]/td/div/div/div/div[2]/div/table/tbody/tr[{}]/td[5]'.format(
                                i))
                        p3 = int(p3.text)

                        if (p3) > (int(temp_2d_list[2][3])):
                            priority_status = True
                            break

                    elif kwargs['priority'] == 'Low':

                        p4 = self.driver.find_element_by_xpath(
                            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[2]/table/tbody/tr[1]/td/div/div/div/div[2]/div/table/tbody/tr[{}]/td[6]'.format(
                                i))
                        p4 = int(p4.text)

                        if (p4) > (int(temp_2d_list[2][4])):
                            priority_status = True
                            break

        """table 3rd"""
        WebDriverWait(self.driver, 100).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                               '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[2]/table/tbody/tr[2]/td/div/div/div/div[2]/div/table/tbody')))
        table = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[2]/table/tbody/tr[2]/td/div/div/div/div[2]/div/table/tbody')

        count = 0
        for i in table.find_elements_by_tag_name('tr'):
            count += 1

        priority_status = False

        if count != 0:

            for i in range(1, count):

                support_group = self.driver.find_element_by_xpath(
                    '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[2]/table/tbody/tr[2]/td/div/div/div/div[2]/div/table/tbody/tr[{}]/td[1]'.format(
                        i))

                if support_group.text == kwargs['support_group']:

                    if kwargs['priority'] == 'Critical':

                        page = self.driver.find_element_by_tag_name("html")
                        page.send_keys(Keys.END)

                        p0 = self.driver.find_element_by_xpath(
                            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[2]/table/tbody/tr[2]/td/div/div/div/div[2]/div/table/tbody/tr[{}]/td[2]'.format(
                                i))
                        page = self.driver.find_element_by_tag_name("html")
                        page.send_keys(Keys.END)

                        p1 = self.driver.find_element_by_xpath(
                            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[2]/table/tbody/tr[2]/td/div/div/div/div[2]/div/table/tbody/tr[{}]/td[3]'.format(
                                i))

                        p0 = int(p0.text)
                        p1 = int(p1.text)

                        if (p0 + p1) == (int(temp_2d_list[3][0]) + int(temp_2d_list[3][1])):
                            priority_status = True
                            break

                    elif kwargs['priority'] == 'High':

                        p2 = self.driver.find_element_by_xpath(
                            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[2]/table/tbody/tr[2]/td/div/div/div/div[2]/div/table/tbody/tr[{}]/td[4]'.format(
                                i))

                        p2 = int(p2.text)

                        if (p2) == (int(temp_2d_list[3][2])):
                            priority_status = True
                            break


                    elif kwargs['priority'] == 'Medium':

                        p3 = self.driver.find_element_by_xpath(
                            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[2]/table/tbody/tr[2]/td/div/div/div/div[2]/div/table/tbody/tr[{}]/td[5]'.format(
                                i))
                        p3 = int(p3.text)

                        if (p3) == (int(temp_2d_list[3][3])):
                            priority_status = True
                            break

                    elif kwargs['priority'] == 'Low':

                        p4 = self.driver.find_element_by_xpath(
                            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[2]/table/tbody/tr[2]/td/div/div/div/div[2]/div/table/tbody/tr[{}]/td[6]'.format(
                                i))
                        p4 = int(p4.text)

                        if (p4) == (int(temp_2d_list[3][4])):
                            priority_status = True
                            break

        return priority_status

    def upcoming_problems_sla_breach_details_report_name_verification_main(self, kwargs):
        logger.info("Execuitng smart_reporting()")
        """ Clicking on Application"""
        appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
        appl.click()

        """Clicking on Smart Reporting -> Smart Reporting Console"""
        smrtrep = self.driver.find_element_by_link_text('Smart Reporting')
        smrtrep.click()
        smrtrepcon = self.driver.find_element_by_link_text('Smart Reporting Console')
        """Clicking on smart reporting console and switchingg windows"""
        window_before = self.driver.window_handles[0]
        smrtrepcon.click()
        WebDriverWait(self.driver, 10).until(expected_conditions.number_of_windows_to_be(2))
        window_after = self.driver.window_handles[1]
        self.driver.switch_to.window(window_after)
        time.sleep(3)
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')))
        time.sleep(3)
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')))
        search_report = self.driver.find_element(By.XPATH,
                                                 '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/input')
        search_report.send_keys(kwargs['Report Name'])
        search_report.send_keys(Keys.ENTER)
        time.sleep(2)
        """opening H3G Folder"""
        h3gopfoler = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')
        time.sleep(2)
        h3gopfoler.click()
        """Opening Rebus Reports Folder"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          "/html[1]/body[1]/form[1]/div[12]/div[1]/div[2]/div[4]/div[1]/div[2]/div[3]/div[1]/div[2]/div[8]/div[1]/div[1]")))
        rebus_reports = self.driver.find_element(By.XPATH,
                                                 "/html[1]/body[1]/form[1]/div[12]/div[1]/div[2]/div[4]/div[1]/div[2]/div[3]/div[1]/div[2]/div[8]/div[1]/div[1]")
        rebus_reports.click()
        time.sleep(3)
        """Taking Screen shot"""
        self.driver.get_screenshot_as_file('C:\GIT\output\ITSM_REBUS Reporting_174_1.png')
        """Double-click on incident-sla-dashboard report"""
        incident_sla_dashboard = self.driver.find_element(By.XPATH,
                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div[2]')
        time.sleep(2)
        action = ActionChains(self.driver)
        action.double_click(incident_sla_dashboard)
        action.perform()
        time.sleep(10)

        """Taking Screen shot"""
        self.driver.get_screenshot_as_file('C:\GIT\output\ITSM_REBUS Reporting_174_2.png')

        """Getting the text of the table name"""
        WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
            (By.XPATH, '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[1]/table/tbody/tr[1]/td')))
        table_title = self.driver.find_element(By.XPATH,
                                               '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/div[3]/div/div/div[1]/table/tbody/tr[1]/td').text
        logger.info("Table title: {}".format(table_title))
        self.driver.switch_to.window(window_before)
        Matching = True
        if table_title != kwargs['Table_title']:
            Matching = False
        return Matching

    def verify_incident_backlog_names_columns(self, kwargs):
        logger.info("Execuitng verify_incident_backlog_names_columns()")
        window_before = self.driver.window_handles[0]
        self.driver.get_screenshot_as_file('C:/Users/sparsh/Desktop/New folder (2)/screenshot0.png')
        """ Clicking on Application"""
        appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
        appl.click()

        """Clicking on Smart Reporting -> Smart Reporting Console"""
        smrtrep = self.driver.find_element_by_link_text('Smart Reporting')
        smrtrep.click()
        smrtrepcon = self.driver.find_element_by_link_text('Smart Reporting Console')
        smrtrepcon.click()

        # WebDriverWait(self.driver, 10).until(expected_conditions.number_of_windows_to_be(2))
        time.sleep(6)
        window_after = self.driver.window_handles[1]
        self.driver.switch_to.window(window_after)

        time.sleep(14)

        """ScreenShot - Taken"""
        self.driver.get_screenshot_as_file('C:/Users/sparsh/Desktop/New folder (2)/screenshot1.png')

        """All already clicked"""
        """Click H3G"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')))

        obj_h3g = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')
        obj_h3g.click()
        """click on Rebus Reports"""
        obj_rebus = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[2]/div[8]/div/div/div/div[2]')
        obj_rebus.click()

        """Search content"""
        send_repo = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/input')
        send_repo.send_keys(kwargs['Report_name'])

        search_icon = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/div[2]/div[2]/img')
        search_icon.click()

        """ScreenShot - Taken"""
        self.driver.get_screenshot_as_file('C:/Users/sparsh/Desktop/New folder (2)/screenshot2.png')

        time.sleep(2)
        """Double clicking on report"""
        repo = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div[2]')
        action = ActionChains(self.driver)
        action.double_click(repo).perform()

        # time.sleep(7)
        """ScreenShot - Taken"""
        self.driver.get_screenshot_as_file('C:/Users/sparsh/Desktop/New folder (2)/screenshot3.png')

        """Verify coloumn - Number of Incident"""
        WebDriverWait(self.driver, 50).until(expected_conditions.visibility_of_element_located((By.XPATH,
                                                                                                '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[1]/div/div/div/div[2]/div/table/thead/tr[1]/td[1]/div')))

        num_of_incident = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[1]/div/div/div/div[2]/div/table/thead/tr[1]/td[1]/div').text

        """Verify coloumn - Backlog Age"""
        backlog_age = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[1]/div/div/div/div[2]/div/table/thead/tr[1]/td[2]/div').text

        """Verify coloumn - Priority"""
        priority = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[2]/table/tbody/tr/td/div/div/div/div[2]/div/table/thead/tr/td[1]/div').text

        """Verify coloumn - Mean average age"""
        mean_avg_age = self.driver.find_element_by_xpath(
            '//*[@id="pagecontent"]/div[2]/div[3]/div[3]/table/tbody/tr/td[2]/table/tbody/tr/td/div/div/div/div[2]/div/table/thead/tr/td[2]/div').text

        time.sleep(2)
        """Verify if the mentioned names & columns are available in the reports as in requirement sheet"""
        names_columns_status = True

        if num_of_incident != kwargs['Num_of_incident']:
            names_columns_status = False
        elif backlog_age != kwargs['Backlog_age']:
            names_columns_status = False
        elif priority != kwargs['Priority']:
            names_columns_status = False
        elif mean_avg_age != kwargs['mean_avg_age']:
            names_columns_status = False

        if names_columns_status == False:
            logger.info("Failed - The mentioned names & columns are not available in the report as in requirement")
        else:
            logger.info("Passed - The mentioned names & columns are available in the report as in requirement")

        return names_columns_status

    def report_refresh_and_data_sync_up_new_incident_main(self, kwargs):
        logger.info("Execuitng smart_reporting()")
        """ Clicking on Application"""
        appl = self.driver.find_element_by_xpath('//img[@id="reg_img_304316340"]')
        appl.click()
    
        """Clicking on Smart Reporting -> Smart Reporting Console"""
        smrtrep = self.driver.find_element_by_link_text('Smart Reporting')
        smrtrep.click()
        smrtrepcon = self.driver.find_element_by_link_text('Smart Reporting Console')
        """Clicking on smart reporting console and switchingg windows"""
        window_zero = self.driver.window_handles[0]
        smrtrepcon.click()
        WebDriverWait(self.driver, 10).until(expected_conditions.number_of_windows_to_be(2))
        window_one = self.driver.window_handles[1]
        self.driver.switch_to.window(window_one)
        time.sleep(3)
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')))
        time.sleep(3)
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')))
        search_report = self.driver.find_element(By.XPATH,
                                                 '//*[@id="browsePageBody"]/form/div[12]/div/div[1]/div[2]/div/input')
        search_report.send_keys(kwargs['Report Name'])
        search_report.send_keys(Keys.ENTER)
        time.sleep(2)
        """Opening H3G Folder"""
        h3gopfoler = self.driver.find_element_by_xpath(
            '//*[@id="browsePageBody"]/form/div[12]/div/div[2]/div[4]/div/div[2]/div[3]/div/div[1]/div/div[2]')
        time.sleep(2)
        h3gopfoler.click()
        """Opening Rebus Reports Folder"""
        WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                          "/html[1]/body[1]/form[1]/div[12]/div[1]/div[2]/div[4]/div[1]/div[2]/div[3]/div[1]/div[2]/div[8]/div[1]/div[1]")))
        rebus_reports = self.driver.find_element(By.XPATH,
                                                 "/html[1]/body[1]/form[1]/div[12]/div[1]/div[2]/div[4]/div[1]/div[2]/div[3]/div[1]/div[2]/div[8]/div[1]/div[1]")
        rebus_reports.click()
        time.sleep(3)
        """Taking Screen shot"""
        self.driver.get_screenshot_as_file('C:\GIT\output\ITSM_REBUS Reporting_new_incident_1.png')
        """Double-click on incident-sla-dashboard report"""
        incident_sla_dashboard = self.driver.find_element(By.XPATH,
                                                          '//*[@id="browsePageBody"]/form/div[12]/div/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div[2]')
        time.sleep(2)
        action = ActionChains(self.driver)
        action.double_click(incident_sla_dashboard)
        action.perform()
        time.sleep(10)
    
        """refreshing the data"""
        self.driver.refresh()
        time.sleep(7)
    
        for i in range(1, 2):
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                (By.XPATH,
                 "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                     i))))
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable((By.XPATH,
                                                                                              "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                                                                                  i))))
            time.sleep(3)
            obj = self.driver.find_element(By.XPATH,
                                           "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/thead[1]/tr[1]/td[{}]/img[1]".format(
                                               i))
            obj.click()
            WebDriverWait(self.driver, 50).until(expected_conditions.presence_of_element_located(
                (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")))
            obj1 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/div[1]")
            time.sleep(1)
            obj1.click()
            WebDriverWait(self.driver, 50).until(expected_conditions.element_to_be_clickable(
                (By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[3]/div[2]")))
            obj2 = self.driver.find_element(By.XPATH, "/html[1]/body[1]/ul[1]/li[2]/ul[1]/li[3]/div[2]")
            time.sleep(1)
            obj2.click()
            time.sleep(7)
    
        """Taking Screen shots"""
        self.driver.get_screenshot_as_file('C:\GIT\output\ITSM_REBUS Reporting_new_incident_2.png')
    
        """Extracting the incident incident id"""
        recent_ten_incidents = []
        for i in range(1, 10):
            recent_ten_incidents.append(self.driver.find_element(By.XPATH,
                                                                 "/html[1]/body[1]/div[5]/div[2]/div[3]/div[3]/div[3]/div[1]/div[1]/div[2]/div[1]/table[1]/tbody[1]/tr[{}]/td[1]/a[1]".format(
                                                                     i)).text)
        logger.info("The recent ten incidents are:")
        for i in recent_ten_incidents:
            logger.info(i)
    
        matching = True
        if kwargs['Incident_id'] not in recent_ten_incidents:
            matching = False
            logger.info("The incident id failed to update")
        return matching

    def incident_response_sla_data(self, kwargs):
        try:
            self.login_bmc()
            status = self.incident_response_sla_data_main(kwargs)
        except BaseException as be:
            logger.fatal('Fatal exception occured in incident_response_sla_data_lib {}'.format(self.name))
            logger.error(traceback.print_exc())
        finally:
            self.bmc_logout()
            return status

    def incident_response_sla_data_1(self, kwargs):
        try:
            self.login_bmc()
            status = self.incident_response_sla_data_main1(kwargs)
        except BaseException as be:
            logger.fatal('Fatal exception occured in incident_response_sla_data_1_lib) in {}'.format(self.name))
            logger.error(traceback.print_exc())
        finally:
            self.bmc_logout()
            return status

    def incident_response_sla_data_2(self, kwargs):
        try:
            self.login_bmc()
            status = self.incident_response_sla_data_main2(kwargs)
        except BaseException as be:
            logger.fatal('Fatal exception occured in incident_response_sla_data_2_lib in {}'.format(self.name))
            logger.error(traceback.print_exc())
        finally:
            self.bmc_logout()
            return status

    def incident_restore_sla_data(self, kwargs):
        try:
            self.login_bmc()
            status = self.incident_restore_sla_data_main(kwargs)
        except BaseException as be:
            logger.fatal('Fatal exception occured in incident_restore_sla_data_lib in {}'.format(self.name))
            logger.error(traceback.print_exc())
        finally:
            self.bmc_logout()
            return status

    def incident_restore_sla_data_1(self, kwargs):
        try:
            self.login_bmc()
            status = self.incident_restore_sla_data_main1(kwargs)
        except BaseException as be:
            logger.fatal('Fatal exception occured in incident_restore_sla_data_1_lib in {}'.format(self.name))
            logger.error(traceback.print_exc())
        finally:
            self.bmc_logout()
            return status

    def incident_restore_sla_data_2(self, kwargs):
        try:
            self.login_bmc()
            status = self.incident_restore_sla_data_main2(kwargs)
        except BaseException as be:
            logger.fatal('Fatal exception occured in incident_restore_sla_data_2_lib in {}'.format(self.name))
            logger.error(traceback.print_exc())
        finally:
            self.bmc_logout()
            return status

    def work_order_volumes_by_priority(self, kwargs):
        try:
            self.login_bmc()
            status = False
            status = self.work_order_priority(kwargs)
        except BaseException as be:
            logger.fatal('Fatal exception occured in work order volumes by priority() in {}'.format(self.name))
            logger.error(traceback.print_exc())
        finally:
            self.bmc_logout()
            return status

    def work_order_volumes_by_priority_names_columns(self, kwargs):
        try:
            self.login_bmc()
            status = False
            status = self.work_order_priority_names_columns(kwargs)
        except BaseException as be:
            logger.fatal(
                'Fatal exception occured in work order volumes by priority names columns() in {}'.format(self.name))
            logger.error(traceback.print_exc())
        finally:
            self.bmc_logout()
            return status

    def work_order_volumes_by_status(self, kwargs):
        try:
            self.login_bmc()
            status = False
            status = self.work_order_status(kwargs)
        except BaseException as be:
            logger.fatal('Fatal exception occured in work order volumes by status() in {}'.format(self.name))
            logger.error(traceback.print_exc())
        finally:
            self.bmc_logout()
            return status

    def work_order_volumes_by_status_names_columns(self, kwargs):
        try:
            self.login_bmc()
            status = False
            status = self.work_order_status_names_columns(kwargs)
        except BaseException as be:
            logger.fatal(
                'Fatal exception occured in work order volumes by status names columns() in {}'.format(self.name))
            logger.error(traceback.print_exc())
        finally:
            self.bmc_logout()
            return status

    def work_order_volumes_by_priority_sorting_of_data(self, kwargs):
        try:
            self.login_bmc()
            status = False
            status = self.work_order_priority_sorting_of_data(kwargs)
        except BaseException as be:
            logger.fatal(
                'Fatal exception occured in work_order_volumes_by_priority_sorting_of_data() in {}'.format(self.name))
            logger.error(traceback.print_exc())
        finally:
            self.bmc_logout()
            return status

    def work_order_volumes_by_status_sorting_of_data(self, kwargs):
        try:
            self.login_bmc()
            status = False
            status = self.work_order_status_sorting_of_data(kwargs)
        except BaseException as be:
            logger.fatal(
                'Fatal exception occured in work_order_volumes_by_status_sorting_of_data() in {}'.format(self.name))
            logger.error(traceback.print_exc())
        finally:
            self.bmc_logout()
            return status

    def verify_filter_condition_for_breached_incident_sla_tickets(self, kwargs):
        try:
            self.login_bmc()
            status = False
            status = self.verify_filter_condition(kwargs)
        except BaseException as be:
            logger.fatal(
                'Fatal exception occured in verify_filter_condition_for_breached_incident_sla_tickets() in {}'.format(
                    self.name))
            logger.error(traceback.print_exc())
        finally:
            self.bmc_logout()
            return status

    def verify_filter_condition_for_breached_incident_sla_tickets(self, kwargs):
        try:
            self.login_bmc()
            status = False
            status = self.verify_filter_condition(kwargs)
        except BaseException as be:
            logger.fatal(
                'Fatal exception occured in verify_filter_condition_for_breached_incident_sla_tickets() in {}'.format(
                    self.name))
            logger.error(traceback.print_exc())
        finally:
            self.bmc_logout()
            return status

    def verify_filter_condition_for_upcoming_incident_sla_breach_details(self, kwargs):
        try:
            self.login_bmc()
            status = False
            status = self.verify_filter_condition(kwargs)
        except BaseException as be:
            logger.fatal(
                'Fatal exception occured in verify_filter_condition_for_upcoming_incident_sla_breach_details() in {}'.format(
                    self.name))
            logger.error(traceback.print_exc())
        finally:
            self.bmc_logout()
            return status

    def verify_filter_condition_for_upcoming_incident_sla_breach_details(self, kwargs):
        try:
            self.login_bmc()
            status = False
            status = self.verify_filter_condition(kwargs)
        except BaseException as be:
            logger.fatal(
                'Fatal exception occured in verify_filter_condition_for_upcoming_incident_sla_breach_details() in {}'.format(
                    self.name))
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
            logger.fatal(
                'fatal exception occured in verify_risk_assessments_questions_of_change_tickets_via_gui() in {}'.format(
                    self.name))
            logger.error(traceback.print_exc())
        finally:
            self.bmc_logout()
            return status

    def report_refresh_and_sync_up(self, kwargs):
        try:
            self.login_bmc()
            status = self.report_refresh_and_data_sync_up_main(kwargs)
        except BaseException as be:
            logger.fatal('Fatal exception occured in report_refresh_and_sync_up_lib in {}'.format(self.name))
            logger.error(traceback.print_exc())
        finally:
            self.bmc_logout()
            return status

    def report_refresh_and_sync_up_breach_details(self, kwargs):
        try:
            self.login_bmc()
            status = self.report_refresh_and_data_sync_up_breach_details_main(kwargs)
        except BaseException as be:
            logger.fatal(
                'Fatal exception occured in report_refresh_and_sync_up_breach_details_lib in {}'.format(self.name))
            logger.error(traceback.print_exc())
        finally:
            self.bmc_logout()
            return status

    def report_refresh_and_sync_up_new_incident(self, kwargs):
        try:
            self.login_bmc()
            status = self.report_refresh_and_data_sync_up_new_incident_main(kwargs)
        except BaseException as be:
            logger.fatal(
                'Fatal exception occured in report_refresh_and_sync_up_new_incident_lib in {}'.format(self.name))
            logger.error(traceback.print_exc())
        finally:
            self.bmc_logout()
            return status

    def report_refresh_and_sync_up_upcoming_problems(self, kwargs):
        try:
            self.login_bmc()
            status = self.report_refresh_and_sync_up_upcoming_problems_main(kwargs)
        except BaseException as be:
            logger.fatal(
                'Fatal exception occured in report_refresh_and_sync_up_Upcoming_problems_sla_breach_details_lib in {}'.format(
                    self.name))
            logger.error(traceback.print_exc())
        finally:
            self.bmc_logout()
            return status

    def upcoming_problems_sla_breach_details_column_name_verification(self, kwargs):
        try:
            self.login_bmc()
            status = self.upcoming_problems_sla_breach_details_column_name_verification_main(kwargs)
        except BaseException as be:
            logger.fatal(
                'Fatal exception occured in upcoming_problems_sla_breach_details_column_name_verification_lib in {}'.format(
                    self.name))
            logger.error(traceback.print_exc())
        finally:
            self.bmc_logout()
            return status

    def problem_volumes_by_priority(self, kwargs):
        try:
            self.login_bmc()
            status = False
            status = self.problem_volumes_priority(kwargs)
        except BaseException as be:
            logger.fatal('Fatal exception occured in work order volumes by status() in {}'.format(self.name))
            logger.error(traceback.print_exc())
        finally:
            self.bmc_logout()
            return status

    def problem_volumes_by_priority_names_columns(self, kwargs):
        try:
            self.login_bmc()
            status = False
            status = self.problem_volumes_priority_names_columns(kwargs)
        except BaseException as be:
            logger.fatal(
                'Fatal exception occured in work order volumes by status names columns() in {}'.format(self.name))
            logger.error(traceback.print_exc())
        finally:
            self.bmc_logout()
            return status

    def breached_problems_SLA_tickets_by_names_via_gui(self, kwargs):
        try:
            self.login_bmc()
            status = False
            status = self.breached_problems_SLA_tickets_by_names(kwargs)
        except BaseException as be:
            logger.fatal('Fatal exception occured in breached_problems_SLA_tickets_by_names_via_gui() in {}'.format(
                self.name))
            logger.error(traceback.print_exc())
        finally:
            self.bmc_logout()
            return status

    def breached_problems_SLA_tickets_by_names_columns(self, kwargs):
        try:
            self.login_bmc()
            status = False
            status = self.breached_problems_SLA_tickets_by_names_columns_gui(kwargs)
        except BaseException as be:
            logger.fatal(
                'Fatal exception occured in breached_problems_SLA_tickets names columns() in {}'.format(self.name))
            logger.error(traceback.print_exc())
        finally:
            self.bmc_logout()
            return status

    def breached_problems_by_status_sorting_of_data(self, kwargs):
        try:
            self.login_bmc()
            status = False
            status = self.breached_problem_sorting_of_data(kwargs)
        except BaseException as be:
            logger.fatal(
                'Fatal exception occured in breached_problems_by_status_sorting_of_data() in {}'.format(self.name))
            logger.error(traceback.print_exc())
        finally:
            self.bmc_logout()
            return status

    def breached_problems_verification_of_status(self, kwargs):
        try:
            self.login_bmc()
            status = False
            status = self.breached_problems_verification_of_status_gui(kwargs)
        except BaseException as be:
            logger.fatal(
                'Fatal exception occured in breached_problems_verification_of_status() in {}'.format(self.name))
            logger.error(traceback.print_exc())
        finally:
            self.bmc_logout()
            return status

    def incident_backlog_and_backlog_age_by_priority_smart_reporting_displays(self, kwargs):
        try:
            self.login_bmc()
            status = False
            status = self.verify_incident_backlog_smart_reporting_displays(kwargs)
        except BaseException as be:
            logger.fatal(
                'Fatal exception occured in incident_backlog_and_backlog_age_by_priority_smart_reporting_displays() in {}'.format(
                    self.name))
            logger.error(traceback.print_exc())
        finally:
            self.bmc_logout()
            return status

    def incident_monitoring_efficiency_smart_reporting_displays(self, kwargs):
        try:
            self.login_bmc()
            status = False  #
            status = self.verify_monitoring_efficiency_smart_reporting_displays(kwargs)
        except BaseException as be:
            logger.fatal(
                'Fatal exception occured in incident_monitoring_efficiency_smart_reporting_displays() in {}'.format(
                    self.name))
            logger.error(traceback.print_exc())
        finally:
            self.bmc_logout()
            return status

    def incident_monitoring_efficiency_names_columns(self, kwargs):
        try:
            self.login_bmc()
            status = False
            status = self.verify_incident_monitoring_efficiency_names_columns(kwargs)
        except BaseException as be:
            logger.fatal(
                'Fatal exception occured in incident_monitoring_efficiency_names_columns() in {}'.format(self.name))
            logger.error(traceback.print_exc())
        finally:
            self.bmc_logout()
            return status

    def incident_monitoring_efficiency_sorting_of_data(self, kwargs):
        try:
            self.login_bmc()
            status = False
            status = self.verify_monitoring_efficiency_sorting_of_data(kwargs)
        except BaseException as be:
            logger.fatal(
                'Fatal exception occured in incident_monitoring_efficiency_sorting_of_data() in {}'.format(self.name))
            logger.error(traceback.print_exc())
        finally:
            self.bmc_logout()
            return status

    def incident_volumes_by_priority_smart_reporting_displays(self, kwargs):
        try:
            self.login_bmc()
            status = False
            status = self.verify_incident_volumes_by_priority_smart_reporting_displays(kwargs)
        except BaseException as be:
            logger.fatal(
                'Fatal exception occured in incident_volumes_by_priority_smart_reporting_displays() in {}'.format(
                    self.name))
            logger.error(traceback.print_exc())
        finally:
            self.bmc_logout()
            return status

    def verify_filter_condition_for_breached_problem_sla_tickets(self, kwargs):
        try:
            self.login_bmc()
            status = False
            status = self.verify_filter_condition_problem(kwargs)
        except BaseException as be:
            logger.fatal(
                'Fatal exception occured in verify_filter_condition_for_breached_problem_sla_tickets() in {}'.format(
                    self.name))
            logger.error(traceback.print_exc())
        finally:
            self.bmc_logout()
            return status

    def breached_incident_SLA_tickets_unique_id_and_hyper_link(self, kwargs):
        try:
            self.login_bmc()
            status = self.check_for_unique_id_and_hyper_link(kwargs)
        except BaseException as be:
            logger.fatal(
                'Fatal exception occured in breached_incident_SLA_tickets_unique_id_and_hyper_link() in {}'.format(
                    self.name))
            logger.error(traceback.print_exc())
        finally:
            self.bmc_logout()
            return status

    def upcoming_incident_SLA_breach_details_unique_id_and_hyper_link(self, kwargs):
        try:
            self.login_bmc()
            status = self.check_for_unique_id_and_hyper_link(kwargs)
        except BaseException as be:
            logger.fatal(
                'Fatal exception occured in upcoming_incident_SLA_breach_details_unique_id_and_hyper_link() in {}'.format(
                    self.name))
            logger.error(traceback.print_exc())
        finally:
            self.bmc_logout()
            return status

    def problem_volumes_by_support_group_per_priority_smart_reporting_displays(self, kwargs):
        try:
            self.login_bmc()
            status = self.verify_smart_reporting_status_for_report_problem_volumes_by_support(kwargs)
        except BaseException as be:
            logger.fatal(
                'Fatal exception occured in problem_volumes_by_support_group_per_priority_smart_reporting_displays() in {}'.format(
                    self.name))
            logger.error(traceback.print_exc())
        finally:
            self.bmc_logout()
            return status

    def problem_volumes_by_support_group_per_priority_names_columns(self, kwargs):
        try:
            self.login_bmc()
            status = self.verify_problem_volumes_by_support_group_per_priority_names_columns(kwargs)
        except BaseException as be:
            logger.fatal(
                'Fatal exception occured in problem_volumes_by_support_group_per_priority_names_columns() in {}'.format(
                    self.name))
            logger.error(traceback.print_exc())
        finally:
            self.bmc_logout()
            return status

    def problem_volumes_by_support_group_per_priority_verify_created_incident_and_change_of_status_is_reflected_in_report(
            self, kwargs):
        try:
            self.login_bmc()
            status = False
            status = self.verify_created_incident_and_change_of_status_is_reflected_in_report(kwargs)

        except BaseException as be:
            logger.fatal(
                'Fatal exception occured in problem_volumes_by_support_group_per_priority_names_columns() in {}'.format(
                    self.name))
            logger.error(traceback.print_exc())
        finally:
            self.bmc_logout()
            return status

    def upcoming_problems_sla_breach_details_report_name_verification(self, kwargs):
        try:
            self.login_bmc()
            status = self.upcoming_problems_sla_breach_details_report_name_verification_main(kwargs)
        except BaseException as be:
            logger.fatal(
                'Fatal exception occured in upcoming_problems_sla_breach_details_report_name_verification_lib in {}'.format(
                    self.name))
            logger.error(traceback.print_exc())
        finally:
            self.bmc_logout()
            return status

    def sorting_upcoming_problems_sla_breach_details(self, kwargs):
        try:
            self.login_bmc()
            status = self.sorting_upcoming_problems_sla_breach_details_main(kwargs)
        except BaseException as be:
            logger.fatal(
                'Fatal exception occured in sorting_upcoming_problems_sla_breach_details_lib in {}'.format(self.name))
            logger.error(traceback.print_exc())
        finally:
            self.bmc_logout()
            return status

    def open_smart_reporting_mbnl_all(self, kwargs):
        try:
            self.login_bmc()
            status = self.open_smart_reporting_mbnl_all_main(kwargs)
        except BaseException as be:
            logger.fatal("Fatal exception occured in open_smart_reporting_mbnl_all_lib() in {}".format(self.name))
            logger.error(traceback.print_exc())
        finally:
            self.bmc_logout()
            return status

    def status_change_verification_smart_report(self, kwargs):
        try:
            self.login_bmc()
            incident_status = self.status_change_verification_smart_report_main(kwargs)
        except BaseException as be:
            logger.fatal("Fatal exception occured in status_change_verification_in_repor() in {}".format(self.name))
            logger.error(traceback.print_exc())
        finally:
            self.bmc_logout()
            if not incident_status:
                raise BmcError("Nothing returned")
            return incident_status

    def incident_volumes_by_priority_names_columns(self, kwargs):
        try:
            self.login_bmc()
            self.verify_popup()
            status = False
            status = self.verify_incident_volumes_by_priority_names_columns(kwargs)
        except BaseException as be:
            logger.fatal(
                'Fatal exception occured in incident_volumes_by_priority_names_columns() in {}'.format(self.name))
            logger.error(traceback.print_exc())
        finally:
            self.bmc_logout()
            return status

    def incident_backlog_and_backlog_age_by_priority_names_columns(self, kwargs):
        try:
            self.login_bmc()
            status = False
            status = self.verify_incident_backlog_names_columns(kwargs)
        except BaseException as be:
            logger.fatal(
                'Fatal exception occured in incident_backlog_and_backlog_age_by_priority_names_columns() in {}'.format(
                    self.name))
            logger.error(traceback.print_exc())
        finally:
            self.bmc_logout()
            return status

    def incident_backlog_and_backlog_age_by_priority_names_columns(self, kwargs):
        try:
            self.login_bmc()
            status = False
            status = self.verify_incident_backlog_names_columns(kwargs)
        except BaseException as be:
            logger.fatal(
                'Fatal exception occured in incident_backlog_and_backlog_age_by_priority_names_columns() in {}'.format(
                    self.name))
            logger.error(traceback.print_exc())
        finally:
            self.bmc_logout()
            return status
