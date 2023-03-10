import io

import large_image
from aiohttp import web


class Tiler:
    def __init__(self, filename):
        self.open_source(filename)

    def open_source(self, filename):
        self.source = large_image.open(
            filename,
            projection="EPSG:3857",
            encoding="PNG",
        )

    def bounds(self, srs="EPSG:4326"):
        return self.source.getBounds(srs=srs)

    def center(self, srs="EPSG:4326"):
        bounds = self.bounds(srs=srs)
        return (
            (bounds["ymax"] - bounds["ymin"]) / 2 + bounds["ymin"],
            (bounds["xmax"] - bounds["xmin"]) / 2 + bounds["xmin"],
        )

    async def metadata(self, request):
        """REST endpoint to get image metadata."""
        return web.json_response(self.source.getMetadata())

    async def tile(self, request):
        """REST endpoint to server tiles from image in slippy maps standard."""
        z = int(request.match_info["z"])
        x = int(request.match_info["x"])
        y = int(request.match_info["y"])
        tile_binary = self.source.getTile(x, y, z)
        return web.Response(body=io.BytesIO(tile_binary), content_type="image/png")
