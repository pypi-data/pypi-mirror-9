from hypchat import HypChat
from twisted.internet import reactor
from twisted.words.protocols.jabber import jid

from helga import log, settings
from helga.plugins import Plugin, PRIORITY_HIGH


logger = log.getLogger(__name__)


class HipChatNicks(Plugin):

    priority = PRIORITY_HIGH

    def __init__(self, *args, **kwargs):
        super(HipChatNicks, self).__init__(*args, **kwargs)

        self.api_token = settings.HIPCHAT_API_TOKEN
        self.api_endpoint = getattr(settings, 'HIPCHAT_API_ENDPOINT', 'https://api.hipchat.com')
        self.client = HypChat(self.api_token, endpoint=self.api_endpoint)
        self.nick_map = {}
        reactor.callLater(0, self._init_nicks)

    def _init_nicks(self):
        logger.info('Getting all hipchat nicks from %s', self.api_endpoint)
        for user in self.client.users()['items']:
            mention_name = '@{0}'.format(user['mention_name'])

            # Full name -> mention name
            self.nick_map[user['name']] = mention_name

            # Also and include the XMPP JID in the mapping
            try:
                details = self.client.get_user(user['id'])
                user_jid = jid.JID(details['xmpp_jid'])
                self.nick_map[user_jid.user] = mention_name
            except:
                logger.exception("Failed to get user's JID for HipChat mapping: %s", user)

    def preprocess(self, client, channel, nick, message):
        return channel, self.nick_map.get(nick, nick), message
