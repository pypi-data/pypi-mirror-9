class AdditionalHandlingMixin(object):

    """ Marker class to allow for extra handling after save """

    def handle(self, form):

        """ Do extra handling that may or may not be related to an instance """

        pass
