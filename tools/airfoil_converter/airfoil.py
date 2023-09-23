#!/usr/bin/env python

# import an airfoil and convert it
import argparse
import numpy as np
import sys
import tempfile
import svgwrite
from dxfwrite import DXFEngine as dxf
import subprocess
import matplotlib.pyplot as plt

class AirfoilException(Exception):
    pass

class Airfoil:
    def __init__(self, filename=None, fileobj=None):
        if filename is None and fileobj is None:
            raise AirfoilException("You  must specify either a filename or fileobj")

        self.filename = None
        if filename is not None:
            self.filename = filename
            fileobj = open(filename, "rb") # need 'b' because some files have ^Z
#            x = fileobj.read().decode('UTF-8', errors='ignore')
#            fileobj = io.StringIO(x)
        self.name, self.coords = self.to_xfoil(fileobj)

    @staticmethod
    def to_xfoil(fileobj):
        f = fileobj
        name = f.readline()
        lines = f.readlines()
        # split the lines into x and y coordinates.  any number of spaces or tabs is allowed.  
        # Each line has exactly one x and one y coordinate
        # if the line is empty, skip it
        lines = [line for line in lines if line.strip()]
        lines = [line.split() for line in lines]
        # convert the strings to floats
        new_lines = []
        for line in lines:
            try:
                new_lines.append([float(x) for x in line])
            except ValueError:
                continue
        lines = new_lines
        if lines[0][0] > 1.1 or lines[1][1] > 1.1:
            # Convert this format
            n_coords_top, n_coords_bottom = np.array(lines[0], dtype=int)
            # delete item 0
            del lines[0]
            # reverse the first half of the list
            lines = lines[:n_coords_top][::-1] + lines[n_coords_top+1:]  # +1 so don't duplicate first coordinate
        lines = np.array(lines)
        return name, lines

    def interpolate(self, N):
        # I need two files/file names for xfoil
        with tempfile.NamedTemporaryFile(mode="w") as f_in:
            dat_in = f_in.name
            self.write_xfoil(f_in)
            f_in.flush()
            with tempfile.NamedTemporaryFile() as f_out:
                dat_out = f_out.name
                f_out.close()
                script = f"""
                    LOAD {dat_in}
                    PPAR
                    N {N}



                    SAVE {dat_out}
                    QUIT
                    """
                process = subprocess.Popen(["xfoil"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                process.stdin.write(script)
                stdout, stderr = process.communicate()
                # f_out should now contain the interpolated airfoil
                new_airfoil = Airfoil(fileobj=open(f_out.name, "r"))
                self.coords = new_airfoil.coords
        
    def write_xfoil(self, fileobj):
        name, data = self.name, self.coords
        fileobj.write(name)
        for line in data:
            fileobj.write(f"  {line[0]} {line[1]}\n")

    def write_dxf(self, fileobj, chord=None):
        # dxfwrite needs a filesystem object to write to.
        with tempfile.NamedTemporaryFile() as f:
            name = f.name
            f.close()
            drawing = dxf.drawing(name)
            drawing.add_layer('AIRFOIL')
            if chord is None:
                chord = 100
            points = self.coords * 100
            the_chord = np.max(points[:, 0])
            points = points / the_chord * chord
            points = np.append(points, [points[0, :]], axis=0) # close the shape
            drawing.add(dxf.polyline(points, layer='AIRFOIL'))
            drawing.save()
            with open(name, "r") as ff:
                fileobj.write(ff.read())

    def get_coords(self, closed=False):
        coords = self.coords
        if closed:
            coords = np.append(coords, [coords[0, :]], axis=0) # close the shape
        return coords
        
    def write_svg(self, fileobj, stroke=10, chord=100):
        # svgwrite needs a filesystem object to write to.
        with tempfile.NamedTemporaryFile() as f:
            name = f.name
            f.close()
            points = self.coords * 1000
            points[:, 1] = -points[:, 1] # Flip for svg space
            # offset so not negative
            minpoint = np.min(points, axis=0)

            points = points - minpoint
            # and offset some more for the stroke width
            points = points + stroke*2
            maxpoint = np.max(points, axis=0)+stroke*4
            doc = svgwrite.Drawing(filename=name, size=maxpoint)
            polygon = doc.polygon(points=points, fill='none', stroke='black', stroke_width=stroke)
            doc.add(polygon)
            doc.save()
            with open(name, "r") as ff:
                fileobj.write(ff.read())

    def plot(self, fig=None, axis=None):
        if fig is None:
            fig, axis = plt.subplots(nrows=1, ncols=1, sharex=True)
        axis.plot(self.coords[:, 0], self.coords[:, 1], label=self.name)
        return fig, axis


def get_args():
    parser = argparse.ArgumentParser(description='Convert an airfoil for use in xfoil')
    parser.add_argument('dat_in', type=str, help="The name of the file to convert")
    parser.add_argument('dat_out', type=str, help="output file name")
    parser.add_argument("-p", "--plot", action='store_true', help="Plot the airfoil")
    parser.add_argument("--chord", help="Set the chord dimension, in mm when converting.  Useful for svg and dxf", type=float, default=None)
    parser.add_argument("-i", "--interpolate", type=int,
                        help="""
                        Interpolate the airfoil while converting.  N is the number of panels.
                        Max is 350 or so with standard xfoil, but can be bigger with a custom compiled one
                        """)
    parser.add_argument("--stroke", type=float, help="Width of stroke to use. Default=10", default=10)
    choices = ["xfoil", "svg", "dxf"]
    def valid(x):
        if x in choices:
            return x
        else:
            raise argparse.ArgumentTypeError(f"Invalid format {x}")
    parser.add_argument('--fmt', type=valid, help=f"Output format.  Choices are {choices}.  Default=xfoil", default="xfoil")
    args = parser.parse_args()
    return args

def main():
    args = get_args()
    fin = sys.stdin
    fout = sys.stdout
    if args.dat_in != '-':
        fin = open(args.dat_in, "r")
    if args.dat_out != '-':
        fout = open(args.dat_out, "w")
    airfoil = Airfoil(fileobj=fin)
    if args.plot:
        fig, axis = airfoil.plot()
    if args.interpolate is not None:
        airfoil.interpolate(N=args.interpolate)
        if args.plot:
            fig, axis = airfoil.plot(fig, axis)
    if args.fmt == "xfoil":
        airfoil.write_xfoil(fileobj=fout)
    elif args.fmt == "svg":
        airfoil.write_svg(fileobj=fout, stroke=args.stroke, chord=args.chord)
    elif args.fmt == "dxf":
        airfoil.write_dxf(fileobj=fout, chord=args.chord)
    else:
        sys.stderr.write("Unhandled airfoil format {fmt}")
        exit(-1)
    if args.plot:
        plt.gca().set_aspect('equal')
        axis.grid()
        plt.show()

if __name__=="__main__":
    main()
