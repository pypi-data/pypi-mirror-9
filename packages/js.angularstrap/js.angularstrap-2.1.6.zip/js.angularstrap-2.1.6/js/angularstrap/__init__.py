import fanstatic
import js.angular

library = fanstatic.Library('angularstrap', 'resources')

strap = fanstatic.Resource(
    library, 'angular-strap.js',
    minified='angular-strap.min.js',
    depends=[js.angular.angular])

templates = fanstatic.Resource(
    library, 'angular-strap.tpl.js',
    minified='angular-strap.tpl.min.js',
    depends=[js.angular.angular])

angularstrap = fanstatic.Group([strap, templates])
