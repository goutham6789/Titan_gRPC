*** Settings ***
Library           SSHLibrary
Library           Collections
Library           OperatingSystem
Variables         ../constant.yaml
Resource          ../TestSuit/grpc_keywords.robot


*** Test Cases ***

Testcase1
    
    Log To Console    \n\n********* Establishing connection with the remote server ***********\n
    ${rec_res}    Reciver command    ${reciver.host}    ${reciver.user}   ${reciver.pwd}   ${reciver.bin_dir}/grpc_receiver ${reciver.c_option} ${reciver.l_option} ${reciver.D_option} ${reciver.d_option} ${reciver.target_dir}

    ${snd_result}    Sender command specifed path             

    Establish SSH Connection    ${reciver.host}    ${reciver.user}   ${reciver.pwd}
    ${open_home}=    SSHLibrary.List Directory     ${reciver.target_dir}
    Should Contain     ${open_home}    ${sender.file_name}

    Kill the Process


Testcase2
    ${rec_res}    Reciver command    ${reciver.host}    ${reciver.user}   ${reciver.pwd}   ${reciver.bin_dir}/grpc_receiver ${reciver.c_option} ${reciver.l_option} ${reciver.D_option} ${reciver.d_option} .    
    Log To Console   ${rec_res}

    ${snd_result}    Sender command unspecifed path             

    Establish SSH Connection    ${reciver.host}    ${reciver.user}   ${reciver.pwd}
    ${open_home}=    SSHLibrary.List Directory     ${reciver.bin_dir}
    Should Contain     ${open_home}    ${sender.file_name}

    Kill the Process

Testcase3

    ${rec_res}    Reciver command    ${reciver.host}    ${reciver.user}   ${reciver.pwd}   ${reciver.bin_dir}/grpc_receiver ${reciver.c_option} ${reciver.l_option} ${reciver.D_option} ${reciver.d_option} .   
    Log To Console   ${rec_res}

    ${snd_result}    Send multiple mutiple_files             

    Establish SSH Connection    ${reciver.host}    ${reciver.user}   ${reciver.pwd}
    ${open_home}=    SSHLibrary.List Directory     ${reciver.bin_dir}

    Kill the Process
    

Testcase4

    ${rec_res}    Reciver command    ${reciver.host}    ${reciver.user}   ${reciver.pwd}   ${reciver.bin_dir}/grpc_receiver ${reciver.D_option} ${reciver.d_option} .    
    Log To Console   ${rec_res}

    ${snd_result}    Sender command unspecifed path             

    Establish SSH Connection    ${reciver.host}    ${reciver.user}   ${reciver.pwd}
    ${open_home}=    SSHLibrary.List Directory     ${reciver.bin_dir}
    Should Contain     ${open_home}    ${sender.file_name}

    Kill the Process

Testcase5

    ${rec_res}    Reciver command    ${reciver.host}    ${reciver.user}   ${reciver.pwd}   ${reciver.bin_dir}/grpc_receiver ${reciver.c_option} ${reciver.l_option} ${reciver.D_option} ${reciver.d_option} .    
    Log To Console   ${rec_res}

    ${snd_result}    Receiver compress enabled              

    Establish SSH Connection    ${reciver.host}    ${reciver.user}   ${reciver.pwd}
    ${open_home}=    SSHLibrary.List Directory     ${reciver.bin_dir}
    Should Contain     ${open_home}    ${sender.file_name}

    Kill the Process

Testcase6
    ${rec_res}    Reciver command    ${reciver.host}    ${reciver.user}   ${reciver.pwd}   ${reciver.bin_dir}/grpc_receiver ${reciver.c_option} ${reciver.l_option} ${reciver.D_option} ${reciver.d_option} .    
    Log To Console   ${rec_res}

    ${snd_result}    Sender CheckSum OFF             

    Establish SSH Connection    ${reciver.host}    ${reciver.user}   ${reciver.pwd}
    ${open_home}=    SSHLibrary.List Directory     ${reciver.bin_dir}
    Should Contain     ${open_home}    ${sender.file_name}

    Kill the Process

Testcase7
    ${rec_res}    Reciver command    ${reciver.host}    ${reciver.user}   ${reciver.pwd}   ${reciver.bin_dir}/grpc_receiver ${reciver.c_option} ${reciver.l_option} ${reciver.D_option} ${reciver.d_option} .    
    Log To Console   ${rec_res}

    ${snd_result}    Sender CheckSum ON          

    Establish SSH Connection    ${reciver.host}    ${reciver.user}   ${reciver.pwd}
    ${open_home}=    SSHLibrary.List Directory     ${reciver.bin_dir}
    Should Contain     ${open_home}    ${sender.file_name}

    Kill the Process

