from allauth.account.adapter import DefaultAccountAdapter


class AccountAdapter(DefaultAccountAdapter):
    def clean_password(self, password):
        password = super(AccountAdapter)
        return password
