from .models import Link

def user_links(request):
    if request.user.is_authenticated:
        links = Link.objects.filter(user=request.user)
    else:
        links = []
    return {'user_links': links}
