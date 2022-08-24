from eth_account._utils.legacy_transactions \
import encode_transaction,serializable_unsigned_transaction_from_dict
import eth_utils
import RPi.GPIO as GPIO
from termcolor import colored
import time
from eth_utils.curried import keccak
from hexbytes import HexBytes
from web3 import Web3
from web3.middleware import geth_poa_middleware
import cryptnoxpy as cp
import json
import ecdsa
import os
import getpass
import cryptos
import os
import sys

#Web3 variables
infura_url = "https://rinkeby.infura.io/v3/ac389dd3ded74e4a85cc05c8927825e8"
w3 = Web3(Web3.HTTPProvider(infura_url))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
try:
    wallet_address = w3.toChecksumAddress(sys.argv[1])
except:
    print(f'Please provide your wallet address as argument when running the script.\n(e.g `python pulse_monitor.py 0x1a2b3c4d5e6f 40)`')
    sys.exit(0)
contract_address = w3.toChecksumAddress('0xB8Eb640d68A73c48FA94aBAccaB49e56399E24F5')
abi = json.loads('[{"constant":true,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"spender","type":"address"},{"name":"amount","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"sender","type":"address"},{"name":"recipient","type":"address"},{"name":"amount","type":"uint256"}],"name":"transferFrom","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"initialSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"spender","type":"address"},{"name":"addedValue","type":"uint256"}],"name":"increaseAllowance","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"account","type":"address"},{"name":"amount","type":"uint256"}],"name":"mint","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"amount","type":"uint256"}],"name":"burn","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"account","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"account","type":"address"},{"name":"amount","type":"uint256"}],"name":"burnFrom","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"account","type":"address"}],"name":"addMinter","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[],"name":"renounceMinter","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"spender","type":"address"},{"name":"subtractedValue","type":"uint256"}],"name":"decreaseAllowance","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"recipient","type":"address"},{"name":"amount","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"account","type":"address"}],"name":"isMinter","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"owner","type":"address"},{"name":"spender","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"inputs":[],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"name":"account","type":"address"}],"name":"MinterAdded","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"account","type":"address"}],"name":"MinterRemoved","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"from","type":"address"},{"indexed":true,"name":"to","type":"address"},{"indexed":false,"name":"value","type":"uint256"}],"name":"Transfer","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"owner","type":"address"},{"indexed":true,"name":"spender","type":"address"},{"indexed":false,"name":"value","type":"uint256"}],"name":"Approval","type":"event"}]')
contract=w3.eth.contract(address=contract_address, abi=abi)

#set GPIO numbering mode and define input pin
try:
    pulse_input_pin = int(sys.argv[2])
except:
    print(f'Please provide GPIO pin number to use in monitoring input pulses.\n(e.g `python pulse_monitor.py 0x1a2b3c4d5e6f 40)')
GPIO.setmode(GPIO.BOARD)
GPIO.setup(pulse_input_pin,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
counter = 0
time_t1 = time.time()

def transaction_hash(transaction, chain_id =4 ,vrs: bool = False):
        try:
            del transaction["maxFeePerGas"]
            del transaction["maxPriorityFeePerGas"]
        except KeyError:
            pass
        unsigned_transaction = serializable_unsigned_transaction_from_dict(transaction)
        encoded_transaction = encode_transaction(unsigned_transaction, (chain_id, 0, 0))
        return keccak(encoded_transaction)


def push(transaction, signature, public_key,chain_id = 4):
        unsigned_transaction = serializable_unsigned_transaction_from_dict(transaction)
        var_v, var_r, var_s = _decode_vrs(signature, chain_id,
                                                transaction_hash(transaction),
                                                cryptos.decode_pubkey(public_key))
                        

        rlp_encoded = encode_transaction(unsigned_transaction, (var_v, var_r, var_s))

        return w3.eth.send_raw_transaction(HexBytes(rlp_encoded))


def _decode_vrs(signature_der: bytes, chain_id: int, transaction: bytes, q_pub: tuple) -> tuple:
        curve = ecdsa.curves.SECP256k1
        signature_decode = ecdsa.util.sigdecode_der
        generator = curve.generator
        var_r, var_s = signature_decode(signature_der, generator.order())

        # Parity recovery
        var_q = ecdsa.keys.VerifyingKey.from_public_key_recovery_with_digest(
            signature_der, transaction, curve, sigdecode=signature_decode)[1]

        i = 35
        if var_q.to_string("uncompressed") == cryptos.encode_pubkey(q_pub, "bin"):
            i += 1

        var_v = 2 * chain_id + i

        return var_v, var_r, var_s


def mint_token(qty):
    if qty > 0:
        print(colored(f"Minting {qty*0.001} tokens","blue"))
        mint_tx = contract.functions.mint(wallet_address,qty).buildTransaction({'from':wallet_address})
        del mint_tx['from']
        mint_tx['gasPrice'] = Web3.toWei('50', 'gwei')
        mint_tx['nonce'] = w3.eth.getTransactionCount(wallet_address)
        card = cp.factory.get_card(cp.Connection())
        pin = getpass.getpass(prompt="Please input your PIN to sign transaction: ")
        valid_pin = pin if pin != '' else '000000000'
        card.verify_pin(valid_pin)
        PATH = "m/44'/60'/0'/0/0"
        public_key = card.get_public_key(0x01,path=PATH,compressed=False)
        card.derive(path=PATH)
        digest = transaction_hash(mint_tx)
        signature = card.sign(digest,pin=valid_pin)
        print(f'Transaction hash: {bytes(push(mint_tx,signature,public_key)).hex()}')
    else:
        print(colored(f"Not minting tokens.","grey"))

def pulse_callback(channel):
    global counter
    if GPIO.input(channel)==1:
        print(colored("Pulse detected","green"))
        counter += 1


try:
    print('Starting pulse monitoring.')
    GPIO.add_event_detect(pulse_input_pin, GPIO.RISING, callback=pulse_callback)
    loop_seconds = 30
    remaining_seconds = 0
    while True:
        if remaining_seconds == 0:
            remaining_seconds = loop_seconds
        time_t2 = time.time()
        if (int(time_t2 - time_t1)) == (loop_seconds - remaining_seconds):
            print(colored(f"Looping in {remaining_seconds}","grey"))
            remaining_seconds -= 1
        if (time_t2 - time_t1) > loop_seconds:
            os.system('cls' if os.name == 'nt' else 'clear')
            mint_token(counter)
            counter = 0
            time_t1 = time.time()
except KeyboardInterrupt:
    print(colored("\nExiting program on Keyboard Interrupt","yellow"))
finally:
    #cleanup the GPIO pins before ending
    GPIO.cleanup()

