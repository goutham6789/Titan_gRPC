*** Settings ***
Library           SSHLibrary
Library           Collections
Library           OperatingSystem
Variables         ../constant.yaml


*** Keywords ***
Establish SSH Connection
    [Arguments]    ${host}    ${user}   ${pwd} 
    Open Connection    ${host}
    
    Login    ${user}    ${pwd} 
    

Reciver command
    [Arguments]    ${host}    ${user}   ${pwd}  ${cmd}
    Establish SSH Connection    ${host}    ${user}   ${pwd}
    Write   cd ${receiver.bin_dir}
    Write   ${cmd}
    ${output}=    Read    delay=2s
    Log To Console    ${output}
    Log To Console  *********${cmd}***********
    ${open_home}=    SSHLibrary.List Directory     ${receiver.bin_dir}
    
    [return]    ${open_home}

Sender command specifed path
    [Arguments]    ${host}    ${user}   ${pwd}  
    Establish SSH Connection    ${host}    ${user}   ${pwd}
    Write   cd ${sender.bin_dir}
   
    FOR    ${element}    IN    @{sender.senders_ip}


        ${stdout}=    write    ./grpc_sender -D -s ${element} -f ${sender.bin_dir}/${sender.file_name} -v 1 -b 1MB -o ${sender.target_path}
        ${output}=    Read    delay=2s
        log    ${output}
        Should Contain    ${output}    File ${sender.bin_dir}/${sender.file_name} transfer succeeded.
        
    END

Sender command unspecifed path
    [Arguments]    ${host}    ${user}   ${pwd}  
    Establish SSH Connection    ${host}    ${user}   ${pwd}
   
   
    FOR    ${element}    IN    @{sender.senders_ip}

        Log To Console  ${sender.bin_dir}/grpc_sender -D -s ${element} -f ${sender.bin_dir}/${sender.file_name} -v 1 -b 1MB
        ${stdout}=         Execute Command    ${sender.bin_dir}/grpc_sender -D -s ${element} -f ${sender.bin_dir}/${sender.file_name} -v 1 -b 1MB    return_stdout=False    return_stdout=True
        Log To Console      ${stdout}
        Should Contain    ${stdout}    File ${sender.bin_dir}/${sender.file_name} transfer succeeded.
        
    END

Send multiple mutiple_files
    [Arguments]    ${host}    ${user}   ${pwd}  
    Establish SSH Connection    ${host}    ${user}   ${pwd}
    
    
    ${files_with_prefix} =    Create List
    FOR    ${file}    IN    @{sender.mutiple_files}
        ${file_with_prefix}     Evaluate    "${sender.bin_dir}/${file}"
        Append To List    ${files_with_prefix}    ${file_with_prefix}
    END
    ${result}     Evaluate    ",".join(${files_with_prefix})
    
   
    FOR    ${element}    IN    @{sender.senders_ip}

        Log To Console  ${sender.bin_dir}/grpc_sender -D -s ${element} -f ${result} -v 1 -c 2 -l3 -o ${sender.target_path}
        ${stdout}=         Execute Command    ${sender.bin_dir}/grpc_sender -D -s ${element} -f ${result} -v 1 -c 2 -l3 -o ${sender.target_path}    return_stdout=False    return_stdout=True
        Log To Console      ${stdout}
        Should Contain    ${stdout}    Files ${result} transfer succeeded.
        
    END

Receiver compress enabled 
    [Arguments]    ${host}    ${user}   ${pwd}  
    Establish SSH Connection    ${host}    ${user}   ${pwd}
   
   
    FOR    ${element}    IN    @{sender.senders_ip}

        Log To Console  ${sender.bin_dir}/grpc_sender -D -s ${element} -f ${sender.bin_dir}/${sender.file_name} -v 1 -c 2 -l3 -o ${sender.target_path}
        ${stdout}=         Execute Command    ${sender.bin_dir}/grpc_sender -D -s ${element} -f ${sender.bin_dir}/${sender.file_name} -v 1 -c 2 -l3 -o ${sender.target_path}    return_stdout=False    return_stdout=True
        Log To Console      ${stdout}
        Should Contain    ${stdout}    File ${sender.bin_dir}/${sender.file_name} transfer succeeded.
        
    END

Sender CheckSum OFF

    [Arguments]    ${host}    ${user}   ${pwd}  
    Establish SSH Connection    ${host}    ${user}   ${pwd}
   
   
    FOR    ${element}    IN    @{sender.senders_ip}

        Log To Console  ${sender.bin_dir}/grpc_sender -D -s ${element} -f ${sender.bin_dir}/${sender.file_name} -v 0 -b 10KB
        ${stdout}=         Execute Command    ${sender.bin_dir}/grpc_sender -D -s ${element} -f ${sender.bin_dir}/${sender.file_name} -v 0 -b 10KB     return_stdout=False    return_stdout=True
        Log To Console      ${stdout}
        Should Contain    ${stdout}    checksum algorithm: 0
        
    END

Sender CheckSum ON

    [Arguments]    ${host}    ${user}   ${pwd}  
    Establish SSH Connection    ${host}    ${user}   ${pwd}
   
   
    FOR    ${element}    IN    @{sender.senders_ip}

        Log To Console  ${sender.bin_dir}/grpc_sender -D -s ${element} -f ${sender.bin_dir}/${sender.file_name} -v 1 -b 20KB
        ${stdout}=         Execute Command    ${sender.bin_dir}/grpc_sender -D -s ${element} -f ${sender.bin_dir}/${sender.file_name} -v 1 -b 20KB     return_stdout=False    return_stdout=True
        Log To Console      ${stdout}
        Should Contain    ${stdout}    checksum algorithm: 1
        
    END

Test Case To Check
    [Arguments]    ${sender}    ${reciver}
    log    ${sender.host}
    log    ${reciver.host}

Transfer File With Specified Location Using gRPC Protocol Via SSH
    [Arguments]    ${sender}    ${receiver}
    ${receiver_result}    Reciver command    ${receiver.host}    ${receiver.user}   ${receiver.pwd}   ./${receiver.gRPC_Receiver_Command}
    ${snd_result}    Sender command specifed path    ${sender.host}    ${sender.user}   ${sender.pwd}
    Establish SSH Connection    ${receiver.host}    ${receiver.user}   ${receiver.pwd}
    ${open_home}=    SSHLibrary.List Directory     ${sender.target_path}
    Should Contain     ${open_home}    ${sender.file_name}

Suite Setup Demo
    log    Suite Setup Demo is executed


test setup demo
    log    the test setup demo keyword is executed
test teardown demo
    log    the test teardown keyword is executed

Suite Teardown Demo
    Close All Connections