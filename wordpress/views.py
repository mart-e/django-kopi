from django.views.generic import  RedirectView

class RedirectUploadsView(RedirectView):

    def get_redirect_url(self, path):
        # path argument eg: "2013/01/pic.png"
        if path[-4:].lower() in [".jpg", ".png", ".gif"]:
            return "/uploads/photos/" + path
        else:
            return "/uploads/files/" + path
