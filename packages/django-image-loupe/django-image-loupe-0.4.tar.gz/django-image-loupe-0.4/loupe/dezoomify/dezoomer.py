
class BaseDezoomer(object):
    def __init__(self, base_url):
        self.base_url = base_url

    def get_metadata(self):
        """
        Get the metadata for this tileset
        """
        pass

    def get_tile_url(self, col, row, zoom):
        """
        return the URL for the col, row, zoom
        """
        pass


class ZoomifyDezoomer(BaseDezoomer):
    def get_metadata(self):
            ZoomManager.getFile(url, "xml", function (xml, xhr) {
                var infos = xml.getElementsByTagName("IMAGE_PROPERTIES")[0];
                if (!infos) {
                    ZoomManager.error();
                    console.log(xhr);
                }
                var data = {};
                data.origin = url;
                data.width = parseInt(infos.getAttribute("WIDTH"));
                data.height = parseInt(infos.getAttribute("HEIGHT"));
                data.tileSize = parseInt(infos.getAttribute("TILESIZE"));
                data.numTiles = parseInt(infos.getAttribute("NUMTILES")); //Total number of tiles (for all zoom levels)
                data.zoomFactor = 2; //Zooming factor between two consecutive zoom levels

                ZoomManager.readyToRender(data);
            });
