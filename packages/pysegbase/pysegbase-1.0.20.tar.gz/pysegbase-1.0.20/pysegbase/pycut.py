#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Organ segmentation

Example:

$ pycat -f head.mat -o brain.mat
"""

# import unittest
# from optparse import OptionParser
import argparse
import sys
import logging
logger = logging.getLogger(__name__)

from scipy.io import loadmat
import numpy as np

import pygco
# from pygco import cut_from_graph

import sklearn
import sklearn.mixture

# version comparison
from pkg_resources import parse_version
import scipy.ndimage


if parse_version(sklearn.__version__) > parse_version('0.10'):
    # new versions
    gmm__cvtype = 'covariance_type'
    gmm__cvtype_bad = 'cvtype'
    defaultmodelparams = {'type': 'gmmsame',
                          'params': {'covariance_type': 'full'},
                          'fv_type': 'intensity'
                          }
else:
    gmm__cvtype = 'cvtype'
    gmm__cvtype_bad = 'covariance_type'
    defaultmodelparams = {'type': 'gmmsame',
                          'params': {'cvtype': 'full'},
                          'fv_type': 'intensity'
                          }

methods = ['graphcut', 'multiscale_graphcut']


class Model:

    """ Model for image intensity. Last dimension represent feature vector.
    m = Model()
    m.train(cla, clb)
    X = numpy.random.random([2,3,4])
    # we have data 2x3 with fature vector with 4 fatures
    m.likelihood(X,0)

    modelparams['type']: type of model estimation. Gaussian mixture from EM
    algorithm is implemented as 'gmmsame'. Gaussian kernel density estimation
    is implemented as 'gaussian_kde'. General kernel estimation ('kernel')
    is from scipy version 0.14 and it is not tested.
    """

    def __init__(self, nObjects=2, modelparams={}):

        # fix change of cvtype and covariancetype
        # print modelparams
        if 'params' in modelparams.keys() and\
                gmm__cvtype_bad in modelparams['params']:
            value = modelparams['params'].pop(gmm__cvtype_bad)
            modelparams['params'][gmm__cvtype] = value

        self.mdl = {}
        self.modelparams = defaultmodelparams.copy()
        self.modelparams.update(modelparams)

    def trainFromImageAndSeeds(self, data, seeds, cl):
        """
        This Method allows computes feature vector and train model.

        :cl: scalar index number of class
        """
        logger.debug('cl: ' + str(cl))
        fv = self.createFV(data, seeds, cl)
        self.train(fv, cl)

    def createFV(self, data, seeds=None, cl=None):
        """
        Input data is 3d image
        """
        fv_type = self.modelparams['fv_type']
        logger.debug("fv_type " + fv_type)
        if fv_type == 'intensity':
            if seeds is not None:
                fv = data[seeds == cl]
                fv = fv.reshape(-1, 1)
            else:
                fv = data
                fv = fv.reshape(-1, 1)
            # print fv.shape
        elif fv_type == 'fv001':
            # intensity in pixel, gaussian blur intensity
            data2 = scipy.ndimage.filters.gaussian_filter(data, sigma=5)
            data2 = data2 - data
            if seeds is not None:

                fv1 = data[seeds == cl].reshape(-1, 1)
                fv2 = data2[seeds == cl].reshape(-1, 1)
            else:
                fv1 = data.reshape(-1, 1)
                fv2 = data2.reshape(-1, 1)
            fv = np.hstack((fv1, fv2))
            fv = fv.reshape(-1, 2)
            logger.debug(str(fv[:10, :]))

            # from PyQt4.QtCore import pyqtRemoveInputHook
            # pyqtRemoveInputHook()

            # print fv1.shape
            # print fv2.shape
            # print fv.shape

        else:
            logger.error("Unknown feature vector type: " +
                         self.modelparams['fv_type'])
        return fv

    def train(self, clx, cl):
        """ Train clas number cl with data clx.

        Use trainFromImageAndSeeds() function if you want to use 3D image data
        as an input.

        clx: data, 2d matrix
        cl: label, integer

        label: gmmsame, gaussian_kde, dpgmm, stored
        """

        logger.debug('clx ' + str(clx[:10, :]))
        logger.debug('clx type' + str(clx.dtype))
        # name = 'clx' + str(cl) + '.npy'
        # print name
        # np.save(name, clx)

        if self.modelparams['type'] == 'gmmsame':
            if len(clx.shape) == 1:
                logger.warning('reshaping in train will be removed. Use \
                                \ntrainFromImageAndSeeds() function')

                print 'Warning deprecated feature in train() function'
                #  je to jen jednorozměrný vektor, tak je potřeba to
                # převést na 2d matici
                clx = clx.reshape(-1, 1)
            gmmparams = self.modelparams['params']
            self.mdl[cl] = sklearn.mixture.GMM(**gmmparams)
            self.mdl[cl].fit(clx)

        elif self.modelparams['type'] == 'kernel':
            # Not working (probably) in old versions of scikits
            # from sklearn.neighbors.kde import KernelDensity
            from sklearn.neighbors import KernelDensity
            # kernelmodelparams = {'kernel': 'gaussian', 'bandwidth': 0.2}
            kernelmodelparams = self.modelparams['params']
            self.mdl[cl] = KernelDensity(**kernelmodelparams).fit(clx)
        elif self.modelparams['type'] == 'gaussian_kde':
            # print clx
            import scipy.stats
            # from PyQt4.QtCore import pyqtRemoveInputHook
            # pyqtRemoveInputHook()

            # gaussian_kde works only with floating point types
            self.mdl[cl] = scipy.stats.gaussian_kde(clx.astype(np.float))
        elif self.modelparams['type'] == 'dpgmm':
            # print 'clx.shape ', clx.shape
            # print 'cl ', cl
            gmmparams = self.modelparams['params']
            self.mdl[cl] = sklearn.mixture.DPGMM(**gmmparams)
# todo here is a hack
# dpgmm z nějakého důvodu nefunguje pro naše data
# vždy natrénuje jednu složku v blízkosti nuly
# patrně to bude mít něco společného s parametrem alpha
# přenásobí-li se to malým číslem, zázračně to chodí
            self.mdl[cl].fit(clx * 0.001)
        elif self.modelparams['type'] == 'stored':
            # Classifer is trained before segmentation and stored to pickle
            import pickle
            print "stored"
            mdl_file = self.modelparams['params']['mdl_file']

            self.mdl = pickle.load(open(mdl_file, "rb"))

        else:
            raise NameError("Unknown model type")

        # pdb.set_trace();
# TODO remove saving
        self.save('classif.p')

    def save(self, filename):
        """
        Save model to pickle file
        """
        import pickle
        pickle.dump(self.mdl, open(filename, "wb"))

    def likelihoodFromImage(self, data, cl):
        sha = data.shape

        likel = self.likelihood(self.createFV(data), cl)
        return likel.reshape(sha)

    def likelihood(self, x, cl):
        """
        X = numpy.random.random([2,3,4])
        # we have data 2x3 with fature vector with 4 fatures

        Use likelihoodFromImage() function for 3d image input
        m.likelihood(X,0)
        """

        # sha = x.shape
        # xr = x.reshape(-1, sha[-1])
        # outsha = sha[:-1]
        # from PyQt4.QtCore import pyqtRemoveInputHook
        # pyqtRemoveInputHook()
        if self.modelparams['type'] == 'gmmsame':

            px = self.mdl[cl].score(x)

# todo ošetřit více dimenzionální fv
            # px = px.reshape(outsha)
        elif self.modelparams['type'] == 'kernel':
            px = self.mdl[cl].score_samples(x)
        elif self.modelparams['type'] == 'gaussian_kde':
            # print x
            # np.log because it is likelihood
            # @TODO Zde je patrně problém s reshape
            # old
            # px = np.log(self.mdl[cl](x.reshape(-1)))
            # new
            px = np.log(self.mdl[cl](x))
            # px = px.reshape(outsha)
            # from PyQt4.QtCore import pyqtRemoveInputHook
            # pyqtRemoveInputHook()
        elif self.modelparams['type'] == 'dpgmm':
            # todo here is a hack
            # dpgmm z nějakého důvodu nefunguje pro naše data
            # vždy natrénuje jednu složku v blízkosti nuly
            # patrně to bude mít něco společného s parametrem alpha
            # přenásobí-li se to malým číslem, zázračně to chodí
            px = self.mdl[cl].score(x * 0.01)
        elif self.modelparams['type'] == 'stored':
            px = self.mdl[cl].score(x)
        return px


class ImageGraphCut:

    """
    Interactive Graph Cut.

    ImageGraphCut(data, zoom, modelparams)
    scale

    Example:

    igc = ImageGraphCut(data)
    igc.interactivity()
    igc.make_gc()
    igc.show_segmentation()

    """

    def __init__(self, img,
                 modelparams={},
                 segparams={},
                 voxelsize=None,
                 debug_images=False,
                 volume_unit='mm3'
                 ):
        logger.debug('modelparams: ' + str(modelparams) + ' segparams: ' +
                     str(segparams) + " voxelsize: " + str(voxelsize) +
                     " debug_images: " + str(debug_images))

# default values                              use_boundary_penalties
        # self.segparams = {'pairwiseAlpha':10, 'use_boundary_penalties':False}
        self.segparams = {
            'type': 'graphcut',
            'pairwise_alpha': 20,
            'use_boundary_penalties': False,
            'boundary_penalties_sigma': 200,
            'boundary_penalties_weight': 30,
            'return_only_object_with_seeds': False,
            'use_old_similarity': True  # New similarity not implemented @TODO
        }
        self.segparams.update(segparams)

        self.img = img
        self.tdata = {}
        self.segmentation = None
        self.imgshape = img.shape
        self.modelparams = defaultmodelparams.copy()
        self.modelparams.update(modelparams)
        # self.segparams = segparams
        self.seeds = np.zeros(self.img.shape, dtype=np.int8)
        self.debug_images = debug_images
        self.volume_unit = volume_unit

        self.voxelsize = voxelsize
        if voxelsize is not None:
            self.voxel_volume = np.prod(voxelsize)

        else:
            self.voxel_volume = None

        self.interactivity_counter = 0

    def interactivity_loop(self, pyed):
        # @TODO stálo by za to, přehodit tlačítka na myši. Levé má teď
        # jedničku, pravé dvojku. Pravým však zpravidla označujeme pozadí a tak
        # nám vyjde popředí jako nula a pozadí jako jednička.
        # Tím také dopadne jinak interaktivní a neinteraktivní varianta.
        # import sys
        # print "logger ", logging.getLogger().getEffectiveLevel()
        # from guppy import hpy
        # h = hpy()
        # print h.heap()
        # import pdb

        # logger.debug("obj gc   " + str(sys.getsizeof(self)))

        if self.segparams['method'] in ('graphcut'):

            self.set_seeds(pyed.getSeeds())
            # self.seeds = pyed.getSeeds()
            # self.voxels1 = pyed.getSeedsVal(1)
            # self.voxels2 = pyed.getSeedsVal(2)

            self.make_gc()

            pyed.setContours(1 - self.segmentation.astype(np.int8))

        elif self.segparams['method'] in ('multiscale_gc'):
            self.set_seeds(pyed.getSeeds())
            self.__multiscale_gc(pyed)
            pyed.setContours(1 - self.segmentation.astype(np.int8))
        else:
            logger.error('Unknown segmentation method')

        try:
            from lisa import audiosupport
            audiosupport.beep()
        except:
            print("cannot open audiosupport")

        self.interactivity_counter += 1
        logger.debug('interactivity counter: ' +
                     str(self.interactivity_counter))

    def __seed_zoom(self, seeds, zoom):
        """
        Smart zoom for sparse matrix. If there is resize to bigger resolution
        thin line of label could be lost. This function prefers labels larger
        then zero. If there is only one small voxel in larger volume with zeros
        it is selected.
        """
        # import scipy
        # loseeds=seeds
        labels = np.unique(seeds)
# remove first label - 0
        labels = np.delete(labels, 0)
# @TODO smart interpolation for seeds in one block
#        loseeds = scipy.ndimage.interpolation.zoom(
#            seeds, zoom, order=0)
        loshape = np.ceil(np.array(seeds.shape) * 1.0 / zoom)
        loseeds = np.zeros(loshape, dtype=np.int8)
        loseeds = loseeds.astype(np.int8)
        for label in labels:
            a, b, c = np.where(seeds == label)
            loa = np.round(a / zoom)
            lob = np.round(b / zoom)
            loc = np.round(c / zoom)
            # loseeds = np.zeros(loshape)

            loseeds[loa, lob, loc] = label

        # import py3DSeedEditor
        # ped = py3DSeedEditor.py3DSeedEditor(loseeds)
        # ped.show()

        return loseeds

    def __ms_npenalty_fcn(self, axis, mask, ms_zoom, orig_shape):
        """
        Neighboorhood penalty between small pixels should be smaller then in
        bigger tiles. This is the way how to set it.

        """
        # import scipy.ndimage.filters as scf

        ms_zoom = ms_zoom * 30
        # for axis in range(0,dim):
        # filtered = scf.prewitt(self.img, axis=axis)
        maskz = self.__zoom_to_shape(mask, orig_shape)
        maskz = 1 - maskz.astype(np.int8)
        maskz = (maskz * (ms_zoom - 1)) + 1
        return maskz

    def __multiscale_gc(self):  # , pyed):
        """
        In first step is performed normal GC.
        Second step construct finer grid on edges of segmentation from first
        step.
        """
        deb = False
        # import py3DSeedEditor as ped

        from PyQt4.QtCore import pyqtRemoveInputHook
        pyqtRemoveInputHook()
        import scipy
        import scipy.ndimage
        logger.debug('performing multiscale_gc')
# default parameters
        sparams = {
            'boundary_dilatation_distance': 2,
            'block_size': 6,
            'use_boundary_penalties': True,
            'boundary_penalties_weight': 1
        }

        sparams.update(self.segparams)
        self.segparams = sparams

# step 1:  low res GC
        hiseeds = self.seeds
        ms_zoom = 4  # 0.125 #self.segparams['scale']
        # loseeds = pyed.getSeeds()
        # logger.debug("msc " + str(np.unique(hiseeds)))
        loseeds = self.__seed_zoom(hiseeds, ms_zoom)

        area_weight = 1
        hard_constraints = True

        self.seeds = loseeds
        self.voxels1 = self.img[self.seeds == 1]
        self.voxels2 = self.img[self.seeds == 2]
        # self.voxels1 = pyed.getSeedsVal(1)
        # self.voxels2 = pyed.getSeedsVal(2)

        img_orig = self.img

        self.img = scipy.ndimage.interpolation.zoom(img_orig, 1.0 / ms_zoom,
                                                    order=0)

        self.make_gc()
        logger.debug(
            'segmentation - max: %d min: %d' % (
                np.max(self.segmentation),
                np.min(self.segmentation)
            )
        )

        seg = 1 - self.segmentation.astype(np.int8)
        # in seg is now stored low resolution segmentation
# step 2: discontinuity localization
        segl = scipy.ndimage.filters.laplace(seg, mode='constant')
        logger.debug(str(np.max(segl)))
        logger.debug(str(np.min(segl)))
        segl[segl != 0] = 1
        logger.debug(str(np.max(segl)))
        logger.debug(str(np.min(segl)))
        # scipy.ndimage.morphology.distance_transform_edt
        boundary_dilatation_distance = self.segparams[
            'boundary_dilatation_distance']
        seg = scipy.ndimage.morphology.binary_dilation(
            seg,
            np.ones([
                (boundary_dilatation_distance * 2) + 1,
                (boundary_dilatation_distance * 2) + 1,
                (boundary_dilatation_distance * 2) + 1
            ])
        )
        if deb:
            import sed3
            pd = sed3.sed3(seg)  # ), contour=seg)
            pd.show()
#        segzoom = scipy.ndimage.interpolation.zoom(seg.astype('float'), zoom,
#                                                order=0).astype('int8')
# @todo back resize
#        segshape = np.zeros(img_orig.shape, dtype='int8')
#        segshape[:segzoom.shape[0],
#                 :segzoom.shape[1],
#                 :segzoom.shape[2]] = segzoom
#        if self.debug_images:
#            pyed.img = segshape * 100
#            import py3DSeedEditor
#            ped = py3DSeedEditor.py3DSeedEditor(segshape)
#            ped.show()
# step 3: indexes of new dual graph
        msinds = self.__multiscale_indexes(seg, img_orig.shape, ms_zoom)
        logger.debug('multiscale inds ' + str(msinds.shape))
        # if deb:
        #     import sed3
        #     pd = sed3.sed3(msinds)  # ), contour=seg)
        #     pd.show()

        # intensity values for indexes
        # @TODO compute average values for low resolution
        ms_img = img_orig

        # @TODO __ms_create_nlinks , use __ordered_values_by_indexes
        # import pdb; pdb.set_trace() # BREAKPOINT
        # pyed.setContours(seg)

        # there is need to set correct weights between neighbooring pixels
        # this is not nice hack.
        # @TODO reorganise segparams and create_nlinks function
        self.img = img_orig  # not necessary
        orig_shape = img_orig.shape
        ms_npenalty_fcn = lambda x: self.__ms_npenalty_fcn(x, seg, ms_zoom,
                                                           orig_shape)

# here are not unique couples of nodes
        nlinks_not_unique = self.__create_nlinks(
            ms_img,
            msinds,
            boundary_penalties_fcn=ms_npenalty_fcn
        )

# get unique set
        nlinks = np.array(
            [list(x) for x in set(tuple(x) for x in nlinks_not_unique)]
        )

# tlinks - indexes, data_merge
        ms_values_lin = self.__ordered_values_by_indexes(img_orig, msinds)
        seeds = hiseeds
        # seeds = pyed.getSeeds()
        # if deb:
        #     import sed3
        #     se = sed3.sed3(seeds)
        #     se.show()
        ms_seeds_lin = self.__ordered_values_by_indexes(seeds, msinds)
        logger.debug("unique seeds " + str(np.unique(seeds)))
        logger.debug("unique seeds " + str(np.unique(ms_seeds_lin)))

        unariesalt = self.__create_tlinks(ms_values_lin,
                                          self.voxels1, self.voxels2,
                                          ms_seeds_lin,
                                          area_weight, hard_constraints)

# create potts pairwise
        # pairwiseAlpha = -10
        pairwise = -(np.eye(2) - 1)
        pairwise = (self.segparams['pairwise_alpha'] * pairwise
                    ).astype(np.int32)

        # print 'data shape ', img_orig.shape
        # print 'nlinks sh ', nlinks.shape
        # print 'tlinks sh ', unariesalt.shape

    # Same functionality is in self.seg_data()
        result_graph = pygco.cut_from_graph(
            nlinks,
            unariesalt.reshape(-1, 2),
            pairwise
        )

# probably not necessary
#        del nlinks
#        del unariesalt

        # print "unaries %.3g , %.3g" % (np.max(unariesalt),np.min(unariesalt))
        # @TODO get back original data
        # result_labeling = result_graph.reshape(data.shape)
        result_labeling = result_graph[msinds]
        # import py3DSeedEditor
        # ped = py3DSeedEditor.py3DSeedEditor(result_labeling)
        # ped.show()
        self.segmentation = result_labeling

    def __ordered_values_by_indexes(self, data, inds):
        """
        Return values (intensities) by indexes.

        Used for multiscale graph cut.
        data = [[0 1 1],
                [0 2 2],
                [0 2 2]]

        inds = [[0 1 2],
                [3 4 4],
                [5 4 4]]

        return: [0, 1, 1, 0, 2, 0]

        If the data are not consistent, it will take the maximal value

        """
        # get unique labels and their first indexes
        # lab, linds = np.unique(inds, return_index=True)
# compute values by indexes
        # values = data.reshape(-1)[linds]

# alternative slow implementation
# if there are different data on same index, it will take
# maximal value
        # lab = np.unique(inds)
        # values = [0]*len(lab)
        # for label in lab:
        #     values[label] = np.max(data[inds == label])
        #
        # values = np.asarray(values)

# yet another implementation
        values = [None] * (np.max(inds) + 1)

        linear_inds = inds.ravel()
        linear_data = data.ravel()
        for i in range(0, len(linear_inds)):
            # going over all data pixels

            if values[linear_inds[i]] is None:
                # this index is found for first
                values[linear_inds[i]] = linear_data[i]
            elif values[linear_inds[i]] < linear_data[i]:
                # here can be changed maximal or minimal value
                values[linear_inds[i]] = linear_data[i]

        values = np.asarray(values)

        return values

    def __relabel(self, data):
        """  Makes relabeling of data if there are unused values.  """
        palette, index = np.unique(data, return_inverse=True)
        data = index.reshape(data.shape)
# realy slow solution
#        unq = np.unique(data)
#        actual_label = 0
#        for lab in unq:
#            data[data == lab] = actual_label
#            actual_label += 1

        # one another solution probably slower
        # arr = data
# data = (np.digitize(arr.reshape(-1,),np.unique(arr))-1).reshape(arr.shape)

        return data

    def __multiscale_indexes(self, mask, orig_shape, zoom):
        """
        Function computes multiscale indexes of ndarray.

        mask: Says where is original resolution (0) and where is small
        resolution (1). Mask is in small resolution.

        orig_shape: Original shape of input data.
        zoom: Usually number greater then 1

        result = [[0 1 2],
                  [3 4 4],
                  [5 4 4]]
        """

        mask_orig = self.__zoom_to_shape(mask, orig_shape, dtype=np.int8)

        inds_small = np.arange(mask.size).reshape(mask.shape)
        inds_small_in_orig = self.__zoom_to_shape(inds_small,
                                                  orig_shape, dtype=np.int8)
        inds_orig = np.arange(np.prod(orig_shape)).reshape(orig_shape)

        # inds_orig = inds_orig * mask_orig
        inds_orig += np.max(inds_small_in_orig) + 1
        # print 'indexes'
        # import py3DSeedEditor as ped
        # import pdb; pdb.set_trace() # BREAKPOINT

#  '==' is not the same as 'is' for numpy.array
        inds_small_in_orig[mask_orig == True] = inds_orig[mask_orig == True]  # noqa
        inds = inds_small_in_orig
        # print np.max(inds)
        # print np.min(inds)
        inds = self.__relabel(inds)
        logger.debug("Maximal index after relabeling: " + str(np.max(inds)))
        logger.debug("Minimal index after relabeling: " + str(np.min(inds)))
        # inds_orig[mask_orig==True] = 0
        # inds_small_in_orig[mask_orig==False] = 0
# inds = (inds_orig + np.max(inds_small_in_orig) + 1) + inds_small_in_orig

        return inds

    def __merge_indexes_by_mask(self, mask, inds1, inds2):
        """
        Return array of indexes.

        inds1: Array with numbers starting from 0
        inds2: Array with numbers starting from 0
        mask: array of same size as inds1 and inds2 with 0 where should be
            inds1 and 1 where sould be inds2

        To values of inds2 is added maximal value of inds1.

        """
        inds1[mask == 1]

    def __zoom_to_shape(self, data, shape, dtype=None):
        """
        Zoom data to specific shape.
        """
        import scipy
        import scipy.ndimage
        zoomd = np.array(shape) / np.array(data.shape, dtype=np.double)
        datares = scipy.ndimage.interpolation.zoom(data, zoomd, order=0)

        if datares.shape != shape:
            logger.warning('Zoom with different output shape')
        dataout = np.zeros(shape, dtype=dtype)
        shpmin = np.minimum(dataout.shape, shape)

        dataout[:shpmin[0], :shpmin[1], :shpmin[2]] = datares[
            :shpmin[0], :shpmin[1], :shpmin[2]]
        return datares

    def interactivity(self, min_val=None, max_val=None, qt_app=None):
        """
        Interactive seed setting with 3d seed editor
        """
        from seed_editor_qt import QTSeedEditor
        from PyQt4.QtGui import QApplication
        if min_val is None:
            min_val = np.min(self.img)

        if max_val is None:
            max_val = np.max(self.img)

        window_c = ((max_val + min_val) / 2)  # .astype(np.int16)
        window_w = (max_val - min_val)  # .astype(np.int16)

        if qt_app is None:
            qt_app = QApplication(sys.argv)

        pyed = QTSeedEditor(self.img,
                            modeFun=self.interactivity_loop,
                            voxelSize=self.voxelsize,
                            seeds=self.seeds,
                            volume_unit=self.volume_unit
                            )

        pyed.changeC(window_c)
        pyed.changeW(window_w)

        qt_app.exec_()

    def set_seeds(self, seeds):
        """
        Function for manual seed setting. Sets variable seeds and prepares
        voxels for density model.
        """
        if self.img.shape != seeds.shape:
            raise Exception("Seeds must be same size as input image")

        self.seeds = seeds.astype('int8')
        self.voxels1 = self.img[self.seeds == 1]
        self.voxels2 = self.img[self.seeds == 2]

    def run(self):
        if self.segparams['method'] in ('graphcut', 'GC'):
            self.make_gc()
        elif self.segparams['method'] in ('multiscale_graphcut'):
            self.__multiscale_gc()
        else:
            logger.error('Unknown method: ' + self.segparams['method'])

    def make_gc(self):
        res_segm = self.set_data(self.img,
                                 self.voxels1, self.voxels2,
                                 seeds=self.seeds)

        if self.segparams['return_only_object_with_seeds']:
            try:
                # because of negative problem is as 1 segmented background and
                # as 0 is segmented foreground
                # import thresholding_functions
                # newData = thresholding_functions.getPriorityObjects(
                newData = getPriorityObjects(
                    (1 - res_segm),
                    nObj=-1,
                    seeds=(self.seeds == 1).nonzero(),
                    debug=False
                )
                res_segm = 1 - newData
            except:
                import traceback
                logger.warning('Cannot import thresholding_funcions')
                traceback.print_exc()

        self.segmentation = res_segm

    def set_hard_hard_constraints(self, tdata1, tdata2, seeds):
        tdata1[seeds == 2] = np.max(tdata1) + 1
        tdata2[seeds == 1] = np.max(tdata2) + 1
        tdata1[seeds == 1] = 0
        tdata2[seeds == 2] = 0

        return tdata1, tdata2

    def boundary_penalties_array(self, axis, sigma=None):

        import scipy.ndimage.filters as scf

        # for axis in range(0,dim):
        filtered = scf.prewitt(self.img, axis=axis)
        if sigma is None:
            sigma2 = np.var(self.img)
        else:
            sigma2 = sigma ** 2

        filtered = np.exp(-np.power(filtered, 2) / (256 * sigma2))

        # srovnán hodnot tak, aby to vycházelo mezi 0 a 100
        # cc = 10
        # filtered = ((filtered - 1)*cc) + 10
        logger.debug(
            'ax %.1g max %.3g min %.3g  avg %.3g' % (
                axis, np.max(filtered), np.min(filtered), np.mean(filtered))
        )
#
# @TODO Check why forumla with exp is not stable
# Oproti Boykov2001b tady nedělím dvojkou. Ta je tam jen proto,
# aby to slušně vycházelo, takže jsem si jí upravil
# Originální vzorec je
# Bpq = exp( - (Ip - Iq)^2 / (2 * \sigma^2) ) * 1 / dist(p,q)
#        filtered = (-np.power(filtered,2)/(16*sigma))
# Přičítám tu 256 což je empiricky zjištěná hodnota - aby to dobře vyšlo
# nedávám to do exponenciely, protože je to numericky nestabilní
# filtered = filtered + 255 # - np.min(filtered2) + 1e-30
# Ještě by tady měl a následovat exponenciela, ale s ní je to numericky
# nestabilní. Netuším proč.
# if dim >= 1:
# odecitame od sebe tentyz obrazek
# df0 = self.img[:-1,:] - self.img[]
# diffs.insert(0,
        return filtered

    def __similarity_for_tlinks_obj_bgr(self, data, voxels1, voxels2,
                                        seeds, otherfeatures=None):
        """
        Compute edge values for graph cut tlinks based on image intensity
        and texture.
        """

        # Dobře to fungovalo area_weight = 0.05 a cc = 6 a diference se
        # počítaly z :-1

        mdl = Model(modelparams=self.modelparams)
        mdl.trainFromImageAndSeeds(data, seeds, 1)
        mdl.trainFromImageAndSeeds(data, seeds, 2)
        # mdl.train(voxels1, 1)
        # mdl.train(voxels2, 2)
        # pdb.set_trace();
        # tdata = {}
# as we convert to int, we need to multipy to get sensible values

# There is a need to have small vaues for good fit
# R(obj) = -ln( Pr (Ip | O) )
# R(bck) = -ln( Pr (Ip | B) )
# Boykov2001b
# ln is computed in likelihood
        tdata1 = (-(mdl.likelihoodFromImage(data, 1))) * 10
        tdata2 = (-(mdl.likelihoodFromImage(data, 2))) * 10

        if self.debug_images:
            # Show model parameters
            logger.debug('tdata1 shape ' + str(tdata1.shape))
            try:
                import matplotlib.pyplot as plt
                fig = plt.figure()
                ax = fig.add_subplot(111)
                ax.imshow(tdata1[5, :, :])
                print 'max ', np.max(tdata1), 'min ', np.min(tdata1)

                fig = plt.figure()
                ax = fig.add_subplot(111)
                ax.imshow(tdata2[5, :, :])
                print 'max ', np.max(tdata2), 'min ', np.min(tdata2)

                fig = plt.figure()
                ax = fig.add_subplot(111)
                hstx = np.linspace(-1000, 1000, 400)
                ax.plot(hstx, np.exp(mdl.likelihoodFromImage(hstx, 1)))
                ax.plot(hstx, np.exp(mdl.likelihoodFromImage(hstx, 2)))

# histogram
                fig = plt.figure()
                plt.hist([voxels1, voxels2], 30)

                # plt.hist(voxels2)

                plt.show()
            except:
                logger.debug('problem with showing debug images')
        return tdata1, tdata2

    def __create_tlinks(self, data, voxels1, voxels2, seeds,
                        area_weight, hard_constraints):
        tdata1, tdata2 = self.__similarity_for_tlinks_obj_bgr(data, voxels1,
                                                              voxels2, seeds)

        logger.debug('tdata1 min %f , max %f' % (tdata1.min(), tdata1.max()))
        logger.debug('tdata2 min %f , max %f' % (tdata2.min(), tdata2.max()))
        if hard_constraints:
            # pdb.set_trace();
            if (type(seeds) == 'bool'):
                raise Exception(
                    'Seeds variable  not set',
                    'There is need set seed if you want use hard constraints')
            tdata1, tdata2 = self.set_hard_hard_constraints(tdata1,
                                                            tdata2,
                                                            seeds)

        unariesalt = (0 + (area_weight *
                           np.dstack([tdata1.reshape(-1, 1),
                                      tdata2.reshape(-1, 1)]).copy("C"))
                      ).astype(np.int32)

        return unariesalt

    def __create_nlinks(self, data, inds=None, boundary_penalties_fcn=None):
        """
        Compute nlinks grid from data shape information. For boundary penalties
        are data (intensities) values are used.

        ins: Default is None. Used for multiscale GC. This are indexes of
        multiscale pixels. Next example shows one superpixel witn index 2.
        inds = [
            [1 2 2],
            [3 2 2],
            [4 5 6]]

        boundary_penalties_fcn: is function with one argument - axis. It can
            it can be used for setting penalty weights between neighbooring
            pixels.

        """
# use the gerneral graph algorithm
# first, we construct the grid graph
        if inds is None:
            inds = np.arange(data.size).reshape(data.shape)
        if self.segparams['use_boundary_penalties']:
            # print 'use_boundary_penalties'
            logger.debug('use_boundary_penalties')
            bpw = self.segparams['boundary_penalties_weight']
            sigma = self.segparams['boundary_penalties_sigma']
# set boundary penalties function
# Default are penalties based on intensity differences
            if boundary_penalties_fcn is None:
                boundary_penalties_fcn = lambda ax: \
                    self.boundary_penalties_array(axis=ax, sigma=sigma)

            bpa = boundary_penalties_fcn(2)
            # id1=inds[:, :, :-1].ravel()
            edgx = np.c_[
                inds[:, :, :-1].ravel(),
                inds[:, :, 1:].ravel(),
                # cc * np.ones(id1.shape)]
                bpw * bpa[:, :, 1:].ravel()
            ]

            bpa = boundary_penalties_fcn(1)
            # id1 =inds[:, 1:, :].ravel()
            edgy = np.c_[
                inds[:, :-1, :].ravel(),
                inds[:, 1:, :].ravel(),
                # cc * np.ones(id1.shape)]
                bpw * bpa[:, 1:, :].ravel()
            ]

            bpa = boundary_penalties_fcn(0)
            # id1 = inds[1:, :, :].ravel()
            edgz = np.c_[
                inds[:-1, :, :].ravel(),
                inds[1:, :, :].ravel(),
                # cc * np.ones(id1.shape)]
                bpw * bpa[1:, :, :].ravel()
            ]
        else:

            edgx = np.c_[inds[:, :, :-1].ravel(), inds[:, :, 1:].ravel()]
            edgy = np.c_[inds[:, :-1, :].ravel(), inds[:, 1:, :].ravel()]
            edgz = np.c_[inds[:-1, :, :].ravel(), inds[1:, :, :].ravel()]

        # import pdb; pdb.set_trace()
        edges = np.vstack([edgx, edgy, edgz]).astype(np.int32)
# edges - seznam indexu hran, kteres spolu sousedi
        return edges

    def set_data(self, data, voxels1, voxels2,
                 seeds=False,
                 hard_constraints=True,
                 area_weight=1):
        """
        Setting of data.
        You need set seeds if you want use hard_constraints.
        """
        # from PyQt4.QtCore import pyqtRemoveInputHook
        # pyqtRemoveInputHook()
        # import pdb; pdb.set_trace() # BREAKPOINT

        unariesalt = self.__create_tlinks(data, voxels1, voxels2, seeds,
                                          area_weight, hard_constraints)
#  některém testu  organ semgmentation dosahují unaries -15. což je podiné
# stačí vyhodit print před if a je to vidět
        logger.debug("unaries %.3g , %.3g" % (
            np.max(unariesalt), np.min(unariesalt)))
# create potts pairwise
        # pairwiseAlpha = -10
        pairwise = -(np.eye(2) - 1)
        pairwise = (self.segparams['pairwise_alpha'] * pairwise
                    ).astype(np.int32)
        # pairwise = np.array([[0,30],[30,0]]).astype(np.int32)
        # print pairwise

        self.iparams = {}

        nlinks = self.__create_nlinks(data)

        # print 'data shape ', data.shape
        # print 'nlinks sh ', nlinks.shape
        # print 'tlinks sh ', unariesalt.shape
# edges - seznam indexu hran, kteres spolu sousedi

# we flatten the unaries
        # result_graph = cut_from_graph(nlinks, unaries.reshape(-1, 2),
        # pairwise)
        result_graph = pygco.cut_from_graph(
            nlinks,
            unariesalt.reshape(-1, 2),
            pairwise
        )

# probably not necessary
#        del nlinks
#        del unariesalt

        # print "unaries %.3g , %.3g" % (np.max(unariesalt),
        # np.min(unariesalt))
        result_labeling = result_graph.reshape(data.shape)

        return result_labeling


def getPriorityObjects(data, nObj=1, seeds=None, debug=False):
    """

    Vraceni N nejvetsich objektu.
        input:
            data - data, ve kterych chceme zachovat pouze nejvetsi objekty
            nObj - pocet nejvetsich objektu k vraceni
            seeds - dvourozmerne pole s umistenim pixelu, ktere chce uzivatel
                vratit (odpovidaji matici "data")

        returns:
            data s nejvetsimi objekty

    """

    # Oznaceni dat.
    # labels - oznacena data.
    # length - pocet rozdilnych oznaceni.
    dataLabels, length = scipy.ndimage.label(data)

    logger.info('Olabelovano oblasti: ' + str(length))

    if debug:
        logger.debug('data labels: ' + str(dataLabels))

    # Uzivatel si nevybral specificke objekty.
    if (seeds == None):

        logger.info('Vraceni bez seedu')
        logger.debug('Objekty: ' + str(nObj))

        # Zjisteni nejvetsich objektu.
        arrayLabelsSum, arrayLabels = areaIndexes(dataLabels, length)
        # Serazeni labelu podle velikosti oznacenych dat (prvku / ploch).
        arrayLabelsSum, arrayLabels = selectSort(arrayLabelsSum, arrayLabels)

        returning = None
        label = 0
        stop = nObj - 1

        # Budeme postupne prochazet arrayLabels a postupne pridavat jednu
        # oblast za druhou (od te nejvetsi - mimo nuloveho pozadi) dokud
        # nebudeme mit dany pocet objektu (nObj).
        while label <= stop:

            if label >= len(arrayLabels):
                break

            if arrayLabels[label] != 0:
                if returning == None:
                    # "Prvni" iterace
                    returning = data * (dataLabels == arrayLabels[label])
                else:
                    # Jakakoli dalsi iterace
                    returning = returning + data * \
                        (dataLabels == arrayLabels[label])
            else:
                # Musime prodlouzit hledany interval, protoze jsme narazili na
                # nulove pozadi.
                stop = stop + 1

            label = label + 1

            if debug:
                logger.debug(str(label - 1) + ': ' + str(returning))

        if returning == None:
            logger.info(
                'Zadna validni olabelovana data! (DEBUG: returning == None)')

        return returning

    # Uzivatel si vybral specificke objekty (seeds != None).
    else:

        logger.info('Vraceni se seedy')

        # Zalozeni pole pro ulozeni seedu
        arrSeed = []
        # Zjisteni poctu seedu.
        stop = seeds[0].size
        tmpSeed = 0
        dim = np.ndim(dataLabels)
        for index in range(0, stop):
            # Tady se ukladaji labely na mistech, ve kterych kliknul uzivatel.
            if dim == 3:
                # 3D data.
                tmpSeed = dataLabels[
                    seeds[0][index], seeds[1][index], seeds[2][index]]
            elif dim == 2:
                # 2D data.
                tmpSeed = dataLabels[seeds[0][index], seeds[1][index]]

            # Tady opet pocitam s tim, ze oznaceni nulou pripada cerne oblasti
            # (pozadi).
            if tmpSeed != 0:
                # Pokud se nejedna o pozadi (cernou oblast), tak se novy seed
                # ulozi do pole "arrSeed"
                arrSeed.append(tmpSeed)

        # Pokud existuji vhodne labely, vytvori se nova data k vraceni.
        # Pokud ne, vrati se "None" typ. { Deprecated: Pokud ne, vrati se cela
        # nafiltrovana data, ktera do funkce prisla (nedojde k vraceni
        # specifickych objektu). }
        if len(arrSeed) > 0:

            # Zbaveni se duplikatu.
            arrSeed = list(set(arrSeed))
            if debug:
                logger.debug('seed list:' + str(arrSeed))

            logger.info(
                'Ruznych prioritnich objektu k vraceni: ' +
                str(len(arrSeed))
            )

            # Vytvoreni vystupu - postupne pricitani dat prislunych specif.
            # labelu.
            returning = None
            for index in range(0, len(arrSeed)):

                if returning == None:
                    returning = data * (dataLabels == arrSeed[index])
                else:
                    returning = returning + data * \
                        (dataLabels == arrSeed[index])

                if debug:
                    logger.debug((str(index)) + ':' + str(returning))

            return returning

        else:

            logger.info(
                'Zadna validni data k vraceni - zadne prioritni objekty ' +
                'nenalezeny (DEBUG: function getPriorityObjects:' +
                str(len(arrSeed) == 0))
            return None
# class Tests(unittest.TestCase):
#     def setUp(self):
#         pass

#     def test_segmentation(self):
#         data_shp = [16,16,16]
#         data = generate_data(data_shp)
#         seeds = np.zeros(data_shp)
# setting background seeds
#         seeds[:,0,0] = 1
#         seeds[6,8:-5,2] = 2
# x[4:-4, 6:-2, 1:-6] = -1

#         igc = ImageGraphCut(data)
# igc.interactivity()
# instead of interacitivity just set seeeds
#         igc.noninteractivity(seeds)

# instead of showing just test results
# igc.show_segmentation()
#         segmentation = igc.segmentation
# Testin some pixels for result
#         self.assertTrue(segmentation[0, 0, -1] == 0)
#         self.assertTrue(segmentation[7, 9, 3] == 1)
#         self.assertTrue(np.sum(segmentation) > 10)
# pdb.set_trace()
# self.assertTrue(True)


# logger.debug(igc.segmentation.shape)

usage = '%prog [options]\n' + __doc__.rstrip()
help = {
    'in_file': 'input *.mat file with "data" field',
    'out_file': 'store the output matrix to the file',
    'debug': 'debug mode',
    'debug_interactivity': "turn on interactive debug mode",
    'test': 'run unit test',
}
# @profile


def main():
    logger = logging.getLogger()
    logger.setLevel(logging.WARNING)
    logging.basicConfig(format='%(message)s')
    ch = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(levelname)-5s [%(module)s:%(funcName)s:%(lineno)d] %(message)s"
    )
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # parser = OptionParser(description='Organ segmentation')

    parser = argparse.ArgumentParser(
        description=__doc__
    )
    parser.add_argument('-d', '--debug', action='store_true',
                        help=help['debug'])
    parser.add_argument('-di', '--debug-interactivity', action='store_true',
                        help=help['debug_interactivity'])
    parser.add_argument('-i', '--input-file', action='store',
                        default=None,
                        help=help['in_file'])
    parser.add_argument('-t', '--tests', action='store_true',
                        help=help['test'])
    parser.add_argument('-o', '--outputfile', action='store',
                        dest='out_filename', default='output.mat',
                        help=help['out_file'])
    # (options, args) = parser.parse_args()
    options = parser.parse_args()

    debug_images = False

    if options.debug:
        logger.setLevel(logging.DEBUG)
        # print DEBUG
        # DEBUG = True

    if options.debug_interactivity:
        debug_images = True

    # if options.tests:
    #     sys.argv[1:]=[]
    #     unittest.main()

    if options.input_file is None:
        raise IOError('No input data!')

    else:
        dataraw = loadmat(options.input_file,
                          variable_names=['data', 'voxelsize_mm'])
    # import pdb; pdb.set_trace() # BREAKPOINT

    logger.debug('\nvoxelsize_mm ' + dataraw['voxelsize_mm'].__str__())

    if sys.platform == 'win32':
        # hack, on windows is voxelsize read as 2D array like [[1, 0.5, 0.5]]
        dataraw['voxelsize_mm'] = dataraw['voxelsize_mm'][0]

    igc = ImageGraphCut(dataraw['data'], voxelsize=dataraw['voxelsize_mm'],
                        debug_images=debug_images  # noqa
                        # , modelparams={'type': 'gaussian_kde', 'params': []}
                        # , modelparams={'type':'kernel', 'params':[]}  #noqa not in  old scipy
                        # , modelparams={'type':'gmmsame', 'params':{'cvtype':'full', 'n_components':3}} # noqa 3 components
                        # , segparams={'type': 'multiscale_gc'}  # multisc gc
                        , segparams={'method': 'multiscale_graphcut'}  # multisc gc
                        # , modelparams={'fv_type': 'fv001'}
                        # , modelparams={'type': 'dpgmm', 'params': {'cvtype': 'full', 'n_components': 5, 'alpha': 10}}  # noqa 3 components
                        )
    igc.interactivity()

    logger.debug('igc interactivity countr: ' + str(igc.interactivity_counter))

    logger.debug(igc.segmentation.shape)

if __name__ == "__main__":
    main()
