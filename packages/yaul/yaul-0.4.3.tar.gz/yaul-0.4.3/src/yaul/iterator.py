def iter_chunks(collection, chunksize):
    """
    iter_chunks(collection, chunksize) -> iterator
    
    Get an iterator that returns lists containing chunksize items,
    sequentially extracted from the given collection.
    """
    iterator = iter(collection)
    
    class OutOfInputException(Exception):
        pass
    
    def get_chunk():
        buffer = []
        counter = 0
        for value in iterator:
            buffer.append(value)
            counter += 1
            if counter >= chunksize:
                break
        if not counter:
            raise OutOfInputException()
        return buffer
    
    while True:
        try:
            yield get_chunk()
        except OutOfInputException:
            break

    