import logging

import db

cfg = db.Config()

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("status")
log.setLevel(logging.INFO)


class Users:
    def __init__(self) -> None:
        self.log = logging.getLogger(f"Users")
        self.log.setLevel(logging.INFO)
        self.log.info("__init__")
        self.users = {}

    def add(self, message):
        self.log.info(f"add({message.json})")
        if message.chat.id not in self.users:
            self.users[message.chat.id] = User(message.chat.id)
        self.log.info(f"add: status=({self.users.keys()})")
        return self.users[message.chat.id]

    def get(self, message):
        self.log.info(f"get({message.json})")
        if message.chat.id in self.users:
            return self.users[message.chat.id]
        else:
            return None

    def pop(self, message):
        self.log.info(f"pop({message.json})")
        # if self.get(message):
        #    return self.status.pop(message.chat.id)
        # else:
        #    return None
        return self.users.pop(message.chat.id) or None

    def remove(self, message):
        self.log.info(f"remove({message.json})")
        if self.get(message):
            del self.users[message.chat.id]

    def reset(self, message):
        self.log.info(f"reset({message.json})")
        return self.add(message).reset()


class User:
    def __init__(self, id, parent=None):
        self.log = logging.getLogger(f"User({id}, {parent})")
        self.log.setLevel(logging.INFO)

        self.log.info(f"__init__(id={id}, parent={parent})")
        self.id = id
        self._parent = [parent]
        self._dlgs = []

    def __str__(self):
        return f"{self.id}"

    @property
    def parent(self):
        return self._parent[-1]

    @property
    def dlgs(self):
        return self._dlgs[-1]

    def reset(self):
        self.log.info("reset()")
        self._parent = [None]
        return self._parent

    def fwd(self, id):
        self.log.info(f"fwd({id})")
        # d = self.dlgGet(id=id)
        self._addDlg(id)
        self.log.info(f"self.dlgs=({self.dlgs})")
        return self._parent.append(id)

    def bwd(self):
        self.log.info("bwd()")
        if len(self._parent) > 1:
            self._popDlg()
            return self._parent.pop()
        else:
            return self.parent

    def _addDlg(self, id):
        dlg = self.dlgGet(id=id)
        log.info(f"_addDlg({dlg.text}, id={dlg.id})")
        self._dlgs.append(dlg)
        log.info(f"self._dlgs={self._dlgs}")

    def _popDlg(self):
        return self._dlgs.pop()

    def dlgGet(self, **kwargs):
        if not kwargs:
            kwargs = {"parent": self.parent}
        self.log.info(f"cfg.dlg.get({kwargs})")
        return cfg.dlg.get(**kwargs)

    def dlgFilter(self, **kwargs):
        if not kwargs:
            kwargs = {"parent": self.parent}
        self.log.info(f"dlgFilter({kwargs})")
        return [_ for _ in cfg.dlg.filter(**kwargs)]
