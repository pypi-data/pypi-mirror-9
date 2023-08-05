import logging
from django.db.models import get_model
from djinn_contenttypes.views.base import MimeTypeMixin, CTDetailView


LOGGER = logging.getLogger("djinn_forms")


class ContentImages(MimeTypeMixin, CTDetailView):

    """ Return listing of all images"""

    mimetype = "text/plain"
    template_name = "djinn_forms/snippets/contentimages.html"

    def has_images(self):

        return self.object.images.exists() or self.request.GET.get("image_ids")

    def list_images(self):

        """ List images, both already stored and added in the front end """

        images = self.object.images.all()

        if self.request.GET.get("image_ids", None):

            split_by_comma = self.request.GET["image_ids"].split(",")
            split_by_semicolon = [item.split(":")[0] for item in
                                  split_by_comma]

            image_ids = [img_id for img_id in split_by_semicolon if img_id]

            img_type = self.request.GET.get("img_type",
                                            "pgcontent.ImageAttachment")

            images_by_id = get_model(*img_type.split(".")).objects.filter(
                pk__in=image_ids)

            images = images | images_by_id

        return images
