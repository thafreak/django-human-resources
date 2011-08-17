from django.utils.translation import ugettext_lazy as _

from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool

class HRAppHook(CMSApp):
	name = _('HR App Hook')
	urls = ['human_resources.plugins.urls']
	#menus = APP_MENUS

apphook_pool.register(HRAppHook)