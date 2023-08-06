# -*- encoding:utf-8 -*-

import linecache
import os
import re

from PIL import Image
import images2gif
import matplotlib


# this line must be put between plab and matplotlib
matplotlib.use('Agg')

import numpy as np
import pylab as pl

# import common function module
import ddp.inc as inc


class PVTR:
    # colorbar clim amplification factor
    amp_factor = 1
    # vtr file name
    vtr_file = r'VTRoutput_1.vtr'
    # gif file name
    gif_file = r'efield.gif'
    # gif_duration
    gif_duration = 0.2
    # if true means use single clim value, otherwise use total clim value.
    clim_slice_flag = True
    # default slice flag
    slice_flag = 'x_slice'
    # default slice int item
    int_item = 0
    # show title or not
    title_flag = False
    # cord ratio
    cord_ratio = 1000

    def __init__(self, vtrfile=True):
        """
        construct of pvtr class. can be used to process efield data and shape data.
        if you set vtrfile VTRoutput_1.vtr as default it will process efiled
        if you set vtrfile output_1.vtr, then you will draw shape
        """
        self.vtr_path = inc.get_efield_path()
        self.path = inc.get_project_path()

        # if vtrfile is false, means vtr is shape file, otherwise is efield file
        if not vtrfile:
            PVTR.cord_ratio = 1
            self.vtr_path = inc.get_shape_path()

        # get intensity data
        self.intensity_size = PVTR.get_size(self.vtr_path)
        self.intensity, self.i_min, self.i_max = PVTR.get_intensity(self.vtr_path, self.intensity_size)

        # get cord data
        self.x_cord, self.y_cord, self.z_cord = PVTR.get_cord(self.vtr_path)
        self.x_min, self.y_min, self.z_min = min(self.x_cord), min(self.y_cord), min(self.z_cord)
        self.x_max, self.y_max, self.z_max = max(self.x_cord), max(self.y_cord), max(self.z_cord)

        # get size data
        self.x_size, self.y_size, self.z_size = PVTR.get_size(self.vtr_path)

        # get clim data
        self._clim_value = [self.i_min, self.i_max]

    @property
    def clim_value(self):
        """
        if you use sentence such as 'self.clim_value' then this function will be called.
        """ 
        if not PVTR.clim_slice_flag :
            return [PVTR.amp_factor * x for x in self._clim_value]

        if PVTR.clim_slice_flag:
            slice_info = self.get_item_info(PVTR.slice_flag, PVTR.int_item)
            return [np.min(slice_info['slice_intensity']),
                    np.max(slice_info['slice_intensity'])]

    @clim_value.setter
    def clim_value(self, new_clim):
        """
        if set clim value then this function will be called
        :param new_clim: type:list new clim value
        :return: null
        """
        self._clim_value = new_clim

    @staticmethod
    def get_size(file_path):
        """ get intensity array x cord , y cord , z cord size
        :param file_path: vtr file path
        :return:(int, int, int)
        """
        obj_str = linecache.getline(file_path,2)
        m = re.search(r'\d+\s+(\d+)\s+\d+\s+(\d+)\s+\d+\s+(\d+)', obj_str)
        return int(m.group(1)), int(m.group(2)), int(m.group(3))

    @staticmethod
    def get_intensity(file_path, array_size):
        """
        get format intensity array according file path and array size
        :param file_path: vtr file path
        :param array_size: reshape intensity array by array_size
        :return: (array, min, max)
        """
        intensity_line = linecache.getline(file_path,17)
        intensity_array = re.split(r'\s+',intensity_line)
        slice_data = map(lambda x:float(x), intensity_array[1:-1])
        slice_array = np.array(slice_data)
        # take care size array was flipped
        slice_array.shape = array_size[::-1]
        i_min, i_max = np.min(slice_array), np.max(slice_array)
        return slice_array, i_min, i_max

    @staticmethod
    def get_cord(file_path):
        """
        get cord according vtr file path
        :param file_path: file path where exits vtr file
        :return: (list, list, list)
        """
        x_line = linecache.getline(file_path,6)
        y_line = linecache.getline(file_path,9)
        z_line = linecache.getline(file_path,12)
        x_arr = re.split(r'\s+',x_line.lstrip().rstrip())
        y_arr = re.split(r'\s+',y_line.lstrip().rstrip())
        z_arr = re.split(r'\s+',z_line.lstrip().rstrip())
        x_data = [float(x)*PVTR.cord_ratio for x in x_arr]
        y_data = [float(y)*PVTR.cord_ratio for y in y_arr]
        z_data = [float(z)*PVTR.cord_ratio for z in z_arr]
        return x_data, y_data, z_data

    @staticmethod
    def clear_path(path):
        """
        files will be deleted totally under path
        :param path: path to be processed
        :return: null
        """
        if not os.path.exists(path):
            os.mkdir(path)
        else:
            file_list = os.listdir(path)
            for file in file_list:
                file_path = os.path.join(path,file)
                if os.path.isfile(file_path):
                    os.remove(file_path)

    @staticmethod
    def convert_to_gif(slice_path):
        """
        convert image files to gif file
        :param slice_path: path where have slice png files
        :return: null
        """
        # if a function don't need dynamic property then it can be static
        gif_path = os.path.join(slice_path, PVTR.gif_file)
        if os.path.exists(gif_path):
            os.remove(gif_path)
        file_list = os.listdir(slice_path)
        file_list.sort(key= lambda x:int(x[:-4]))
        images = [Image.open(os.path.join(slice_path, f)) for f in file_list if f.endswith('.png')]
        images2gif.writeGif(gif_path,images,duration=PVTR.gif_duration)

    @staticmethod
    def draw_scalar_field(file_path, int_header, size_order, size_array, multi_flag):
        """
        draw scalar field figure
        :param file_path: full path of csv file
        :param int_header: header line nums
        :param size_order: type:list which help decide x, y, intensity order
        :param size_array: type:tuple cord size of column x and column y
        :param multi_flag: if intensity need to multiply 100
        :return: null
        """
        f = open(file_path)
        for i in range(int_header):
            next(f)

        x, y, intensity = [], [], []

        for line in f:
            line_data = line.lstrip('\n').split(',')
            line_array = [float(i) for i in line_data ]
            if multi_flag:
                x.append(PVTR.cord_ratio*line_array[size_order[0]])
                y.append(PVTR.cord_ratio*line_array[size_order[1]])
            if not multi_flag:
                x.append(line_array[size_order[0]])
                y.append(line_array[size_order[1]])
            intensity.append(line_array[size_order[2]])

        x_min, y_min, i_min = min(x), min(y), min(intensity)
        x_max, y_max, i_max = max(x), max(y), max(intensity)

        x_array = np.array(x)
        y_array = np.array(y)
        intensity_array = np.array(intensity)
        x_array.shape, y_array.shape, intensity_array.shape = [size_array] * 3

        pl.pcolormesh(x_array, y_array, intensity_array, shading='gouraud')
        pl.xlim([x_min, x_max])
        pl.ylim([y_min, y_max])
        pl.clim([i_min, i_max])
        pl.xlabel('nm')
        pl.ylabel('nm')
        pl.colorbar()

        path = os.path.dirname(file_path)
        pl.savefig(os.path.join(path, 'efield.png'))
        return

    def get_slice_info(self, slice_flag):
        """
        get slice info without specific index
        :param slice_flag: decided which slice direction to be processed ['x_slice'|'y_slice'|'z_slice']
        :return: dict
        """
        """ get slice info without specific index
        :param slice_flag: decided which slice direction to be processed ['x_slice'|'y_slice'|'z_slice']
        :return: dict
        """
        slice_info = {}
        PVTR.slice_flag = slice_flag
        slice_info['slice_path'] = os.path.join(self.path, PVTR.slice_flag)
        if PVTR.slice_flag == 'x_slice':
            slice_info['cord'] = self.x_cord
            slice_info['label'] = ('y(nm)', 'z(nm)')
            slice_info['mesh_cord'] = np.meshgrid(self.y_cord, self.z_cord)
            slice_info['op_cord'] = (self.y_cord, self.z_cord)
            slice_info['lim'] = ([self.y_min, self.y_max], [self.z_min, self.z_max])
            slice_info['slice_num'] = self.x_size
            slice_info['fig_size'] = (self.y_size/self.z_size, self.y_size*6/self.z_size, 6) \
                if self.y_size > self.z_size else (self.z_size/self.y_size, 6, self.z_size*6/self.y_size)
            abs_sort_array = np.sort(np.abs(np.array(self.x_cord)))
            slice_info['origin_index'] = self.x_cord.index(abs_sort_array[0])
            slice_info['size_info'] = '%s,%d,%d\n'%('null',self.y_size,self.z_size)
        if PVTR.slice_flag == 'y_slice':
            slice_info['cord'] = self.y_cord
            slice_info['label'] = ('x(nm)', 'z(nm)')
            slice_info['mesh_cord'] = np.meshgrid(self.x_cord, self.z_cord)
            slice_info['op_cord'] = (self.x_cord, self.z_cord)
            slice_info['lim'] = ([self.x_min, self.x_max], [self.z_min, self.z_max])
            slice_info['slice_num'] = self.y_size
            slice_info['fig_size'] = (self.x_size/self.z_size, self.x_size*6/self.z_size, 6) \
                if self.x_size > self.z_size else (self.z_size/self.x_size, 6, self.z_size*6/self.x_size)
            abs_sort_array = np.sort(np.abs(np.array(self.y_cord)))
            slice_info['origin_index'] = self.y_cord.index(abs_sort_array[0])
            slice_info['size_info'] = '%s,%d,%d\n'%('null',self.x_size,self.z_size)
        if PVTR.slice_flag == 'z_slice':
            slice_info['cord'] = self.z_cord
            slice_info['label'] = ('x(nm)', 'y(nm)')
            slice_info['mesh_cord'] = np.meshgrid(self.x_cord, self.y_cord)
            slice_info['op_cord'] = (self.x_cord, self.y_cord)
            slice_info['lim'] = ([self.x_min, self.x_max], [self.y_min, self.y_max])
            slice_info['slice_num'] = self.z_size
            slice_info['fig_size'] = (self.x_size/self.y_size, self.x_size*6/self.y_size, 6) \
                if self.x_size > self.y_size else (self.y_size/self.x_size, 6, self.y_size*6/self.x_size)
            abs_sort_array = np.sort(np.abs(np.array(self.z_cord)))
            slice_info['origin_index'] = self.z_cord.index(abs_sort_array[0])
            slice_info['size_info'] = '%s,%d,%d\n'%('null',self.x_size,self.y_size)
        return slice_info
    
    def get_item_info(self, slice_flag, int_item):
        """
        get slice info with index
        :param slice_flag: decided which slice direction to be processed ['x_slice'|'y_slice'|'z_slice']
        :param int_item: index
        :return: dict
        """
        item_info = {}
        PVTR.slice_flag = slice_flag
        PVTR.int_item = int_item
        if PVTR.slice_flag == 'x_slice':
            item_info['slice_loc'] = self.x_cord[PVTR.int_item]
            slice_intensity = self.intensity[:, :, PVTR.int_item]
            slice_intensity_array = np.array(slice_intensity)
            item_info['slice_intensity'] = slice_intensity
            item_info['i_lim'] = [np.min(slice_intensity_array), np.max(slice_intensity_array)]
            item_info['title'] = 'slice of x direction index %d at %f' % (PVTR.int_item, self.x_cord[PVTR.int_item])
            item_info['process_msg'] = '> processing ' + str(PVTR.int_item+1) + ' totally ' + str(self.x_size)+' ...'
            item_info['size_info'] = '%s,%d,%d\n'%('null',self.y_size,self.z_size)
        if PVTR.slice_flag == 'y_slice':
            item_info['slice_loc'] = self.y_cord[PVTR.int_item]
            slice_intensity = self.intensity[:, PVTR.int_item, :]
            item_info['slice_intensity'] = slice_intensity
            slice_intensity_array = np.array(slice_intensity)
            item_info['i_lim'] = [np.min(slice_intensity_array), np.max(slice_intensity_array)]
            item_info['title'] = 'slice of y direction index %d at %f' % (PVTR.int_item, self.y_cord[PVTR.int_item])
            item_info['process_msg'] = '> processing ' + str(PVTR.int_item+1) + ' totally ' + str(self.y_size)+' ...'
            item_info['size_info'] = '%s,%d,%d\n'%('null',self.x_size,self.z_size)
        if PVTR.slice_flag == 'z_slice':
            item_info['slice_loc'] = self.z_cord[PVTR.int_item]
            slice_intensity = self.intensity[PVTR.int_item, :, :]
            slice_intensity_array = np.array(slice_intensity)
            item_info['slice_intensity'] = slice_intensity
            item_info['i_lim'] = [np.min(slice_intensity_array), np.max(slice_intensity_array)]
            item_info['title'] = 'slice of z direction index %d at %f' % (PVTR.int_item, self.z_cord[PVTR.int_item])
            item_info['process_msg'] = '> processing ' + str(PVTR.int_item+1) + ' totally ' + str(self.z_size)+' ...'
            item_info['size_info'] = '%s,%d,%d\n'%('null',self.x_size,self.y_size)
        return item_info

    def get_single_slice(self, slice_flag, int_item):
        """
        get one slice along slice direction according item and save as png file
        :param slice_flag: decided which slice direction to be processed ['x_slice'|'y_slice'|'z_slice']
        :param int_item: one number decided special slice to be processed
        :return: null
        """
        PVTR.slice_flag = slice_flag
        PVTR.int_item = int_item
        # get slice info and item info
        item_info = self.get_item_info(PVTR.slice_flag, PVTR.int_item)
        print item_info['process_msg']
        slice_info = self.get_slice_info(PVTR.slice_flag)
        # if not have slice path then create it
        if not os.path.exists(slice_info['slice_path']):
            os.mkdir(slice_info['slice_path'])
        # clear the figure
        pl.clf()
        h, v = slice_info['mesh_cord']
        pl.pcolormesh(h, v, item_info['slice_intensity'], shading='gouraud')
        pl.xlim(slice_info['lim'][0])
        pl.ylim(slice_info['lim'][1])
        pl.xlabel(slice_info['label'][0])
        pl.ylabel(slice_info['label'][1])
        pl.clim(self.clim_value)
        pl.colorbar()
        # show title or not
        if PVTR.title_flag:
            pl.title(item_info['title'])
        # create png path
        png_path = os.path.join(slice_info['slice_path'], str(PVTR.int_item) + '.png')
        if os.path.exists(png_path):
            os.remove(png_path)
        # rescale figure size
        fig = pl.gcf()
        ratio, x_fig, y_fig = slice_info['fig_size']
        if ratio > 1.4:
            fig.set_size_inches(x_fig, y_fig)
        # save figure
        fig.savefig(png_path)

    def get_origin_slice(self, slice_flag):
        """
        get origin slice along slice direction and save as png
        :param slice_flag: decided which slice direction to be processed ['x_slice'|'y_slice'|'z_slice']
        :return: null
        """
        PVTR.slice_flag = slice_flag
        slice_info = self.get_slice_info(PVTR.slice_flag)
        self.get_single_slice(PVTR.slice_flag, slice_info['origin_index'])

    def get_all_slice(self, slice_flag):
        """
        get all the slices along slice flag and save as png file and convert them to gif file
        :param slice_flag: decided which slice direction to be processed ['x_slice'|'y_slice'|'z_slice']
        :return: null
        """
        PVTR.slice_flag = slice_flag
        slice_info = self.get_slice_info(PVTR.slice_flag)
        PVTR.clear_path(slice_info['slice_path'])
        for i in range(slice_info['slice_num']):
            self.get_single_slice(PVTR.slice_flag, i)
        print '> convert images to gif ...'
        PVTR.convert_to_gif(slice_info['slice_path'])
        print '> process is finished.'

    def set_single_slice(self, slice_flag, int_item):
        """
        get one slice data and save as csv file according slice flag and item
        :param slice_flag: decided which slice direction to be processed ['x_slice'|'y_slice'|'z_slice']
        :param int_item: decided one special slice to be processed among all slices [int]
        :return: null
        """
        PVTR.slice_flag = slice_flag
        PVTR.int_item = int_item
        # get slice info and item info
        slice_info = self.get_slice_info(PVTR.slice_flag)
        item_info = self.get_item_info(PVTR.slice_flag, PVTR.int_item)
        print item_info['process_msg']
        # if not have slice_path create it
        if not os.path.exists(slice_info['slice_path']):
            os.mkdir(slice_info['slice_path'])
        # create csv file and write headerlines
        csv_path = os.path.join(slice_info['slice_path'], str(PVTR.int_item)+'.csv')
        if os.path.exists(csv_path):
            os.remove(csv_path)
        f = open(csv_path, 'ab+')
        f.write('PointA,PointB,Intensity\n')
        f.write(slice_info['size_info'])
        # transfer slice intensity data and write slice intensity data
        h, v = slice_info['mesh_cord']
        intensity_slice = item_info['slice_intensity']
        h_array, v_array, intensity_slice_array = np.array(h), np.array(v),np.array(intensity_slice)
        h_array.shape, v_array.shape, intensity_slice_array.shape = [(h_array.size,1)]*3
        for line in zip(h_array, v_array, intensity_slice_array):
            f.write(str(line[0][0])+','+str(line[1][0])+','+str(line[2][0])+'\n')
        f.close()

    def set_origin_slice(self, slice_flag):
        """
        get origin slice data according slice flag
        :param slice_flag: decided which slice direction to be processed ['x_slice'|'y_slice'|'z_slice']
        :return: null
        """
        PVTR.slice_flag = slice_flag
        slice_info = self.get_slice_info(PVTR.slice_flag)
        self.set_single_slice(PVTR.slice_flag, slice_info['origin_index'])

    def set_all_slice(self, slice_flag):
        """
        get all the slice and save as csv file
        :param slice_flag: decided which slice direction to be processed ['x_slice'|'y_slice'|'z_slice']
        :return:
        """
        PVTR.slice_flag = slice_flag
        slice_info = self.get_slice_info(PVTR.slice_flag)
        slice_path = os.path.join(self.path, PVTR.slice_flag)
        self.clear_path(slice_path)
        for i in range(slice_info['slice_num']):
            self.set_single_slice(PVTR.slice_flag, i)
        print '> process is finished.'
