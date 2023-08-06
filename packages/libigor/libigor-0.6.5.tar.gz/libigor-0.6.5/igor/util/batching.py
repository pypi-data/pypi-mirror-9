# -*- coding: utf-8 -*-


#----------------------------------------------------------------------------//
def mkranges(size, batchSize):
    nBatches    = int(size / batchSize)
    batches     = [(i*batchSize, (i+1)*batchSize-1) for i in range(nBatches)]
    batches.append((nBatches * batchSize, size))
    return batches


#==============================================================================
def rangeiter(size, batchSize):
    nBatches    = int(size / batchSize)
    for i in range(nBatches):
        yield (i*batchSize, (i+1)*batchSize)
    yield (nBatches * batchSize, size)


#==============================================================================
def batchiter(size, batchSize):
    nBatches    = int(size / batchSize)
    for i in range(nBatches):
        yield (i*batchSize, batchSize)

    if size > nBatches * batchSize:
        yield (nBatches * batchSize, batchSize)


#----------------------------------------------------------------------------//
def range_from_batch(offset, limit, count = None):
    end     = None
    if limit is None:
        end = None
    else:
        end = offset + limit
        end = count if end > count else end

    return offset, end
