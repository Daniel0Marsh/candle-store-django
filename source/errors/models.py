from django.db import models


class ErrorPage(models.Model):
    """
    Model representing the error page information for the website.
    """

    error_400 = models.FileField(upload_to="errors/videos/", help_text="Upload the 400 error video", default="default/error_400.mp4")
    error_403 = models.FileField(upload_to="errors/videos/", help_text="Upload the 403 error video", default="default/error_403.mp4")
    error_404 = models.FileField(upload_to="errors/videos/", help_text="Upload the 404 error video", default="default/error_404.mp4")
    error_500 = models.FileField(upload_to="errors/videos/", help_text="Upload the 404 error video", default="default/error_500.mp4")

    def __str__(self):
        return f"Error_page"
