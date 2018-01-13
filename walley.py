# walley.py
# A simple Coil CLI
# wallet

import os
import sys
import time
from pathlib import Path

from coil.wallet import readWallet

WALLET_DIR = str(Path.home()) + "/.config/coil/wallets"
WIDTH = 26

def getWallet():
    wallet = False
    print("Select a wallet to use...")
    wallets = os.listdir(WALLET_DIR)
    priv_wallets = filter(lambda x: not x.endswith(".pub.pem"), wallets)
    for k, j in enumerate(priv_wallets):
        print(k, j)
    
    while not wallet:
        print("="*WIDTH)

        id = input("Enter an id: ")
        if id.isdigit() and int(id) <= len(list(priv_wallets)):
            wallet = readWallet(
                WALLET_DIR + "/" + wallets[int(id)],
                WALLET_DIR + "/" + wallets[int(id) + 1]
            )
            return wallet
        else:
            print("Invalid Wallet")

def menu():
    while True:
        try:
            actions = ["View balance", "Send Funds"]
            print("What would you like to do?")
            for j, k in enumerate(actions):
                print(j, k)

            print("="*WIDTH)
            while True:
                action = input("Enter an id: ")
                if action.isdigit() and int(id) <= len(list(actions)):
                    pass

        except KeyboardInterrupt:
            sys.exit(0)

def main():
    print("="*WIDTH)
    print("Welcome to walley")
    print("A microwallet for coilcoin")
    print("Ctrl-C to quit")
    print("="*WIDTH)
    time.sleep(1)

    wallet = getWallet()
    print("="*WIDTH)
    menu()

if __name__ == "__main__":
    main()