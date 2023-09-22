*** Settings ***
Library           SSHLibrary
Library           String
Library           Process
Variables         ../../profiles/gRPCGuiVariables.py


*** Keywords ***
Suite Setup Demo
    log    Suite Setup Demo is executed
Suite Teardown Demo
    Close All Connections

test setup demo
    log    the test setup demo keyword is executed
test teardown demo
    log    the test teardown keyword is executed

Transfer File With Specified Location Using gRPC Protocol Via
    [Arguments]    ${No_Of_VMS}    ${Host1}    ${Host2}    ${Sender_Command}    ${Receiver_Command}    ${Sender_Check_Value}    ${Receiver_Check_Value}    ${VMpath}
    ${output1}=    Connect To VM    ${Host2}   ${Receiver_Command}    ${VMpath}
    log    ${output1}
    ${output2}=    Connect To VM    ${Host1}   ${Sender_Command}    ${VMpath}
    log    ${output2}
    ${output3}=    Connect To VM    ${Host2}   ls    cd /tmp
    log    ${output3}
    #${type1}=    Evaluate    type($output1).__name__
    #${output2}=    Connect To VM    ${Host2}    ${Receiver_Command}
    #${output1}    File Should Exist    121_hs.PCAP
    ${status}=    Run Keyword And Return Status    Should Contain    ${output1}    ${Sender_Check_Value}
    ${status}=    Run Keyword And Return Status    Should Contain    ${output2}    ${Receiver_Check_Value}
    [return]    ${output3}

Transfer File With Unspecified Location Using gRPC Protocol Via
    [Arguments]    ${No_Of_VMS}    ${Host1}    ${Host2}    ${Sender_Command}    ${Receiver_Command}    ${Sender_Check_Value}    ${Receiver_Check_Value}
    ${output1}=    Connect To VM    ${Host2}   ${Receiver_Command}
    log    ${output1}
    ${output2}=    Connect To VM    ${Host1}   ${Sender_Command}
    log    ${output2}
    #${type1}=    Evaluate    type($output1).__name__
    #${output2}=    Connect To VM    ${Host2}    ${Receiver_Command}
    #${output1}    File Should Exist    121_hs.PCAP
    ${status}=    Run Keyword And Return Status    Should Contain    ${output1}    ${Sender_Check_Value}
    ${status}=    Run Keyword And Return Status    Should Contain    ${output2}    ${Receiver_Check_Value}
    [return]    ${status}

Transfer Multiple File With Specified Location Using gRPC Protocol Via
    [Arguments]    ${No_Of_VMS}    ${Host1}    ${Host2}    ${Sender_Command}    ${Receiver_Command}    ${Sender_Check_Value}    ${Receiver_Check_Value}
    ${output1}=    Connect To VM    ${Host2}   ${Receiver_Command}
    log    ${output1}
    ${output2}=    Connect To VM    ${Host1}   ${Sender_Command}
    log    ${output2}
    #${type1}=    Evaluate    type($output1).__name__
    #${output2}=    Connect To VM    ${Host2}    ${Receiver_Command}
    #${output1}    File Should Exist    121_hs.PCAP
    ${status}=    Run Keyword And Return Status    Should Contain    ${output1}    ${Sender_Check_Value}
    ${status}=    Run Keyword And Return Status    Should Contain    ${output2}    ${Receiver_Check_Value}
    [return]    ${status}






#Connect To VM    ${Host2}


Connect To VM
    [Arguments]    ${Host}    ${Command}    ${VMpath}
    Open Connection    ${Host}[0]
    Login              ${Host}[1]    ${Host}[2]    delay=10
    ${stdout}=         Write    ${VMpath}
    ${p}=         Write    pwd
    Log To Console    ${p}
    ${command}    Set Variable    ./grpc_sender -D -s 192.168.29.141:50051 -f test.txt -v 1 -b 1MB -o /tmp     
    ${output}    Run Process    ssh username@192.168.29.141 bash -c '${command}'    
    Log    ${output}
    ${zip_file}=    SSHLibrary.List Directory    /home/admin/project/bin
    Log To Console    ${zip_file}
    #${crtl_c}    Evaluate    chr(int(3))
    #SSHLibrary.Write    Bare    ${crtl_c}
    log    ${stdout}
    [return]    ${stdout}


