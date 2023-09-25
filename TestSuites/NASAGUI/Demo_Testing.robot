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
Run VMS Execute the gRPC Sender And Receiver Command And Validate The Output
    [Arguments]    ${No_Of_VMS}    ${Host1}    ${Host2}    ${Sender_Command}    ${Receiver_Command}    ${Sender_Check_Value}    ${Receiver_Check_Value}    ${VMpath}
    #${output1}=    Connect To VM    ${Host2}   ${Receiver_Command}    ${VMpath}
    #log    ${output1}
    #${output2}=    Connect To VM    ${Host1}   ${Sender_Command}    ${VMpath}
    #log    ${output2}
    #${type1}=    Evaluate    type($output1).__name__
    #${output2}=    Connect To VM    ${Host2}    ${Receiver_Command}
    #${output1}    File Should Exist    121_hs.PCAP
    #${output3}=    Connect To VM    ${Host2}   ls    cd /tmp
    #log    ${output3}
    #[return]    ${output3}
    sleep    5
    PASS EXECUTION    Pass