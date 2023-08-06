
from facebookads.objects import AdAccount

account = AdAccount('act_999111243667')
account.remote_read(fields=[AdAccount.Field.name])
print account
