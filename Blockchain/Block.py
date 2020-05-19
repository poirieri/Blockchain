import copy
import hashlib


class Block:
    def __init__(self, index, timestamp, data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.hashing()

    def hashing(self):
        key = hashlib.sha256()
        key.update(str(self.index).encode('utf-8'))
        key.update(str(self.timestamp).encode('utf-8'))
        key.update(str(self.data).encode('utf-8'))
        key.update(str(self.previous_hash).encode('utf-8'))
        return key.hexdigest()

    def __repr__(self) -> str:
        return "index: " + str(self.index) + "\ntimestamp: " + self.timestamp + "\ndata: " + str(self.data) + \
               "\nprevious hash: " + self.previous_hash + "\nhash: " + self.hash


class Chain:
    def __init__(self):  # initialize when creating a chain
        self.blocks = []

    @staticmethod
    def get_first_block(time, transactions):
        return Block(0,
                     time,
                     transactions,
                     'arbitrary')

    def add_block(self, time, data):
        self.blocks.append(Block(len(self.blocks),
                                 time,
                                 data,
                                 self.blocks[len(self.blocks) - 1].hash))

    def get_chain_size(self):  # exclude genesis block
        return len(self.blocks) - 1

    def verify_hash(self, verbose=True):
        verified = True
        for i in range(1, len(self.blocks)):
            if self.blocks[i - 1].hash != self.blocks[i].previous_hash:
                verified = False
                if verbose:
                    print(f'Wrong previous hash at block {i}.')
            if self.blocks[i].hash != self.blocks[i].hashing():
                verified = False
                if verbose:
                    print(f'Wrong hash at block {i}.')
            if self.blocks[i - 1].timestamp >= self.blocks[i].timestamp:
                verified = False
                if verbose:
                    print(f'Backdating at block {i}.')
            return verified

    def fork(self, head='latest'):
        if head in ['latest', 'whole', 'all']:
            return copy.deepcopy(self)
        else:
            c = copy.deepcopy(self)
            c.blocks = c.blocks[0:head + '1']
            return

    def get_root(self, chain_2):
        min_chain_size = min(self.get_chain_size(), chain_2.get_chain_size())
        for i in range(1, min_chain_size + 1):
            if self.blocks[i] != chain_2.blocks[i]:
                return self.fork(i - 1)
        return self.fork(min_chain_size)
