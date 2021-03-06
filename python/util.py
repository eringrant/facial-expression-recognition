#from zca import ZCA
import scipy.io
from scipy import misc
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from sklearn.decomposition import PCA


"""
Given a set of labels and a file name,
produce an output file which we can submit
to the kaggle website.
"""
def write_results(labels, file):
    with open(file, 'w') as out:
        out.write("Id,Prediction\n")
        for i, l in enumerate(labels):
            out.write(','.join([str(i+1),str(l)])+"\n")
        if len(labels) < 1253:
            for i in range(len(labels), 1253):
                out.write(','.join([str(i+1),"0"])+"\n")

"""
Load in labeled images and labels, after having run
ZCA and PCA preprocessing on them, trained
from unlabeled images.
"""
def load_pca_proj(K=30):
    test_images, labels = load_labeled_training(flatten=True)
    train_images = load_unlabeled_training(flatten=True)
    test_images = standardize(test_images)
    train_images = standardize(train_images)
    pca = PCA(n_components=K).fit(train_images)
    proj_test = pca.transform(test_images)
    shuffle_in_unison(proj_test, labels)
    return proj_test, labels

def load_pca_test(K=30):
    test_images = load_public_test(flatten=True)
    train_images = load_unlabeled_training(flatten=True)
    test_images = standardize(test_images)
    train_images = standardize(train_images)
    pca = PCA(n_components=K).fit(train_images)
    proj_test = pca.transform(test_images)
    return proj_test

def load_pca_hidden(K=30):
    test_images = load_hidden_test(flatten=True)
    train_images = load_unlabeled_training(flatten=True)
    test_images = standardize(test_images)
    train_images = standardize(train_images)
    pca = PCA(n_components=K).fit(train_images)
    proj_test = pca.transform(test_images)
    return proj_test

def load_public_test(flatten=False):
    test = scipy.io.loadmat('../public_test_images.mat')
    images = np.array(test['public_test_images'], dtype='float32')
    # permute dimensions so that the number of instances is first
    x, y, n = images.shape
    images = np.transpose(images, [2, 0, 1])
    assert images.shape == (n, x, y)

    # flatten the pixel dimensions
    if flatten is True:
        n, x, y = images.shape
        images = images.reshape(images.shape[0], images.shape[1]*images.shape[2])
        assert images.shape == (n, x*y)

    return images

def load_hidden_test(flatten=False):
    test = scipy.io.loadmat('../hidden_test_images.mat')
    images = np.array(test['hidden_test_images'], dtype='float32')
    # permute dimensions so that the number of instances is first
    x, y, n = images.shape
    images = np.transpose(images, [2, 0, 1])
    assert images.shape == (n, x, y)

    # flatten the pixel dimensions
    if flatten is True:
        n, x, y = images.shape
        images = images.reshape(images.shape[0], images.shape[1]*images.shape[2])
        assert images.shape == (n, x*y)

    return images

def load_all_test(flatten=False):
    public = scipy.io.loadmat('../public_test_images.mat')
    hidden = scipy.io.loadmat('../hidden_test_images.mat')

    a = np.array(public['public_test_images'], dtype='float32')
    x, y, n = a.shape
    a = np.transpose(a, [2, 0, 1])
    assert a.shape == (n, x, y)

    b = np.array(hidden['hidden_test_images'], dtype='float32')
    x, y, n = b.shape
    b = np.transpose(b, [2, 0, 1])
    assert b.shape == (n, x, y)

    images = np.concatenate([a, b])

    # flatten the pixel dimensions
    if flatten is True:
        n, x, y = images.shape
        images = images.reshape(images.shape[0], images.shape[1]*images.shape[2])
        assert images.shape == (n, x*y)

    return images

def standardize(images):
    images = images.astype(float)
    mean = np.mean(images,axis=1)
    sd = np.sqrt(np.var(images, axis=1) + 1e-20)
    for i in range(images.shape[0]):
        for j in range(len(images[i])):
            images[i][j] -= mean[i]

    for i in range(images.shape[0]):
        for j in range(len(images[i])):
            images[i][j] /= sd[i]
    return images

def log_uniform(low, high):
    """
    Generates a number that's uniformly distributed in the log-space between
    `low` and `high`

    Parameters
    ----------
    low : float
    Lower bound of the randomly generated number
    high : float
    Upper bound of the randomly generated number

    Returns
    -------
    rval : float
    Random number uniformly distributed in the log-space specified by `low`
    and `high`
    """
    log_low = np.log(low)
    log_high = np.log(high)

    log_rval = np.random.uniform(log_low, log_high)
    rval = float(np.exp(log_rval))

    return rval

def load_labeled_training(flatten=False, zero_index=False):
    labeled = scipy.io.loadmat('../labeled_images.mat')
    labels = labeled['tr_labels']
    labels = np.asarray([l[0] for l in labels])
    #images = np.array(labeled['tr_images'], dtype='float32')
    images = np.array(labeled['tr_images'], dtype='int32')

    # permute dimensions so that the number of instances is first
    x, y, n = images.shape
    images = np.transpose(images, [2, 0, 1])
    assert images.shape == (n, x, y)

    # flatten the pixel dimensions
    if flatten is True:
        n, x, y = images.shape
        images = images.reshape(images.shape[0], images.shape[1]*images.shape[2])
        assert images.shape == (n, x*y)

    if zero_index:
        labels -= 1

    return images, labels

def load_unlabeled_training(flatten=False):
    unlabeled = scipy.io.loadmat('../unlabeled_images.mat')
    images = np.array(unlabeled['unlabeled_images'], dtype='float32')

    # permute dimensions so that the number of instances is first
    x, y, n = images.shape
    images = np.transpose(images, [2, 0, 1])
    assert images.shape == (n, x, y)

    # flatten the pixel dimensions
    if flatten is True:
        n, x, y = images.shape
        images = images.reshape(images.shape[0], images.shape[1]*images.shape[2])
        assert images.shape == (n, x*y)

    return images

def shuffle_in_unison(a, b):
    """Shuffle two arrays in unison, so that previously aligned indices
    remain aligned. The arrays can be multidimensional; in any
    case, the first dimension is shuffled.
    """
    assert len(a) == len(b)
    rng_state = np.random.get_state()
    np.random.shuffle(a)
    np.random.set_state(rng_state)
    np.random.shuffle(b)

"""The following function is adapted from A3.
"""

def render_matrix(matrix, flattened=False, image_height=None,
        image_width=None, ncols=15, show=True):
    """Shows matrix as a set of images.
    Plots images in row-major order.
    """
    if matrix.shape[0] > 600:
        print('Too many images to render efficiently.')
        return
    nrows = matrix.shape[0]//ncols+1

    plt.clf()
    plt.figure(1)
    fig, axs = plt.subplots(nrows, ncols)
    axs = axs.ravel()

    if flattened is True:
        if image_height is None and image_width is None:
            image_height = int(np.sqrt(matrix.shape[1]))
            image_width = int(np.sqrt(matrix.shape[1]))
        for i in xrange(matrix.shape[0]):
            image = matrix[i, :]
            image = image.reshape(image_height, image_width)
            axs[i].imshow(image, cmap = plt.get_cmap('gray'),
                interpolation='none') # for no anti-aliasing
            axs[i].axis('off')
    else:
        for i in xrange(matrix.shape[0]):
            axs[i].imshow(matrix[i, :, :], cmap = cm.Greys_r,
                interpolation='none') # for no anti-aliasing
            axs[i].axis('off')

    # clear empty subplots
    for i in xrange(matrix.shape[0], nrows*ncols):
        fig.delaxes(axs[i])

    if show:
        plt.show()


"""The following two functions are from
http://deeplearning.net/tutorial/code/utils.py.
"""

def scale_to_unit_interval(ndar, eps=1e-20):
    """ Scales all values in the ndarray ndar to be between 0 and 1 """
    ndar = ndar.copy()
    ndar -= ndar.min()
    ndar *= 1.0 / (ndar.max() + eps)
    return ndar

def tile_raster_images(X, img_shape, tile_shape, tile_spacing=(0, 0),
                       scale_rows_to_unit_interval=True,
                       output_pixel_vals=True):
    """
    Transform an array with one flattened image per row, into an array in
    which images are reshaped and laid out like tiles on a floor.

    This function is useful for visualizing datasets whose rows are images,
    and also columns of matrices for transforming those rows
    (such as the first layer of a neural net).

    :type X: a 2-D ndarray or a tuple of 4 channels, elements of which can
    be 2-D ndarrays or None;
    :param X: a 2-D array in which every row is a flattened image.

    :type img_shape: tuple; (height, width)
    :param img_shape: the original shape of each image

    :type tile_shape: tuple; (rows, cols)
    :param tile_shape: the number of images to tile (rows, cols)

    :param output_pixel_vals: if output should be pixel values (i.e. int8
    values) or floats

    :param scale_rows_to_unit_interval: if the values need to be scaled before
    being plotted to [0,1] or not


    :returns: array suitable for viewing as an image.
    (See:`Image.fromarray`.)
    :rtype: a 2-d array with same dtype as X.

    """

    assert len(img_shape) == 2
    assert len(tile_shape) == 2
    assert len(tile_spacing) == 2

    # The expression below can be re-written in a more C style as
    # follows :
    #
    # out_shape    = [0,0]
    # out_shape[0] = (img_shape[0]+tile_spacing[0])*tile_shape[0] -
    #                tile_spacing[0]
    # out_shape[1] = (img_shape[1]+tile_spacing[1])*tile_shape[1] -
    #                tile_spacing[1]
    out_shape = [
        (ishp + tsp) * tshp - tsp
        for ishp, tshp, tsp in zip(img_shape, tile_shape, tile_spacing)
    ]

    if isinstance(X, tuple):
        assert len(X) == 4
        # Create an output numpy ndarray to store the image
        if output_pixel_vals:
            out_array = np.zeros((out_shape[0], out_shape[1], 4),
                                    dtype='uint8')
        else:
            out_array = np.zeros((out_shape[0], out_shape[1], 4),
                                    dtype=X.dtype)

        #colors default to 0, alpha defaults to 1 (opaque)
        if output_pixel_vals:
            channel_defaults = [0, 0, 0, 255]
        else:
            channel_defaults = [0., 0., 0., 1.]

        for i in xrange(4):
            if X[i] is None:
                # if channel is None, fill it with zeros of the correct
                # dtype
                dt = out_array.dtype
                if output_pixel_vals:
                    dt = 'uint8'
                out_array[:, :, i] = np.zeros(
                    out_shape,
                    dtype=dt
                ) + channel_defaults[i]
            else:
                # use a recurrent call to compute the channel and store it
                # in the output
                out_array[:, :, i] = tile_raster_images(
                    X[i], img_shape, tile_shape, tile_spacing,
                    scale_rows_to_unit_interval, output_pixel_vals)
        return out_array

    else:
        # if we are dealing with only one channel
        H, W = img_shape
        Hs, Ws = tile_spacing

        # generate a matrix to store the output
        dt = X.dtype
        if output_pixel_vals:
            dt = 'uint8'
        out_array = np.zeros(out_shape, dtype=dt)

        for tile_row in xrange(tile_shape[0]):
            for tile_col in xrange(tile_shape[1]):
                if tile_row * tile_shape[1] + tile_col < X.shape[0]:
                    this_x = X[tile_row * tile_shape[1] + tile_col]
                    if scale_rows_to_unit_interval:
                        # if we should scale values to be between 0 and 1
                        # do this by calling the `scale_to_unit_interval`
                        # function
                        this_img = scale_to_unit_interval(
                            this_x.reshape(img_shape))
                    else:
                        this_img = this_x.reshape(img_shape)
                    # add the slice to the corresponding position in the
                    # output array
                    c = 1
                    if output_pixel_vals:
                        c = 255
                    out_array[
                        tile_row * (H + Hs): tile_row * (H + Hs) + H,
                        tile_col * (W + Ws): tile_col * (W + Ws) + W
                    ] = this_img * c
        return out_array

def write_image(data, imshape, imgname, flat_type='rrggbb'):
    noimg_inrow = 15;
    noimg_incol = np.ceil(data.shape[0] / float(noimg_inrow)).astype('int32')
    space_bw_img = int(max(min(imshape[0], imshape[1]) * .1, 2))  # pixels
    # print 'Figure spacing = {0:d}'.format(space_bw_img)
    if len(imshape) == 2 or imshape[2] == 1:
        F = np.zeros((imshape[0] * noimg_incol + space_bw_img * (noimg_incol - 1), \
                      imshape[1] * noimg_inrow + space_bw_img * (noimg_inrow - 1))) + data.max() / 2
        imshape = imshape[0:2]
    else:
        F = np.zeros((imshape[0] * noimg_incol + space_bw_img * (noimg_incol - 1), \
                      imshape[1] * noimg_inrow + space_bw_img * (noimg_inrow - 1), imshape[2])) + data.max() / 2

    im_idx = 0
    for r in range(noimg_incol):
        for c in range(noimg_inrow):
            if im_idx < data.shape[0]:
                if len(imshape) == 2 or imshape[2] == 1:
                    im = data[im_idx].reshape(imshape)
                else:
                    if flat_type == 'rrggbb':
                        r_ch = data[im_idx][0:np.prod(imshape[0:2])].reshape(imshape[0:2])
                        g_ch = data[im_idx][np.prod(imshape[0:2]):2 * np.prod(imshape[0:2])].reshape(imshape[0:2])
                        b_ch = data[im_idx][2 * np.prod(imshape[0:2]):].reshape(imshape[0:2])
                    elif flat_type == 'rgbrgb':
                        r_ch = data[im_idx][0::3].reshape(imshape[0:2])
                        g_ch = data[im_idx][1::3].reshape(imshape[0:2])
                        b_ch = data[im_idx][2::3].reshape(imshape[0:2])
                    im = np.dstack((r_ch, g_ch, b_ch))

                F[r * (imshape[0] + space_bw_img):(r + 1) * (imshape[0]) + r * space_bw_img, \
                  c * (imshape[1] + space_bw_img):(c + 1) * (imshape[1]) + c * space_bw_img ] = im
                im_idx += 1

    misc.imsave(imgname, F)
    fig = plt.figure()
    plt.imshow(F, cmap=cm.Greys_r)
    fig.savefig(imgname)
    plt.close(fig)
    plt.close()

#if __name__ == '__main__':
    #data = load_labeled_training()
    #render_matrix(data[0][:100, : , :])
