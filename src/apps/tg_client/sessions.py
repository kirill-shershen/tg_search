import logging

from django.core.exceptions import ObjectDoesNotExist
from telethon.crypto import AuthKey
from telethon.sessions import MemorySession

from .models import ClientSession
from .models import Session

"""
Read the following carefully before changing anything in this file.
https://github.com/LonamiWebs/Telethon/blob/master/telethon/sessions.py
"""


class DjangoSession(MemorySession):
    """This session contains the required information to login into your
    Telegram account. NEVER give the saved session file to anyone, since
    they would gain instant access to all your messages and contacts.
    If you think the session has been compromised, close all the sessions
    through an official Telegram client to revoke the authorization.
    """

    def __init__(self, client_session: ClientSession, *args, **kwargs):
        self.save_entities = True
        super().__init__()
        self.client_session = client_session
        if hasattr(self.client_session, "session"):
            session = self.client_session.session
            self._dc_id = session.data_center_id
            self._server_address = session.server_address
            self._port = session.port
            self._takeout_id = session.takeout_id
            auth_key = session.auth_key
            if isinstance(auth_key, memoryview):
                auth_key = auth_key.tobytes()
            self._auth_key = AuthKey(data=auth_key)
        else:
            self._auth_key = None

    def clone(self, to_instance=None):
        cloned = super().clone(to_instance)
        cloned.save_entities = self.save_entities
        return cloned

    # Data from sessions should be kept as properties
    # not to fetch the database every time we need it
    def set_dc(self, dc_id, server_address, port):
        super().set_dc(dc_id, server_address, port)
        self._update_session_table()
        # Fetch the auth_key corresponding to this data center
        try:
            session = Session.objects.get(client_session=self.client_session)
            auth_key = session.auth_key
            if isinstance(auth_key, memoryview):
                auth_key = auth_key.tobytes()
        except ObjectDoesNotExist:
            auth_key = None
        self._auth_key = AuthKey(data=auth_key) if auth_key else None

    @MemorySession.auth_key.setter
    def auth_key(self, value):
        if value == self._auth_key:
            return
        self._auth_key = value
        self._update_session_table()

    @MemorySession.takeout_id.setter
    def takeout_id(self, value):
        self._takeout_id = value
        if value == self._takeout_id:
            return
        self._update_session_table()

    def _update_session_table(self):
        # While we can save multiple rows into the sessions table
        # currently we only want to keep ONE as the tables don't
        # tell us which auth_key's are usable and will work. Needs
        # some more work before being able to save auth_key's for
        # multiple DCs. Probably done differently.
        defaults = {
            "data_center_id": self._dc_id,
            "server_address": self._server_address,
            "port": self._port,
            "auth_key": self._auth_key.key if self._auth_key else b"",
            "takeout_id": self._takeout_id,
        }
        Session.objects.update_or_create(
            client_session=self.client_session,
            defaults=defaults,
        )

    def set_update_state(self, entity_id, state):
        Session.objects.update_or_create(
            pk=entity_id,
            defaults={
                "pts": state.pts,
                "qts": state.qts,
                "date": state.date,
                "seq": state.seq,
            },
        )

    def save(self):
        """Saves the current session object as session_user_id.session"""
        # This is a no-op if there are no changes to commit, so there's
        # no need for us to keep track of an "unsaved changes" variable.
        pass

    def delete(self):

        """Deletes the current session file"""
        try:
            self.client_session.session.delete()
            return True
        except Exception:
            logging.exception("Failed to delete session")
            return False

    @classmethod
    def list_sessions(cls):

        """Lists all the sessions of the users who have ever connected
        using this client and never logged out
        """
        return ClientSession.objects.all().values_list("name", flat=True)
