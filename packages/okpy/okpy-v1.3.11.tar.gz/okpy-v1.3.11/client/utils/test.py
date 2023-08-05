#!/usr/bin/env python3

def pick_free_port():
    import socket
    port_guess = 7777
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind(('localhost', port_guess))
        except Exception as e: # Something went wrong with the binding
            port_guess += 1
            continue
        finally:
            s.close()
        
        return port_guess
