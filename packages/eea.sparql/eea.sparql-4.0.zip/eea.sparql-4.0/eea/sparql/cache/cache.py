""" Caching
"""
def cacheSparqlKey(method, self, *args, **kwargs):
    """ Generate unique cache id
    """
    return self.absolute_url(1)
