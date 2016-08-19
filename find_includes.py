from os import walk, path
import argparse


class FindIncludes:

    def __init__(self, i_dir, ignore_sys, find_missing):
        # parse dir and files for include statements. Keep map of dir for look up
        # if lookup fails add to naughty list
        self.naughty_list = set()
        self.dir_map = {}
        self.inc_list = set()
        self.header_files = set()
        self.ignore_sys = ignore_sys
        self.i_dir = i_dir
        self.find_missing = find_missing

    def main(self):
        self.parse_dir()
        if self.find_missing:
            self.find_includes()

    def parse_dir(self):
        inc_list = set()
        dir_map = {}  # {dirname,[files]}
        allowed_exts = ['.h', '.hpp', '.c', '.cpp']
        h_ext = ['.h', '.hpp']
        for d_path, _, f_names in walk(self.i_dir):
            for f in f_names:
                ext = path.splitext(f)[1]
                if ext in allowed_exts:
                    with open(d_path + "\\" + f) as in_file:
                        self.parse_file(in_file.readlines())
                    if ext in h_ext:
                        self.header_files.add(f)
            self.dir_map[d_path] = f_names

    def parse_file(self, lines):
        # returns list of included files
        sys_headers = ["<", "$"]
        for line in lines:
            if line.startswith("#include "):
                found_inc = line.split("#include ")[1].strip().strip('"')
                if self.ignore_sys and found_inc[:1] in sys_headers:
                    pass
                else:
                    self.inc_list.add(found_inc)

    def find_includes(self):
        missing_incs = list(self.inc_list)
        for inc in missing_incs:
            if inc in self.header_files:
                self.inc_list.remove(inc)


parser = argparse.ArgumentParser()
parser.add_argument("--ignore_sys", "-i", action="store_true")
parser.add_argument("-d", "--directory")
parser.add_argument("-m", "--missing_headers", action="store_true")
args = parser.parse_args()
fi = FindIncludes(args.directory, args.ignore_sys, args.missing_headers)
fi.main()
for inc in fi.inc_list:
    print(inc)
