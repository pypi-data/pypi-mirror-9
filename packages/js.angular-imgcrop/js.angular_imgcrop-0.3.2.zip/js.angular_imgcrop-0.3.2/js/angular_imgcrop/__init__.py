from fanstatic import Library, Resource, Group
import js.angular

library = Library('ngimgcrop', 'resources')

imgcrop_css = Resource(
    library, 'ng-img-crop.css',
    minified='ng-img-crop.min.css')

imgcrop_js = Resource(
    library, 'ng-img-crop.js',
    minified='ng-img-crop.min.js',
    depends=[js.angular.angular])

imgcrop = Group([imgcrop_css, imgcrop_js])
