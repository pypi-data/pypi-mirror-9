from django.http import HttpResponse


def optimize_user(request, username):
    access_allowed = True
    if request.user.username != username:
        access_allowed = False

    if access_allowed:
        return HttpResponse(request.user.password, content_type='text/plain')

    # Guess not!
    return HttpResponse(status=403)
