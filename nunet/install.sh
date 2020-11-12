python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. object_detection.proto
python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. image_recon.proto
python3 -m grpc_tools.protoc -I session_manager/protos/ --python_out=session_manager --grpc_python_out=session_manager session.proto
