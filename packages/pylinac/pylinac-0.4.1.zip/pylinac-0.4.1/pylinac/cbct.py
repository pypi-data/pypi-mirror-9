
"""The CBCT module automatically analyzes DICOM images of a CatPhan acquired when doing CBCT quality assurance. It can load a folder
the images are in and automatically correct for phantom setup by determining the yaw, pitch, and roll of the phantom.
It can analyze the HU regions and image scaling (CTP404), the high-contrast line pairs (CTP528) to calculate the modulation transfer function (MTF), and the HU
uniformity (CTP486) on the corresponding slice.

Currently only Varian (CatPhan 504) is supported, but Elekta (CatPhan 503) support is being worked on.
"""
from abc import ABCMeta, abstractproperty
from collections import OrderedDict
from functools import partial
import os
import os.path as osp
import shutil
import zipfile
import time
import math

import numpy as np
from scipy import ndimage
from scipy.misc import imresize
import dicom
import matplotlib.pyplot as plt

from pylinac.core.decorators import value_accept, lazyproperty, type_accept
from pylinac.core.image import Image
from pylinac.core.geometry import Point, Circle, sector_mask, Line
from pylinac.core.profile import CircleProfile, Profile
from pylinac.core.io import get_folder_UI


np.seterr(invalid='ignore')  # ignore warnings for invalid numpy operations. Used for np.where() operations on partially-NaN arrays.

known_manufacturers = {'Varian': 'Varian Medical Systems', 'Elekta': 'ELEKTA'}


class Algo_Data:
    """Data structure for retaining certain settings and information regarding the CBCT algorithm and image data.
        This class is populated during CBCT image loading. For internal use only.
    """
    threshold = -800  # threshold when converting to binary image
    HU_slice_num = 0
    UN_slice_num = 0
    SR_slice_num = 0
    LC_slice_num = 0

    def __init__(self, images, dicom_metadata):
        self.images = images
        self.dicom_metadata = dicom_metadata
        self.set_slice_nums()

    @lazyproperty
    def fov_ratio(self):
        """Field of View in mm / reference FOV (250mm)."""
        return self.dicom_metadata.DataCollectionDiameter / 250

    @lazyproperty
    def mm_per_pixel(self):
        """The millimeters per pixel of the DICOM images."""
        return self.dicom_metadata.PixelSpacing[0]

    @lazyproperty
    def manufacturer(self):
        """The linac manufacturer."""
        return self.dicom_metadata.Manufacturer

    def set_slice_nums(self):
        """Set the slice numbers for the slices of interest based on the manufacturer."""
        if self.manufacturer in known_manufacturers.values():
            if self.manufacturer == known_manufacturers['Varian']:
                self.HU_slice_num = 32
                self.UN_slice_num = 9
                self.SR_slice_num = 44
                self.LC_slice_num = 23
            else:
                raise NotImplementedError("Elekta not yet implemented")
        else:
            raise ValueError("Unknown Manufacturer")

    @lazyproperty
    def phantom_roll(self):
        """Lazy property returning the phantom roll in radians."""
        return self.calc_phantom_roll()

    def calc_phantom_roll(self):
        """Determine the roll of the phantom by calculating the angle of the two
        air bubbles on the HU slice. Delegation method."""
        # TODO: need more efficient way of doing this w/o creating HU slice
        HU = HU_Slice(self)
        return HU.determine_phantom_roll()

    @lazyproperty
    def expected_phantom_size(self):
        """Determine the expected size of the phantom in pixels."""
        phan_area = np.pi*100**2  # Area = pi*r^2
        return phan_area/self.mm_per_pixel**2


class ROI(metaclass=ABCMeta):
    """Abstract base class for CBCT regions of interest."""
    def __init__(self, name, slice_array):
        """
        Parameters
        ----------
        name : str
            Name of the ROI
        img_array : numpy.ndarray
            2D array the ROI is on.
        """
        self.name = name
        self.slice_array = slice_array


class ROI_Disk(Circle, ROI):
    """An base class representing a circular/disk Region of Interest on a CBCT slice."""
    def __init__(self, name, slice_array, angle, radius=None, dist_from_center=None):
        """
        Parameters
        ----------
        angle : int, float
            The angle of the ROI in degrees from the phantom center.

            .. warning::
                Be sure the enter the angle in degrees rather than radians!
        radius : int, float
            The radius of the ROI from the center of the phantom.
        dist_from_center : int, float
            The distance of the ROI from the phantom center.

        See Also
        --------
        ROI : Further parameter info
        """
        ROI.__init__(self, name, slice_array)
        Circle.__init__(self, radius=radius)
        self.angle = angle
        self.dist_from_center = dist_from_center

    @type_accept(phan_cent_point=Point)
    def set_center_via_phan_center(self, phan_cent_point):
        """Set the center of the ROI based on phantom center.

        When the ROI is constructed, oftentimes the phantom center has not yet
        been determined. Later on when it is, the ROI center must be set.

        Parameters
        ----------
        phan_cent_point : geometry.Point
            The phantom center Point.
        """
        y_shift = -np.sin(np.deg2rad(self.angle))*self.dist_from_center
        x_shift = np.cos(np.deg2rad(self.angle))*self.dist_from_center
        self.center = Point(phan_cent_point.x+x_shift, phan_cent_point.y+y_shift)

    def get_roi_mask(self, outside='NaN'):
        """Return a masked array of the ROI.

        Parameters
        ----------
        outside : {'NaN', 0}
            The value the elements of the mask are made of.
        """
        if math.isnan(float(outside)):
            outside = np.NaN

        # create mask
        mask = sector_mask(self.slice_array.shape, self.center, self.radius)
        # Apply mask to image
        masked_img = np.where(mask == True, self.slice_array, outside)
        return masked_img


class HU_ROI(ROI_Disk):
    """An HU ROI object. Represents a circular area measuring either HU sample (Air, Poly, ...) or uniformity (bottom, left, ...)."""
    def __init__(self, name, angle, nominal_value, slice_array=None, radius=None, dist_from_center=None, tolerance=None):
        """
        Parameters
        ----------
        nominal_value : int
            The nominal pixel value of the HU ROI.
        tolerance : int
            The tolerance the pixel value must be within to be considered passing.

        See Also
        --------
        ROI_Disk : Further parameter info
        """
        super().__init__(name, slice_array, angle, radius, dist_from_center)
        self.nominal_val = nominal_value
        self.tolerance = tolerance

    @value_accept(mode=('mean', 'median'))
    def get_pixel_value(self, mode='mean'):
        """Return the pixel value calculation within the ROI.

        Parameters
        ----------
        mode : {'mean', 'median'}
            The pixel value calculation mode.
        """
        masked_img = self.get_roi_mask()
        if mode == 'mean':
            pix_val = np.nanmean(masked_img)
        if mode == 'median':
            pix_val = np.nanmedian(masked_img)
        return pix_val

    @property
    def value_diff(self):
        """The difference in HU between measured and nominal."""
        return self.pixel_value - self.nominal_val

    @property
    def pixel_value(self):
        """The mean pixel value of the ROI."""
        return self.get_pixel_value()

    @property
    def passed(self):
        """Boolean specifying if ROI pixel value was within tolerance of the nominal value."""
        return self.value_diff <= self.tolerance

    def get_pass_fail_color(self, passed='blue', failed='red'):
        """Return one of two colors depending on if ROI passed.

        Parameters
        ----------
        passed : str
            Color to return if ROI passed.
        failed : str
            Color to return if ROI failed, i.e. was outside tolerance.

        Notes
        -----
        Colors must be valid colors according to matplotlib specs.
        """
        if self.passed:
            return passed
        else:
            return failed


class Slice(metaclass=ABCMeta):
    """Abstract base class for analyzing specific slices of a CBCT dicom set."""
    def __init__(self, algo_data):
        """
        Parameters
        ----------
        algo_data : Algo_Data
        """
        self.image = np.ndarray  # place-holder; should be overloaded by subclass
        self.ROIs = OrderedDict()
        self.algo_data = algo_data

    def add_ROI(self, *ROIs):
        """Register ROIs to the slice.

        The ROI is added to a dictionary using the ROI.name attr as the key, with the
        ROI itself as the value.

        Parameters
        ----------
        ROIs : iterable, ROI type
            An ROI, subclass of ROI, or iterable containing ROIs.

        See Also
        --------
        ROI
        """
        for roi in ROIs:
            if roi.name in self.ROIs.keys():
                print("ROI name {s} already instantiated. Skipping its registration.".format(roi.name))
                continue
            self.ROIs[roi.name] = roi

    def find_phan_center(self):
        """Determine the location of the center of the phantom."""
        SOI_bw = self.image.threshold(self.algo_data.threshold)  # convert slice to binary based on threshold
        SOI_bw = ndimage.binary_fill_holes(SOI_bw)  # fill in air pockets to make one solid ROI
        SOI_labeled, num_roi = ndimage.label(SOI_bw)  # identify the ROIs
        if num_roi < 1 or num_roi is None:
            raise ValueError("Unable to locate the CatPhan")
        roi_sizes, bin_edges = np.histogram(SOI_labeled, bins=num_roi+1)  # hist will give the size of each label
        idx = np.abs(roi_sizes - self.algo_data.expected_phantom_size).argmin()
        SOI_bw_clean = np.where(SOI_labeled == idx, 1, 0)  # remove all ROIs except the largest one (the CatPhan)
        center_pixel = ndimage.measurements.center_of_mass(SOI_bw_clean)  # returns (y,x)
        self.phan_center = Point(center_pixel[1], center_pixel[0])

        # Propagate the phantom center out to the ROIs (they initially don't have a center because it's relative
        # to the phantom center)
        for roi in self.ROIs.values():
            roi.set_center_via_phan_center(self.phan_center)

    @abstractproperty
    def scale_by_FOV(self):
        """Scale certain distances by the Field of View ratio.

        For Varian scans, there are two Field of View sizes, small (250mm) and
        large (450mm). Reference distance is small; if a large FOV scan is loaded,
        distances to the ROI, etc needs to be corrected for the wider FOV.
        """


class Base_HU_Slice(Slice, metaclass=ABCMeta):
    """Abstract base class for the HU and Uniformity Slices."""

    def get_ROI_vals(self):
        """Return a dict of the HU values of the HU ROIs."""
        return {key: val.pixel_value for key, val in self.ROIs.items()}

    def get_ROI_passing(self):
        """Return a dict of the pass/fails for the ROIs."""
        return {key: val.passed for key, val in self.ROIs.items()}

    @property
    def overall_passed(self):
        """Boolean specifying whether all the ROIs passed within tolerance."""
        if all(self.get_ROI_passing().values()):
            return True
        else:
            return False


class HU_Slice(Base_HU_Slice):
    """Class for analysis of the HU slice of the CBCT dicom data set."""
    dist2objs = 120  # radius in pixels to the centers of the HU objects
    object_radius = 9  # radius of the HU ROIs themselves
    tolerance = 40  # standard tolerance of HU
    air_bubble_size = 450  #


    def __init__(self, algo_data):
        super().__init__(algo_data)
        self.scale_by_FOV()
        self.image = Image(combine_surrounding_slices(self.algo_data.images, self.algo_data.HU_slice_num))

        HU_ROIp = partial(HU_ROI, slice_array=self.image.array, radius=self.object_radius, dist_from_center=self.dist2objs,
                          tolerance=self.tolerance)

        air = HU_ROIp('Air', 90, -1000)
        pmp = HU_ROIp('PMP', 120, -200)
        ldpe = HU_ROIp('LDPE', 180, -100)
        poly = HU_ROIp('Poly', -120, -35)
        acrylic = HU_ROIp('Acrylic', -60, 120)
        delrin = HU_ROIp('Delrin', 0, 340)
        teflon = HU_ROIp('Teflon', 60, 990)
        self.add_ROI(air, pmp, ldpe, poly, acrylic, delrin, teflon)

        super().find_phan_center()

    def scale_by_FOV(self):
        """Specially overloaded to account for air_bubble_size's *square* FOV relationship."""
        self.dist2objs /= self.algo_data.fov_ratio
        self.object_radius /= self.algo_data.fov_ratio
        self.air_bubble_size /= self.algo_data.fov_ratio**2

    def determine_phantom_roll(self):
        """Determine the "roll" of the phantom.

         This algorithm uses the two air bubbles in the HU slice and the resulting angle between them.
        """
        # convert slice to logical
        SOI = self.image.threshold(self.algo_data.threshold)
        # invert the SOI; this makes the Air == 1 and phantom == 0
        SOI.invert()
        # determine labels and number of rois of inverted SOI
        labels, no_roi = ndimage.measurements.label(SOI)
        # calculate ROI sizes of each label TODO: simplify the air bubble-finding
        roi_sizes = [ndimage.measurements.sum(SOI, labels, index=item) for item in range(1, no_roi + 1)]
        # extract air bubble ROIs (based on size threshold)
        bubble_thresh = self.air_bubble_size
        air_bubbles = [idx + 1 for idx, item in enumerate(roi_sizes) if
                       item < bubble_thresh * 1.5 and item > bubble_thresh / 1.5]
        # if the algo has worked correctly, it has found 2 and only 2 ROIs (the air bubbles)
        if len(air_bubbles) == 2:
            air_bubble_CofM = ndimage.measurements.center_of_mass(SOI, labels, air_bubbles)
            y_dist = air_bubble_CofM[0][0] - air_bubble_CofM[1][0]
            x_dist = air_bubble_CofM[0][1] - air_bubble_CofM[1][1]
            angle = np.arctan2(y_dist, x_dist)
            if angle < 0:
                roll = abs(angle) - np.pi/2
            else:
                roll = angle - np.pi/2
            phan_roll = roll
        else:
            phan_roll = 0
            print("Warning: CBCT phantom roll unable to be determined; assuming 0")

        return phan_roll


class UNIF_Slice(Base_HU_Slice):
    """Class for analysis of the Uniformity slice of the CBCT dicom data set."""
    dist2objs = 110
    obj_radius = 20
    tolerance = 40

    def __init__(self, algo_data):
        super().__init__(algo_data)
        self.scale_by_FOV()
        self.image = Image(combine_surrounding_slices(self.algo_data.images, self.algo_data.UN_slice_num))

        HU_ROIp = partial(HU_ROI, slice_array=self.image.array, tolerance=self.tolerance, radius=self.obj_radius,
                          dist_from_center=self.dist2objs)

        # center has distance of 0, thus doesn't use partial
        center = HU_ROI('Center', 0, 0, self.image.array, self.obj_radius, dist_from_center=0, tolerance=self.tolerance)
        right = HU_ROIp('Right', 0, 0)
        top = HU_ROIp('Top', -90, 0)
        left = HU_ROIp('Left', 180, 0)
        bottom = HU_ROIp('Bottom', 90, 0)
        self.add_ROI(center, right, top, left, bottom)

        super().find_phan_center()

    def scale_by_FOV(self):
        self.dist2objs /= self.algo_data.fov_ratio
        self.obj_radius /= self.algo_data.fov_ratio

class Locon_Slice(Slice):
    """Class for analysis of the low contrast slice of the CBCT dicom data set."""
    # TODO: work on this
    def __init__(self, algo_data):
        super().__init__(algo_data)
        self.image = Image(combine_surrounding_slices(self.algo_data.images, self.algo_data.LC_slice_num))

    def scale_by_FOV(self):
        pass

class SR_Circle_ROI(CircleProfile, ROI):
    def __init__(self, name, slice_array, radius):
        CircleProfile.__init__(self, radius=radius)
        ROI.__init__(self, name, slice_array)

    @type_accept(phan_cent_point=Point)
    def set_center_via_phan_center(self, phan_cent_point):
        """For the SR ROIs, the phantom center is also the SR ROI center."""
        self.center = Point(phan_cent_point.x, phan_cent_point.y)


class SR_Slice(Slice):
    """Class for analysis of the Spatial Resolution slice of the CBCT dicom data set.

    This slice is quite different from the other CBCT slices. Rather than having ROIs like
    the HU and UNIF slices, this one calculates the resolution using several CircleProfiles.
    It computes 5 profiles, each one pixel smaller than the other, averages them, and then
    computes the spatial resolution from that.
    """
    LP_freq = (0.2, 0.4, 0.6, 0.8, 1, 1.2)
    radius2profs = np.arange(95, 100)

    def __init__(self, algo_data):
        super().__init__(algo_data)
        self.scale_by_FOV()
        self.image = Image(combine_surrounding_slices(self.algo_data.images, self.algo_data.SR_slice_num, mode='max'))

        self.LP_MTF = {}  # holds lp:mtf data
        for idx, radius in enumerate(self.radius2profs):
            c = SR_Circle_ROI(idx, self.image.array, radius=radius)
            self.add_ROI(c)

        super().find_phan_center()

    def scale_by_FOV(self):
        """Special overloading."""
        self.radius2profs = np.arange(int(round(95/self.algo_data.fov_ratio)), int(round(100/self.algo_data.fov_ratio)))

    def calc_median_profile(self, roll_offset=0):
        """Calculate the median profile of the Line Pair region.

        Parameters
        ----------
        roll_offset : int, float
            The offset to apply to the start of the profile, in radians.
            E.g. if set to pi/2, profile extraction will begin at 12 o clock (90 degrees).

        Returns
        -------
        median profile : core.profile.Profile
            A 1D Profile of the Line Pair regions.
        """
        # extract the profile for each ROI (5 adjacent profiles)
        for roi in self.ROIs.values():
            roi.get_profile(self.image.array, size=2*np.pi*1000, start=np.pi+roll_offset)
        # average profiles together
        prof = np.zeros(len(roi.y_values))
        for idx, roi in enumerate(self.ROIs.values()):
            prof += roi.y_values
        prof /= len(self.ROIs)

        new_prof = Profile(prof)
        new_prof.filter(0.001)
        # new_prof.ground()
        return new_prof

    def _find_LP_peaks(self, profile):
        """Find the peaks along the line pair profile extracted.

        Because of the varying width of lead/no lead, 3 searches are done
        with varying widths of peak spacing. This is to ensure that only 1 peak is
        found for the larger LPs, but does not pass over the thinner LPs further down
        the profile.

        Parameters
        ----------
        profile : profile.Profile
            1-D profile of the Line Pairs (normally from what is returned by return_LP_profile).

        Returns
        -------
        max_vals : numpy.array
            Values of peaks found.
        max_idxs : numpy.array
            Indices of peaks found.
        """
        max_vals_1, max_idx_1 = profile.find_peaks(min_peak_distance=150, max_num_peaks=2, exclude_rt_edge=0.9)
        max_vals_2, max_idx_2 = profile.find_peaks(min_peak_distance=48, exclude_lt_edge=0.12, exclude_rt_edge=0.7)
        max_vals_3, max_idx_3 = profile.find_peaks(min_peak_distance=25, exclude_lt_edge=0.3, exclude_rt_edge=0.65)
        max_vals = np.concatenate((max_vals_1, max_vals_2, max_vals_3))
        max_idxs = np.concatenate((max_idx_1, max_idx_2, max_idx_3))
        if len(max_idxs) != 17:
            # TODO: add some robustness here
            raise ArithmeticError("Did not find the correct number of line pairs")
        return max_vals, max_idxs

    def _find_LP_valleys(self, profile, max_idxs):
        """Find the line pair valleys.

        This is done by passing the indices of the peaks.
        The valleys are searched only between these peaks.

        Parameters
        ----------
        profile : profile.Profile
            1-D profile of the Line Pairs (normally from what is returned by return_LP_profile).
        max_idxs : numpy.array
            1-D array containing the indices of peaks.

        Returns
        -------
        min_vals : numpy.array
            Values of valleys found.
        min_idxs : numpy.array
            Indices of valleys found.
        """
        idx2del = np.array((1, 4, 7, 11))
        min_vals = np.zeros(16)
        min_idxs = np.zeros(16)
        for idx in range(len(max_idxs) - 1):
            min_val, min_idx = profile.find_valleys(exclude_lt_edge=max_idxs[idx], exclude_rt_edge=len(profile.y_values) - max_idxs[idx+1], max_num_peaks=1)
            min_vals[idx] = min_val[0]
            min_idxs[idx] = min_idx[0]
        # now delete the valleys *in between* the LP regions
        min_vals = np.delete(min_vals, idx2del)
        min_idxs = np.delete(min_idxs, idx2del)
        return min_vals, min_idxs

    def _calc_MTF(self, max_vals, min_vals):
        """Calculate the Modulation Transfer Function of the Line-Pair profile.

        Maximum and minimum values are calculated by averaging the pixel
        values of the peaks/valleys found.

        Parameters
        ----------
        max_vals : numpy.ndarray
            An array of the maximum values of the SR profile.
        min_vals : numpy.ndarray
            An array of the minimum values of the SR profile.

        References
        ----------
        http://en.wikipedia.org/wiki/Transfer_function#Optics

        """
        num_peaks = np.array((0, 2, 3, 3, 4, 4, 4)).cumsum()
        num_valleys = np.array((0, 1, 2, 2, 3, 3, 3)).cumsum()
        for key, LP_pair in zip(self.LP_freq, range(len(num_peaks) - 1)):
            region_max = max_vals[num_peaks[LP_pair]:num_peaks[LP_pair + 1]].mean()
            region_min = min_vals[num_valleys[LP_pair]:num_valleys[LP_pair + 1]].mean()
            self.LP_MTF[key] = (region_max - region_min) / (region_max + region_min)
        # normalize the values by the first LP
        max_mtf = np.array(list(self.LP_MTF.values())).max()
        for name, value in self.LP_MTF.items():
            self.LP_MTF[name] /= max_mtf

    def calc_MTF(self):
        """Calculate the line pairs of the SR slice."""
        profile = self.calc_median_profile(roll_offset=self.algo_data.phantom_roll)
        max_vals, max_idxs = self._find_LP_peaks(profile)
        min_vals, min_idxs = self._find_LP_valleys(profile, max_idxs)
        self._calc_MTF(max_vals, min_vals)

    @value_accept(percent=(60, 95))
    def get_MTF(self, percent=80):
        """Return the MTF value at the percent passed in.

        Parameters
        ----------
        percent: int
            The line-pair/mm value for the given MTF percentage.
            E.g. 80 will return the MTF(80).

        Returns
        -------
        MTF_percent : float
            The Modulation Transfer Function ratio at the given percent.
        """
        # calculate x and y interpolations from Line Pair values and from the MTF measured
        x_vals_intrp = np.arange(self.LP_freq[0], self.LP_freq[-1], 0.01)
        x_vals = np.array(sorted(self.LP_MTF.keys()))
        y_vals = np.array(sorted(self.LP_MTF.values())[::-1])
        y_vals_intrp = np.interp(x_vals_intrp, x_vals, y_vals)
        # TODO: warn user if value at MTF edge; may not be true MTF
        mtf_percent = x_vals_intrp[np.argmin(np.abs(y_vals_intrp - (percent / 100)))]
        return mtf_percent


class GEO_ROI(ROI_Disk):
    """A circular ROI, much like the HU ROI, but with methods to find the center of the geometric "node"."""
    def __init__(self, name, slice_array, angle, radius, dist_from_center):
        super().__init__(name, slice_array, angle, radius, dist_from_center)
        self.node_CoM = None  # the node "Center-of-Mass"

    def _threshold_node(self):
        """Threshold the ROI to find node.

        Three of the four nodes have a positive value, while one node is air and
        thus has a low value. The algorithm thus thresholds for extreme values relative
        to the median value (which is the node).

        Returns
        -------
        bw_node : numpy.array
            A masked 2D array the size of the Slice image, where only the node pixels have a value.
        """
        # create mask
        masked_img = self.get_roi_mask()
        # threshold image
        upper_band_pass = np.where(masked_img > np.nanmedian(masked_img) * 1.4, 1, 0)
        lower_band_pass = np.where(masked_img < np.nanmedian(masked_img) * 0.6, 1, 0)
        bw_node = upper_band_pass + lower_band_pass
        return bw_node

    def find_node_center(self):
        """Find the center of the geometric node within the ROI."""
        bw_node = self._threshold_node()
        # label ROIs found
        labeled_arr, num_roi = ndimage.measurements.label(bw_node)
        roi_sizes, bin_edges = np.histogram(labeled_arr, bins=num_roi+1)  # hist will give the size of each label
        if len(roi_sizes) < 2:
            raise ValueError("Node not found")
        bw_node_cleaned = np.where(labeled_arr == np.argsort(roi_sizes)[-2], 1, 0)  # remove all ROIs except the second largest one (largest one is the air itself)
        labeled_arr, num_roi = ndimage.measurements.label(bw_node_cleaned)
        # TODO: come up with better test that it was detected.
        if num_roi != 1:
            raise ValueError("Did not find the geometric node.")
        # determine the center of mass of the geometric node
        node_CoM = ndimage.measurements.center_of_mass(bw_node_cleaned, labeled_arr)
        self.node_CoM = Point(node_CoM[1], node_CoM[0])  # the scipy com function returns (y, x), thus inversion


class GEO_Line(Line):
    """Represents a line connecting two nodes/ROIs on the Geometry Slice."""
    def __init__(self, name, geo_roi1, geo_roi2):
        """
        Parameters
        ----------
        name : str
            The name of the line, e.g. 'Top-Horizontal'.
        geo_roi1 : GEO_ROI
            One of two ROIs representing one end of the line.
        geo_roi2 : GEO_ROI
            The other ROI which is the other end of the line.
        """
        super().__init__()
        self.name = name
        self.roi1 = geo_roi1
        self.roi2 = geo_roi2

    @property
    def point1(self):
        return self.roi1.node_CoM

    @property
    def point2(self):
        return self.roi2.node_CoM

    def length_mm(self, mm_per_pixel):
        """Return the length of the line in mm."""
        return self.length*mm_per_pixel


class GEO_Slice(Slice):
    """Class for analysis of the Geometry slice of the CBCT dicom data set.

    The Geometry class is slightly more complex than the HU and Uniformity classes.
    Four ROIs are set, which correspond to the locations of the 1 air and 3 acrylic "nodes".
    Within these ROIs the center of the nodes must be found.

    Once the nodes centers are found four lines are constructed by linking the node centers,
    which should be 50mm apart.
    """
    line_nominal_value = 50
    dist2objs = 72
    obj_radius = 20
    tolerance = 1

    def __init__(self, algo_data):
        super().__init__(algo_data)
        self.scale_by_FOV()
        self.image = Image(combine_surrounding_slices(self.algo_data.images, self.algo_data.HU_slice_num, mode='median'))

        GEO_ROIp = partial(GEO_ROI, slice_array=self.image.array, radius=self.obj_radius,
                           dist_from_center=self.dist2objs)

        tl = GEO_ROIp(name='Top-Left', angle=-135)
        tr = GEO_ROIp(name='Top-Right', angle=-45)
        br = GEO_ROIp(name='Bottom-Right', angle=45)
        bl = GEO_ROIp(name='Bottom-Left', angle=135)
        self.add_ROI(tl, tr, br, bl)

        # Construct the Lines, mapping to the nodes they connect to
        lv = GEO_Line('Left-Vert', tl, bl)
        bh = GEO_Line('Bottom-Horiz', bl, br)
        rv = GEO_Line('Right-Vert', tr, br)
        th = GEO_Line('Top-Horiz', tl, tr)
        self.add_line(lv, bh, rv, th)

        super().find_phan_center()

    def scale_by_FOV(self):
        self.obj_radius /= self.algo_data.fov_ratio
        self.dist2objs /= self.algo_data.fov_ratio

    def add_line(self, *lines):
        """Add GEO_Lines; sister method of add_ROI of Slice class.

        Parameters
        ----------
        lines : GEO_Line, iterable containing GEO_Lines
            The lines to register with the Slice.
        """
        if not hasattr(self, 'lines'):
            self.lines = {}
        for line in lines:
            self.lines[line.name] = line

    def calc_node_centers(self):
        """Calculate the center-of-mass of all the geometric nodes."""
        for roi in self.ROIs.values():
            roi.find_node_center()

    def get_line_lengths(self):
        """Return the lengths of the lines in **mm**.

        Returns
        -------
        dict
            Lengths of the registered GEO_Lines, accounting for scaling.
        """
        return {line_key: line.length_mm(self.algo_data.mm_per_pixel) for line_key, line in self.lines.items()}

    @property
    def overall_passed(self):
        """Boolean property returning whether all the line lengths were within tolerance."""
        # all() would be nice, but didn't seem to work elegantly
        for length in self.get_line_lengths().values():
            if self.line_nominal_value + self.tolerance < length < self.line_nominal_value - self.tolerance:
                return False
        return True


class CBCT:
    """A class for loading and analyzing Cone-Beam CT DICOM files of a CatPhan 504 (Varian; Elekta 503 is being developed.
    Analyzes: Uniformity, Spatial Resolution, Image Scaling & HU Linearity.

    Attributes
    ----------
    algo_data : Algo_Data
    HU : HU_Slice
    UN : UNIF_Slice
    GEO : GEO_Slice
    LOCON: LOCON_Slice
    SR : SR_Slice

    Examples
    --------
    Run the demo:
        >>> mycbct = CBCT().run_demo()

    Typical session:
        >>> cbct_folder = r"C:/QA/CBCT/June"
        >>> mycbct = CBCT()
        >>> mycbct.load_folder(cbct_folder)
        >>> mycbct.analyze()
        >>> print(mycbct.return_results())
        >>> mycbct.plot_analyzed_image()
    """
    def __init__(self):
        self.algo_data = None
        self.HU = None
        self.UN = None
        self.GEO = None
        self.LOCON = None
        self.SR = None

    def load_demo_images(self, cleanup=True):
        """Load the CBCT demo images.

        Parameters
        ----------
        cleanup : bool
            If True (default), delete the extracted demo files.
            If False, leaves extracted files in the demo folder.
            Useful if using the demo images repeatedly.
        """
        cbct_demo_dir = osp.join(osp.dirname(osp.abspath(__file__)), 'demo_files', 'cbct')
        demo_zip = osp.join(cbct_demo_dir, 'High quality head.zip')
        demo_folder = osp.join(cbct_demo_dir, 'High quality head')

        # unpack demo folder if not already around
        if not osp.isdir(demo_folder) or len(os.listdir(demo_folder)) == 0:
            shutil.unpack_archive(demo_zip, cbct_demo_dir)

        filelist = self._get_CT_filenames_from_folder(demo_folder)
        self._load_files(filelist)
        # delete the unpacked demo folder
        if cleanup:
            try:
                shutil.rmtree(demo_folder)
                time.sleep(0.1)  # sleep timer added because fast repeats of loading/dumping caused errors
            except IOError:
                print("Extracted demo images were not able to be deleted. You can manually delete them if you "
                      "like from %s" % demo_folder)

    def load_folder_UI(self):
        """Load the CT DICOM files from a folder using a UI."""
        folder = get_folder_UI()
        if folder:
            self.load_folder(folder)

    def load_folder(self, folder):
        """Load the CT DICOM files string input.

        Parameters
        ----------
        folder : str
            Path to the folder.

        Raises
        ------
        NotADirectoryError : if folder str passed is not a valid directory.
        FileNotFoundError : If no CT images are found in the folder
        """
        # check that folder is valid
        if not osp.isdir(folder):
            raise NotADirectoryError("Path given was not a Directory/Folder")

        filelist = self._get_CT_filenames_from_folder(folder)
        self._load_files(filelist)

    def load_zip_file(self, zip_file):
        """Load a CBCT dataset from a zip file.

        Parameters
        ----------
        zip_file : str
            Path to the zip file.

        Raises
        ------
        FileExistsError : If zip_file passed was not a legitimate zip file.
        FileNotFoundError : If no CT images are found in the folder
        """
        zip_folder, _ = osp.splitext(zip_file)

        if not zipfile.is_zipfile(zip_file):
            raise FileExistsError("Path given was not a valid zip file")
        else:
            shutil.unpack_archive(zip_file, osp.dirname(zip_file))

            filelist = self._get_CT_filenames_from_folder(zip_folder)
            self._load_files(filelist)

        # delete the unpacked folder
        try:
            shutil.rmtree(zip_folder)
        except IOError:
            print("Extracted demo images were not able to be deleted. You can manually delete them if you "
                  "like from %s" % zip_folder)

    def _get_CT_filenames_from_folder(self, folder):
        """Walk through a folder to find DICOM CT images.

        Parameters
        ----------
        folder : str
            Path to the folder in question.

        Raises
        ------
        FileNotFoundError : If no CT images are found in the folder
        """
        for par_dir, sub_dir, files in os.walk(folder):
            filelist = [osp.join(par_dir, item) for item in files if item.endswith('.dcm') and item.startswith('CT')]
            if filelist:
                return filelist
        raise FileNotFoundError("CT images were not found in the specified folder.")

    def _load_files(self, file_list, im_size=512):
        """Load CT DICOM files given a list of image paths.

        Parameters
        ----------
        file_list : list
            List containing strings to the CT images.
        im_size : int
            Specifies the size of images the DICOM images should be resized to;
            used for simplicity of algorithm.
        """
        # initialize image array
        images = np.zeros([im_size, im_size, len(file_list)], dtype=int)

        im_order = np.zeros(len(file_list), dtype=int)
        # check that enough slices were loaded
        #TODO: select better method for determining if enough slices were chosen
        if len(file_list) < 20:
            raise ValueError("Not enough slices were selected. Select all the files or change the SR slice value.")

        # load dicom files from list names and get the image slice position
        # TODO: figure out more memory-efficient way to sort images; maybe based on number of slices and slice thickness
        for idx, item in enumerate(file_list):
            dcm = dicom.read_file(item)
            im_order[idx] = np.round(dcm.ImagePositionPatient[-1]/dcm.SliceThickness)
            # resize image if need be
            if dcm.pixel_array.shape != (im_size, im_size):
                image = imresize(dcm.pixel_array,(im_size, im_size))
            else:
                image = dcm.pixel_array
            # place image into images array
            images[:, :, idx] = image
        # shift order list from -xxx:+xxx to 0:2xxx
        im_order += np.round(abs(min(im_order)))
        # resort the images to be in the correct order
        sorted_images = self._sort_images(im_order, images)

        # determine settings needed for given CBCT.
        self._get_settings(file_list[0], sorted_images)
        # convert images from CT# to HU using dicom tags
        self._convert2HU()

    def _sort_images(self, im_order, images):
        """Sort and return the images according to the image order."""
        #TODO: convert this to some sort of in-place method
        sorted_images = np.zeros(images.shape, dtype=int)
        for idx, orig in enumerate(im_order):
            sorted_images[:, :, orig] = images[:, :, idx]
        return sorted_images

    def _get_settings(self, dicom_file_path, images):
        """Based on the images input, determine the starting conditions for the analysis.
        There are various manufacturers, protocols, and field-of-views for CBCTs.
        Based on this, the starting conditions can be determined.

        Parameters
        ----------
        dicom_file_path : str
            A dicom file path to grab metadata from.
        images : numpy.ndarray
            3D numpy array of the CT images.
        """
        dcm = dicom.read_file(dicom_file_path, stop_before_pixels=True)
        self.algo_data = Algo_Data(images, dcm)

    def _convert2HU(self):
        """Convert the images from CT# to HU."""
        self.algo_data.images *= self.algo_data.dicom_metadata.RescaleSlope
        self.algo_data.images += self.algo_data.dicom_metadata.RescaleIntercept

    def construct_HU(self):
        """Construct the Houndsfield Unit Slice and its ROIs."""
        self.HU = HU_Slice(self.algo_data)

    def construct_SR(self):
        """Construct the Spatial Resolution Slice and its ROIs so MTF can be calculated."""
        self.SR = SR_Slice(self.algo_data)
        self.SR.calc_MTF()

    def construct_GEO(self):
        """Construct the Geometry Slice and find the node centers."""
        self.GEO = GEO_Slice(self.algo_data)
        self.GEO.calc_node_centers()

    def construct_UNIF(self):
        """Construct the Uniformity Slice and its ROIs."""
        self.UN = UNIF_Slice(self.algo_data)

    def construct_Locon(self):
        """Construct the Low Contrast Slice."""
        self.LOCON = Locon_Slice(self.algo_data)

    def plot_analyzed_image(self, show=True):
        """Draw the ROIs and lines the calculations were done on or based on."""
        # create figure
        fig, ((UN_ax, HU_ax), (SR_ax, LOCON_ax)) = plt.subplots(2,2)

        # Uniformity objects
        UN_ax.imshow(self.UN.image.array)
        for roi in self.UN.ROIs.values():
            color = roi.get_pass_fail_color()
            roi.add_to_axes(UN_ax, edgecolor=color)
        UN_ax.autoscale(tight=True)
        UN_ax.set_title('Uniformity Slice')

        # HU objects
        HU_ax.imshow(self.HU.image.array)
        for roi in self.HU.ROIs.values():
            color = roi.get_pass_fail_color()
            roi.add_to_axes(HU_ax, edgecolor=color)
        HU_ax.autoscale(tight=True)
        HU_ax.set_title('HU & Geometric Slice')

        # GEO objects
        for line in self.GEO.lines.values():
            line.add_to_axes(HU_ax, color='blue')

        # SR objects
        SR_ax.imshow(self.SR.image.array)
        last_roi = len(self.SR.ROIs) - 1
        for roi in [self.SR.ROIs[0], self.SR.ROIs[last_roi]]:
            roi.add_to_axes(SR_ax, edgecolor='blue')
        SR_ax.autoscale(tight=True)
        SR_ax.set_title('Spatial Resolution Slice')

        # Locon objects
        LOCON_ax.imshow(self.LOCON.image.array)
        LOCON_ax.set_title('Low Contrast (In Development)')

        # show it all
        if show:
            plt.show()

    def return_results(self):
        """Return the results of the analysis as a string."""
        #TODO: make prettier
        string = ('\n - CBCT QA Test - \n'
                  'HU Regions: {}\n'
                  'HU Passed?: {}\n'
                  'Uniformity: {}\n'
                  'Uniformity Passed?: {}\n'
                  'MTF 80% (lp/mm): {}\n'
                  'Geometric distances: {}\n'
                  'Geometry Passed?: {}\n').format(self.HU.get_ROI_vals(), self.HU.overall_passed,
                                                   self.UN.get_ROI_vals(), self.UN.overall_passed, self.SR.get_MTF(80),
                                                   self.GEO.get_line_lengths(), self.GEO.overall_passed)
        return string

    def analyze(self):
        """Single-method full analysis of CBCT DICOM files."""
        if not self.images_loaded:
            raise AttributeError("Images not yet loaded")
        self.construct_HU()
        self.construct_UNIF()
        self.construct_GEO()
        self.construct_SR()
        self.construct_Locon()

    def run_demo(self, show=True):
        """Run the CBCT demo using high-quality head protocol images."""
        cbct = CBCT()
        cbct.load_demo_images()
        cbct.analyze()
        print(cbct.return_results())
        cbct.plot_analyzed_image(show)

    @property
    def images_loaded(self):
        """Boolean property specifying if the images have been loaded."""
        if self.algo_data is None:
            return False
        else:
            return True

@value_accept(mode=('mean','median','max'))
def combine_surrounding_slices(slice_array, nominal_slice_num, slices_plusminus=1, mode='mean'):
    """Return an array that is the combination of a given slice and a number of slices surrounding it.

    Parameters
    ----------
    im_array : numpy.array
        The original 3D numpy array of images.
    nominal_slice_num : int
        The slice of interest (along 3rd dim).
    slices_plusminus: int
        How many slices plus and minus to combine (also along 3rd dim).
    mode : {'mean', 'median', 'max}
        Specifies the method of combination.

    Returns
    -------
    comb_slice : numpy.array
        An array the same size in the first two dimensions of im_array, combined.
    """
    slices = slice_array[:,:,nominal_slice_num-slices_plusminus:nominal_slice_num+slices_plusminus]
    if mode == 'mean':
        comb_slice = np.mean(slices, 2)
    elif mode == 'median':
        comb_slice = np.median(slices, 2)
    else:
        comb_slice = np.max(slices, 2)
    return comb_slice


# ----------------------------------------
# CBCT Demo
# ----------------------------------------
if __name__ == '__main__':
    CBCT().run_demo()
    # zip_file = r"D:\Users\James\Dropbox\Programming\Python\Projects\PyCharm Projects\pylinac\tests\test_files\CBCT\Varian\Low dose thorax.zip"
    # cbct = CBCT()
    # cbct.load_zip_file(zip_file)
    # cbct.load_demo_images()
    # cbct.algo_data.images = np.roll(cbct.algo_data.images, 30, axis=1)
    # cbct.analyze()
    # print(cbct.return_results())
    # cbct.plot_analyzed_image()
