# KWh Minting Meter

## Prerequesites

- Cryptnox Basic card (Initialized & seeded - See 'Card initialization' for steps)
- Meter (or mock) circuit for pulse input
- Raspberry pi 3 or 4
- Card reader

## Setup

1. Clone this repo.
2. Install dependencies with `pip install -r requirements.txt`
3. Request developer (Or person with minter role) to upgrade your wallet address to minter role.
4. Run script (wallet address and GPIO pin number as argument e.g `python pulse_monitor.py 0x1a2b3c4d5e6f 40`)


## Process/Workflow

The script starts a 30 second loop in which it monitors input pulses from the designated GPIO pin. At the end of each loop, the user will be prompted to enter the card PIN to confirm and sign the transaction where the number of pulses recorded multplied by 0.001 will minted via the KWH smart contract. 

## Running the script
Syntax:
`python pulse_monitor.py <wallet_address> <GPIO pin number>`

## Card initialization

1. Run Cryptnoxpro
2. `init -e` or `init`
3. Enter data
4. `seed recover`
5. Enter mnemonics
