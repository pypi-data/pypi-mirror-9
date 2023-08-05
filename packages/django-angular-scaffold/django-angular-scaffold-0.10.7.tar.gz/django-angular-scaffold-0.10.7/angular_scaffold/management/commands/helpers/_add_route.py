import os
import re
from string import Template

_route = Template(""".when('${when}',
        {
            controller: '${controller}',
            templateUrl: '${template}'${resolutions}
        })""")

_resolve = Template("""                ${variable}: function (/*Service*/) {
                    return false; //replace with resolved variable call
                }""")
_header = """app.config(function ($routeProvider) {
    "use strict";
    $routeProvider"""

_footer = """.otherwise({redirectTo: '/'});
});"""


def add_route(directory, when=None, controller=None, template=None, resolves=None):
    if not when:
        when = raw_input("When: ")
    if not controller:
        controller = raw_input("Controller: ")
    if not template:
        template = raw_input("Template (relative to views folder): ")
    template = '/static/app/views/' + template
    if resolves is None:
        resolve_input = True
        resolves = []
        while resolve_input:
            resolve_input = raw_input("Resolve: ")
            if resolve_input:
                resolves.append(resolve_input)
    if resolves:
        resolutions = ",\n            resolve: {\n"
        resolutions += ',\n'.join([_resolve.substitute(variable=variable) for variable in resolves])
        resolutions += "\n            }"
    else:
        resolutions = ""
    new_route = _route.substitute(
        when=when,
        controller=controller,
        template=template,
        resolutions=resolutions
    )
    route_regex = '\.when\(.*?\}\)'
    with open(os.path.join(directory, 'assets', 'app', 'config', 'routes.js'), 'r') as route_file:
        data = route_file.read()
        routes = re.findall(route_regex, data, re.DOTALL)
    routes.append(new_route)
    with open(os.path.join(directory, 'assets', 'app', 'config', 'routes.js'), 'w') as route_file:
        route_file.write(_header + ''.join(routes) + _footer)