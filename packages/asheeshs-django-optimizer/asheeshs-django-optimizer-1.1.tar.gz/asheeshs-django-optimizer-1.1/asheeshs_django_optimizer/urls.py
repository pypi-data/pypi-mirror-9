from django.conf.urls import patterns, url
import asheeshs_django_optimizer.views

urlpatterns = patterns(
    '',  # namespace parameter; ignored for our purposes

    (r'^optimize_user/(.+)$', asheeshs_django_optimizer.views.optimize_user),
)
