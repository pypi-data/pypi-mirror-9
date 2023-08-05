#!/usr/bin/env python
from __future__ import division, with_statement

"""
run: main Segway implementation
"""

__version__ = "$Revision$"

# Copyright 2008-2014 Michael M. Hoffman <michael.hoffman@utoronto.ca>

from collections import defaultdict, namedtuple
from copy import copy
from datetime import datetime
from distutils.spawn import find_executable
from errno import EEXIST, ENOENT
from functools import partial
from itertools import count, izip, product
from math import ceil, ldexp
from os import environ, extsep
import re
from shutil import copy2
from string import letters
import sys
from threading import Event, Lock, Thread
from time import sleep
from urllib import quote
from uuid import uuid1
from warnings import warn

from genomedata import Genome
from numpy import (arcsinh, array, empty, finfo, float32, int64, inf,
                   square, vstack, zeros)
from optplus import str2slice_or_int
from optbuild import AddableMixin
from path import path
from pkg_resources import Requirement, working_set
from tabdelim import DictReader, ListWriter

from .bed import parse_bed4, read_native
from .cluster import (make_native_spec, JobTemplateFactory, RestartableJob,
                      RestartableJobDict, Session)
from .include import IncludeSaver
from .input_master import InputMasterSaver
from .observations import Observations
from .output import IdentifySaver, PosteriorSaver
from .structure import StructureSaver
from ._util import (data_filename, DTYPE_OBS_INT, DISTRIBUTION_NORM,
                    DISTRIBUTION_GAMMA, DISTRIBUTION_ASINH_NORMAL,
                    EXT_BED, EXT_FLOAT, EXT_GZ, EXT_INT, EXT_PARAMS,
                    EXT_TAB, extjoin, extjoin_not_none, GB,
                    ISLAND_BASE_NA, ISLAND_LST_NA, load_coords,
                    make_default_filename, make_filelistpath,
                    make_prefix_fmt, MB, memoized_property,
                    OFFSET_START, OFFSET_END, OFFSET_STEP,
                    OptionBuilder_GMTK, POSTERIOR_PROG,
                    PREFIX_LIKELIHOOD, PREFIX_PARAMS, SEG_TABLE_WIDTH,
                    SUBDIRNAME_LOG, SUBDIRNAME_PARAMS,
                    SUPERVISION_LABEL_OFFSET,
                    SUPERVISION_UNSUPERVISED,
                    SUPERVISION_SEMISUPERVISED, USE_MFSDG,
                    VITERBI_PROG)

# set once per file run
UUID = uuid1().hex

# XXX: I should really get some sort of Enum for this, I think Peter
# Norvig has one
DISTRIBUTIONS = [DISTRIBUTION_NORM, DISTRIBUTION_GAMMA,
                 DISTRIBUTION_ASINH_NORMAL]
DISTRIBUTION_DEFAULT = DISTRIBUTION_ASINH_NORMAL

MIN_NUM_SEGS = 2
NUM_SEGS = MIN_NUM_SEGS
NUM_SUBSEGS = 1
OUTPUT_LABEL = "seg"
RULER_SCALE = 10
MAX_EM_ITERS = 100
CARD_SUPERVISIONLABEL_NONE = -1

ISLAND = True

# XXX: temporary code to allow easy switching
if ISLAND:
    ISLAND_BASE = 3
    ISLAND_LST = 100000
    HASH_LOAD_FACTOR = 0.98
else:
    ISLAND_BASE = ISLAND_BASE_NA
    ISLAND_LST = ISLAND_LST_NA
    HASH_LOAD_FACTOR = None

COMPONENT_CACHE = not ISLAND
DETERMINISTIC_CHILDREN_STORE = not ISLAND

assert (ISLAND or
        (ISLAND_LST == ISLAND_LST_NA and ISLAND_BASE == ISLAND_BASE_NA))

LINEAR_MEM_USAGE_MULTIPLIER = 1
MEM_USAGE_MULTIPLIER = 2

JOIN_TIMEOUT = finfo(float).max

SWAP_ENDIAN = False

## option defaults
VERBOSITY = 0
PRIOR_STRENGTH = 0

FINFO_FLOAT32 = finfo(float32)
MACHEP_FLOAT32 = FINFO_FLOAT32.machep
TINY_FLOAT32 = FINFO_FLOAT32.tiny

SIZEOF_FLOAT32 = float32().nbytes
SIZEOF_DTYPE_OBS_INT = DTYPE_OBS_INT().nbytes

# sizeof tmp space used per frame
SIZEOF_FRAME_TMP = (SIZEOF_FLOAT32 + SIZEOF_DTYPE_OBS_INT)

FUDGE_EP = -17  # ldexp(1, -17) = ~1e-6
assert FUDGE_EP > MACHEP_FLOAT32

FUDGE_TINY = -ldexp(TINY_FLOAT32, 6)

LOG_LIKELIHOOD_DIFF_FRAC = 1e-5

NUM_SEQ_COLS = 2   # dinucleotide, presence_dinucleotide

MAX_FRAMES = 2000000  # 2 million
MEM_USAGE_BUNDLE = 100 * MB  # XXX: should start using this again
MEM_USAGE_PROGRESSION = "2,3,4,6,8,10,12,14,15"

TMP_USAGE_BASE = 10 * MB  # just a guess

POSTERIOR_CLIQUE_INDICES = dict(p=1, c=1, e=1)

## defaults
NUM_INSTANCES = 1

CPP_DIRECTIVE_FMT = "-D%s=%s"

GMTK_INDEX_PLACEHOLDER = "@D"
NAME_BUNDLE_PLACEHOLDER = "bundle"

# programs
ENV_CMD = "/usr/bin/env"

# XXX: need to differentiate this (prog) from prog.prog == progname throughout
TRIANGULATE_PROG = OptionBuilder_GMTK("gmtkTriangulate")
EM_TRAIN_PROG = OptionBuilder_GMTK("gmtkEMtrain")

TMP_OBS_PROGS = frozenset([VITERBI_PROG, POSTERIOR_PROG])

# extensions and suffixes
EXT_BEDGRAPH = "bedGraph"
EXT_BIN = "bin"
EXT_LIKELIHOOD = "ll"
EXT_LOG = "log"
EXT_OUT = "out"
EXT_POSTERIOR = "posterior"
EXT_SH = "sh"
EXT_TXT = "txt"
EXT_TRIFILE = "trifile"

PREFIX_ACC = "acc"
PREFIX_CMDLINE_SHORT = "run"
PREFIX_CMDLINE_LONG = "details"
PREFIX_CMDLINE_TOP = "segway"
PREFIX_TRAIN = "train"
PREFIX_POSTERIOR = "posterior%s"

PREFIX_VITERBI = "viterbi"
PREFIX_WINDOW = "window"
PREFIX_JT_INFO = "jt_info"
PREFIX_JOB_LOG = "jobs"

PREFIX_JOB_NAME_TRAIN = "emt"
PREFIX_JOB_NAME_VITERBI = "vit"
PREFIX_JOB_NAME_POSTERIOR = "jt"
PREFIX_JOB_NAMES = dict(identify=PREFIX_JOB_NAME_VITERBI,
                        posterior=PREFIX_JOB_NAME_POSTERIOR)

SUFFIX_OUT = extsep + EXT_OUT
SUFFIX_TRIFILE = extsep + EXT_TRIFILE

## "segway.bed.gz"
BED_FILEBASENAME = extjoin(__package__, EXT_BED, EXT_GZ)

## "segway.%d.bed.gz"
BED_FILEBASEFMT = extjoin(__package__, "%d", EXT_BED, EXT_GZ)

## "posterior%s.bed.gz"
BEDGRAPH_FILEBASENAME = extjoin(PREFIX_POSTERIOR, EXT_BEDGRAPH, EXT_GZ)

## "posterior%s.%%d.bed.gz"
BEDGRAPH_FILEBASEFMT = extjoin(PREFIX_POSTERIOR, "%%d", EXT_BEDGRAPH, EXT_GZ)
FLOAT_TABFILEBASENAME = extjoin("observations", EXT_TAB)
TRAIN_FILEBASENAME = extjoin(PREFIX_TRAIN, EXT_TAB)

SUBDIRNAME_ACC = "accumulators"
SUBDIRNAME_AUX = "auxiliary"
SUBDIRNAME_LIKELIHOOD = "likelihood"
SUBDIRNAME_OBS = "observations"
SUBDIRNAME_POSTERIOR = "posterior"
SUBDIRNAME_VITERBI = "viterbi"

SUBDIRNAMES_EITHER = [SUBDIRNAME_AUX]
SUBDIRNAMES_TRAIN = [SUBDIRNAME_ACC, SUBDIRNAME_LIKELIHOOD,
                     SUBDIRNAME_PARAMS]

JOB_LOG_FIELDNAMES = ["jobid", "jobname", "prog", "num_segs",
                      "num_frames", "maxvmem", "cpu", "exit_status"]
# XXX: should add num_subsegs as well, but it's complicated to pass
# that data into RestartableJobDict.wait()

TRAIN_FIELDNAMES = ["name", "value"]

TRAIN_OPTION_TYPES = \
    dict(input_master_filename=str, structure_filename=str,
         params_filename=str, dont_train_filename=str, seg_table_filename=str,
         distribution=str, len_seg_strength=float,
         segtransition_weight_scale=float, ruler_scale=int, resolution=int,
         num_segs=int, num_subsegs=int, output_label=str, track_specs=[str],
         reverse_worlds=[int])

# templates and formats
RES_OUTPUT_MASTER = "output.master"
RES_DONT_TRAIN = "dont_train.list"
RES_SEG_TABLE = "seg_table.tab"

TRAIN_ATTRNAMES = ["input_master_filename", "params_filename",
                   "log_likelihood_filename"]
LEN_TRAIN_ATTRNAMES = len(TRAIN_ATTRNAMES)

COMMENT_POSTERIOR_TRIANGULATION = \
    "%% triangulation modified for posterior decoding by %s" % __package__

RESOLUTION = 1

SEGTRANSITION_WEIGHT_SCALE = 1.0

DIRPATH_WORK_DIR_HELP = path("WORKDIR")
DIRPATH_AUX = DIRPATH_WORK_DIR_HELP / SUBDIRNAME_AUX
DIRPATH_PARAMS = DIRPATH_WORK_DIR_HELP / SUBDIRNAME_PARAMS

# 62 so that it's not in sync with the 10 second job wait sleep time
THREAD_START_SLEEP_TIME = 62  # XXX: this should become an option

# -gpr option for GMTK when reversing
REVERSE_GPR = "^0:-1:0"

Results = namedtuple("Results", ["log_likelihood", "num_segs",
                                 "input_master_filename", "params_filename",
                                 "log_likelihood_filename"])
OFFSET_FILENAMES = 2  # where the filenames begin in Results

PROGS = dict(identify=VITERBI_PROG, posterior=POSTERIOR_PROG)


## functions
def quote_trackname(text):
    # legal characters are ident in GMTK_FileTokenizer.ll:
    # {alpha})({alpha}|{dig}|\_|\-)* (alpha is [A-za-z], dig is [0-9])
    res = text.replace("_", "_5F")
    res = res.replace(".", "_2E")

    # quote eliminates everything that doesn't match except for "_.-",
    # replaces with % escapes
    res = quote(res, safe="")  # safe="" => quote "/" too
    res = res.replace("%", "_")

    # add stub to deal with non-alphabetic first characters
    if res[0] not in letters:
         # __ should never appear in strings quoted as before
        res = "x__" + res

    return res


def quote_spaced_str(item):
    """
    add quotes around text if it has spaces in it
    """
    text = str(item)

    if " " in text:
        return '"%s"' % text
    else:
        return text


class NoAdvance(str):
    """
    cause rewrite_strip_comments() to not consume an extra line
    """


class NewLine(NoAdvance):
    """
    add a line rather than replacing existing
    """
    # doesn't actually have any code. used solely for class identification


def rewrite_strip_comments(infile, outfile):
    """
    strips comments, and trailing whitespace from lines
    """
    for line in infile:
        inline = line.rstrip()

        if not inline or inline.startswith("%"):
            outline = inline
        else:
            outline = (yield inline)

            if isinstance(outline, NewLine):
                print >>outfile, inline
            elif outline is None:
                outline = inline

        print >>outfile, outline

        while isinstance(outline, NoAdvance):
            outline = (yield)

            if outline is not None:
                print >>outfile, outline


def consume_until(iterable, text):
    for line in iterable:
        if line.startswith(text):
            break


def slice2range(s):
    if isinstance(s, int):
        return [s]

    start = s.start
    stop = s.stop
    step = s.step

    # need to know the length of the sequence to work with stop == None
    assert stop is not None

    if start is None:
        start = 0

    if step is None:
        step = 1

    return xrange(start, stop, step)


def is_training_progressing(last_ll, curr_ll,
                            min_ll_diff_frac=LOG_LIKELIHOOD_DIFF_FRAC):
    # using x !< y instead of x >= y to give the right default answer
    # in the case of NaNs
    return not abs((curr_ll - last_ll) / last_ll) < min_ll_diff_frac


def set_cwd_job_tmpl(job_tmpl):
    job_tmpl.workingDirectory = path.getcwd()


def rewrite_cliques(rewriter, frame, output_label):
    """
    returns the index of the added clique
    """
    # method
    rewriter.next()

    # number of cliques
    orig_num_cliques = int(rewriter.next())
    rewriter.send(NoAdvance(orig_num_cliques + 1))

    # original cliques
    for clique_index in xrange(orig_num_cliques):
        rewriter.next()

    # new clique
    if output_label != "seg":
        rewriter.send(NewLine("%d 2 seg %d subseg %d" % 
                              (orig_num_cliques, frame, frame)))
    else:
        rewriter.send(NewLine("%d 1 seg %d" % (orig_num_cliques, frame)))

    # XXX: add subseg as a clique to report it in posterior

    return orig_num_cliques


def make_mem_req(mem_usage):
    # double usage at this point
    mem_usage_gibibytes = ceil(mem_usage / GB)

    return "%dG" % mem_usage_gibibytes


class Mixin_Lockable(AddableMixin):  # noqa
    def __init__(self, *args, **kwargs):
        self.lock = Lock()
        return AddableMixin.__init__(self, *args, **kwargs)

LockableDefaultDict = Mixin_Lockable + defaultdict


class TrainThread(Thread):
    def __init__(self, runner, session, instance_index, num_segs):
        # keeps it from rewriting variables that will be used
        # later or in a different thread
        self.runner = copy(runner)

        self.session = session
        self.num_segs = num_segs
        self.instance_index = instance_index

        Thread.__init__(self)

    def run(self):
        self.runner.session = self.session
        self.runner.num_segs = self.num_segs
        self.runner.instance_index = self.instance_index
        self.result = self.runner.run_train_instance()


def maybe_quote_arg(text):
    """return quoted argument, adding backslash quotes

    XXX: would be nice if this were smarter about what needs to be
    quoted, only doing this when special characters or whitespace are
    within the arg

    XXX: Enclosing characters in double quotes (`"') preserves the
    literal value of all characters within the quotes, with the
    exception of `$', ``', `\', and, when history expansion is
    enabled, `!'. The characters `$' and ``' retain their special
    meaning within double quotes (*note Shell Expansions::). The
    backslash retains its special meaning only when followed by one of
    the following characters: `$', ``', `"', `\', or `newline'. Within
    double quotes, backslashes that are followed by one of these
    characters are removed. Backslashes preceding characters without a
    special meaning are left unmodified. A double quote may be quoted
    within double quotes by preceding it with a backslash. If enabled,
    history expansion will be performed unless an `!' appearing in
    double quotes is escaped using a backslash. The backslash
    preceding the `!' is not removed.

    """
    return '"%s"' % text.replace('"', r'\"')


def cmdline2text(cmdline=sys.argv):
    return " ".join(maybe_quote_arg(arg) for arg in cmdline)


def _log_cmdline(logfile, cmdline):
    print >>logfile, " ".join(map(quote_spaced_str, cmdline))


def check_overlapping_supervision_labels(start, end, chrom, coords):
    for coord_start, coord_end in coords[chrom]:
        if not (coord_start >= end or coord_end <= start):
            raise ValueError("supervision label %s(%s, %s) overlaps"
                             "supervision label %s(%s, %s)" %
                             (chrom, coord_start, coord_end,
                              chrom, start, end))


class Track(object):
    def __init__(self, name_unquoted, is_data=True):
        self.name_unquoted = name_unquoted
        self.is_data = is_data
        self.group = None
        self.index = None

    @memoized_property
    def name(self):
        return quote_trackname(self.name_unquoted)

TRACK_DINUCLEOTIDE = Track("dinucleotide", is_data=False)
TRACK_SUPERVISIONLABEL = Track("supervisionLabel", is_data=False)


class TrackGroup(list):
    def _set_group(self, item):
        assert item.group is None
        item.group = self
        return item

    def __init__(self, items=[]):
        return list.__init__(self, [self._set_group(item) for item in items])

    def __setitem__(self, index, item):
        if isinstance(index, slice):
            raise NotImplementedError

        return list.__setitem__(self, index, self._set_group(item))

    def append(self, item):
        return list.append(self, self._set_group(item))

    def extend(self, items):
        return list.extend(self, [self._set_group(item) for item in items])

    def insert(self, index, item):
        return list.insert(self, index, self._set_group(item))

re_num_cliques = re.compile(r"^Number of cliques = (\d+)$")
re_clique_info = re.compile(r"^Clique information: .*, (\d+) unsigned words ")


class Runner(object):
    """
    Purpose:

    1. hold configuration--interface between UI and other code
    2. create necessary files (through Saver objects)
       TODO: move all saving to Saver objects
    3. execute GMTK
    4. monitor GMTK output
    5. convert output to bioinformatics formats
       TODO: move this to some other kind of object
    """
    def __init__(self, **kwargs):
        """
        usually not called directly, instead Runner.fromoptions() is called
        (which calls Runner.__init__())
        """
        self.uuid = UUID

        # filenames
        self.bigbed_filename = None
        self.gmtk_include_filename = None
        self.input_master_filename = None
        self.structure_filename = None
        self.triangulation_filename = None
        self.job_log_filename = None
        self.seg_table_filename = None
        self.supervision_filename = None

        self.params_filename = None  # actual params filename for this instance
        self.params_filenames = []  # list of possible params filenames
        self.recover_dirname = None
        self.work_dirname = None
        self.log_likelihood_filename = None
        self.log_likelihood_tab_filename = None

        self.obs_dirname = None

        self.include_coords_filename = None
        self.exclude_coords_filename = None

        self.posterior_clique_indices = POSTERIOR_CLIQUE_INDICES.copy()

        self.triangulation_filename_is_new = None

        self.supervision_coords = None
        self.supervision_labels = None

        self.card_supervision_label = -1

        # tracks: list: all the tracks used
        self.tracks = []

        # track_groups: list of lists: each one is a grouping of
        # tracks that are similar to each other. Only one track from
        # each track group is used at a time during inference. A set
        # of tracks across groups being used at once is a "world."
        self.track_groups = []

        # default is 0
        self.global_mem_usage = LockableDefaultDict(int)

        # data
        # a "window" is what GMTK calls a segment
        self.windows = None
        self.mins = None
        self.track_specs = []

        # variables
        self.num_segs = NUM_SEGS
        self.num_subsegs = NUM_SUBSEGS
        self.output_label = OUTPUT_LABEL
        self.num_instances = NUM_INSTANCES
        self.len_seg_strength = PRIOR_STRENGTH
        self.distribution = DISTRIBUTION_DEFAULT
        self.max_em_iters = MAX_EM_ITERS
        self.max_frames = MAX_FRAMES
        self.segtransition_weight_scale = SEGTRANSITION_WEIGHT_SCALE
        self.ruler_scale = RULER_SCALE
        self.resolution = RESOLUTION
        self.reverse_worlds = []  # XXXopt: this should be a set

        # flags
        self.clobber = False
        ## XXX: this should become an int for num_starts
        self.train = False  # EM train
        self.posterior = False
        self.identify = False  # viterbi
        self.dry_run = False
        self.verbosity = VERBOSITY

        self.__dict__.update(kwargs)

    def set_tasks(self, text):
        tasks = text.split("+")
        if "train" in tasks and len(tasks) > 1:
            raise ValueError("train task must be run separately")

        for task in tasks:
            if task == "train":
                self.train = True
            elif task == "identify":
                self.identify = True
            elif task == "posterior":
                self.posterior = True
            else:
                raise ValueError("unrecognized task: %s" % task)

    def set_option(self, name, value):
        # want to actually set the Runner option when optparse option
        # is numeric zero (int or float), but not if it is an empty
        # list, empty str, None, False, etc.
        if value or value == 0:
            setattr(self, name, value)

    options_to_attrs = [("recover", "recover_dirname"),
                        ("observations", "obs_dirname"),
                        ("bed", "bed_filename"),
                        ("semisupervised", "supervision_filename"),
                        ("bigBed", "bigbed_filename"),
                        ("include_coords", "include_coords_filename"),
                        ("exclude_coords", "exclude_coords_filename"),
                        ("num_instances",),
                        ("verbosity",),
                        ("split_sequences", "max_frames"),
                        ("clobber",),
                        ("dry_run",),
                        ("input_master", "input_master_filename"),
                        ("structure", "structure_filename"),
                        ("dont_train", "dont_train_filename"),
                        ("seg_table", "seg_table_filename"),
                        ("distribution",),
                        ("prior_strength", "len_seg_strength"),
                        ("segtransition_weight_scale",),
                        ("ruler_scale",),
                        ("resolution",),
                        ("num_labels", "num_segs"),
                        ("num_sublabels", "num_subsegs"),
                        ("output_label", "output_label"),
                        ("max_train_rounds", "max_em_iters"),
                        ("reverse_world", "reverse_worlds"),
                        ("track", "track_specs")]

    @classmethod
    def fromargs(cls, args):
        res = cls()

        task_str = args[0]
        genomedataname = args[1]
        traindirname = args[2]

        res.set_tasks(task_str)
        res.genomedataname = genomedataname

        if res.train:
            res.work_dirname = traindirname
            assert len(args) == 3
            return res

        # identify or posterior
        res.work_dirname = args[3]

        try:
            res.load_train_options(traindirname)
        except IOError, err:
            # train.tab use is optional
            if err.errno != ENOENT:
                raise

        return res

    def add_track_group(self, tracknames):
        tracks = self.tracks
        track_group = TrackGroup()
        tracknames_unquoted = set(track.name_unquoted for track in tracks)

        # non-allowed special trackname
        if "supervisionLabel" in tracknames:
            raise ValueError("'supervisionLabel' trackname is internally "
                             "reserved and not allowed in supplied "
                             "tracknames")

        for trackname in tracknames:
            if trackname in tracknames_unquoted:
                raise ValueError("can't tie one track in multiple groups")

            track = Track(trackname)
            tracks.append(track)
            track_group.append(track)
            tracknames_unquoted.add(trackname)

        self.track_groups.append(track_group)

    @classmethod
    def fromoptions(cls, args, options):
        """This is the usual way a Runner is created.

        Calls Runner.fromargs() first.
        """
        res = cls.fromargs(args)

        # bulk copy options that need no further processing
        for option_to_attr in cls.options_to_attrs:
            try:
                src, dst = option_to_attr
            except ValueError:
                src, = option_to_attr
                dst = src

            res.set_option(dst, getattr(options, src))

        # multiple lists to one
        res.user_native_spec = sum([opt.split(" ")
                                    for opt in options.cluster_opt], [])

        mem_usage_list = map(float, options.mem_usage.split(","))

        # XXX: should do a ceil first?
        # use int64 in case run.py is run on a 32-bit machine to control
        # 64-bit compute nodes
        res.mem_usage_progression = (array(mem_usage_list) * GB).astype(int64)

        # don't change from None if this is false
        params_filenames = options.trainable_params
        if params_filenames:
            res.params_filenames = params_filenames

        ## track option processing
        for track_spec in res.track_specs:
            # local to each value of track_spec
            res.add_track_group(track_spec.split(","))

        if res.num_worlds > 1:
            res.check_world_fmt("bed_filename")
            res.check_world_fmt("bedgraph_filename")
            res.check_world_fmt("bigbed_filename")

        return res

    @memoized_property
    def triangulation_dirpath(self):
        res = self.work_dirpath / "triangulation"
        self.make_dir(res)

        return res

    @memoized_property
    def jt_info_filename(self):
        return self.make_filename(PREFIX_JT_INFO, EXT_TXT,
                                  subdirname=SUBDIRNAME_LOG)

    @memoized_property
    def posterior_jt_info_filename(self):
        return self.make_filename(PREFIX_JT_INFO, "posterior", EXT_TXT,
                                  subdirname=SUBDIRNAME_LOG)

    @memoized_property
    def work_dirpath(self):
        return path(self.work_dirname)

    @memoized_property
    def recover_dirpath(self):
        recover_dirname = self.recover_dirname
        if recover_dirname:
            return path(recover_dirname)

        # recover_dirname is None or ""
        return None

    @memoized_property
    def include_coords(self):
        return load_coords(self.include_coords_filename)

    @memoized_property
    def exclude_coords(self):
        return load_coords(self.exclude_coords_filename)

    @memoized_property
    def seg_table(self):
        filename = self.seg_table_filename

        if not filename:
            filename = data_filename("seg_table.tab")

        # always the last element of the range
        num_segs = slice2range(self.num_segs)[-1]

        res = zeros((num_segs, SEG_TABLE_WIDTH), dtype=int)
        ruler_scale = self.ruler_scale
        res[:, OFFSET_STEP] = ruler_scale

        with open(filename) as infile:
            reader = DictReader(infile)

            # overwriting is allowed
            for row in reader:
                # XXX: factor out
                # get row_indexes
                label = row["label"]
                label_slice = str2slice_or_int(label)

                if isinstance(label_slice, slice) and label_slice.stop is None:
                    label_slice = slice(label_slice.start, num_segs,
                                        label_slice.step)

                row_indexes = slice2range(label_slice)

                # get slice
                len_slice = str2slice_or_int(row["len"])

                # XXX: eventually, should read ruler scale from file
                # instead of using as a command-line option
                assert len_slice.step == ruler_scale

                len_tuple = (len_slice.start, len_slice.stop, len_slice.step)
                len_row = zeros((SEG_TABLE_WIDTH))

                for item_index, item in enumerate(len_tuple):
                    if item is not None:
                        len_row[item_index] = item

                res[row_indexes] = len_row

        return res

    @memoized_property
    def obs_dirpath(self):
        obs_dirname = self.obs_dirname

        if obs_dirname:
            res = path(obs_dirname)
        else:
            res = self.work_dirpath / SUBDIRNAME_OBS
            self.obs_dirname = res

        try:
            self.make_dir(res)
        except OSError, err:
            if not (err.errno == EEXIST and res.isdir()):
                raise

        return res

    @memoized_property
    def float_filelistpath(self):
        return self.make_obs_filelistpath(EXT_FLOAT)

    @memoized_property
    def int_filelistpath(self):
        return self.make_obs_filelistpath(EXT_INT)

    @memoized_property
    def float_tabfilepath(self):
        return self.obs_dirpath / FLOAT_TABFILEBASENAME

    @memoized_property
    def gmtk_include_filename_relative(self):
        return self.gmtk_include_filename

        # XXX: disable until you figure out a good way of dealing with
        # includes from params/input.master as well

        # dirpath_trailing_slash = self.work_dirpath + "/"
        # include_filename_relative = \
        #     include_filename.partition(dirpath_trailing_slash)[2]
        # assert include_filename_relative

        #self.gmtk_include_filename_relative = include_filename_relative

    @memoized_property
    def _means_untransformed(self):
        return self.sums / self.num_datapoints

    @memoized_property
    def means(self):
        return self.transform(self._means_untransformed)

    @memoized_property
    def vars(self):
        # this is an unstable way of calculating the variance,
        # but it should be good enough
        # Numerical Recipes in C, Eqn 14.1.7
        # XXX: best would be to switch to the pairwise parallel method
        # (see Wikipedia)

        sums_squares_normalized = self.sums_squares / self.num_datapoints
        return self.transform(sums_squares_normalized
                              - square(self._means_untransformed))

    @memoized_property
    def dont_train_filename(self):
        return self.save_resource(RES_DONT_TRAIN, SUBDIRNAME_AUX)

    @memoized_property
    def output_master_filename(self):
        return self.save_resource(RES_OUTPUT_MASTER, SUBDIRNAME_PARAMS)

    def make_viterbi_filenames(self, dirpath):
        """
        make viterbi filenames for a particular dirpath
        """
        viterbi_dirpath = dirpath / SUBDIRNAME_VITERBI
        num_windows = self.num_windows

        viterbi_filename_fmt = (PREFIX_VITERBI + make_prefix_fmt(num_windows)
                                + EXT_BED)
        return [viterbi_dirpath / viterbi_filename_fmt % index
                for index in xrange(num_windows)]

    @memoized_property
    def viterbi_filenames(self):
        self.make_subdir(SUBDIRNAME_VITERBI)
        return self.make_viterbi_filenames(self.work_dirpath)

    @memoized_property
    def recover_viterbi_filenames(self):
        recover_dirpath = self.recover_dirpath
        if recover_dirpath:
            return self.make_viterbi_filenames(recover_dirpath)
        else:
            return None

    @memoized_property
    def posterior_filenames(self):
        self.make_subdir(SUBDIRNAME_POSTERIOR)
        return map(self.make_posterior_filename, xrange(self.num_windows))

    @memoized_property
    def recover_posterior_filenames(self):
        raise NotImplementedError  # XXX

    @memoized_property
    def params_dirpath(self):
        return self.work_dirpath / SUBDIRNAME_PARAMS

    @memoized_property
    def recover_params_dirpath(self):
        recover_dirpath = self.recover_dirpath
        if recover_dirpath:
            return recover_dirpath / SUBDIRNAME_PARAMS

    @memoized_property
    def window_lens(self):
        return [len(window) for window in self.windows]

    @memoized_property
    def posterior_triangulation_filename(self):
        infilename = self.triangulation_filename

        # either strip ".trifile" off end, or just use the whole filename
        infilename_stem = (infilename.rpartition(SUFFIX_TRIFILE)[0]
                           or infilename)

        res = extjoin(infilename_stem, EXT_POSTERIOR, EXT_TRIFILE)

        clique_indices = self.posterior_clique_indices

        # XXX: this is a fairly hacky way of doing it and will not
        # work if the triangulation file changes from what GMTK
        # generates. probably need to key on tokens rather than lines
        with open(infilename) as infile:
            with open(res, "w") as outfile:
                print >>outfile, COMMENT_POSTERIOR_TRIANGULATION
                rewriter = rewrite_strip_comments(infile, outfile)

                consume_until(rewriter, "@@@!!!TRIFILE_END_OF_ID_STRING!!!@@@")
                consume_until(rewriter, "CE_PARTITION")

                components_indexed = enumerate(POSTERIOR_CLIQUE_INDICES)
                for component_index, component in components_indexed:
                    clique_index = rewrite_cliques(rewriter, component_index,
                                                   self.output_label)
                    clique_indices[component] = clique_index

                for line in rewriter:
                    pass

        return res

    @memoized_property
    def output_dirpath(self):
        return self.make_output_dirpath("o", self.instance_index)

    @memoized_property
    def error_dirpath(self):
        return self.make_output_dirpath("e", self.instance_index)

    @memoized_property
    def use_dinucleotide(self):
        return TRACK_DINUCLEOTIDE in self.tracks

    @memoized_property
    def num_int_cols(self):
        if not USE_MFSDG or self.resolution > 1:
            res = self.num_track_groups
        else:
            res = 0

        if self.use_dinucleotide:
            res += NUM_SEQ_COLS
        if self.supervision_type != SUPERVISION_UNSUPERVISED:
            res += 1

        return res

    @memoized_property
    def bed_filename(self):
        if self.num_worlds == 1:
            basename = BED_FILEBASENAME
        else:
            basename = BED_FILEBASEFMT

        return self.work_dirpath / basename

    @memoized_property
    def bedgraph_filename(self):
        if self.num_worlds == 1:
            basename = BEDGRAPH_FILEBASENAME
        else:
            basename = BEDGRAPH_FILEBASEFMT

        return self.work_dirpath / basename

    @memoized_property
    def train_prog(self):
        return self.prog_factory(EM_TRAIN_PROG)

    @memoized_property
    def seg_countdowns_initial(self):
        table = self.seg_table

        starts = table[:, OFFSET_START]
        ends = table[:, OFFSET_END]
        steps = table[:, OFFSET_STEP]

        # XXX: need to assert that ends are either 0 or are always
        # greater than starts

        # starts and ends must all be divisible by steps
        assert not (starts % steps).any()
        assert not (ends % steps).any()

        # // = floor division
        seg_countdowns_start = starts // steps

        # need minus one to guarantee maximum
        seg_countdowns_end = (ends // steps) - 1

        seg_countdowns_both = vstack([seg_countdowns_start,
                                      seg_countdowns_end])

        return seg_countdowns_both.max(axis=0)

    @memoized_property
    def card_seg_countdown(self):
        return self.seg_countdowns_initial.max() + 1

    @memoized_property
    def num_track_groups(self):
        return len(self.track_groups)

    @memoized_property
    def num_windows(self):
        return len(self.windows)

    @memoized_property
    def num_bases(self):
        return sum(self.window_lens)

    @memoized_property
    def supervision_type(self):
        if self.supervision_filename:
            return SUPERVISION_SEMISUPERVISED
        else:
            return SUPERVISION_UNSUPERVISED

    @memoized_property
    def world_track_indexes(self):
        """
        Track indexes for a particular world.
        """
        return [[track.index for track in world]
                for world in zip(*self.track_groups)]

    @memoized_property
    def num_worlds(self):
        # XXX: add support for some heads having only one trackname
        # that is repeated

        track_groups = self.track_groups
        if not track_groups:  # use all the data in the archive
            return 1

        res = len(track_groups[0])

        assert all(len(track_group) == res for track_group in track_groups)

        return res

    @memoized_property
    def instance_make_new_params(self):
        """
        should I make new parameters in each instance?
        """
        return self.num_instances > 1 or isinstance(self.num_segs, slice)

    @memoized_property
    def num_segs_range(self):
        return slice2range(self.num_segs)

    def check_world_fmt(self, attr):
        """ensure that all options that need a template have it
        """
        value = getattr(self, attr)
        if value is None:
            return

        try:
            value % 0
        except TypeError:
            raise TypeError("%s for use with multiple worlds must contain "
                            "one format string character such as %%s" % attr)

    def transform(self, num):
        if self.distribution == DISTRIBUTION_ASINH_NORMAL:
            return arcsinh(num)
        else:
            return num

    def make_cpp_options(self, input_params_filename=None,
                         output_params_filename=None):
        directives = {}

        if input_params_filename:
            directives["INPUT_PARAMS_FILENAME"] = input_params_filename

        if output_params_filename:
            directives["OUTPUT_PARAMS_FILENAME"] = output_params_filename

        # prevent supervised variable from being inherited from train task
        if self.identify:
            directives["CARD_SUPERVISIONLABEL"] = CARD_SUPERVISIONLABEL_NONE

        directives["CARD_SEG"] = self.num_segs
        directives["CARD_SUBSEG"] = self.num_subsegs
        directives["CARD_FRAMEINDEX"] = self.max_frames
        directives["SEGTRANSITION_WEIGHT_SCALE"] = \
            self.segtransition_weight_scale

        res = " ".join(CPP_DIRECTIVE_FMT % item
                       for item in directives.iteritems())

        if res:
            return res

        # default: return None

    def load_log_likelihood(self):
        with open(self.log_likelihood_filename) as infile:
            log_likelihood = float(infile.read().strip())

        with open(self.log_likelihood_tab_filename, "a") as logfile:
            print >>logfile, str(log_likelihood)

        return log_likelihood

    def make_filename(self, *exts, **kwargs):
        """
        makes a filename by joining together exts

        kwargs:
        dirname: top level directory (default self.work_dirname)
        subdirname: next level directory
        """
        filebasename = extjoin_not_none(*exts)

        # add subdirname if it exists
        return path(kwargs.get("dirname", self.work_dirname)) \
            / kwargs.get("subdirname", "") \
            / filebasename

    def set_tracknames(self, genome):
        """Set up track groups if not done already.

        Add index in Genomedata file for each data track.
        """
        tracks = self.tracks
        if not tracks:
            ## default: use all tracks in archive
            for trackname in genome.tracknames_continuous:
                self.add_track_group([trackname])

        # set indexes for each track
        for track in tracks:
            if not track.is_data:
                continue

            track.index = genome.index_continuous(track.name_unquoted)

        if not any(track.is_data for track in tracks):
            self.float_filelistpath = None

        # assert: none of the quoted tracknames are the same
        if __debug__:
            tracknames_quoted = [track.name for track in tracks]
            assert len(tracknames_quoted) == len(frozenset(tracknames_quoted))

    def get_last_params_filename(self, params_filename):
        if params_filename is not None and path(params_filename).exists():
            return params_filename

        # otherwise, None is returned by default. if it doesn't exist,
        # then it's actually a new filename, but the only time this
        # will be used is when new is not set. And this will only
        # happen from the master thread.

    def make_params_filename(self, instance_index=None, dirname=None):
        if dirname is None:
            dirname = self.work_dirname

        return self.make_filename(PREFIX_PARAMS, instance_index, EXT_PARAMS,
                                  dirname=dirname,
                                  subdirname=SUBDIRNAME_PARAMS)

    def get_params_filename(self, instance_index=None, new=False):
        # this is an unexpected corner case for now
        assert not (instance_index is None and new)

        params_filenames = self.params_filenames
        num_params_filenames = len(params_filenames)

        if instance_index is None and num_params_filenames == 1:
            # special case if there is only one param filename set
            # otherwise generate "params.params" anew
            params_filename = params_filenames[0]
        elif (instance_index is not None
              and num_params_filenames > instance_index):
            params_filename = params_filenames[instance_index]
        else:
            params_filename = None

        last_params_filename = self.get_last_params_filename(params_filename)

        # make new filenames when new is set, or params_filename is
        # not set, or the file already exists and we are training
        if (new or not params_filename
                or (self.train and path(params_filename).exists())):
            params_filename = self.make_params_filename(instance_index)

        return params_filename, last_params_filename

    def set_params_filename(self, instance_index=None, new=False):
        """
        None means the final params file, not for any particular thread
        """
        # if this is not run and params_filename is
        # unspecified, then it won't be passed to gmtkViterbiNew

        self.params_filename, self.last_params_filename = \
            self.get_params_filename(instance_index, new)

    def make_log_likelihood_tab_filename(self, instance_index, dirname):
        return self.make_filename(PREFIX_LIKELIHOOD, instance_index, EXT_TAB,
                                  dirname=dirname,
                                  subdirname=SUBDIRNAME_LOG)

    def set_log_likelihood_filenames(self, instance_index=0, new=False):
        if new or not self.log_likelihood_filename:
            log_likelihood_filename = \
                self.make_filename(PREFIX_LIKELIHOOD, instance_index,
                                   EXT_LIKELIHOOD,
                                   subdirname=SUBDIRNAME_LIKELIHOOD)

            self.log_likelihood_filename = log_likelihood_filename

            self.log_likelihood_tab_filename = \
                self.make_log_likelihood_tab_filename(instance_index,
                                                      self.work_dirname)

    def make_output_dirpath(self, dirname, instance_index):
        res = self.work_dirpath / "output" / dirname / str(instance_index)
        self.make_dir(res)

        return res

    def make_dir(self, dirname, clobber=None):
        if clobber is None:
            clobber = self.clobber

        dirpath = path(dirname)

        if clobber:
            # just always try to delete it
            try:
                dirpath.rmtree()
            except OSError, err:
                if err.errno != ENOENT:
                    raise
        try:
            dirpath.makedirs()
        except OSError, err:
            # if the error is because directory exists, but it's
            # empty, then do nothing
            if (err.errno != EEXIST or not dirpath.isdir() or
                    dirpath.listdir()):
                raise

    def make_subdir(self, subdirname):
        self.make_dir(self.work_dirpath / subdirname)

    def make_subdirs(self, subdirnames):
        for subdirname in subdirnames:
            self.make_subdir(subdirname)

    def make_obs_filelistpath(self, ext):
        return make_filelistpath(self.obs_dirpath, ext)

    def save_resource(self, resname, subdirname=""):
        orig_filename = data_filename(resname)

        orig_filepath = path(orig_filename)
        dirpath = self.work_dirpath / subdirname

        orig_filepath.copy(dirpath)
        return dirpath / orig_filepath.name

    def save_include(self):
        # XXX: can this become a memoized property?
        # We may need to write the file even if it is specified
        aux_dirpath = self.work_dirpath / SUBDIRNAME_AUX

        self.gmtk_include_filename, self.gmtk_include_filename_is_new = \
            IncludeSaver(self)(self.gmtk_include_filename, aux_dirpath,
                               self.clobber)

    def subset_metadata_attr(self, genome, name, reducer=sum):
        """subset a single metadata attribute to only the used tracks,
        grouping things in the same track groups together
        """
        attr = getattr(genome, name)

        track_groups = self.track_groups

        shape = len(track_groups)
        subset_array = empty(shape, attr.dtype)

        for track_group_index, track_group in enumerate(track_groups):
            track_indexes = [track.index for track in track_group]
            subset_array[track_group_index] = reducer(attr[track_indexes])

        setattr(self, name, subset_array)

    def subset_metadata(self, genome):
        """limits all the metadata attributes to only tracks that are used
        """
        subset_metadata_attr = self.subset_metadata_attr
        subset_metadata_attr(genome, "mins", min)
        subset_metadata_attr(genome, "sums")
        subset_metadata_attr(genome, "sums_squares")
        subset_metadata_attr(genome, "num_datapoints")

    def save_input_master(self, instance_index=None, new=False):
        if new:
            input_master_filename = None
        else:
            input_master_filename = self.input_master_filename

        self.input_master_filename, input_master_filename_is_new = \
            InputMasterSaver(self)(input_master_filename, self.params_dirpath,
                                   self.clobber, instance_index)

    def load_supervision(self):
        # The semi-supervised mode changes the DBN structure so there is an
        # additional "supervisionLabel" observed variable at every frame. This
        # can then be used to deterministically force the hidden state to have
        # a certain value at certain positions. From the Segway application's
        # point of view, absolutely everything else is the same--it works just
        # like unsupervised segmentation with an extra observed variable and
        # slightly different. GMTK does all the magic here (and from GMTK's
        # point of view, it's just a slightly different structure with a
        # different observed variable).
        #
        # The *semi* part of semi-supervised is that you can do this only at
        # certain positions and leave the rest of the genome unsupervised.

        supervision_type = self.supervision_type
        if supervision_type == SUPERVISION_UNSUPERVISED:
            return

        assert supervision_type == SUPERVISION_SEMISUPERVISED

        # defaultdict of list of ints
        # key: chrom
        # value: list of ints (label as number)
        supervision_labels = defaultdict(list)

        # defaultdict of lists of tuples
        # key: chrom
        # value: list of tuples (start, end)
        supervision_coords = defaultdict(list)

        with open(self.supervision_filename) as supervision_file:
            for datum in read_native(supervision_file):
                chrom = datum.chrom
                start = datum.chromStart
                end = datum.chromEnd

                check_overlapping_supervision_labels(start, end, chrom,
                                                     supervision_coords)

                supervision_coords[chrom].append((start, end))
                supervision_labels[chrom].append(int(datum.name))

        max_supervision_label = max(max(labels)
                                    for labels
                                    in supervision_labels.itervalues())

        self.supervision_coords = supervision_coords
        self.supervision_labels = supervision_labels

        self.tracks.append(TRACK_SUPERVISIONLABEL)
        self.card_supervision_label = (max_supervision_label + 1 +
                                       SUPERVISION_LABEL_OFFSET)

    def save_structure(self):
        self.structure_filename, _ = \
            StructureSaver(self)(self.structure_filename, self.work_dirname,
                                 self.clobber)

    def save_observations_params(self):
        # XXX: these expect different filepaths
        assert not ((self.identify or self.posterior) and self.train)

        self.load_supervision()

        # need to open Genomedata archive first in order to finalize
        # tracks and track_groups
        with Genome(self.genomedataname) as genome:
            self.set_tracknames(genome)

            observations = Observations(self)
            observations.locate_windows(genome)

            self.windows = observations.windows
            ## XXX: does this need to be done before save()?
            self.subset_metadata(genome)

            observations.save(genome)

        self.float_filepaths = observations.float_filepaths
        self.int_filepaths = observations.int_filepaths

        if self.train:
            self.set_log_likelihood_filenames()

        self.save_include()
        self.set_params_filename()
        self.save_structure()

    def copy_results(self, name, src_filename, dst_filename):
        if dst_filename:
            copy2(src_filename, dst_filename)
        else:
            dst_filename = src_filename

        setattr(self, name, dst_filename)

    def prog_factory(self, prog):
        """
        allows dry_run
        """
        # XXX: this poisons a global variable
        prog.dry_run = self.dry_run

        return prog

    def make_acc_filename(self, instance_index, window_index):
        return self.make_filename(PREFIX_ACC, instance_index, window_index,
                                  EXT_BIN, subdirname=SUBDIRNAME_ACC)

    def make_posterior_filename(self, window_index):
        return self.make_filename(PREFIX_POSTERIOR, window_index, EXT_BED,
                                  subdirname=SUBDIRNAME_POSTERIOR)

    def make_job_name_train(self, instance_index, round_index, window_index):
        return "%s%d.%d.%s.%s.%s" % (PREFIX_JOB_NAME_TRAIN, instance_index,
                                     round_index, window_index,
                                     self.work_dirpath.name, self.uuid)

    def make_job_name_identify(self, prefix, window_index):
        return "%s%d.%s.%s" % (prefix, window_index, self.work_dirpath.name,
                               self.uuid)

    def make_gmtk_kwargs(self):
        """
        shared args to gmtkEMtrain, gmtkViterbi, gmtkJT
        """
        res = dict(strFile=self.structure_filename,
                   verbosity=self.verbosity,
                   island=ISLAND,
                   componentCache=COMPONENT_CACHE,
                   deterministicChildrenStore=DETERMINISTIC_CHILDREN_STORE,
                   jtFile=self.jt_info_filename,
                   obsNAN=True)

        if ISLAND:
            res["base"] = ISLAND_BASE
            res["lst"] = ISLAND_LST

        if HASH_LOAD_FACTOR is not None:
            res["hashLoadFactor"] = HASH_LOAD_FACTOR

        # XXX: dinucleotide-only won't work, because it has no float data
        assert (self.float_filelistpath
                and any(track.is_data for track in self.tracks))

        if self.float_filelistpath:
            res.update(of1=self.float_filelistpath,
                       fmt1="binary",
                       nf1=self.num_track_groups,
                       ni1=0,
                       iswp1=SWAP_ENDIAN)

        if self.int_filelistpath and self.num_int_cols:
            res.update(of2=self.int_filelistpath,
                       fmt2="binary",
                       nf2=0,
                       ni2=self.num_int_cols,
                       iswp2=SWAP_ENDIAN)

        return res

    def window_lens_sorted(self, reverse=True):
        """
        yields (window_index, window_mem_usage)

        if reverse: sort windows by decreasing size, so the most
        difficult windows are dropped in the queue first
        """
        window_lens = self.window_lens

        # XXX: use key=itemgetter(2) and enumerate instead of this silliness
        zipper = sorted(izip(window_lens, count()), reverse=reverse)

        # XXX: use itertools instead of a generator
        for window_len, window_index in zipper:
            yield window_index, window_len

    def log_cmdline(self, cmdline, args=None):
        if args is None:
            args = cmdline

        _log_cmdline(self.cmdline_short_file, cmdline)
        _log_cmdline(self.cmdline_long_file, args)

    def calc_tmp_usage_obs(self, num_frames, prog):
        if prog not in TMP_OBS_PROGS:
            return 0

        return num_frames * self.num_track_groups * SIZEOF_FRAME_TMP

    def calc_tmp_usage(self, num_frames, prog):
        return self.calc_tmp_usage_obs(num_frames, prog) + TMP_USAGE_BASE

    def queue_gmtk(self, prog, kwargs, job_name, num_frames,
                   output_filename=None, prefix_args=[]):
        gmtk_cmdline = prog.build_cmdline(options=kwargs)

        if prefix_args:
            # remove the command name itself from the passed arguments
            # XXX: this is ugly
            args = prefix_args + gmtk_cmdline[1:]
        else:
            args = gmtk_cmdline

        # this doesn't include use of segway-wrapper, which takes the
        # memory usage as an argument, and may be run multiple times
        self.log_cmdline(gmtk_cmdline, args)

        if self.dry_run:
            return None

        session = self.session
        job_tmpl = session.createJobTemplate()

        job_tmpl.jobName = job_name
        job_tmpl.remoteCommand = ENV_CMD
        job_tmpl.args = map(str, args)

        # this is going to cause problems on heterogeneous systems
        environment = environ.copy()
        try:
            # this causes errors
            del environment["PYTHONINSPECT"]
        except KeyError:
            pass
        job_tmpl.jobEnvironment = environment

        if output_filename is None:
            output_filename = self.output_dirpath / job_name
        error_filename = self.error_dirpath / job_name

        job_tmpl.blockEmail = True

        job_tmpl.nativeSpecification = make_native_spec(*self.user_native_spec)

        set_cwd_job_tmpl(job_tmpl)

        tmp_usage = self.calc_tmp_usage(num_frames, prog)

        job_tmpl_factory = JobTemplateFactory(job_tmpl,
                                              tmp_usage,
                                              self.mem_usage_progression,
                                              output_filename,
                                              error_filename)

        mem_usage_key = (prog.prog, self.num_segs, num_frames)

        # XXXopt: should be able to calculate exactly the first
        # trial_index to start with, need to at least be able to load
        # data into RAM

        # XXX: should not have MemoryErrors

        return RestartableJob(session, job_tmpl_factory, self.global_mem_usage,
                              mem_usage_key)

    def queue_train(self, instance_index, round_index, window_index,
                    num_frames=0, **kwargs):
        """this calls Runner.queue_gmtk()

        if num_frames is not specified, then it is set to 0, where
        everyone will share their min/max memory usage. Used for calls
        from queue_train_bundle()
        """
        kwargs["inputMasterFile"] = self.input_master_filename

        name = self.make_job_name_train(instance_index, round_index,
                                        window_index)

        return self.queue_gmtk(self.train_prog, kwargs, name, num_frames)

    def queue_train_parallel(self, input_params_filename, instance_index,
                             round_index, **kwargs):
        kwargs["cppCommandOptions"] = \
            self.make_cpp_options(input_params_filename)

        res = RestartableJobDict(self.session, self.job_log_file)

        make_acc_filename_custom = partial(self.make_acc_filename,
                                           instance_index)

        for window_index, window_len in self.window_lens_sorted():
            acc_filename = make_acc_filename_custom(window_index)
            kwargs_window = dict(trrng=window_index, storeAccFile=acc_filename,
                                 **kwargs)

            # -dirichletPriors T only on the first window
            kwargs_window["dirichletPriors"] = (window_index == 0)

            if self.is_in_reversed_world(window_index):
                kwargs_window["gpr"] = REVERSE_GPR

            num_frames = self.window_lens[window_index]

            restartable_job = self.queue_train(instance_index, round_index,
                                               window_index, num_frames,
                                               **kwargs_window)
            res.queue(restartable_job)

        return res

    def queue_train_bundle(self, input_params_filename, output_params_filename,
                           instance_index, round_index, **kwargs):
        """bundle step: take parallel accumulators and combine them
        """
        acc_filename = self.make_acc_filename(instance_index,
                                              GMTK_INDEX_PLACEHOLDER)

        cpp_options = self.make_cpp_options(input_params_filename,
                                            output_params_filename)

        last_window = self.num_windows - 1

        kwargs = dict(outputMasterFile=self.output_master_filename,
                      cppCommandOptions=cpp_options,
                      trrng="nil",
                      loadAccRange="0:%s" % last_window,
                      loadAccFile=acc_filename,
                      **kwargs)

        restartable_job = self.queue_train(instance_index, round_index,
                                           NAME_BUNDLE_PLACEHOLDER, **kwargs)

        res = RestartableJobDict(self.session, self.job_log_file)
        res.queue(restartable_job)

        return res

    def get_posterior_clique_print_ranges(self):
        res = {}

        for clique, clique_index in self.posterior_clique_indices.iteritems():
            range_str = "%d:%d" % (clique_index, clique_index)
            res[clique + "CliquePrintRange"] = range_str

        return res

    def set_triangulation_filename(self, num_segs=None, num_subsegs=None):
        if num_segs is None:
            num_segs = self.num_segs

        if num_subsegs is None:
            num_subsegs = self.num_subsegs

        if (self.triangulation_filename_is_new
                or not self.triangulation_filename):
            self.triangulation_filename_is_new = True

            structure_filebasename = path(self.structure_filename).name
            triangulation_filebasename = \
                extjoin(structure_filebasename, str(num_segs),
                        str(num_subsegs), EXT_TRIFILE)

            self.triangulation_filename = (self.triangulation_dirpath
                                           / triangulation_filebasename)

        # print >>sys.stderr, ("setting triangulation_filename = %s"
        #                     % self.triangulation_filename)

    def run_triangulate_single(self, num_segs, num_subsegs=None):
        # print >>sys.stderr, "running triangulation"
        prog = self.prog_factory(TRIANGULATE_PROG)

        self.set_triangulation_filename(num_segs, num_subsegs)

        cpp_options = self.make_cpp_options()
        kwargs = dict(strFile=self.structure_filename,
                      cppCommandOptions=cpp_options,
                      outputTriangulatedFile=self.triangulation_filename,
                      verbosity=self.verbosity)

        # XXX: need exist/clobber logic here
        # XXX: repetitive with queue_gmtk
        self.log_cmdline(prog.build_cmdline(options=kwargs))

        prog(**kwargs)

    def run_triangulate(self):
        for num_segs in self.num_segs_range:
            self.run_triangulate_single(num_segs)

    def run_train_round(self, instance_index, round_index, **kwargs):
        """
        returns None: normal
        returns not None: abort
        """
        last_params_filename = self.last_params_filename
        curr_params_filename = extjoin(self.params_filename, str(round_index))

        restartable_jobs = \
            self.queue_train_parallel(last_params_filename, instance_index,
                                      round_index, **kwargs)
        restartable_jobs.wait()

        restartable_jobs = \
            self.queue_train_bundle(last_params_filename, curr_params_filename,
                                    instance_index, round_index,
                                    llStoreFile=self.log_likelihood_filename,
                                    **kwargs)
        restartable_jobs.wait()

        self.last_params_filename = curr_params_filename

    def run_train_instance(self):
        self.set_triangulation_filename()

        # make new files if there is more than one instance
        new = self.instance_make_new_params

        instance_index = self.instance_index
        self.set_log_likelihood_filenames(instance_index, new)
        self.set_params_filename(instance_index, new)

        # get previous (or initial) values
        last_log_likelihood, log_likelihood, round_index = \
            self.make_instance_initial_results()

        if round_index == 0:
            # if round > 0, this is set by self.recover_train_instance()
            self.save_input_master(instance_index, new)

        kwargs = dict(objsNotToTrain=self.dont_train_filename,
                      maxEmIters=1,
                      lldp=LOG_LIKELIHOOD_DIFF_FRAC * 100.0,
                      triFile=self.triangulation_filename,
                      **self.make_gmtk_kwargs())

        if self.dry_run:
            self.run_train_round(self.instance_index, round_index, **kwargs)
            return Results(None, None, None, None, None)

        return self.progress_train_instance(last_log_likelihood,
                                            log_likelihood,
                                            round_index, kwargs)

    def progress_train_instance(self, last_log_likelihood, log_likelihood,
                                round_index, kwargs):
        while (round_index < self.max_em_iters and
               is_training_progressing(last_log_likelihood, log_likelihood)):
            self.run_train_round(self.instance_index, round_index, **kwargs)

            last_log_likelihood = log_likelihood
            log_likelihood = self.load_log_likelihood()
            round_index += 1

        # log_likelihood, num_segs and a list of src_filenames to save
        return Results(log_likelihood, self.num_segs,
                       self.input_master_filename, self.last_params_filename,
                       self.log_likelihood_filename)

    def save_train_options(self):
        filename = self.make_filename(TRAIN_FILEBASENAME)

        with open(filename, "w") as tabfile:
            writer = ListWriter(tabfile)
            writer.writerow(TRAIN_FIELDNAMES)

            for name, typ in sorted(TRAIN_OPTION_TYPES.iteritems()):
                value = getattr(self, name)
                if isinstance(typ, list):
                    for item in value:
                        writer.writerow([name, item])
                else:
                    writer.writerow([name, value])

    def load_train_options(self, traindirname):
        """
        load options from training and convert to appropriate type
        """
        filename = path(traindirname) / TRAIN_FILEBASENAME

        with open(filename) as tabfile:
            reader = DictReader(tabfile)

            for row in reader:
                name = row["name"]
                value = row["value"]

                typ = TRAIN_OPTION_TYPES[name]
                if isinstance(typ, list):
                    assert len(typ) == 1
                    item_typ = typ[0]
                    getattr(self, name).append(item_typ(value))
                else:
                    setattr(self, name, typ(value))

        if self.params_filename is not None:
            self.params_filenames = [self.params_filename]

    def setup_train(self):
        """
        return value: dst_filenames
        """
        assert self.num_instances >= 1

        # save the destination file for input_master as we will be
        # generating new input masters for each start

        # must be before file creation. Otherwise
        # input_master_filename_is_new will be wrong
        input_master_filename, input_master_filename_is_new = \
            InputMasterSaver(self)(self.input_master_filename,
                                   self.params_dirpath, self.clobber)

        self.input_master_filename = input_master_filename

        # should I make new parameters in each instance?
        if not self.instance_make_new_params:
            self.save_input_master()

        ## save file locations to tab-delimited file
        self.save_train_options()

        if not input_master_filename_is_new:
            # do not overwrite existing file
            input_master_filename = None

        return [input_master_filename, self.params_filename,
                self.log_likelihood_filename]

    def get_thread_run_func(self):
        if len(self.num_segs_range) > 1 or self.num_instances > 1:
            return self.run_train_multithread
        else:
            return self.run_train_singlethread

    def finish_train(self, instance_params, dst_filenames):
        if self.instance_make_new_params:
            self.proc_train_results(instance_params, dst_filenames)
        elif not self.dry_run:
            # only one instance
            assert len(instance_params) == 1
            last_params_filename = instance_params[0].params_filename
            copy2(last_params_filename, self.params_filename)

            # always overwrite params.params
            copy2(last_params_filename, self.make_params_filename())

    def run_train(self):
        dst_filenames = self.setup_train()

        run_train_func = self.get_thread_run_func()

        ## this is where the actual training takes place
        instance_params = run_train_func(self.num_segs_range)

        self.finish_train(instance_params, dst_filenames)

    def run_train_singlethread(self, num_segs_range):
        # having a single-threaded version makes debugging much easier
        with Session() as session:
            self.session = session
            self.instance_index = 0
            res = [self.run_train_instance()]

        self.session = None

        return res

    def run_train_multithread(self, num_segs_range):
        seg_instance_indexes = xrange(self.num_instances)
        enumerator = enumerate(product(num_segs_range, seg_instance_indexes))

        # ensure memoization before threading
        self.triangulation_dirpath
        self.jt_info_filename
        self.include_coords
        self.exclude_coords
        self.card_seg_countdown
        self.obs_dirpath
        self.float_filelistpath
        self.int_filelistpath
        self.float_tabfilepath
        self.gmtk_include_filename_relative
        self.means
        self.vars
        self.dont_train_filename
        self.output_master_filename
        self.params_dirpath
        self.window_lens
        self.use_dinucleotide
        self.num_int_cols
        self.train_prog

        threads = []
        with Session() as session:
            try:
                for instance_index, instance_features in enumerator:
                    num_seg, seg_instance_index = instance_features
                    # print >>sys.stderr, (
                    #    "instance_index %s, num_seg %s, seg_instance_index %s"
                    #    % (instance_index, num_seg, seg_instance_index))
                    thread = TrainThread(self, session, instance_index,
                                         num_seg)
                    thread.start()
                    threads.append(thread)

                    # let all of one thread's jobs drop in the queue
                    # before you do the next one
                    # XXX: using some sort of semaphore would be better
                    # XXX: using a priority option to the system would be best
                    sleep(THREAD_START_SLEEP_TIME)

                # list of tuples(log_likelihood, input_master_filename,
                #                params_filename)
                instance_params = []
                for thread in threads:
                    while thread.isAlive():
                        # XXX: KeyboardInterrupts only occur if there is a
                        # timeout specified here. Is this a Python bug?
                        thread.join(JOIN_TIMEOUT)

                    # this will get AttributeError if the thread failed and
                    # therefore did not set thread.result
                    try:
                        thread_result = thread.result
                    except AttributeError:
                        raise AttributeError("""\
Training instance %s failed. See previously printed error for reason.
Final params file will not be written. Rerun the instance or use segway-winner
to find the winning instance anyway.""" % thread.instance_index)
                    else:
                        instance_params.append(thread_result)
            except KeyboardInterrupt:
                self.interrupt_event.set()
                for thread in threads:
                    thread.join()

                raise

        return instance_params

    def proc_train_results(self, instance_params, dst_filenames):
        if self.dry_run:
            return

        # finds the min by info_criterion (maximize log_likelihood)
        max_params = max(instance_params)

        self.num_segs = max_params.num_segs
        self.set_triangulation_filename()

        src_filenames = max_params[OFFSET_FILENAMES:]

        if None in src_filenames:
            raise ValueError("all training instances failed")

        assert LEN_TRAIN_ATTRNAMES == len(src_filenames) == len(dst_filenames)

        zipper = zip(TRAIN_ATTRNAMES, src_filenames, dst_filenames)
        for name, src_filename, dst_filename in zipper:
            self.copy_results(name, src_filename, dst_filename)

    def recover_filename(self, resource):
        instance_index = self.instance_index

        # only want "input.master" not "input.0.master" if there is
        # only one instance
        if (not self.instance_make_new_params
                and resource == InputMasterSaver.resource_name):
            instance_index = None

        old_filename = make_default_filename(resource,
                                             self.recover_params_dirpath,
                                             instance_index)

        new_filename = make_default_filename(resource, self.params_dirpath,
                                             instance_index)

        path(old_filename).copy2(new_filename)
        return new_filename

    def recover_train_instance(self, last_log_likelihood, log_likelihood):
        instance_index = self.instance_index
        recover_dirname = self.recover_dirname

        self.input_master_filename = \
            self.recover_filename(InputMasterSaver.resource_name)

        recover_log_likelihood_tab_filepath = \
            path(self.make_log_likelihood_tab_filename(instance_index,
                                                       recover_dirname))

        with open(recover_log_likelihood_tab_filepath) \
                as log_likelihood_tab_file:
            log_likelihoods = [float(line.rstrip())
                               for line in log_likelihood_tab_file.readlines()]

        final_round_index = len(log_likelihoods)
        if final_round_index > 0:
            log_likelihood = log_likelihoods[-1]
        if final_round_index > 1:
            last_log_likelihood = log_likelihoods[-2]

        log_likelihood_tab_filename = self.log_likelihood_tab_filename
        recover_log_likelihood_tab_filepath.copy2(log_likelihood_tab_filename)

        old_params_filename = self.make_params_filename(instance_index,
                                                        recover_dirname)
        new_params_filename = self.params_filename
        for round_index in xrange(final_round_index):
            old_curr_params_filename = extjoin(old_params_filename,
                                               str(round_index))
            new_curr_params_filename = extjoin(new_params_filename,
                                               str(round_index))

            path(old_curr_params_filename).copy2(new_curr_params_filename)

        self.last_params_filename = new_curr_params_filename

        return last_log_likelihood, log_likelihood, final_round_index

    def make_instance_initial_results(self):
        """
        returns last_log_likelihood, log_likelihood, round_index
        -inf, -inf, 0 if there is no recovery--this is also used to set initial
        values
        """
        ## initial values:
        last_log_likelihood = -inf
        log_likelihood = -inf
        final_round_index = 0

        if self.recover_dirpath:
            return self.recover_train_instance(last_log_likelihood,
                                               log_likelihood)

        return last_log_likelihood, log_likelihood, final_round_index

    def recover_viterbi_window(self, window_index):
        """
        returns False if no recovery
                True if recovery
        """
        recover_filenames = self.recover_viterbi_filenames
        if not recover_filenames:
            return False

        recover_filename = recover_filenames[window_index]
        try:
            with open(recover_filename) as oldfile:
                lines = oldfile.readlines()
        except IOError, err:
            if err.errno == ENOENT:
                return False
            else:
                raise

        window = self.windows[window_index]
        window_chrom = window.chrom

        # XXX: duplicative
        row, line_coords = parse_bed4(lines[0])
        (line_chrom, line_start, line_end, seg) = line_coords
        if line_chrom != window_chrom or int(line_start) != window.start:
            return False

        row, line_coords = parse_bed4(lines[-1])
        (line_chrom, line_start, line_end, seg) = line_coords
        if line_chrom != window_chrom or int(line_end) != window.end:
            return False

        # copy the old filename to where the job's output would have
        # landed
        path(recover_filename).copy2(self.viterbi_filenames[window_index])

        print >>sys.stderr, "window %d already complete" % window_index

        return True

    def queue_identify(self, restartable_jobs, window_index, prefix_job_name,
                       prog, kwargs, output_filenames):
        prog = self.prog_factory(prog)
        job_name = self.make_job_name_identify(prefix_job_name, window_index)
        output_filename = output_filenames[window_index]

        kwargs = self.get_identify_kwargs(window_index, kwargs)

        if prog == VITERBI_PROG:
            kind = "viterbi"
        else:
            kind = "posterior"

        # "0" or "1"
        is_reverse = str(int(self.is_in_reversed_world(window_index)))

        window = self.windows[window_index]
        float_filepath = self.float_filepaths[window_index]
        int_filepath = self.int_filepaths[window_index]

        track_indexes = self.world_track_indexes[window.world]
        track_indexes_text = ",".join(map(str, track_indexes))

        prefix_args = [find_executable("segway-task"), "run", kind,
                       output_filename, window.chrom,
                       window.start, window.end, self.resolution, is_reverse,
                       self.num_segs, self.num_subsegs, self.output_label,
                       self.genomedataname, float_filepath, int_filepath,
                       self.distribution, track_indexes_text]
        output_filename = None

        num_frames = self.window_lens[window_index]

        restartable_job = self.queue_gmtk(prog, kwargs, job_name,
                                          num_frames,
                                          output_filename=output_filename,
                                          prefix_args=prefix_args)

        restartable_jobs.queue(restartable_job)

    def get_identify_kwargs(self, window_index, extra_kwargs):
        cpp_command_options = self.make_cpp_options(self.params_filename)

        res = dict(inputMasterFile=self.input_master_filename,
                   cppCommandOptions=cpp_command_options,
                   cliqueTableNormalize="0.0",
                   **self.make_gmtk_kwargs())

        if self.is_in_reversed_world(window_index):
            res["gpr"] = REVERSE_GPR

        res.update(extra_kwargs)

        return res

    def is_in_reversed_world(self, window_index):
        return self.windows[window_index].world in self.reverse_worlds

    def setup_identify_posterior(self):
        self.instance_index = "identify"

        ## setup files
        if not self.input_master_filename:
            warn("Input master not specified. Generating.")
            self.save_input_master()

    def save_identify_posterior(self):
        for world in xrange(self.num_worlds):
            if self.identify:
                IdentifySaver(self)(world)

            if self.posterior:
                PosteriorSaver(self)(world)

    def run_identify_posterior(self):
        self.setup_identify_posterior()

        filenames = dict(identify=self.viterbi_filenames,
                         posterior=self.posterior_filenames)
        
        # if output_label == "subseg" or "full", need to catch
        # superlabel and sublabel output from gmtk
        if self.output_label != "seg":
            VITERBI_REGEX_FILTER = "^(seg|subseg)$"
        else:
            VITERBI_REGEX_FILTER = "^seg$"

        # -: standard output, processed by segway-task
        kwargs = {"identify":
                  dict(triFile=self.triangulation_filename,
                       pVitRegexFilter=VITERBI_REGEX_FILTER,
                       cVitRegexFilter=VITERBI_REGEX_FILTER,
                       eVitRegexFilter=VITERBI_REGEX_FILTER,
                       vitCaseSensitiveRegexFilter=True, mVitValsFile="-"),
                  "posterior":
                  dict(triFile=self.posterior_triangulation_filename,
                       jtFile=self.posterior_jt_info_filename,
                       doDistributeEvidence=True,
                       **self.get_posterior_clique_print_ranges())}

        tasks = []
        if self.identify:
            tasks.append("identify")
        if self.posterior:
            tasks.append("posterior")

        with Session() as session:
            self.session = session
            restartable_jobs = RestartableJobDict(session, self.job_log_file)

            for window_index, window_len in self.window_lens_sorted():
                for task in tasks:
                    if (task == "identify"
                            and self.recover_viterbi_window(window_index)):
                        # XXX: should be able to recover posterior also
                        continue

                    self.queue_identify(restartable_jobs, window_index,
                                        PREFIX_JOB_NAMES[task], PROGS[task],
                                        kwargs[task], filenames[task])

            if self.dry_run:
                return

            restartable_jobs.wait()

        self.save_identify_posterior()

    def make_script_filename(self, prefix):
        return self.make_filename(prefix, EXT_SH, subdirname=SUBDIRNAME_LOG)

    def make_run_msg(self):
        now = datetime.now()
        pkg_desc = working_set.find(Requirement.parse(__package__))
        run_msg = "## %s run %s at %s" % (pkg_desc, self.uuid, now)

        cmdline_top_filename = self.make_script_filename(PREFIX_CMDLINE_TOP)

        with open(cmdline_top_filename, "w") as cmdline_top_file:
            print >>cmdline_top_file, run_msg
            print >>cmdline_top_file
            print >>cmdline_top_file, "cd %s" % maybe_quote_arg(path.getcwd())
            print >>cmdline_top_file, cmdline2text()

        return run_msg

    def run(self):
        """
        main run, after dirname is specified

        this is exposed so that it can be overriden in a subclass

        opens log files, saves parameters, and calls main function
        run_train() or run_identify_posterior()
        """
        # XXXopt: use binary I/O to gmtk rather than ascii for parameters

        self.interrupt_event = Event()

        ## start log files
        self.make_subdir(SUBDIRNAME_LOG)
        run_msg = self.make_run_msg()

        cmdline_short_filename = \
            self.make_script_filename(PREFIX_CMDLINE_SHORT)
        cmdline_long_filename = self.make_script_filename(PREFIX_CMDLINE_LONG)
        job_log_filename = self.make_filename(PREFIX_JOB_LOG, EXT_TAB,
                                              subdirname=SUBDIRNAME_LOG)

        self.make_subdirs(SUBDIRNAMES_EITHER)

        if self.train:
            self.make_subdirs(SUBDIRNAMES_TRAIN)

        self.save_observations_params()

        with open(cmdline_short_filename, "w") as self.cmdline_short_file:
            with open(cmdline_long_filename, "w") as self.cmdline_long_file:
                print >>self.cmdline_short_file, run_msg
                print >>self.cmdline_long_file, run_msg

                self.run_triangulate()

                with open(job_log_filename, "w") as self.job_log_file:
                    print >>self.job_log_file, "\t".join(JOB_LOG_FIELDNAMES)

                    if self.train:
                        self.run_train()

                    if self.identify or self.posterior:
                        if self.supervision_filename:
                            raise NotImplementedError  # XXX

                        if not self.dry_run:
                            # resave now that num_segs is determined,
                            # in case you tested multiple num_segs
                            self.save_include()

                        if (self.posterior and (self.recover_dirname
                                                or self.num_worlds != 1)):
                            raise NotImplementedError  # XXX

                        self.run_identify_posterior()

    def __call__(self, *args, **kwargs):
        # XXX: register atexit for cleanup_resources

        work_dirname = self.work_dirname
        if not path(work_dirname).isdir():
            self.make_dir(work_dirname, self.clobber)

        self.run(*args, **kwargs)


def parse_options(args):
    from optplus import OptionParser, OptionGroup

    usage = "%prog [OPTION]... TASK GENOMEDATA TRAINDIR [IDENTIFYDIR]"
    version = "%%prog %s" % __version__
    citation = \
    "Citation: Hoffman MM, Buske OJ, Wang J, Weng Z, Bilmes J, Noble WS.\n" \
    "2012. Unsupervised pattern discovery in human chromatin structure\n" \
    "through genomic segmentation. Nat Methods 9:473-476.\n" \
    "http://dx.doi.org/10.1038/nmeth.1937"

    usage += "\n" + citation

    parser = OptionParser(usage=usage, version=version)

    with OptionGroup(parser, "Data selection") as group:
        group.add_option("-t", "--track", action="append", default=[],
                         metavar="TRACK",
                         help="append TRACK to list of tracks to use, using "
                         " commas to separate tied tracks (default all)")

        group.add_option("--tracks-from", action="load", metavar="FILE",
                         dest="track",
                         help="append tracks from newline-delimited FILE to"
                         " list of tracks to use")

        # This is a 0-based file.
        # I know because ENm008 starts at position 0 in encodeRegions.txt.gz
        group.add_option("--include-coords", metavar="FILE",
                         help="limit to genomic coordinates in FILE"
                         " (default all)")

        # exclude goes after all includes
        group.add_option("--exclude-coords", metavar="FILE",
                         help="filter out genomic coordinates in FILE"
                         " (default none)")

        group.add_option("--resolution", type=int, metavar="RES",
                         help="downsample to every RES bp (default %d)" %
                         RESOLUTION)

    with OptionGroup(parser, "Model files") as group:
        group.add_option("-i", "--input-master", metavar="FILE",
                         help="use or create input master in FILE"
                         " (default %s)" %
                         make_default_filename(InputMasterSaver.resource_name,
                                               DIRPATH_PARAMS))

        group.add_option("-s", "--structure", metavar="FILE",
                         help="use or create structure in FILE (default %s)" %
                         make_default_filename(StructureSaver.resource_name))

        group.add_option("-p", "--trainable-params", action="append",
                         default=[], metavar="FILE",
                         help="use or create trainable parameters in FILE"
                         " (default WORKDIR/params/params.params)")

        group.add_option("--dont-train", metavar="FILE",
                         help="use FILE as list of parameters not to train"
                         " (default %s)" %
                         make_default_filename(RES_DONT_TRAIN, DIRPATH_AUX))

        group.add_option("--seg-table", metavar="FILE",
                         help="load segment hyperparameters from FILE"
                         " (default none)")

        group.add_option("--semisupervised", metavar="FILE",
                         help="semisupervised segmentation with labels in "
                         "FILE (default none)")

    with OptionGroup(parser, "Intermediate files") as group:
        group.add_option("-o", "--observations", metavar="DIR",
                         help="use or create observations in DIR"
                         " (default %s)" %
                         (DIRPATH_WORK_DIR_HELP / SUBDIRNAME_OBS))

        group.add_option("-r", "--recover", metavar="DIR",
                         help="continue from interrupted run in DIR")

    with OptionGroup(parser, "Output files") as group:
        group.add_option("-b", "--bed", metavar="FILE",
                         help="create identification BED track in FILE"
                         " (default WORKDIR/%s)" % BED_FILEBASENAME)

        group.add_option("--bigBed", metavar="FILE",
                         help="specify layered bigBed filename")

    with OptionGroup(parser, "Modeling variables") as group:
        group.add_option("-D", "--distribution", choices=DISTRIBUTIONS,
                         metavar="DIST",
                         help="use DIST distribution"
                         " (default %s)" % DISTRIBUTION_DEFAULT)

        group.add_option("--num-instances", type=int,
                         default=NUM_INSTANCES, metavar="NUM",
                         help="run NUM training instances, randomizing start"
                         " parameters NUM times (default %d)" % NUM_INSTANCES)

        group.add_option("-N", "--num-labels", type=slice, metavar="SLICE",
                         help="make SLICE segment labels"
                         " (default %d)" % NUM_SEGS)

        group.add_option("--num-sublabels", type=int, metavar="NUM",
                         help="make NUM segment sublabels"
                         " (default %d)" % NUM_SUBSEGS)

        group.add_option("--output-label", type=str,
                         help="in the segmentation file, for each coordinate "
                         "print only its superlabel (\"seg\"), only its "
                         "sublabel (\"subseg\"), or both (\"full\")"
                         "  (default %s)" % OUTPUT_LABEL)

        group.add_option("--max-train-rounds", type=int, metavar="NUM",
                         help="each training instance runs a maximum of NUM"
                         " rounds (default %d)" % MAX_EM_ITERS)

        group.add_option("--ruler-scale", type=int, metavar="SCALE",
                         help="ruler marking every SCALE bp (default %d)" %
                         RULER_SCALE)

        group.add_option("--prior-strength", type=float, metavar="RATIO",
                         help="use RATIO times the number of data counts as"
                         " the number of pseudocounts for the segment length"
                         " prior (default %f)" % PRIOR_STRENGTH)

        group.add_option("--segtransition-weight-scale", type=float,
                         metavar="SCALE",
                         help="exponent for segment transition probability "
                         " (default %f)" % SEGTRANSITION_WEIGHT_SCALE)

        group.add_option("--reverse-world", action="append", type=int,
                         default=[], metavar="WORLD",
                         help="reverse sequences in concatenated world WORLD"
                         " (0-based)")

    with OptionGroup(parser, "Technical variables") as group:
        group.add_option("-m", "--mem-usage", default=MEM_USAGE_PROGRESSION,
                         metavar="PROGRESSION",
                         help="try each float in PROGRESSION as the number "
                         "of gibibytes of memory to allocate in turn "
                         "(default %s)" % MEM_USAGE_PROGRESSION)

        group.add_option("-S", "--split-sequences", metavar="SIZE",
                         default=MAX_FRAMES, type=int,
                         help="split up sequences that are larger than SIZE "
                         "bp (default %s)" % MAX_FRAMES)

        group.add_option("-v", "--verbosity", type=int, default=VERBOSITY,
                         metavar="NUM",
                         help="show messages with verbosity NUM"
                         " (default %d)" % VERBOSITY)

        group.add_option("--cluster-opt", action="append", default=[],
                         metavar="OPT",
                         help="specify an option to be passed to the "
                         "cluster manager")

    with OptionGroup(parser, "Flags") as group:
        group.add_option("-c", "--clobber", action="store_true",
                         help="delete any preexisting files and assumes any "
                         "model files specified in options as output to be "
                         "overwritten")
        group.add_option("-n", "--dry-run", action="store_true",
                         help="write all files, but do not run any"
                         " executables")

    options, args = parser.parse_args(args)

    if len(args) < 3:
        parser.error("Expected at least 3 arguments.")
    if args[0] == "train":
        if len(args) != 3:
            parser.error("Expected 3 arguments for the train task.")
    else:
        if len(args) != 4:
            parser.error("Expected 4 arguments for the identify task.")

    return options, args


def main(args=sys.argv[1:]):
    options, args = parse_options(args)

    runner = Runner.fromoptions(args, options)

    return runner()

if __name__ == "__main__":
    sys.exit(main())
