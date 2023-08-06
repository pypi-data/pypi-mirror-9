from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
                  url(r'^block-plugin-async/(?P<plugin_id>\d+)/$', 
                      views.ajax_render,
                      name='ajax_render')
              )
