import sublime_plugin


class VRusEngCommand(sublime_plugin.TextCommand):
    """
        Converts Russian/English words that were
        printed on wrong keyboard.
    """

    @property
    def ruletters(self):
        return 'йцукенгшщзхъфывапролджэячсмитьбю'

    @property
    def enletters(self):
        return 'qwertyuiop[]asdfghjkl;\'zxcvbnm,.'

    @property
    def dic(self):
        d = dict(zip(self.ruletters, self.enletters))
        return d

    def convert(self, text):
        ru = set(self.ruletters)
        en = set(self.enletters)
        t = set(text)

        rulen = len(ru.intersection(t))
        enlen = len(en.intersection(t))

        sp = list(text)

        if rulen > enlen:
            d = dict(zip(self.ruletters, self.enletters))
            sp = list(map(lambda ch: d[ch] if ch in d else ch, sp))
            return ''.join(sp)

        elif rulen < enlen:
            d = dict(zip(self.enletters, self.ruletters))
            sp = list(map(lambda ch: d[ch] if ch in d else ch, sp))
            return ''.join(sp)

        return text

    def run(self, edit, **kw):
        selection = self.view.sel()
        for region in selection:
            reg_text = self.view.substr(region)
            self.view.replace(edit, region, self.convert(reg_text))
