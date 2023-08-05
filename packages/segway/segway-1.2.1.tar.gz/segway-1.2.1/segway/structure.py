#!/usr/bin/env python
from __future__ import division

"""structure.py: write structure file
"""

__version__ = "$Revision$"

## Copyright 2012, 2013 Michael M. Hoffman <michael.hoffman@utoronto.ca>

from itertools import count, izip

from ._util import (resource_substitute, Saver, SUPERVISION_UNSUPERVISED,
                    USE_MFSDG)

MAX_WEIGHT_SCALE = 25


def add_observation(observations, resourcename, **kwargs):
    observations.append(resource_substitute(resourcename)(**kwargs))


def make_weight_scale(scale):
    return "scale %f" % scale


class StructureSaver(Saver):
    resource_name = "segway.str.tmpl"
    copy_attrs = ["num_track_groups", "num_datapoints",
                  "use_dinucleotide", "window_lens", "resolution",
                  "supervision_type", "track_groups",
                  "gmtk_include_filename_relative"]

    def make_weight_spec(self, multiplier):
        resolution = self.resolution
        if resolution == 1:
            return make_weight_scale(multiplier)
        else:
            # weight scale switches on the number of present data
            # points that make a model frame
            return " | ".join(make_weight_scale(index * multiplier)
                              for index in xrange(resolution + 1))

    def make_conditionalparents_spec(self, trackname):
        """
        this defines the parents of every observation
        """

        missing_spec = "CONDITIONALPARENTS_NIL_CONTINUOUS"
        present_spec = 'CONDITIONALPARENTS_OBS ' \
            'using mixture collection("collection_seg_%s") ' \
            'MAPPING_OBS' % trackname

        # The switching parent ("presence__...") is overloaded for
        # both switching weight and switching conditional parents. If
        # resolution > 1, then we repeat the present_spec as many
        # times as necessary to match the cardinality of the switching
        # parent
        return " | ".join([missing_spec] + [present_spec] * self.resolution)

    def make_mapping(self):
        num_track_groups = self.num_track_groups
        num_datapoints = self.num_datapoints

        assert (num_track_groups == len(num_datapoints))

        if self.use_dinucleotide:
            max_num_datapoints_track = sum(self.window_lens)
        else:
            max_num_datapoints_track = num_datapoints.max()

        observation_items = []

        zipper = izip(count(), self.track_groups, num_datapoints)
        for track_index, track_group, num_datapoints_track in zipper:
            trackname = track_group[0].name

            # relates current num_datapoints to total number of
            # possible positions. This is better than making the
            # highest num_datapoints equivalent to 1, because it
            # becomes easier to mix and match different tracks without
            # changing the weights of any of them

            # XXX: this should be done based on the minimum seg len in
            # the seg table instead
            # weight scale cannot be more than MAX_WEIGHT_SCALE to avoid
            # artifactual problems

            weight_multiplier = min(max_num_datapoints_track
                                    / num_datapoints_track, MAX_WEIGHT_SCALE)
            # weight_scale = 1.0
            # assert weight_scale == 1.0

            conditionalparents_spec = \
                self.make_conditionalparents_spec(trackname)
            weight_spec = self.make_weight_spec(weight_multiplier)

            # XXX: should avoid a weight line at all when weight_scale == 1.0
            # might avoid some extra multiplication in GMTK
            add_observation(observation_items, "observation.tmpl",
                            track=trackname, track_index=track_index,
                            presence_index=num_track_groups + track_index,
                            conditionalparents_spec=conditionalparents_spec,
                            weight_spec=weight_spec)

        if USE_MFSDG:
            next_int_track_index = num_track_groups + 1
        else:
            next_int_track_index = num_track_groups * 2

        # XXX: duplicative
        if self.use_dinucleotide:
            add_observation(observation_items, "dinucleotide.tmpl",
                            track_index=next_int_track_index,
                            presence_index=next_int_track_index + 1)
            next_int_track_index += 2

        if self.supervision_type != SUPERVISION_UNSUPERVISED:
            add_observation(observation_items, "supervision.tmpl",
                            track_index=next_int_track_index)
            next_int_track_index += 1

        assert observation_items  # must be at least one track
        observations = "\n".join(observation_items)

        return dict(include_filename=self.gmtk_include_filename_relative,
                    observations=observations)
