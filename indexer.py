import web3
import time


w3 = web3.Web3(web3.Web3.WebsocketProvider("wss://ropsten.infura.io/ws/v3/090e2fb264dd4c5fbb28f4af2f6ccaba"))


def handle_event(event):
    print(event)

def log_loop(event_filter, poll_interval):
    while True:
        for event in event_filter.get_new_entries():
            handle_event(event)
        time.sleep(poll_interval)

def main():
    block_filter = w3.eth.filter('latest')
    log_loop(block_filter, 2)

if __name__ == '__main__':
    main()