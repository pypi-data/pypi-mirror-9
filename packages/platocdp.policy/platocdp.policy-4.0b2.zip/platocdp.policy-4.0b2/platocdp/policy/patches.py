
def apply_patches():

    # Set default convertible types
    from collective.documentviewer.interfaces import IGlobalDocumentViewerSettings
    from collective.documentviewer.config import CONVERTABLE_TYPES
    IGlobalDocumentViewerSettings['auto_layout_file_types'].default = (
        CONVERTABLE_TYPES.keys()
    )
    patch_documentviewer_mimetype()


def patch_documentviewer_mimetype():
    # Set mimetype of getTranslatedJSLabels as text/javascript

    from collective.documentviewer.views import DocumentViewerView

    if getattr(DocumentViewerView, '__platocdp_mimetype_patched', False):
        return

    _orig_getTranslatedJSLabels = DocumentViewerView.getTranslatedJSLabels

    def getTranslatedJSLabels(self):
        o = _orig_getTranslatedJSLabels(self)
        self.request.response.setHeader('Content-type','text/javascript')
        return o

    DocumentViewerView.getTranslatedJSLabels = getTranslatedJSLabels
    DocumentViewerView.__platocdp_mimetype_patched = True
