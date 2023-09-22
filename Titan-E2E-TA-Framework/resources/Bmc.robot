*** Settings ***
Resource          all.robot
Library           Selenium2Library
Library           OperatingSystem

*** Keywords ***
LoginBMC
    Input Text    XPath=/html/body/div/div/form/div[2]/div/label/input    jbonthu
    Input Password    id=login-user-password    Automation!
    Click Button    id=login-jsp-btn

Kill_Crome_Driver
    [Documentation]    just kills stray local chromedriver.exe instances.
    ...    useful if you are trying to clean your project, and your ide is complaining
    Run    ${CURDIR}\\Kill_Crome.bat
    Sleep    4s

Kill_Crome_Driver2
    [Documentation]    just kills stray local chromedriver.exe instances.
    ...    useful if you are trying to clean your project, and your ide is complaining
    Run    ${CURDIR}\\Kill_Crome.bat
    Sleep    4s
