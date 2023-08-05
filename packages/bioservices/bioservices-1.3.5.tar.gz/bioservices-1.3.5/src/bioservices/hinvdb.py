from bioservices import REST



class HInvDB(REST):
    def __init__(self, verbose=True, cache=False):
        super(HInvDB, self).__init__(name="hinvdb", url='http://h-invitational.jp/hinv/hws/',
                verbose=verbose, cache=cache)


