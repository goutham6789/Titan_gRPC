*** Settings ***
Suite Setup       Suite Setup Demo
Suite Teardown    Suite Teardown Demo
Force Tags        gRPC
Test Timeout      15 minutes
Library           SSHLibrary
Library           Collections
Library           OperatingSystem
Variables         ../constant.yaml
Resource          ../TestSuit/grpc_keywords.robot

*** Test Cases ***

Testcase
    Test Case To Check    ${sender}    ${receiver}

GRPC_Test_01
        [Documentation]    DESIGN STEPS
    ...
    ...    ============
    ...
    ...    gRPC Tool Testing Using Automation
    ...
    ...    Step1:
    ...
    ...    Login to VM1.
    ...
    ...    Step 2:
    ...
    ...    Execute the gRPC Receiver Command.
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
    ${status}=    Transfer File With Specified Location Using gRPC Protocol Via SSH    ${Sender}    ${Receiver}
    log    ${status}
    Run Keyword If    '${status}' == '${False}'    fail    Test case is Failed
    [Teardown]    Test Teardown Demo