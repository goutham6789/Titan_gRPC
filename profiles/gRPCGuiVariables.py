# Variables for Netact GUI

#Netact Mycom SDM Generic
host="172.17.160.37"
username="vncuser1"
password="vncuser1"
alias="HayesPP"
grpcIP = "172.17.160.37"

VM1_IP_Address = "172.17.160.37"
VM1_Username ="vncuser1"
VM1_Password="vncuser1"
VM1_Aliasname="HayesPP"

i =[]

VM1 =["192.168.29.141","admin","admin123","Receiver"]
VM2 =["192.168.29.11","admin","admin123","Sender"]
VMpath ="cd /home/admin/project/bin"
Sender_Output_Check= "File test.txt transfer succeeded"
Receiver_Output_Check="output file is /tmp/test.txt"
gRPC_Sender_Command_Transfer_File_With_Specified_Location = "./grpc_sender -D -s 192.168.29.141:50051 -f test.txt -v 1 -b 1MB -o /tmp"
gRPC_Receiver_Command_Transfer_File_With_Specified_Location = "./grpc_receiver -c 1 -l 3 –D -d /tmp"
gRPC_Sender_Command_Transfer_File_With_Unspecified_Location = "./grpc_sender -D -s 192.168.29.141:50051 -f test1.txt -v 1 -b 1MB"
gRPC_Receiver_Command_Transfer_File_With_Unspecified_Location = "./grpc_receiver -c 1 -l 3 –D -d /.."
gRPC_Sender_Command_Transfer_Multiple_File_With_Specified_Location = "./grpc_sender -D -s 192.168.29.141:50051 -f test2.txt -v 1 -b 1MB -o /tmp"
gRPC_Receiver_Command_Transfer_Multiple_File_With_Specified_Location = "./grpc_receiver -c 1 -l 3 –D -d /tmp"

