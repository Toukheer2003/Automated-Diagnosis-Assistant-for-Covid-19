import threading
import respond
import socket

HEADER = 30
PORT = 8000  
SERVER = socket.gethostbyname(socket.gethostname())
ADDRESS = (SERVER, PORT)   
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDRESS)  
data_client = {}  

def status(label, condition):
    status_message = ""
    if len(data_client[label]) != 9:
        if condition == "VALID":
            
            status_message = f'[CONFIRMED] {9 - len(data_client[label])} questions left'
        elif condition == "INVALID":
            
            status_message = f'[UNVALID] Please send an appropiate response'
           
        elif condition == "IDLE":
            status_message = '!DISCONNECT'
    elif len(data_client[label]) == 9:
        status_message = respond.respond(data_client[label])
        data_client[label] = []
        

    
    status_header = len(status_message)
    status = f"{status_header:<{HEADER}}"+status_message
    status_encoded = status.encode('utf-8')
    return status_encoded

def client_control(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    connected = True  
    data_client[addr[1]] = []
    while connected:
        try:
            conn.settimeout(20.0)
            msg_length = conn.recv(HEADER).decode('utf-8')
            conn.settimeout(None)
            if msg_length:  
                msg_lenght = int(msg_length)
                msg = conn.recv(msg_lenght).decode('utf-8')
                if msg == '!DISCONNECT':
                    print(f"[DISCONNECTED] {addr} has disconnected")
                    connected = False
                    continue
                print(f"[{addr}] sent a message : {msg}")
                
                
                if msg == 'Yes':
                    data_client[addr[1]].append(1)
                   
                    conn.send(status(addr[1], "VALID"))
                elif msg == 'No':
                    
                    data_client[addr[1]].append(0)
                    
                    conn.send(status(addr[1], "VALID"))
                else:
                    
                    conn.send(status(addr[1], "INVALID"))
                    
        except socket.timeout as e:
            print("[TIME OUT] Timed out after 20 seconds")
            conn.send(status(addr[1], "IDLE"))
            print(f"[DISCONNECTED] {addr} has disconnected")
            connected = False

        except ConnectionResetError:
            print("[FORCED CLOSED] Connection to the socket was forcedly closed by the client ... ")
            connected = False


    conn.close()  


def start():
    print("[STARTING] server is starting ...")
    server.listen()  
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        conn, addr = server.accept()  
        thread = threading.Thread(target=client_control, args=(conn,addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1} clients have connected ...")
start()
