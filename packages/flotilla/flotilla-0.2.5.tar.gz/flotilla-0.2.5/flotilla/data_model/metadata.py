from collections import defaultdict
import sys
import warnings

import matplotlib as mpl
import seaborn as sns

from .base import BaseData, subsets_from_metadata
from ..visualize.color import str_to_color


POOLED_COL = 'pooled'
PHENOTYPE_COL = 'phenotype'
MINIMUM_SAMPLE_SUBSET = 10
OUTLIER_COL = 'outlier'


class MetaData(BaseData):
    def __init__(self, data, phenotype_order=None, phenotype_to_color=None,
                 phenotype_to_marker=None,
                 phenotype_col=PHENOTYPE_COL,
                 pooled_col=POOLED_COL,
                 outlier_col=OUTLIER_COL,
                 predictor_config_manager=None,
                 minimum_sample_subset=MINIMUM_SAMPLE_SUBSET):
        super(MetaData, self).__init__(
            data, outliers=None,
            predictor_config_manager=predictor_config_manager)

        self.phenotype_col = phenotype_col if phenotype_col is not None else \
            self._default_phenotype_col
        self.phenotype_order = phenotype_order
        self.phenotype_to_color = phenotype_to_color
        self.pooled_col = pooled_col
        self.minimum_sample_subset = minimum_sample_subset
        self.outlier_col = outlier_col

        phenotypes_not_in_order = set(self.unique_phenotypes).difference(
            set(self.phenotype_order))

        if len(phenotypes_not_in_order) > 0:
            self.phenotype_order.extend(phenotypes_not_in_order)

        if self.phenotype_col not in self.data:
            sys.stderr.write('The required column name "{}" does not exist in '
                             'the sample metadata. All samples will be '
                             'treated as the same phenotype. You may also '
                             'specify "phenotype_col" in the metadata section '
                             'of the '
                             'datapackage.\n'.format(self.phenotype_col))
            self.data[self.phenotype_col] = 'phenotype'
            self.phenotype_order = None
            self.phenotype_to_color = None

        # Convert color strings to non-default matplotlib colors
        if self.phenotype_to_color is not None:
            # colors = iter(self._colors)
            for phenotype, color in self.phenotype_to_color.iteritems():
                try:
                    color = str_to_color[color]
                except KeyError:
                    pass
                self._phenotype_to_color[phenotype] = color

        self.phenotype_to_marker = phenotype_to_marker
        if self.phenotype_to_marker is not None:
            for phenotype in self.unique_phenotypes:
                try:
                    marker = self.phenotype_to_marker[phenotype]
                except KeyError:
                    sys.stderr.write(
                        '{} does not have marker style, '
                        'falling back on "o" (circle)'.format(phenotype))
                    marker = 'o'
                if marker not in mpl.markers.MarkerStyle.filled_markers:
                    sys.stderr.write(
                        '{} is not a valid matplotlib marker style, '
                        'falling back on "o" (circle)'.format(marker))
                    marker = 'o'
                self.phenotype_to_marker[phenotype] = marker

    @property
    def sample_id_to_phenotype(self):
        return self.data[self.phenotype_col]

    @property
    def unique_phenotypes(self):
        return self.sample_id_to_phenotype.unique()

    @property
    def n_phenotypes(self):
        return len(self.unique_phenotypes)

    @property
    def _default_phenotype_order(self):
        return list(sorted(self.unique_phenotypes))

    @property
    def phenotype_order(self):
        if len(set(self._phenotype_order) & set(self.unique_phenotypes)) > 0:
            return [v for v in self._phenotype_order if
                    v in self.unique_phenotypes]
        else:
            return self._default_phenotype_order

    @phenotype_order.setter
    def phenotype_order(self, value):
        if value is not None:
            self._phenotype_order = value
        else:
            self._phenotype_order = self._default_phenotype_order

    @property
    def phenotype_transitions(self):
        return zip(self.phenotype_order[:-1], self.phenotype_order[1:])

    @property
    def _colors(self):
        return map(mpl.colors.rgb2hex,
                   sns.color_palette('husl', n_colors=self.n_phenotypes))

    @property
    def _default_phenotype_to_color(self):
        colors = iter(self._colors)

        def color_factory():
            return colors.next()

        return defaultdict(color_factory)

    @property
    def phenotype_to_color(self):
        _default_phenotype_to_color = self._default_phenotype_to_color
        all_phenotypes = self._phenotype_to_color.keys()
        all_phenotypes.extend(self.phenotype_order)
        return dict((k, self._phenotype_to_color[k])
                    if k in self._phenotype_to_color else
                    (k, _default_phenotype_to_color[k])
                    for k in all_phenotypes)

    @phenotype_to_color.setter
    def phenotype_to_color(self, value):
        if value is not None:
            self._phenotype_to_color = value
        else:
            sys.stderr.write('No phenotype to color mapping was provided, '
                             'falling back on reasonable defaults.\n')
            self._phenotype_to_color = self._default_phenotype_to_color

    @property
    def phenotype_to_marker(self):
        _default_phenotype_to_marker = defaultdict(lambda: 'o')
        all_phenotypes = self._phenotype_to_marker.keys()
        all_phenotypes.extend(self.phenotype_order)
        return dict((k, self._phenotype_to_marker[k])
                    if k in self._phenotype_to_marker else
                    (k, _default_phenotype_to_marker[k])
                    for k in all_phenotypes)

    @phenotype_to_marker.setter
    def phenotype_to_marker(self, value):
        if value is not None:
            self._phenotype_to_marker = value
        else:
            sys.stderr.write('No phenotype to marker (matplotlib plotting '
                             'symbol) was provided, so each phenotype will be '
                             'plotted as a circle in visualizations.\n')
            self._phenotype_to_marker = dict.fromkeys(self.unique_phenotypes,
                                                      'o')

    @property
    def phenotype_color_order(self):
        return [self.phenotype_to_color[p] for p in self.phenotype_order]

    @property
    def sample_id_to_color(self):
        return dict((sample_id, self.phenotype_to_color[p])
                    for sample_id, p in
                    self.sample_id_to_phenotype.iteritems())

    @property
    def sample_subsets(self):
        return subsets_from_metadata(self.data, self.minimum_sample_subset,
                                     'samples')

    @property
    def phenotype_series(self):
        warnings.warn('MetaData.phenotype_series will be deprecated in 0.3.0')
        return self.data[self.phenotype_col]
