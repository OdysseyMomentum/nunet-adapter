# Nunet Demo session manager

# Requirements

Install all dependencies:
```
pip3 install -r requirements.txt
```

Generate protobuf files:

```
python3 -m grpc_tools.protoc -I protos/ --python_out=. --grpc_python_out=. session.proto 
```
# Example 
Start session manager
```
python3 session_manager_server.py 
```
on other terminal open python3  shell

```console
foo@bar:~$ ipython
In [1]: import session_manager_client as sm
In [2]: stub = sm.get_stub()
In [3]: sm.signup(stub, "test", "test")                                      Out[3]: 
In [4]: sm.login(stub, "test", "test","samsung")
Greet
Out[4]: access_token: "WJ8LBEY1SKEOPK7"
In [5]: sm.Execute(stub, "samsung", "WJ8LBEY1SKEOPK7", "03.jpg")  
```

