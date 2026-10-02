from web3 import AsyncWeb3, Web3
from web3.providers import AsyncHTTPProvider
from hexbytes import HexBytes

w3 = AsyncWeb3(AsyncHTTPProvider("https://ethereum-rpc.publicnode.com"))

ERC20_ABI = [
    {
        "name": "balanceOf",
        "type": "function",
        "stateMutability": "view",
        "inputs": [{"name": "account", "type": "address"}],
        "outputs": [{"name": "", "type": "uint256"}],
    },

    {
        "name":"totalSupply",
        "type":"function",
        "stateMutability":"view",
        "inputs":[],
        "outputs":[{"name":"","type":"uint256"}]
    }
]

MAILBOX_ABI = [
    {
        "inputs": [],
        "name": "latestDispatchedId",
        "outputs": [{"type": "bytes32"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"name": "_id", "type": "bytes32"}],
        "name": "delivered",
        "outputs": [{"type": "bool"}],
        "stateMutability": "view",
        "type": "function",
    },
]

TREE_HOOK_ABI = [
    {
      "inputs":[],
      "name":"count",
      "outputs":[{"internalType":"uint32","name":"","type":"uint32"}],
      "stateMutability":"view",
      "type":"function"
    }
]



async def get_eth_balance_gwei(addr):
  balance_wei = await w3.eth.get_balance(addr)
  return  w3.from_wei(balance_wei, "gwei")

async def get_erc20_balance(token_address, address):
  token = w3.eth.contract(address=Web3.to_checksum_address(token_address), abi=ERC20_ABI)
  return await token.functions.balanceOf(Web3.to_checksum_address(address)).call()

async def get_erc20_total_supply(token_address):
  token = w3.eth.contract(address=Web3.to_checksum_address(token_address), abi=ERC20_ABI)
  return await token.functions.totalSupply().call()

async def mailbox_get_latest_dispath_id(addr):
  mailbox = w3.eth.contract(address=addr,abi=MAILBOX_ABI)
  msg_id = await mailbox.functions.latestDispatchedId().call()
  return msg_id.hex()

async def mailbox_delivered(addr, _id):
  mailbox = w3.eth.contract(address=addr,abi=MAILBOX_ABI)
  return await mailbox.functions.delivered(HexBytes(_id)).call()

async def get_tree_hook_count(addr):
  hook = w3.eth.contract(address=addr, abi=TREE_HOOK_ABI)
  result = await hook.functions.count().call()
  return result - 1