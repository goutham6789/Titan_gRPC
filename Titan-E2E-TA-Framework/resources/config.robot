*** Settings ***
Library           ../libraries/config/ConfigLibrary.py

*** Keywords ***
Setup
    [Arguments]    ${equipment}
    : FOR    ${event}    IN    @{equipment.get_setup_events()}
    \    Run Keyword    ${event.keyword}    @{event.args}    &{event.kwargs}

Teardown
    [Arguments]    ${equipment}
    : FOR    ${event}    IN    @{equipment.get_teardown_events()}
    \    ${status}=    Run Keyword And Return Status    ${event.keyword}    @{event.args}    &{event.kwargs}
    \    Run Keyword If    ${status} is ${False}    Run Keywords    Set Global Variable    ${TEST_STATUS}    FAIL
    \    ...    AND    Fail    ${event.keyword} keyword failed.

Suite Setup
    [Arguments]    @{equipments}
    Comment    Get Svn Version
    Initialize Test Suite Path    ${OUTPUT DIR}    ${SUITE NAME}
    Initialize Test Case Path    Suite
    : FOR    ${equipment}    IN    @{equipments}
    \    Setup    ${equipment}

Suite Teardown
    [Arguments]    @{equipments}
    Initialize Test Case Path    Suite
    : FOR    ${equipment}    IN    @{equipments}
    \    Teardown    ${equipment}

Test Setup
    [Arguments]    @{equipments}
    Initialize Test Case Path    ${TEST NAME}
    : FOR    ${equipment}    IN    @{equipments}
    \    Setup    ${equipment}

Test Teardown
    [Arguments]    @{equipments}
    : FOR    ${equipment}    IN    @{equipments}
    \    Teardown    ${equipment}
    Compress Build File
    Add Status Suffix    ${TEST_STATUS}
