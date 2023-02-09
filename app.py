"""Image tile serving with large-image and trame."""
from aiohttp import web
from trame.app import get_server
from trame.ui.vuetify import SinglePageWithDrawerLayout
from trame.widgets import html, leaflet, vuetify

from tileserver import Tiler  # see adjacent file

server = get_server()
state, ctrl = server.state, server.controller

state.trame__title = "Large Image Trame Web App"


tiler = Tiler("TC_NG_SFBay_US_Geo_COG.tif")

bounds = tiler.bounds()
center = tiler.center()
state["metadata"] = tiler.source.getMetadata()

# Add tile endpoints to Trame app
my_routes = [
    web.get("/metadata", tiler.metadata),
    web.get("/tile/{z}/{x}/{y}.png", tiler.tile),
]


BASEMAPS = [
    {"text": "osm", "value": "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"},
    {
        "text": "positron",
        "value": "http://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png",
    },
    {
        "text": "dark-matter",
        "value": "https://{s}.basemaps.cartocdn.com/rastertiles/dark_all/{z}/{x}/{y}.png",
    },
    {
        "text": "voyager",
        "value": "https://{s}.basemaps.cartocdn.com/rastertiles/voyager_labels_under/{z}/{x}/{y}.png",
    },
    {
        "text": "stamen-terrain",
        "value": "https://stamen-tiles-{s}.a.ssl.fastly.net/terrain/{z}/{x}/{y}.png",
    },
]


@server.controller.add("on_server_bind")
def app_available(wslink_server):
    """Add our custom REST endpoints to the trame server."""
    wslink_server.app.add_routes(my_routes)


with SinglePageWithDrawerLayout(server) as layout:
    layout.title.set_text("Large Image Trame Web App")

    with layout.toolbar:
        layout.toolbar.style = "z-index: 1000;"  # really bump it to be above leaflet
        vuetify.VSpacer()

        vuetify.VSelect(
            label="Basemap",
            v_model=("basemap_url", BASEMAPS[0]["value"]),
            items=("array_list", BASEMAPS),
            hide_details=True,
            dense=True,
            outlined=True,
            classes="pt-1 ml-2",
            style="max-width: 250px; padding: 10px;",
        )

        vuetify.VSwitch(
            hide_details=True,
            v_model=("$vuetify.theme.dark",),
        )
        vuetify.VProgressLinear(
            indeterminate=True,
            absolute=True,
            bottom=True,
            active=("trame__busy",),
        )

    with layout.drawer:
        with html.Div(style="overflow: auto; width: 100%; height 100%;"):
            vuetify.VTreeview(items=("utils.tree(metadata)",))

    with layout.content:
        with vuetify.VContainer(
            fluid=True,
            classes="pa-0 fill-height",
        ):
            with leaflet.LMap(zoom=("zoom", 9), center=("center", center)):
                leaflet.LTileLayer(
                    url=(
                        "basemap_url",
                        "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
                    ),
                    attribution=(
                        "attribution",
                        '&copy; <a target="_blank" href="http://osm.org/copyright">OpenStreetMap</a> contributors',
                    ),
                )
                # leaflet.VGeosearch(options=("options",{"provider": "OpenStreetMapProvider"}))
                # leaflet.LMarker(lat_lng=("markerLatLng", center))

                # tiles
                leaflet.LTileLayer(url=("tile_url", "/tile/{z}/{x}/{y}.png"))

if __name__ == "__main__":
    server.start()
