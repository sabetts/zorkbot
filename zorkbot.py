import sys
import random
import os
import pickle
import socket
from jericho import FrotzEnv

# Configuration
HOST = "irc.libera.chat"
PORT = 6667
CHAN = env.get(ZORKBOT_CHANNEL, "#zorkbot")
NICK = env.get(ZORKBOT_NICK, "zorkbot")
BASE_PATH = 'z-machine-games-master/jericho-game-suite'

ROMS = list(os.listdir(BASE_PATH))

rom = 'zork1.z5'

def send_cmd(sock, msg):
    """Helper to send properly formatted IRC commands."""
    print("<<<", msg)
    sock.send(f"{msg}\r\n".encode("utf-8"))

def save_state(state):
    with open(f'{rom}_save_game.pkl', 'wb') as out:
        pickle.dump(state, out)

def load_state():
    filename = f'{rom}_save_game.pkl'
    if os.path.exists(filename):
        with open(filename, 'rb') as s:
            return pickle.load(s)
    else:
        return None

def main():
    global rom

    random.seed()
    # 1. Initialize Jericho
    path = os.path.join(BASE_PATH, rom)
    env = FrotzEnv(path)
    initial_obs, _ = env.reset()
    print(f"Loaded {rom}")

    state = load_state()
    if state:
        env.set_state(state)
    last_move = env.get_moves()


    # 2. Setup Socket
    irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    irc.connect((HOST, PORT))
    
    # 3. IRC Handshake
    send_cmd(irc, f"NICK {NICK}")
    send_cmd(irc, f"USER {NICK} 0 * :Jericho Text Adventure Bot")
    
    # 4. Main Loop
    buffer = ""
    joined = False

    while True:
        # Receive data
        data = irc.recv(2048).decode("utf-8", errors="ignore")
        if not data:
            break
        
        buffer += data
        lines = buffer.split("\r\n")
        buffer = lines.pop()

        for line in lines:
            print('>>>', line)

            # Respond to PINGs to stay alive
            if line.startswith("PING"):
                send_cmd(irc, f"PONG {line.split()[1]}")
                continue

            parts = line.split(" ", 2)
            sender = parts[0]
            cmd = parts[1]
            rest = parts[2]

            # Join channel after being welcomed (001 is the RPL_WELCOME code)
            if cmd == "001" and not joined:
                send_cmd(irc, f"JOIN {CHAN}")
                joined = True

            elif cmd == "PRIVMSG":
                # sender starts with a colon
                sender_nick = sender.split("!")[0][1:]
                dest, message = rest.split(' ', 1)
                # message starts with a colon
                message = message[1:]

                # Check if the bot is addressed directly
                prefix = f"{NICK}:".lower()
                if message.lower().startswith(prefix):
                    command = message[len(prefix):].strip()
                    
                    done = False
                    if command:
                        if command == 'actions':
                            actions = env.get_valid_actions()
                            clean_output = ' '.join(actions)
                        elif command == 'reset':
                            observation, _ = env.reset()
                            clean_output = " ".join(observation.splitlines()).strip()
                        elif command == 'randrom':
                            rom = random.choice(ROMS)
                            send_cmd(irc, f'PRIVMSG {CHAN} :Loading {rom}')
                            env = FrotzEnv(os.path.join(BASE_PATH, rom))
                            observation, _ = env.reset()
                            clean_output = " ".join(observation.splitlines()).strip()
                            state = load_state()
                            if state:
                                env.set_state(state)
                                clean_output = 'State restored'
                        elif command.startswith == 'rom ':
                            tmp = command.split(' ')[1]
                            if tmp in ROMS:
                                rom = tmp
                                env = FrotzEnv(os.path.join(BASE_PATH, rom))
                                observation, _ = env.reset()
                                clean_output = " ".join(observation.splitlines()).strip()
                                state = load_state()
                                if state:
                                    env.set_state(state)
                                    clean_output = 'state restored'
                            else:
                                clean_output = f'No such rom {tmp}'
                        else:
                            # Process through Jericho
                            observation, _, done, _ = env.step(command)
                            # Clean output: collapse newlines to a single space
                            clean_output = " ".join(observation.splitlines()).strip()
                            if not done and last_move != env.get_moves():
                                save_state(env.get_state())

                        last_move = env.get_moves()
                        # Send response back to IRC
                        #send_cmd(irc, f"PRIVMSG {CHAN} :{sender_nick}: {clean_output}")
                        send_cmd(irc, f"PRIVMSG {CHAN} :{clean_output}")
                        
                        if done:
                            send_cmd(irc, f"PRIVMSG {CHAN} :The game is over. Resetting...")
                            env.reset()

if __name__ == "__main__":
    main()
