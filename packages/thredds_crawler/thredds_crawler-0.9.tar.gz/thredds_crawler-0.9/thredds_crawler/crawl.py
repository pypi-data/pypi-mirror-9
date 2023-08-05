from thredds_crawler.etree import etree
import urllib
import urlparse
import requests
import os
import sys
import re
from thredds_crawler.utils import construct_url

INV_NS = "http://www.unidata.ucar.edu/namespaces/thredds/InvCatalog/v1.0"
XLINK_NS = "http://www.w3.org/1999/xlink"

import logging
try:
    # Python >= 2.7
    from logging import NullHandler
except ImportError:
    # Python < 2.7
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass
logger = logging.getLogger("thredds_crawler")
logger.addHandler(NullHandler())


class Crawl(object):

    SKIPS = [".*files.*", ".*Individual Files.*", ".*File_Access.*", ".*Forecast Model Run.*", ".*Constant Forecast Offset.*", ".*Constant Forecast Date.*"]

    def __init__(self, catalog_url, select=None, skip=None, debug=None):
        """
        select: a list of dataset IDs. Python regex supported.
        skip:   list of dataset names and/or a catalogRef titles.  Python regex supported.
        """

        if debug is True:
            logger.setLevel(logging.DEBUG)
            ch = logging.StreamHandler(sys.stdout)
            ch.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s - [%(levelname)s] %(message)s')
            ch.setFormatter(formatter)
            logger.addHandler(ch)

        # Only process these dataset IDs
        if select is not None:
            select = map(lambda x: re.compile(x), select)
        self.select = select

        # Skip these dataset links, such as a list of files
        # ie. "files/"
        if skip is None:
            skip = Crawl.SKIPS
        self.skip = map(lambda x: re.compile(x), skip)

        self.visited  = []
        datasets = [LeafDataset(url) for url in self._run(url=catalog_url) if url is not None]
        self.datasets = filter(lambda x: x.id is not None, datasets)

    def _run(self, url):
        if url in self.visited:
            logger.debug("Skipping %s (already crawled)" % url)
            return
        self.visited.append(url)

        logger.info("Crawling: %s" % url)

        u = urlparse.urlsplit(url)
        name, ext = os.path.splitext(u.path)
        if ext == ".html":
            u = urlparse.urlsplit(url.replace(".html", ".xml"))
        url = u.geturl()
        # Get an etree object
        try:
            r = requests.get(url)
            tree = etree.XML(str(r.text))
        except BaseException:
            logger.error("Skipping %s (error parsing getting XML)" % url)
            return

        # Crawl the catalogRefs:
        for ref in tree.findall('.//{%s}catalogRef' % INV_NS):
            # Check skips
            title = ref.get("{%s}title" % XLINK_NS)
            if not any([x.match(title) for x in self.skip]):
                for ds in self._run(url=construct_url(url, ref.get("{%s}href" % XLINK_NS))):
                    yield ds
            else:
                logger.info("Skipping catalogRef based on 'skips'.  Title: %s" % title)
                continue

        # Get the leaf datasets
        ds = []
        for leaf in tree.findall('.//{%s}dataset[@urlPath]' % INV_NS):
            # Subset by the skips
            name = leaf.get("name")
            if any([x.match(name) for x in self.skip]):
                logger.info("Skipping dataset based on 'skips'.  Name: %s" % name)
                continue

            # Subset by the Selects defined
            gid = leaf.get('ID')
            if self.select is not None:
                if gid is not None and any([x.match(gid) for x in self.select]):
                    logger.debug("Processing %s" % gid)
                    yield "%s?dataset=%s" % (url, gid)
                else:
                    logger.info("Ignoring dataset based on 'selects'.  ID: %s" % gid)
                    continue
            else:
                logger.debug("Processing %s" % gid)
                yield "%s?dataset=%s" % (url, gid)


class LeafDataset(object):
    def __init__(self, dataset_url):

        self.services    = []
        self.id          = None
        self.name        = None
        self.metadata    = None
        self.catalog_url = None
        self.data_size   = None

        # Get an etree object
        r = requests.get(dataset_url)
        try:
            tree = etree.XML(str(r.text))
        except etree.XMLSyntaxError:
            logger.error("Error procesing %s, invalid XML" % dataset_url)
        else:
            dataset = tree.find("{%s}dataset" % INV_NS)
            self.id = dataset.get("ID")
            self.name = dataset.get("name")
            self.metadata = dataset.find("{%s}metadata" % INV_NS)
            self.catalog_url = dataset_url.split("?")[0]

            # Data Size - http://www.unidata.ucar.edu/software/thredds/current/tds/catalog/InvCatalogSpec.html#dataSize
            data_size = dataset.find("{%s}dataSize" % INV_NS)
            if data_size is not None:
                self.data_size = float(data_size.text)
                data_units = data_size.get('units')
                # Convert to MB
                if data_units == "bytes":
                    self.data_size *= 1e-6
                elif data_units == "Kbytes":
                    self.data_size *= 0.001
                elif data_units == "Gbytes":
                    self.data_size /= 0.001
                elif data_units == "Tbytes":
                    self.data_size /= 1e-6

            # Services
            service_tag = dataset.find("{%s}serviceName" % INV_NS)
            if service_tag is None:
                service_tag = self.metadata.find("{%s}serviceName" % INV_NS)
            service_name = service_tag.text

            for service in tree.findall(".//{%s}service[@name='%s']" % (INV_NS, service_name)):
                if service.get("serviceType") == "Compound":
                    for s in service.findall("{%s}service" % INV_NS):
                        url = construct_url(dataset_url, s.get('base')) + dataset.get("urlPath")
                        if s.get("suffix") is not None:
                            url += s.get("suffix")
                        # ISO like services need additional parameters
                        if s.get('name') in ["iso", "ncml", "uddc"]:
                            url += "?dataset=%s&catalog=%s" % (self.id, urllib.quote_plus(self.catalog_url))
                        self.services.append( {'name' : s.get('name'), 'service' : s.get('serviceType'), 'url' : url } )
                else:
                    url = construct_url(dataset_url, service.get('base')) + dataset.get("urlPath") + service.get("suffix", "")
                    # ISO like services need additional parameters
                    if s.get('name') in ["iso", "ncml", "uddc"]:
                            url += "?dataset=%s&catalog=%s" % (self.id, urllib.quote_plus(self.catalog_url))
                    self.services.append( {'name' : service.get('name'), 'service' : service.get('serviceType'), 'url' : url } )

    @property
    def size(self):
        if self.data_size is not None:
            return self.data_size
        try:
            dap_endpoint = next(s.get("url") for s in self.services if s.get("service").lower() == "opendap")
            # Get sizes from DDS
            try:
                import netCDF4
                nc = netCDF4.Dataset(dap_endpoint)
                bites = 0
                for vname in nc.variables:
                    var = nc.variables.get(vname)
                    bites += var.dtype.itemsize * var.size
                return bites * 1e-6  # Megabytes
            except ImportError:
                logger.error("The python-netcdf4 library is required for computing the size of this dataset.")
                return None
        except StopIteration:
            return None  # We can't calculate

    def __repr__(self):
        return "<LeafDataset id: %s, name: %s, services: %s>" % (self.id, self.name, str([s.get("service") for s in self.services]))
