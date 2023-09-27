*** Settings ***
Library           SSHLibrary
Library           Collections
Library           OperatingSystem
Variables         ../constant.yaml
Library           Process
Library           String


*** Keywords ***
Establish SSH Connection
    [Arguments]    ${host}    ${user}   ${pwd} 
    Open Connection    ${host}
    
    Login    ${user}    ${pwd} 
    
Reciver command
    [Arguments]    ${host}    ${user}   ${pwd}  ${cmd}
    Establish SSH Connection    ${host}    ${user}   ${pwd}  
    
    Write   cd ${reciver.bin_dir}

    Write   ${cmd}
    ${output}=    Read    delay=2s
    Log To Console    ${output}
    
    ${open_home}=    SSHLibrary.List Directory     ${reciver.bin_dir}
    
    [return]    ${open_home}

Kill the Process
    ${output}     Execute Command     lsof -i :${reciver.port}    shell=True
    ${lines} =  Split String  ${output}  \n
    ${pid_line} =  Set Variable  ${EMPTY}
    FOR  ${line}  IN  @{lines}
        ${parts} =  Split String  ${line}  ${SPACE}
        
    END
    ${pid} =  Set Variable  ${parts[1]}  # Replace with the PID you want to kill
    ${kill_pid}     Execute Command  kill -9 ${pid}  
    ${output2}=    Read    delay=2s
    Log To Console    ${output2}
    Log To Console    PID: ${pid}

Sender command specifed path
   
    FOR    ${element}    IN    @{sender.senders_ip}
        ${sender_info}    Get From Dictionary    ${sender}    ${element}
        Log To Console    Sender IP: ${element}
        Log To Console    User: ${sender_info.usr1}
        Log To Console    Password: ${sender_info.pwd}
        Log To Console    filename: ${sender_info.file_name}

        Establish SSH Connection    ${element}     ${sender_info.usr1}   ${sender_info.pwd}
        ${stdout}=         Execute Command    ${sender.bin_dir}/grpc_sender -D -s ${reciver.host}:${reciver.port} -f ${sender.bin_dir}/${sender_info.file_name} -v 1 -b 1MB -o ${sender.target_path}   return_stdout=False    return_stdout=True
        Should Contain    ${stdout}    File ${sender.bin_dir}/${sender_info.file_name} transfer succeeded.
        
    END

Sender command unspecifed path
   
    FOR    ${element}    IN    @{sender.senders_ip}

        ${sender_info}    Get From Dictionary    ${sender}    ${element}

        Establish SSH Connection    ${element}     ${sender_info.usr1}   ${sender_info.pwd}

        ${stdout}=         Execute Command    ${sender.bin_dir}/grpc_sender -D -s ${reciver.host}:${reciver.port} -f ${sender.bin_dir}/${sender_info.file_name} -v 1 -b 1MB    return_stdout=False    return_stdout=True
        Should Contain    ${stdout}    File ${sender.bin_dir}/${sender_info.file_name} transfer succeeded.
        
    END

Send multiple mutiple_files
    
    ${files_with_prefix} =    Create List
    FOR    ${file}    IN    @{sender.mutiple_files}
        ${file_with_prefix}     Evaluate    "${sender.bin_dir}/${file}"
        Append To List    ${files_with_prefix}    ${file_with_prefix}
    END
    ${result}     Evaluate    ",".join(${files_with_prefix})
    
   
    FOR    ${element}    IN    @{sender.senders_ip}

        ${sender_info}    Get From Dictionary    ${sender}    ${element}

        Establish SSH Connection    ${element}     ${sender_info.usr1}   ${sender_info.pwd}

        ${stdout}=         Execute Command    ${sender.bin_dir}/grpc_sender -D -s ${reciver.host}:${reciver.port} -f ${result} -v 1 -c 2 -l3 -o ${sender.target_path}    return_stdout=False    return_stdout=True
        Log To Console      ${stdout}
        Should Contain    ${stdout}    Files ${result} transfer succeeded.
        
    END

Receiver compress enabled 
   
    FOR    ${element}    IN    @{sender.senders_ip}

        ${sender_info}    Get From Dictionary    ${sender}    ${element}

        Establish SSH Connection    ${element}     ${sender_info.usr1}   ${sender_info.pwd}
        ${stdout}=         Execute Command    ${sender.bin_dir}/grpc_sender -D -s ${reciver.host}:${reciver.port} -f ${sender.bin_dir}/${sender_info.file_name} -v 1 -c 2 -l3 -o ${sender.target_path}    return_stdout=False    return_stdout=True
        Should Not Contain    ${stdout}     File ${sender.bin_dir}/${sender_info.file_name} transfer succeeded.
        
    END

Sender CheckSum OFF

   
    FOR    ${element}    IN    @{sender.senders_ip}

        ${sender_info}    Get From Dictionary    ${sender}    ${element}

        Establish SSH Connection    ${element}     ${sender_info.usr1}   ${sender_info.pwd}

        ${stdout}=         Execute Command    ${sender.bin_dir}/grpc_sender -D -s ${reciver.host}:${reciver.port} -f ${sender.bin_dir}/${sender_info.file_name} -v 0 -b 10KB     return_stdout=False    return_stdout=True
        Log To Console      ${stdout}
        Should Contain    ${stdout}    checksum algorithm: 0
        
    END

Sender CheckSum ON

   
    FOR    ${element}    IN    @{sender.senders_ip}

        ${sender_info}    Get From Dictionary    ${sender}    ${element}

        Establish SSH Connection    ${element}     ${sender_info.usr1}   ${sender_info.pwd}

        ${stdout}=         Execute Command    ${sender.bin_dir}/grpc_sender -D -s ${reciver.host}:${reciver.port} -f ${sender.bin_dir}/${sender_info.file_name} -v 1 -b 20KB     return_stdout=False    return_stdout=True
        Log To Console      ${stdout}
        Should Contain    ${stdout}    checksum algorithm: 1
        
    END
