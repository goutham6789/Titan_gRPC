*** Settings ***
Suite Setup       Suite Setup Demo
Suite Teardown    Suite Teardown Demo
Force Tags        netactgui
Test Timeout      15 minutes
Library           Selenium2Library
#Library           OperatingSystem
Library           String
Resource          ../../Titan-E2E-TA-Framework/resources/gRPC Gui-Library.robot
Variables         ../../profiles/gRPCGuiVariables.py

*** Variables ***

*** Test Cases ***
Testcase1
    [Documentation]    DESIGN STEPS
    ...
    ...    ============
    ...
    ...
    ...    gRPC Tool Testing Using Automation
    ...
    ...    Step1:
    ...
    ...    Login to VM.
    ...
    ...    Step 2:
    ...
    ...    Execute the gRPC Command.
    ...
    ...    Step 3:
    ...
    ...    Check the eexcuted command is success or fail
    ...
    ...    Step4:
    ...
    ...    Compare Result with expected Result.
    ...
    ...    *ASSIGNEE=#####*
    [Tags]    GRPC    DEMO
    [Setup]    Test Setup Demo
    ${status}=    Transfer File With Specified Location Using gRPC Protocol Via    2    ${VM1}    ${VM2}    ${gRPC_Sender_Command_Transfer_File_With_Specified_Location}    ${gRPC_Receiver_Command_Transfer_File_With_Specified_Location}    ${Sender_Output_Check}    ${Receiver_Output_Check}    ${VMpath}
    log    ${status}
    Run Keyword If    '${status}' == '${False}'    fail    Test case is Failed
    [Teardown]    Test Teardown Demo