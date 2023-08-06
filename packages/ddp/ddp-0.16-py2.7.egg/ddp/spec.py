# -*- encoding:utf-8 -*-


import os
import matplotlib
matplotlib.use('Agg')
import pylab as pl
import ddp.inc as inc


class SPEC:
    # csv name
    csv_name = 'qtable.csv'

    # file delimiter
    file_delimiter = ' '

    # column order
    column_order = [1, 2, 3, 4]

    # header lines
    header_lines = 14

    wave = []
    ext = []
    abs = []
    sca = []

    # grid flag
    grid_flag = True

    # legend location
    legend_loc = 2

    def __init__(self):
        """ construct file
        :param path: path has file to be processed
        :return: null
        """
        self.path = inc.get_project_path()
        self.qtable_path = inc.get_qtable_path()
        self.get_data()

    def get_data(self):
        """
        fetch data in qtable and write into three data array
        :return: null
        """
        f = open(self.qtable_path)
        for line in list(f)[SPEC.header_lines::]:
            line_array = line.split(SPEC.file_delimiter)
            SPEC.wave.append(1000*float(line_array[SPEC.column_order[0]]))
            SPEC.ext.append(float(line_array[SPEC.column_order[1]]))
            SPEC.abs.append(float(line_array[SPEC.column_order[2]]))
            SPEC.sca.append(float(line_array[SPEC.column_order[3]]))
        f.close()

    def set_data(self):
        """
        write data array into qtable.csv
        :return: null
        """
        csv_path = os.path.join(self.path, SPEC.csv_name)
        if os.path.exists(csv_path):
            os.remove(csv_path)
        f = open(csv_path, 'wb+')
        f.write('Wavelength,Extinction,Absorption,Scattering\n')
        for line in zip(SPEC.wave, SPEC.ext, SPEC.abs, SPEC.sca):
            str_line = [str(x) for x in line]
            f.write(','.join(str_line)+'\n')
        f.close()
        print 'qtable.csv save successful...'

    @staticmethod
    def draw_spec():
        """
        draw spectrum
        :return: null
        """
        p1, = pl.plot(SPEC.wave, SPEC.ext, lw=2.0)
        p2, = pl.plot(SPEC.wave, SPEC.abs, lw=2.0)
        p3, = pl.plot(SPEC.wave, SPEC.sca, lw=2.0)
        pl.legend([p1, p2, p3], ['Extinction', 'Absorption', 'Scattering'], loc=SPEC.legend_loc)
        pl.grid(SPEC.grid_flag)
        pl.xlabel('Wavelength(nm)')
        pl.ylabel('Absorbance(a.u.)')
        pl.show()
        print 'spectrum.png draw successful...'

    def save_spec(self):
        """
        save spectrum figure into spectrum.png
        :return: null
        """
        pl.clf()
        p1, = pl.plot(SPEC.wave, SPEC.ext, lw=2.0)
        p2, = pl.plot(SPEC.wave, SPEC.abs, lw=2.0)
        p3, = pl.plot(SPEC.wave, SPEC.sca, lw=2.0)
        pl.legend([p1, p2, p3], ['Extinction', 'Absorption', 'Scattering'], loc=SPEC.legend_loc)
        pl.grid(SPEC.grid_flag)
        pl.xlabel('Wavelength(nm)')
        pl.ylabel('Absorbance(a.u.)')
        png_path = os.path.join(self.path, 'spectrum.png')
        if os.path.exists(png_path):
            os.remove(png_path)
        pl.savefig(png_path)
        print 'spectrum.png save successfully...'