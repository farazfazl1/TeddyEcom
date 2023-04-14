from .models import Category

def menu_links(req):
    links = Category.objects.all()
    return dict(links=links)
        #Brings all categories links and store them into links variable