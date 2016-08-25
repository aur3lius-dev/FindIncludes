"""Contains classes and functions to parse a source directory to identify
    found and missing header files"""
from os import walk, path
import argparse


class FindIncludes:
    """Main class parses dirs and then files to find
       header files and locations"""
    def __init__(self, i_dir, ignore_sys, find_missing):
        self.dir_map = {}
        self.inc_list = []
        self.header_files = set()
        self.ignore_sys = ignore_sys
        self.i_dir = i_dir
        self.find_missing = find_missing

    def main(self):
        """Calls other functions to process appropriately"""
        self.parse_dir()
        if self.find_missing:
            self.find_includes()
        self.inc_list.sort(key=lambda x: x.name, reverse=True)

    def parse_dir(self):
        """Enumerates files within the i_dir directory"""
        allowed_exts = ['.h', '.hpp', '.c', '.cpp']
        h_ext = ['.h', '.hpp']
        for d_path, _, f_names in walk(self.i_dir):
            for f in f_names:
                ext = path.splitext(f)[1]
                if ext in allowed_exts:
                    self.parse_file(d_path+"\\" + f)
                    if ext in h_ext:
                        self.header_files.add(f)
            self.dir_map[d_path] = f_names

    def parse_file(self, in_file):
        """"returns list of included files"""
        sys_headers = ["<", "$"]
        line_num = 0
        with open(in_file) as f:
            lines = f.readlines()
        for line in lines:
            line_num += 1
            if line.startswith("#include "):
                inc_name = line.split("#include ")[1].strip().strip('"')
                if inc_name not in self.inc_list:
                    found_inc = Includes(inc_name)
                    if self.ignore_sys and found_inc.name[:1] in sys_headers:
                        pass
                    else:
                        self.inc_list.append(found_inc)
                else:
                    found_inc = self.inc_list[self.inc_list.index(inc_name)]
                found_inc.update_location(in_file, line_num)

    def find_includes(self):
        """Produces a list of _only_ missing headers"""
        missing_incs = list(self.inc_list)
        for incl in missing_incs:
            if incl.name in self.header_files:
                self.inc_list.remove(incl)


class Includes:
    """Node class to store header file information"""
    def __init__(self, name):
        self.name = name
        self.locations = set()  # Path/File: line#

    def update_location(self, filename, line_num):
        """Updates the header locations list"""
        loc = (filename, line_num)
        self.locations.add(loc)

    def get_locations(self):
        """Returns the sorted header locations list"""
        listed = list(self.locations)
        listed.sort()
        return listed

    def __eq__(self, other):
        if type(other) is str:
            return self.name == other
        return self.name == other.name

    def __repr__(self):
        return "%s\t%s" % (self.name, self.locations)


def begin():
    """Main init function."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--ignore_sys", action="store_true",
                        help="Ignore system header files")
    parser.add_argument("-m", "--missing_headers", action="store_true",
                        help="Print missing header files only")
    parser.add_argument('-p', '--print_locations', action='store_true',
                        help="Print file locations and line numbers for" +
                        " references to include statements")
    parser.add_argument('-pp', '--print_separate', action='store_true',
                        help="Print file locations after listing discovered" +
                        "header files")
    parser.add_argument("-d", "--directory", required=True)
    args = parser.parse_args()
    fi = FindIncludes(args.directory, args.ignore_sys, args.missing_headers)
    fi.main()
    sep_list = []
    for inc in fi.inc_list:
        print(inc.name)
        if args.print_locations:
            for item in inc.get_locations():
                print("\t%s:%s" % (item[0], item[1]))
        elif args.print_separate:
            for item in inc.get_locations():
                sep_list.append("%s:%s" % (item[0], item[1]))
    if args.print_separate:
        sep_list.sort()
        for i in sep_list:
            print(i)
if __name__ == "__main__":
    begin()
