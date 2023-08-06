
class This_isnt_important():
    def __init__(self):
        self.note = 'you really should ignore this'
        self.command = 'ignore this file'
        self.suggest = 'this file probably wont come in handy later'
        
    def export(self):
        print(self.note)
        print(self.command)
        print(self.suggest)
        return