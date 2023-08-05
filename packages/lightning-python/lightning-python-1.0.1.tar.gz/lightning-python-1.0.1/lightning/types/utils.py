from numpy import asarray, array, ndarray, vstack, newaxis, nonzero, concatenate, transpose, atleast_2d, size, isscalar


def add_property(d, prop, name):

    if prop is not None:
        p = check_property(prop, name)
        d[name] = p

    return d


def check_property(prop, name):
    """
    Check and parse a property with either a specific checking function
    or a generic parser
    """

    checkers = {
        'color': check_color,
        'alpha': check_alpha,
        'size': check_size,
        'index': check_index,
    }

    if name in checkers:
        return checkers[name](prop)
    elif isinstance(prop, list) or isinstance(prop, ndarray) or isscalar(prop):
        return check_1d(prop, name)
    else:
        return prop


def check_color(c):
    """
    Check and parse color specs as either a single [r,g,b] or a list of
    [[r,g,b],[r,g,b]...]
    """

    c = asarray(c)
    if c.ndim == 1:
        c = c.flatten()
        c = c[newaxis, :]
        if c.shape[1] != 3:
            raise Exception("Color must have three values per point")
    elif c.ndim == 2:
        if c.shape[1] != 3:
            raise Exception("Color array must have three values per point")
    return c


def check_colormap(cmap):
    """
    Check if cmap is one of the colorbrewer maps
    """
    names = {'BrBG', 'PiYG', 'PRGn', 'PuOr', 'RdBu', 'RdGy', 'RdYlBu', 'RdYlGn', 'Spectral', 'Blues', 'BuGn', 'BuPu',
             'GnBu', 'Greens', 'Greys', 'Oranges', 'OrRd', 'PuBu', 'PuBuGn', 'PuRd', 'Purples', 'RdPu', 'Reds',
             'YlGn', 'YlGnBu', 'YlOrBr', 'YlOrRd', 'Accent', 'Dark2',
             'Paired', 'Pastel1', 'Pastel2', 'Set1', 'Set2', 'Set3'}
    if cmap not in names:
        raise Exception("Invalid cmap '%s',  must be one of %s" % (cmap, names))


def check_size(s):
    """
    Check and parse size specs as either a single [s] or a list of [s,s,s,...]
    """

    s = check_1d(s, "size")
    if any(map(lambda d: d <= 0, s)):
        raise Exception('Size cannot be 0 or negative')

    return s


def check_index(i):
    """
    Checks and parses an index spec, must be a one-dimensional array [i0, i1, ...]
    """

    i = asarray(i)
    if (i.ndim > 1) or (size(i) < 1):
        raise Exception("Index must be one-dimensional and non-singleton")

    return i


def check_alpha(a):
    """
    Check and parse alpha specs as either a single [a] or a list of [a,a,a,...]
    """

    a = check_1d(a, "alpha")
    if any(map(lambda d: d <= 0, a)):
        raise Exception('Alpha cannot be 0 or negative')

    return a


def check_1d(x, name):
    """
    Check and parse a one-dimensional spec as either a single [x] or a list of [x,x,x...]
    """

    x = asarray(x)
    if size(x) == 1:
        x = asarray([x])
    if x.ndim == 2:
        raise Exception("Property: %s must be one-dimensional" % name)
    x = x.flatten()

    return x


def array_to_lines(data):

    data = asarray(data)

    return data


def vecs_to_points(x, y):
        
    x = asarray(x)
    y = asarray(y)

    if x.ndim > 1 or y.ndim > 1:
        raise Exception('x and y vectors must be one-dimensional')

    if size(x) != size(y):
        raise Exception('x and y vectors must be the same length')

    points = vstack([x, y]).T

    return points


def vecs_to_points_three(x, y, z):

    x = asarray(x)
    y = asarray(y)
    z = asarray(z)

    if x.ndim > 1 or y.ndim > 1 or z.ndim > 1:
        raise Exception('x, y, and z vectors must be one-dimensional')

    if (size(x) != size(y)) or (size(x) != size(z)) or (size(y) != size(z)):
        raise Exception('x, y, and z vectors must be the same length')

    points = vstack([x, y, z]).T

    return points

def mat_to_array(mat):

    mat = asarray(mat)

    if mat.ndim < 2:
        raise Exception('Matrix input must be two-dimensional')

    return mat


def mat_to_links(mat):

    # get nonzero entries as list with the source, target, and value as columns
    
    mat = asarray(mat)
    if mat.ndim < 2:
            raise Exception('Matrix input must be two-dimensional')

    inds = nonzero(mat)
    links = concatenate((transpose(nonzero(mat)), atleast_2d(mat[inds]).T), axis=1)

    return links


def array_to_im(im):

    from matplotlib.pyplot import imsave
    from matplotlib.pyplot import cm
    import io

    im = asarray(im)
    imfile = io.BytesIO()
    if im.ndim == 3:
        # if 3D, show as RGB
        imsave(imfile, im, format="png")
    else:
        # if 2D, show as grayscale
        imsave(imfile, im, format="png", cmap=cm.gray)

    if im.ndim > 3:
        raise Exception("Images must be 2 or 3 dimensions")

    return imfile.getvalue()


def list_to_regions(reg):

    if isinstance(reg, str):
        return [reg]

    if isinstance(reg, list):
        checktwo = all(map(lambda x: len(x) == 2, reg))
        checkthree = all(map(lambda x: len(x) == 3, reg))
        if not (checktwo or checkthree):
            raise Exception("All region names must be two letters (for US) or three letters (for world)")
        return reg