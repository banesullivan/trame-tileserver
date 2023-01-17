"""Image tile serving with large-image and trame."""

import io
import json

import large_image
from aiohttp import web
from trame.app import get_server
from trame.ui.vuetify import SinglePageWithDrawerLayout
from trame.widgets import html, leaflet, vuetify

server = get_server()
state, ctrl = server.state, server.controller

state.trame__title = "Large Image Trame Web App"

# Open raster with large-image
src = large_image.open(
    "TC_NG_SFBay_US_Geo_COG.tif",
    projection="EPSG:3857",
    encoding="PNG",
)

bounds = src.getBounds(srs="EPSG:4326")
center = (
    (bounds["ymax"] - bounds["ymin"]) / 2 + bounds["ymin"],
    (bounds["xmax"] - bounds["xmin"]) / 2 + bounds["xmin"],
)


async def metadata(request):
    """REST endpoint to get image metadata."""
    return web.json_response(src.getMetadata())


async def tile(request):
    """REST endpoint to server tiles from image in slippy maps standard."""
    z = int(request.match_info["z"])
    x = int(request.match_info["x"])
    y = int(request.match_info["y"])
    tile_binary = src.getTile(x, y, z)
    return web.Response(body=io.BytesIO(tile_binary), content_type="image/png")


my_routes = [web.get("/metadata", metadata), web.get("/tile/{z}/{x}/{y}.png", tile)]


@server.controller.add("on_server_bind")
def app_available(wslink_server):
    """Add our custom REST endpoints to the trame server."""
    wslink_server.app.add_routes(my_routes)


with SinglePageWithDrawerLayout(server) as layout:
    layout.title.set_text("Large Image Trame Web App")

    with layout.toolbar:
        vuetify.VSpacer()
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
        with vuetify.VContainer(
            classes="pa-0"
            # TODO: fix so that overfill scrolls
        ):
            meta = json.dumps(src.getMetadata(), indent=2)
            html.Div(f"<pre>{meta}</pre>")

    with layout.content:
        with vuetify.VContainer(
            fluid=True,
            classes="pa-0 fill-height",
        ):
            with leaflet.LMap(zoom=("zoom", 9), center=("center", center)):
                leaflet.LTileLayer(
                    url=("url", "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"),
                    attribution=(
                        "attribution",
                        '&copy; <a target="_blank" href="http://osm.org/copyright">OpenStreetMap</a> contributors',
                    ),
                )
                # leaflet.VGeosearch(options=("options",{"provider": "OpenStreetMapProvider"}))
                # leaflet.LMarker(lat_lng=("markerLatLng", center))

                # tiles
                leaflet.LTileLayer(url="/tile/{z}/{x}/{y}.png")

if __name__ == "__main__":
    server.start()
