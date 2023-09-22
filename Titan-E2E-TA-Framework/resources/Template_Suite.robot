*** Settings ***
Resource          ../E2E-TA-Framework/resources/all.robot
Resource          all_common.robot

*** Keywords ***
Generic Suite Setup
    [Arguments]    &{options}
    [Documentation]    - Sets loglevel based on external --variable parameter (default value = 1).
    ...    - Collects the phones given in parameters.
    ...    - Based on parametering, user lists are created and the users are placed into correct list. Deletes all users from network elements, and re-attaches them (without checking if it was successfull). 3G users can be added as isobox users.
    ...    - Created lists are: VOLTE_USERS, CS_USERS, ISOBOX_USERS, VOWIFI_USERS
    ...
    ...    == Parameters ==
    ...
    ...    | Generic Suite Setup | **Users |
    ...
    ...    == Example ==
    ...
    ...    | Generic Suite Setup | ISOBOX_USER_01=${ISOBOX_PHONE_01.imsi} | CS_USER_01=${ISOBOX_PHONE_02.imsi} | VOWIFI_USER_01=WIFI | VOLTE_USER_01=4G |
    [Timeout]    20 minutes
    Set Logging Level
    Suite Setup    ${TERMINAL_HANDLER}    ${SPEECH_HANDLER}
    Attenuator Reset
    Collect Suite Phones    &{options}
    Return From Keyword If    ${node_based_suite}
    Suite Audio Setup    ${SuitePhones}
    Set Suite Phones
    Custom Suite Setup
    Teardown    ${TERMINAL_HANDLER}
    Teardown    ${SPEECH_HANDLER}

Generic Suite Teardown
    [Documentation]    Disconnects from WAF. No parameters.
    ...
    ...    == Input Parameters ==
    ...
    ...    None.
    [Timeout]    20 minutes
    Setup    ${TERMINAL_HANDLER}
    Setup    ${SPEECH_HANDLER}
    Run Keyword Unless    ${node_based_suite}    Suite Audio Teardown    ${SuitePhones}
    Custom Suite Teardown
    Suite Teardown    ${TERMINAL_HANDLER}    ${SPEECH_HANDLER}

Generic Test Setup
    [Arguments]    @{List}    &{options}
    [Documentation]    Multiple functionalities (in this order):
    ...    1. Makes test level user and equipment lists
    ...    2. Connects to equipments
    ...    3. Initiates Custom Setup (if this KW is made for the suite. Passed parameters: '&{options}')
    ...    4. Checks if users are registered, if not, reregisters them, waits up to 80 seconds for this.
    ...    5. Starts Subscriber traces
    ...    6. Starts advanced logging if loglevel is set to 2.
    ...
    ...    By default it connects to TAS and MSS, if 3G users were chosen. Should you need any additional element for TC, you can add it as parameter.
    ...
    ...    By default all phones collected on suite level will be used, but if you need just a part of them, you can define which ones you need.
    ...
    ...    Key-value pairs added here are passed into Custom Setup KW in case you want to make specific configuration or log collection. You must define and write a Custom Setup KW in your suite (and also a Custom Teardown).
    ...
    ...    == Input Parameters ==
    ...
    ...    Generic Test Setup | *Users, Equipments | **options
    ...
    ...    == Example ==
    ...
    ...    Generic Test Setup | ATTENUATOR_01 | VOLTE_USER_01 | CS_USER_01
    ...
    ...    == Cmm/Cmg trace initialization ==
    ...
    ...    Add cmmCallTraceJobSubs=PARAMETER or cmgCallTraceJobSubs=PARAMETER to the argument line.
    ...    PARAMETER can be:
    ...    Subscriber object | The call trace will be started for only this subscriber.
    ...    List of Subscriber objects | The call trace will be initiated for all the subscribers described.
    ...    'All' string parameter | The call trace job will be initiated for all USERS described in the profile file.
    [Timeout]    20 minutes
    Initialize Test Case Path    ${TEST NAME}
    List Maker    @{List}
    Set Test Equipments    @{Equipments}
    Attenuator Reset
    Test Setup    @{test_equipments}    ${TERMINAL_HANDLER}    ${SPEECH_HANDLER}
    Wireshark Init
    Network Element Subscriber Trace Init    &{options}
    Generic Audio Setup    ${USERS}
    Charging Setup    &{options}
    Run Keyword If    '${LOGGING_LEVEL}' == '0'    Custom Setup    &{options}
    Return From Keyword If    '${LOGGING_LEVEL}' == '0'
    Custom Setup    &{options}
    Reregister Users
    Trace Init
    Return From Keyword If    '${LOGGING_LEVEL}' == '1' or '${check_ws_node}' == '0' or '${check_ws_node}' == '1'
    Start Advanced Logging

Generic Test Teardown
    [Arguments]    ${RESET}=${False}    &{options}
    [Documentation]    Multiple functionalities (in this order):
    ...    1. Releases all remaining calls.
    ...    2. Stops advanced logging if loglevel is set to 2.
    ...    3. Stops and saves traces which are still ongoing.
    ...    4. Downloads used subscribers' data from HSS.
    ...    5. Runs Custom Teardown if exists in suite.
    ...    6. Disconnects from elements.
    ...
    ...    == Input Parameters ==
    ...
    ...    None.
    [Timeout]    20 minutes
    Release All Voice Calls
    Wireshark Stop    &{options}
    Run Keyword If    '${LOGGING_LEVEL}' > '1'    Stop Advanced Logging
    Run Keyword If    '${LOGGING_LEVEL}' > '1'    Get TC User Data
    Run Keyword If    '${LOGGING_LEVEL}' >= '0' and '${RESET}==${False}'    Custom Teardown
    Run Keyword If    '${LOGGING_LEVEL}' > '0'    Charging Teardown
    Test Teardown    @{test_equipments}    ${TERMINAL_HANDLER}    ${SPEECH_HANDLER}