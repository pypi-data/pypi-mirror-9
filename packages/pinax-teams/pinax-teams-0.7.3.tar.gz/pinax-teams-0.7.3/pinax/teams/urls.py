from django.conf.urls import patterns, url

from .views import TeamCreateView, TeamListView


urlpatterns = patterns(
    "pinax.teams.views",

    # overall
    url(r"^$", TeamListView.as_view(), name="team_list"),
    url(r"^:create/$", TeamCreateView.as_view(), name="team_create"),

    # team specific
    url(r"^(?P<slug>[\w\-]+)/$", "team_detail", name="team_detail"),
    url(r"^(?P<slug>[\w\-]+)/join/$", "team_join", name="team_join"),
    url(r"^(?P<slug>[\w\-]+)/leave/$", "team_leave", name="team_leave"),
    url(r"^(?P<slug>[\w\-]+)/apply/$", "team_apply", name="team_apply"),
    url(r"^(?P<slug>[\w\-]+)/edit/$", "team_update", name="team_edit"),
    url(r"^(?P<slug>[\w\-]+)/manage/$", "team_manage", name="team_manage"),

    # membership specific
    url(r"^(?P<slug>[\w\-]+)/ac/users-to-invite/$", "autocomplete_users", name="team_autocomplete_users"),  # noqa
    url(r"^(?P<slug>[\w\-]+)/invite-user/$", "team_invite", name="team_invite"),
    url(r"^(?P<slug>[\w\-]+)/members/(?P<pk>\d+)/revoke-invite/$", "team_member_revoke_invite", name="team_member_revoke_invite"),  # noqa
    url(r"^(?P<slug>[\w\-]+)/members/(?P<pk>\d+)/resend-invite/$", "team_member_resend_invite", name="team_member_resend_invite"),  # noqa
    url(r"^(?P<slug>[\w\-]+)/members/(?P<pk>\d+)/promote/$", "team_member_promote", name="team_member_promote"),  # noqa
    url(r"^(?P<slug>[\w\-]+)/members/(?P<pk>\d+)/demote/$", "team_member_demote", name="team_member_demote"),  # noqa
    url(r"^(?P<slug>[\w\-]+)/members/(?P<pk>\d+)/remove/$", "team_member_remove", name="team_member_remove"),  # noqa

    url(r"^accept/(?P<pk>\d+)/$", "team_accept", name="team_accept"),
    url(r"^reject/(?P<pk>\d+)/$", "team_reject", name="team_reject"),
)
