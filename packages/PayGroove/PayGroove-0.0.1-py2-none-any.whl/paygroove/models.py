class BaseModel(object):
    @classmethod
    def from_dict(cls, data):
        inst = cls()

        for k, v in data.iteritems():
            setattr(inst, k, v)

        return inst


class Player(BaseModel):
    @property
    def name(self):
        '''
        An alias to "player".
        '''
        # noinspection PyUnresolvedReferences
        return self.player


class BitcoinAddress(BaseModel):
    pass


class Transaction(BaseModel):
    pass
