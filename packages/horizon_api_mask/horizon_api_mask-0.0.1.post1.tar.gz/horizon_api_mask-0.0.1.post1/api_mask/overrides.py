from horizon import tables
from django.utils.translation import ugettext as _

from openstack_dashboard.dashboards.project.access_and_security.\
    api_access import tables as api_access_tables
from openstack_dashboard.dashboards.project.access_and_security import tabs, panel

from api_mask.templatetags.mask import mask
from api_mask.api_access import urls

class MaskedEndpointsTable(api_access_tables.EndpointsTable):

    api_endpoint = tables.Column('public_url',
                                 verbose_name=_("Service Endpoint"),
                                 filters=(mask,))

    class Meta:
        name = "endpoints"
        verbose_name = _("API Endpoints")
        table_actions = (api_access_tables.DownloadOpenRC, api_access_tables.DownloadEC2,)

tabs.APIAccessTab.table_classes = (MaskedEndpointsTable,)

panel.AccessAndSecurity.urls = "api_mask.urls"