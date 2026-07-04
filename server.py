import os
import socket
import threading
import json
from datetime import datetime
from time import strftime
import tkinter as tk
from tkinter import *
from tkinter import font as tkFont
from tkinter.scrolledtext import ScrolledText

print("Starting the application...")
print(f"Current working directory: {os.getcwd()}")

server_socket = None    # Global variable to hold the server socket
server_thread = None    # server thread handle (not started yet)
is_server_running = False
clients = []  # List to hold connected clients

# configure live clock
def update_clock():
    # Fetch current time format (HH:MM:SS AM/PM)
    # Use '%H:%M:%S' for a 24-hour format instead
    str_Time = strftime('%H:%M:%S %p')
    clock_label.config(text=str_Time)
    # Call this function again after 1000ms (1 second)
    clock_label.after(1000, update_clock)  # Update every 1000 milliseconds (1 second)

# function to save data to a JSON file
def save_data_to_file(data, path="serverData.json"):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        log_message(f"Error saving data to {path}: {e}")

# print the console into the GUI
def log_message(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"

    print(message)  # Print to console


    if 'console_box' in globals() and console_box.winfo_exists():
        console_box.config(state=tk.NORMAL)  
        console_box.insert(tk.END, log_entry) 
        console_box.config(state=tk.DISABLED)  # נעילה מחדש
        console_box.see(tk.END)                # גלילה אוטומטית למטה
        window.update_idletasks()              # כפיית רענון גרפי של החלון

def handle_client(client_socket, client_address):
    log_message(f"Handling client {client_address}")
    save_data_to_file({"client_address": str(client_address), "status": "connected"})
    try:
        while True:
            data = client_socket.recv(1024).decode()
            if not data:
                break
            log_message(f"Received from {client_address}: {data}")
            save_data_to_file({"client_address": str(client_address), "received_data": data})
            # Echo the data back to the client
            client_socket.sendall(data.encode())
    except Exception as e:
        log_message(f"Error handling client {client_address}: {e}")
    finally:
        log_message(f"Closing connection with {client_address}")
        save_data_to_file({"client_address": str(client_address), "status": "disconnected"})
        client_socket.close()

def broadcast(message, sender_socket):
    for client in clients:
        if client != sender_socket:
            try:
                client.sendall(message.encode())
            except Exception as e:
                log_message(f"Error broadcasting to a client: {e}")
                clients.remove(client)
                client.close()


# configure the server and the socket
def run_server():
    global server_socket, is_server_running
    try:       
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('0.0.0.0', 8820))
        server_socket.listen(5)
        save_data_to_file({"status": "server_started"})
        log_message("Server is listening on port 8820...")
        while True:
            (client_socket, client_address) = server_socket.accept()
            log_message (f"Connection established with {client_address}")

            # Start a new thread to handle the client
            client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
            client_thread.daemon = True
            client_thread.start()
    except Exception as e:
        log_message(f"Error in server: {e}")

def start_server():
    global server_thread
    if server_thread is None or not server_thread.is_alive():
        server_thread = threading.Thread(target=run_server)
        server_thread.daemon = True
        server_thread.start()


def start_server_clicked():
    global server_socket
    if not server_socket:
        status_label.config(text="Server is running...", fg="green")
        start_server()

def stop_server_clicked():
    global server_socket
    if server_socket:
        server_socket.close()
        server_socket = None
        status_label.config(text="Server stopped", fg="red")

# configuring the window
window = tk.Tk()
window.title("RamsChat Server")
window.geometry("600x600")
window.resizable(False, False) 
window.configure(background="lightblue")

# text Fonts
bold_font = tkFont.Font(family="Helvetica", size=12, weight="bold")
normal_font = tkFont.Font(family="Helvetica", size=12)

clock_label = tk.Label(window, font=normal_font, bg="lightblue")
clock_label.place(relx=0.5, rely=0.05, anchor=CENTER)


ServerStatus = Label(window, text="RamsChat Server", font=bold_font)
ServerStatus.place(relx=0.5, rely=0.1, anchor=CENTER)
ServerStatus.configure(background="lightblue")

# status label used to show server state
status_label = Label(window,
                    text="Server stopped", 
                    font=normal_font, fg="red")
status_label.place(relx=0.5, rely=0.18, anchor=CENTER)

start_button = tk.Button(
    window, 
    text="Start Server", font=normal_font, 
    command=start_server_clicked,
    width=15, height=2,
    bg="green", fg="white"

)
start_button.place(relx=0.5, rely=0.75, anchor=CENTER)
#start_button.pack(pady=20)

stop_button = tk.Button(
    window, 
    text="Stop Server", font=normal_font, 
    command=stop_server_clicked,
    width=15, height=2,
    bg="red", fg="white"
)
stop_button.place(relx=0.5, rely=0.90, anchor=CENTER)
#stop_button.pack(pady=20)

console_box = ScrolledText(
    window, 
    width=60, 
    height=15, 
    font=normal_font,
    bg="black",
    fg="white",
    insertbackground="white",  # Cursor color
)
console_box.pack(padx=20, pady=5)
console_box.config(state=tk.DISABLED)  # Make it read-only
console_box.place(relx=0.5, rely=0.45, anchor=CENTER)


if __name__ == "__main__":
    update_clock()  # Start the clock update loop
    # running = True
    print ("opening GUI...")
    window.mainloop()


