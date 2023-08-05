from django.conf.urls import patterns
from shared_auth.views import HomeView

urlpatterns = patterns('',
   (r'^$', HomeView.as_view()),
)
