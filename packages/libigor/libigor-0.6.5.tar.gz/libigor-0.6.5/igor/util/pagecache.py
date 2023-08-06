# -*- coding: utf-8 -*-
from igor import cache
from igor.batching import rangeiter
import logging


#----------------------------------------------------------------------------//
def create(key, items, perpage):
    """ Cache array as pages for faster access.
    :arg key:       The key as string. This will be used as a base for keys for
                    all cache items used in the process.
    :arg items:     The array with items to be cached.
    :arg perpage:   The number of items stored in one page.
    """
    masterkey = '{key}-{pagesize}'.format(key=key, pagesize=perpage)
    allcount  = len(items)
    pgnum     = 0
    cache.set(masterkey, allcount)
    for beg, end in rangeiter(allcount, perpage):
        pgnum += 1
        pgkey  = '{master}-{pagenum}'.format(master=masterkey, pagenum=pgnum)
        cache.set(pgkey, items[beg:end])


#----------------------------------------------------------------------------//
def exists(key, perpage):
    masterkey = '{key}-{pagesize}'.format(key=key, pagesize=perpage)
    return cache.get(masterkey) != None


#----------------------------------------------------------------------------//
def get_size(key, perpage):
    """ Return the number of items in the page cache with the given key

    :arg key:       Key as a string. Same key as in ``pagecache.create()``
    """
    masterkey = '{key}-{pagesize}'.format(key=key, pagesize=perpage)
    return cache.get(masterkey)


#----------------------------------------------------------------------------//
def clear(key, perpage):
    """ Clear page cache with the given key

    :arg key:       Key as a string. Same key as in ``pagecache.create()``
    """
    masterkey = '{key}-{pagesize}'.format(key=key, pagesize=perpage)
    allcount  = cache.get(masterkey)
    pgnum     = 0
    for beg, end in rangeiter(allcount, perpage):
        cache.delete()
        pgnum += 1
        pgkey  = '{master}-{pagenum}'.format(master=masterkey, pagenum=pgnum)
        cache.delete(pgkey)


#----------------------------------------------------------------------------//
def get_page(key, perpage, page):
    """ Get items for the given page

    :arg key:       Key as a string. Same key as in ``pagecache.create()``.
    :arg page:      Page number as integer.
    """
    pagekey = '{key}-{pagesize}-{pagenum}'.format(
        key      = key,
        pagesize = perpage,
        pagenum  = page
    )
    page = cache.get(pagekey)
    return page or []


#==============================================================================
class PageCache(object):
    """
    >>> pcache = PageCache('mykey', 2, lambda: [1, 2, 3, 4])
    >>> pcache.count == 4
    True

    >>> pcache.
    """
    #------------------------------------------------------------------------//
    def __init__(self, key, perpage, datasrc):
        self.master  = '{key}-{pagesize}'.format(key=key, pagesize=perpage)
        self.perpage = perpage or 10
        pcache       = cache.get(self.master)
        if pcache is None:
            self._create(datasrc())
        else:
            self.count    = pcache['count']
            self.numpages = pcache['numpages']

    #------------------------------------------------------------------------//
    def _create(self, items):
        self.numpages = 0
        self.count    = len(items)
        if None in (self.count, self.perpage):
            #import pdb; pdb.set_trace()
            import traceback; logging.error(traceback.format_exc())
            raise RuntimeError("BUG")

        for beg, end in rangeiter(self.count, self.perpage):
            self.numpages += 1
            pgkey = self._pagekey(self.numpages)
            batch = items[beg:end]
            logging.info("CREATING PAGE '{0}' -> {1}:{2} {3}\n  -{4}".format(
                pgkey, beg, end, len(batch),
                "\n  -".join(str(i.pk) for i in batch)
            ))
            cache.set(pgkey, batch)
            batch2 = cache.get(pgkey)
            logging.info("  CHECKING {0}\n    -{1}".format(
                len(batch2), "\n    -".join(str(i.pk) for i in batch2)
            ))

        logging.info("CREATING PAGE CACHE {}".format(self.master))
        logging.info("  count:      {}".format(self.count))
        logging.info("  numpages:   {}".format(self.numpages))
        cache.set(self.master, {
            'count':    self.count,
            'numpages': self.numpages,
        })

    #------------------------------------------------------------------------//
    def _pagekey(self, page):
        return '{master}-{page}'.format(master=self.master, page=page)

    #------------------------------------------------------------------------//
    def clear(self):
        """ Clear page cache. """
        for pgnum in range(1, self.numpages+1):
            pgkey  = self._pagekey(pgnum)
            cache.delete(pgkey)
        cache.delete(self.master)

    #------------------------------------------------------------------------//
    def getoffset(self, offset):
        page = int((offset / self.perpage) + 1)
        return self.getpage(page)

    #------------------------------------------------------------------------//
    def getpage(self, page):
        """ Get items for the given page

        :arg key:       Key as a string. Same key as in ``pagecache.create()``.
        :arg page:      Page number as integer.
        """
        pgkey = self._pagekey(page)
        logging.info("GETTING PAGE '{}'".format(pgkey))
        pgdata = cache.get(pgkey)
        if pgdata is not None:
            logging.info("\n  -{0}".format(
                         "\n  -".join(str(i.pk) for i in pgdata)))
        return pgdata or []
