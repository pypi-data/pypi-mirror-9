from fanstatic import Group
from fanstatic import Library
from fanstatic import Resource
from js.bootstrap import bootstrap_css
from js.bootstrap import bootstrap_js


library = Library('bootstrap_image_gallery', 'resources')

# CSS
blueimp_gallery_css = Resource(
    library,
    'blueimp-gallery/css/blueimp-gallery.css',
    minified='blueimp-gallery/css/blueimp-gallery.min.css',
    depends=[bootstrap_css, ])
bootstrap_image_gallery_css = Resource(
    library,
    'blueimp-bootstrap-image-gallery/css/bootstrap-image-gallery.css',
    minified='blueimp-bootstrap-image-gallery/css/bootstrap-image-gallery.min.css',  # noqa
    depends=[blueimp_gallery_css, ])

# JS
blueimp_gallery_js = Resource(
    library,
    'blueimp-gallery/js/jquery.blueimp-gallery.js',
    minified='blueimp-gallery/js/jquery.blueimp-gallery.min.js',
    depends=[bootstrap_js, ])
bootstrap_image_gallery_js = Resource(
    library,
    'blueimp-bootstrap-image-gallery/js/bootstrap-image-gallery.js',
    minified='blueimp-bootstrap-image-gallery/js/bootstrap-image-gallery.min.js',  # noqa
    depends=[blueimp_gallery_js, ])

# BW COMPAT
gallery_css = bootstrap_image_gallery_css
gallery_js = bootstrap_image_gallery_js

# THE "ALL IN ONE" RESOURCE
gallery = Group([bootstrap_image_gallery_css, bootstrap_image_gallery_js])
