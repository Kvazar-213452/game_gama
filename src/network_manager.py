import socket
import json
import threading

class NetworkManager:
    def __init__(self, host='localhost', port=5555):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.buffer = ""
        self.running = True
    
    def connect(self, player_name):
        try:
            self.client.connect((self.host, self.port))
            self.client.send(json.dumps({"name": player_name}).encode('utf-8'))
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            return False
    
    def start_receive_thread(self, message_handler):
        self.receive_thread = threading.Thread(
            target=self._receive_data, 
            args=(message_handler,)
        )
        self.receive_thread.daemon = True
        self.receive_thread.start()
    
    def _receive_data(self, message_handler):
        while self.running:
            try:
                data = self.client.recv(1024).decode('utf-8')
                if not data:
                    break
                    
                self.buffer += data
                while '\n' in self.buffer:
                    message, self.buffer = self.buffer.split('\n', 1)
                    try:
                        message = json.loads(message)
                        message_handler(message)
                    except json.JSONDecodeError:
                        print(f"Invalid JSON: {message}")
            except ConnectionResetError:
                print("Connection to server lost")
                break
            except Exception as e:
                print(f"Receive error: {e}")
                break
        
        self.running = False
        self.close_connection()
    
    def send(self, data):
        try:
            self.client.send((json.dumps(data) + '\n').encode('utf-8'))
        except Exception as e:
            print(f"Send error: {e}")
            self.running = False
    
    def close_connection(self):
        try:
            self.client.close()
        except:
            pass