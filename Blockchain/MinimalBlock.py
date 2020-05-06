import copy
import hashlib


class Buffer:
    def __init__(self):
        self.index = 0
        self.timestamp = 0
        self.data = 0

    def encrypt_data(self, timestamp, data):
        self.index = self.index + 1


class MinimalBlock:
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


class MinimalChain:
    def __init__(self):  # initialize when creating a chain
        self.blocks = []

    def get_genesis_block(self, time, transactions):
        return MinimalBlock(0,
                            time,
                            transactions,
                            'arbitrary')

    def add_block(self, time, data):
        self.blocks.append(MinimalBlock(len(self.blocks),
                                        time,
                                        data,
                                        self.blocks[len(self.blocks) - 1].hash))

    def get_chain_size(self):  # exclude genesis block
        return len(self.blocks) - 1

    def verify(self, verbose=True):
        flag = True
        for i in range(1, len(self.blocks)):
            if self.blocks[i - 1].hash != self.blocks[i].previous_hash:
                flag = False
                if verbose:
                    print(f'Wrong previous hash at block {i}.')
            if self.blocks[i].hash != self.blocks[i].hashing():
                flag = False
                if verbose:
                    print(f'Wrong hash at block {i}.')
            if self.blocks[i - 1].timestamp >= self.blocks[i].timestamp:
                flag = False
                if verbose:
                    print(f'Backdating at block {i}.')
            return flag

    def fork(self, head='latest'):
        if head in ['latest', 'whole', 'all']:
            return copy.deepcopy(self)  # deepcopy since they are mutable
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

