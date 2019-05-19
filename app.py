import web3, eth_account, pdb, itertools, functools, hashlib, pprint, flask, flask_jsonrpc, toolz, json, logging, coloredlogs, os
import etherscan
import tinydb


__VERSION__ = (6, 2, 1)
ETHERSCAN_KEY = "T772QZEA6VGYD2UMTW5ZT4JJ98AVM6KVME"
ETHEREUM_NETWORK = "ropsten"


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
coloredlogs.install(fmt="%(asctime)-15s %(message)s", datefmt="%m/%d %H:%M:%S", logger=logger)
app = flask.Flask(__name__)
rpc = flask_jsonrpc.JSONRPC(app, "/", enable_web_browsable_api=True)
cache = tinydb.TinyDB("./cache.json")
etherscan_client = lambda: etherscan.Client(ETHERSCAN_KEY, network=ETHEREUM_NETWORK)
brainwallet = lambda data, security = 2000: web3.Web3.sha3(text=str(data) * security)
address = lambda account: eth_account.Account.privateKeyToAccount(brainwallet(account)).address
balances = {}


@rpc.method("getinfo")
def getinfo():
    return {
        "name": "RPC Masq v{}.{}.{}".format(*__VERSION__),
        "plugins": ["ethereum", "web3", "etherscan", "ropsten"],
    }


@rpc.method("listtransactions")
def listtransactions(account, limit):
    print("@listtransactions", "account", account, "address", address(account), "limit", limit)
    txs = etherscan_client().get_transactions_by_address(address(account))
    pprint.pprint(txs)
    Tx = tinydb.Query()
    for tx in txs:
        if not cache.search(Tx.hash == tx["hash"]):
            cache.insert(tx)
    return txs


@rpc.method("move")
def move(from_account, to_account, amount, min_conf=1, comment=None):
    print("@move", "from_account", from_account, "from_address", address(from_account), "to_account", to_account, "to_address", address(to_account), "amount", amount, "min_conf", min_conf)
    return false


@rpc.method("gettransaction")
def gettransaction(tx_hash):
    print("@gettransaction", tx_hash)
    tx = cache.search(tinydb.Query().hash == tx_hash)
    pprint.pprint(tx)
    return tx


@rpc.method("getbalance")
def getbalance(account="*", confirmations=1):
    print("@getbalance", "account", account, "address", address(account), "confirmations", confirmations)
    if account == "*":
        return str(sum(balances.values()))
    if confirmations == 0:
        return '0'
    w3 = web3.Web3(web3.Web3.HTTPProvider("https://ropsten.infura.io/v3/090e2fb264dd4c5fbb28f4af2f6ccaba"))
    balance = str(w3.fromWei(w3.eth.getBalance(address(account)), "ether"))
    # balance = etherscan_client().get_eth_balance(address(account))
    balances[address(account)] = float(balance)
    return balance


@rpc.method("getaccountaddress")
def getaccountaddress(account):
    print("@getaccountaddress", "account", account, "address", address(account))
    return address(account)


logger.info(" * Starting rpcMASQ v{}.{}.{}".format(*__VERSION__))
app.run(debug=True)
