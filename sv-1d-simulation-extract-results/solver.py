#!/usr/bin/env python

from os import path
import logging
from manage import get_logger_name
from node import Node
from segment import Segment 
from parameters import Parameters
from collections import namedtuple

import vtk
print(" vtk version %s\n" % str(vtk.VTK_MAJOR_VERSION))

SegmentData = namedtuple('SegmentData', 'name values')

class Solver(object):

    def __init__(self, params):
        self.params = params
        self.nodes = None
        self.segments = None
        self.graphics = None
        self.logger = logging.getLogger(get_logger_name())

        self.points = vtk.vtkPoints()
        self.vertices = vtk.vtkCellArray()
        self.points_polydata = None
        self.lines_polydata = None

    def read_solver_file(self):
        """ Read in a solver.in file.
        """
        self.logger.info("---------- Read solver file ----------")
        #self.logger.info("Number of points: %d" % num_points)
        self.nodes = []
        self.segments = {}
        file_name = self.params.results_directory + "/" + self.params.solver_file_name

        with open(file_name) as fp:
            line = fp.readline()
            cnt = 1
            while line:
                #print("Line {}: {}".format(cnt, line.strip()))
                line = fp.readline()
                tokens = line.split()
                if len(tokens) == 0: 
                    continue
                if tokens[0] == 'NODE':
                    self.add_node(tokens)
                elif tokens[0] == 'SEGMENT':
                    self.add_segment(tokens)
                elif tokens[0] == 'SOLVEROPTIONS':
                    self.add_solver_options(tokens)
                elif tokens[0] == 'MODEL':
                    self.params.model_name = tokens[1]
            #__while line
        #__with open(self.params.solver_file_name) as fp:

        self.logger.info("Model name: %s" % self.params.model_name)
        self.logger.info("Number of nodes: %d" % len(self.nodes))
        self.logger.info("Number of segments: %d" % len(self.segments))
        self.logger.info("Number of time steps: %d" % self.params.num_steps) 
        self.logger.info("Time step: %g" % self.params.time_step) 

        # Create a points polydata object
        self.points_polydata = vtk.vtkPolyData()
        self.points_polydata.SetPoints(self.points)
        self.points_polydata.SetVerts(self.vertices)

        # Create a lines polydata object
        self.lines_polydata = vtk.vtkPolyData()
        self.lines_polydata.SetPoints(self.points)
        lines = vtk.vtkCellArray()
        for key,segment in self.segments.items():
            line = vtk.vtkLine()
            line.GetPointIds().SetId(0, segment.node1)
            line.GetPointIds().SetId(1, segment.node2)
            lines.InsertNextCell(line)
        self.lines_polydata.SetLines(lines)

    def add_solver_options(self, tokens):
        """ Add solver options.
        """
        time_step = float(tokens[1])
        self.params.time_step = time_step
        save_freq = int(tokens[2])
        num_steps = int(tokens[3])
        self.params.num_steps = num_steps 
        self.params.times = [i*time_step for i in range(0,num_steps+1,save_freq)]

    def add_node(self, tokens):
        """ Add a node..
        """
        id = tokens[1]
        x = float(tokens[2])
        y = float(tokens[3])
        z = float(tokens[4])
        id = self.points.InsertNextPoint([x, y, z])
        self.vertices.InsertNextCell(1)
        self.vertices.InsertCellPoint(id)
 
        self.nodes.append(Node(id,x,y,z))

    def add_segment(self, tokens):
        """ Add a segment.
        """
        name = tokens[1]
        id = tokens[2]
        node1 = int(tokens[5])
        node2 = int(tokens[6])
        self.segments[name] = Segment(id,name,node1,node2)
        self.logger.info("Add segment name: %s" % name) 

    def read_segment_data_file(self, segment_name, data_name):
        """ Read in a segment data file.
        """
        self.logger.info("---------- Read segment data file ----------")
        self.logger.info("Segment name: %s" % segment_name) 

        if not segment_name in self.segments:
            msg = "No segment named: %s" % segment_name
            self.logger.error(msg)
            raise Exception(msg)

        segment = self.segments[segment_name]
        segment.data = {}
        sep = Parameters.FILE_NAME_SEP
        ext = Parameters.DATA_FILE_EXTENSION 

        for data_name in self.params.data_names:
            self.logger.info("Data name: %s" % data_name) 
            file_name = self.params.results_directory + "/" + self.params.model_name + segment_name + sep + data_name + ext
            num_rows = 0
            data = []

            with open(file_name) as fp:
                line = fp.readline()
                cnt = 1
                while line:
                    #print("Line {}: {}".format(cnt, line.strip()))
                    line = fp.readline()
                    tokens = line.split()
                    num_rows += 1
                    if len(tokens) == 0:
                        continue
                    values = [float(v) for v in tokens]
                    num_cols = len(values)
                data.append(values)
                #__while line
            #__with open(file_name) as fp
            segment.data[data_name] = data
        #__for data_name in self.params.data_names:

        self.logger.info("Number of rows read: %d" % num_rows) 
        self.logger.info("Number of columns read: %d" % num_cols) 

    def write_segment_data(self):
        self.logger.info("---------- Write segment data ----------")
        file_format = self.params.output_format
        ext = "." + file_format 
        sep = "_"

        for data_name in self.params.data_names:
            self.logger.info("Data name: %s" % data_name) 
            file_name = self.params.output_directory + "/" + self.params.output_file_name + sep + data_name + ext
            times = self.params.times

            with open(file_name, "w") as fp:
                for i,name in enumerate(self.params.segments):
                    self.logger.info("Segment name: %s" % name) 
                    fp.write(name)
                    if i != len(self.params.segments)-1:
                        fp.write(",")
                fp.write("\n")

                for i,time in enumerate(times):
                    fp.write(str(time) + ",")
                    for j,name in enumerate(self.params.segments):
                        segment = self.segments[name]
                        data_list = segment.data[data_name]
                        data = data_list[-1]
                        fp.write(str(data[i]))
                        if j != len(self.params.segments)-1:
                            fp.write(",")
                    #__for j,name in enumerate(self.params.segments)
                    fp.write("\n")
                #__for i,time in enumerate(times):

        #__for data_name in self.params.data_names

