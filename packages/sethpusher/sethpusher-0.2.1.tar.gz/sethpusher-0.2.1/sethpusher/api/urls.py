from sethpusher.api import views


def get_api_handlers(application_instance):
    urls = [
        (r"/api/users/(?P<user>.+)/", views.UserHandler),
        (r"/api/channels/(?P<channel>.+)/", views.ChannelHandler),
    ]
    if application_instance.debug:
        urls += [
            (r'/debug/', views.OverallDebugHandler),
            (r'/debug/channels/(?P<channel>.+)/', views.ChannelDebugHandler),
        ]
    return urls