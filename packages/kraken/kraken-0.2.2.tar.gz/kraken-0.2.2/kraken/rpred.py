from __future__ import absolute_import, division

import cPickle
import gzip
import bz2
import sys
import numpy as np
import kraken.lib.lstm
import kraken.lib.lineest

from kraken.lib import lstm
from kraken.lib.util import pil2array, array2pil
from kraken.lib.lineest import CenterNormalizer
from kraken.lib.exceptions import KrakenRecordException, KrakenInvalidModelException


class ocr_record(object):
    """
    A record object containing the recognition result of a single line
    """
    def __init__(self, prediction, cuts, confidences):
        self.prediction = prediction
        self.cuts = cuts
        self.confidences = confidences

    def __len__(self):
        return len(self.prediction)

    def __str__(self):
        return self.prediction

    def __iter__(self):
        self.idx = -1
        return self

    def next(self):
        if self.idx < len(self):
            self.idx += 1
            return (self.prediction[self.idx], self.cuts[self.idx],
                    self.confidences[self.idx])
        else:
            raise StopIteration

    def __getitem__(self, key):
        if isinstance(key, slice):
            return [self[i] for i in range(*key.indices(len(self)))]
        elif isinstance(key, int):
            if key < 0:
                key += len(self)
            if key >= len(self):
                raise IndexError('Index (%d) is out of range' % key)
            return (self.prediction[key], self.cuts[key],
                    self.confidences[key])
        else:
            raise TypeError('Invalid argument type')


def load_rnn(fname):
    """
    Loads a pickled lstm rnn.

    Args:
        fname (unicode): Path to the pickle object

    Returns:
        Unpickled object

    Raises:

    """

    def find_global(mname, cname):
        aliases = {
            'lstm.lstm': kraken.lib.lstm,
            'ocrolib.lstm': kraken.lib.lstm,
            'ocrolib.lineest': kraken.lib.lineest,
        }
        if mname in aliases:
            return getattr(aliases[mname], cname)
        return getattr(sys.modules[mname], cname)

    of = open
    if fname.endswith(u'.gz'):
        of = gzip.open
    elif fname.endswith(u'.bz2'):
        of = bz2.BZ2File
    with of(fname, 'rb') as fp:
        unpickler = cPickle.Unpickler(fp)
        unpickler.find_global = find_global
        try: 
            rnn =  unpickler.load()
        except cPickle.UnpicklingError as e:
            raise KrakenInvalidModelException(e.message)
        if not isinstance(rnn, kraken.lib.lstm.SeqRecognizer):
            raise KrakenInvalidModelException('Pickle is %s instead of '
                                              'SeqRecognizer' %
                                              type(rnn).__name__)
        return rnn

def extract_boxes(im, bounds):
    """
    Yields the subimages of image im defined in the list of bounding boxes in
    bounds preserving order.

    Args:
        im (PIL.Image): Input image
        bounds (list): A list of tuples (x1, y1, x2, y2)

    Yields:
        (PIL.Image) the extracted subimage
    """
    for box in bounds:
        yield im.crop(box), box


def dewarp(normalizer, im):
    """
    Dewarps an image of a line using a kraken.lib.lineest.CenterNormalizer
    instance.

    Args:
        normalizer (kraken.lib.lineest.CenterNormalizer): A line normalizer
                                                          instance
        im (PIL.Image): Image to dewarp

    Returns:
        PIL.Image containing the dewarped image.
    """
    line = pil2array(im)
    temp = np.amax(line)-line
    temp = temp*1.0/np.amax(temp)
    normalizer.measure(temp)
    line = normalizer.normalize(line, cval=np.amax(line))
    return array2pil(line)


def rpred(network, im, bounds, pad=16, line_normalization=True):
    """
    Uses a RNN to recognize text

    Args:
        network (kraken.lib.lstm.SegRecognizer): A SegRecognizer object
        im (PIL.Image): Image to extract text from
        bounds (iterable): An iterable returning a tuple defining the absolute
                           coordinates (x0, y0, x1, y1) of a text line in the
                           Image.
        pad (int): Extra blank padding to the left and right of text line
        line_normalization (bool): Dewarp line using the line estimator
                                   contained in the network. If no normalizer
                                   is available one using the default
                                   parameters is created. If a custom line
                                   dewarping is desired set to false and dewarp
                                   manually using the dewarp function.

    Yields:
        A tuple containing the recognized text (0), absolute character
        positions in the image (1), and confidence values for each
        character(2).
    """

    lnorm = getattr(network, 'lnorm', CenterNormalizer())

    for box, coords in extract_boxes(im, bounds):
        if dewarp:
            box = dewarp(lnorm, box)
        line = pil2array(box)
        raw_line = line.copy()
        line = lstm.prepare_line(line, pad)
        pred = network.predictString(line)

        # calculate recognized LSTM locations of characters
        scale = len(raw_line.T)/(len(network.outputs)-2 * pad)
        result = lstm.translate_back(network.outputs, pos=1)
        pos = [(coords[0], coords[1], coords[0], coords[3])]
        conf = []
        for r, c in result:
            pos.append((pos[-1][2], coords[1],
                        coords[0] + int((r-pad) * scale),
                        coords[3]))
            conf.append(network.outputs[r, c])
        yield ocr_record(pred, pos[1:], conf)
