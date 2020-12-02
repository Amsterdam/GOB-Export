import datetime


class CredentialStore:

    # Refresh or request new credentials when the credentials age is past the THRESHOLD of its validity
    THRESHOLD = 0.75

    def __init__(self, get_credentials, refresh_credentials, secure_user=None):
        """
        Initialize the store

        Use the get- and refresh credential methods to get new credentials or refresh existing credentials

        :param get_credentials:
        :param refresh_credentials:
        """
        assert secure_user, "A secure user is required to know which client id and secret to use"
        self._credentials = None
        self._timestamp = None
        self._get_credentials = get_credentials
        self._refresh_credentials = refresh_credentials
        self._secure_user = secure_user

    def _now(self):
        """
        Used to timestamp crecentials

        :return:
        """
        return datetime.datetime.now()

    def _age(self):
        """
        Age of credentials in seconds

        :return:
        """
        return (self._now() - self._timestamp).total_seconds()

    def get_credentials(self):
        """
        Get credentials

        If the current credentials are still valid the return the current credentials
        If the credentials can be refreshed then refresh the credentials and store these as the current credentials
        Else request new credentials

        :return:
        """
        if self._credentials:
            # Get the age of the current credentials in seconds
            age = self._age()
            expires_in = self._credentials['expires_in']
            refresh_expires_in = self._credentials['refresh_expires_in']
            if age < expires_in * self.THRESHOLD:
                # Credentials are still valid, no action required
                pass
            elif age < refresh_expires_in * self.THRESHOLD:
                # Refresh credentials
                credentials = self._refresh_credentials(self._credentials, self._secure_user)
                self._save_credentials(credentials)
            else:
                # Invalidate credentials
                self._credentials = None
                self._timestamp = None

        if not self._credentials:
            # (re)new token
            credentials = self._get_credentials(self._secure_user)
            self._save_credentials(credentials)

        return self._credentials

    def _save_credentials(self, credentials):
        """
        Save the credentials as the current credentials

        :param credentials:
        :return:
        """
        self._credentials = credentials
        self._timestamp = self._now()
