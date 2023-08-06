# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals
import itertools

from chanjo import Store
from chanjo.sex_checker import predict_gender
from chanjo.store import Block, BlockData, Interval, IntervalData, Sample, SuperblockData, Interval_Block
import sqlalchemy as sqa
from toolz import concat, groupby, unique
from toolz.curried import get

from .utils import getitem, limit_query, get_columns
from .._compat import itervalues


class Miner(Store):

  """Thin wrapper around the Chanjo Store to expose an extended API.

  Also works as a basic Flask extensions with lazy loading via the
  ``.init_app`` method.

  Args:
    uri (str): path or URI of Chanjo database
    dialect (str): [adapter +] database type
  """

  def __init__(self, uri=None, dialect='sqlite'):
    super(Miner, self).__init__(uri, dialect)

    if uri:
      self.connect(uri, dialect=dialect)

  def init_app(self, app, base_key='CHANJO_'):
    """Configure API (Flask style) after lazy initialization.

    Args:
      app (Flask app): Flask app instance
      base_key (str): namespace to look for under ``app.config``

    Returns:
      object: ``self`` for chainability
    """
    uri = app.config.get(base_key + 'DB') or 'coverage.sqlite3'
    dialect = app.config.get(base_key + 'DIALECT') or 'sqlite'

    self.connect(uri, dialect=dialect)

    return self

  def samples(self, group=None):
    """Fetch samples from the database.

    Args:
      group (str, optional): limit samples to within a group

    Returns:
      query: query for samples, possibly limited by a group ID
    """
    # initiate base query for all sample data (as objects)
    # order by the ID column, the same as always
    query = self.query(Sample).order_by(Sample.id)

    if group:
      # filter samples by a given group
      query = query.filter(Sample.group_id == group)

    # return the non-exucuted query
    return query

  def get_set_info(self, attributes=None, subset=None,
                     element_class='superblock'):
    """Fetch (sub)set and attributes loaded in the database.

    Args:
      attribute (list, optional): List columns in database. Limit to
                                  subset using first attribute element.
                                  Group by first attribute element.
      subset (str, optional): Limit query to subset
      element_class (str, optional): Id of the element class e.g.
                                     'superblock'

    Returns:
      list: Results (sub)set with attributes from element_class 
            grouped by first attribute
    """
    # Fetch the requested data class ORM
    data_class = self.get('class', element_class)
    
    # Populate attribute with column names if not supplied
    if attributes is None:
      c = data_class.__table__.columns
      attributes = c.keys()

    # Fetch columns from class
    columns = get_columns(attributes, data_class)
    query = self.query(*columns)

    # Filter for subset
    if subset:
      query = query.filter(columns[0].in_(subset))

    # Aggregate result by first attribute
    query = query.group_by(columns[0]) 
    
    # Return query
    return query

  def element_coverage(self, attribute="coverage", samples=None, threshold=10,
                       element_class="superblock_data"):
    """Fetch all elements below threshold for samples
    Args:
      attribute (str, optional): Element attribute to apply threshold for
                                 samples (list, optional): Samples to be queried
      threshold (int, optional): Elements below threshold are returned
      element_class (str, optional): Id of the element class e.g. 'superblock'

    Returns:
      list: Intersect of elements for all samples
    """
    data_class = self.get('class', element_class)
    
    # Collect all samples if none were supplied
    if samples is None:
      samples = self.fetch_samples_list()

    # Holds the queries for each sample
    elements_per_sample = []

    # Irrespective of samples i.e. all genes below threshold for later intersect
    elements = self.query(data_class.parent_id).filter(getattr(data_class, attribute) <= threshold)\
    .group_by(data_class.parent_id)
    
    for sample in samples:
      # Fetch all elements below threshold for each sample
      query = self.query(data_class.parent_id).filter(getattr(data_class, attribute) <= threshold,\
      data_class.sample_id == sample).group_by(data_class.parent_id)
      # Add to list for later intersect
      elements_per_sample.append(query)
    
    # Intersect all elements for all samples
    for query in elements_per_sample: 
      elements = elements.intersect(query)

    # Return list of elements
    return elements

  def interval_to_block(self, subset=None):
    """Fetch all intervals associated with block (sub)set
    Args:
    subset  (str, optional): Limit query to subset
    Returns:
    list:   Result of query
    """
    query = self.query(IntervalData.parent_id, Block.id).\
    join(Interval, IntervalData, Interval_Block, Block)

    samples = self.fetch_samples_list()
    sample = samples.pop()

    # Filter for subset
    if subset:
      query = query.filter(Block.id.in_(subset))

    # Collapse output to singel sample since all blocks are identical for every sample
    query = query.filter(IntervalData.sample_id == sample).group_by(IntervalData.parent_id)
    
    return query

  def average_metrics(self, data_class=IntervalData, superblock_ids=None):
    """Calculate average for coverage and completeness.

    It's possible to build on the returned query to e.g. group results
    by contig.

    To work within the constraints of the SQL schema, queries limited to
    a list of superblocks are calculated on the level of blocks rather
    than intervals.

    Args:
      data_class (class, optional): Chanjo *Data class, e.g.
        :class:`chanjo.store.Interval`
      superblock_ids (list of str, optional): superblock IDs

    Returns:
      query: non-executed SQLAlchemy query
    """
    if superblock_ids:
      # overwrite the default if limiting to a subset of superblocks
      data_class = BlockData

    # set up base query
    query = self.query(data_class.sample_id,
                       data_class.group_id,
                       (sqa.func.avg(data_class.coverage)
                        .label('avg. coverage')),
                       (sqa.func.avg(data_class.completeness)
                        .label('avg. completeness')))

    if superblock_ids:
      # apply the superblock filter on the Block class level
      query = query.join(BlockData.parent)\
                   .filter(Block.superblock_id.in_(superblock_ids))

    # group and order by "sample_id" => return
    return query.group_by(data_class.sample_id).order_by(data_class.sample_id)

  def total_count(self, data_class=IntervalData):
    """Count all rows in a given table.

    Works on any Chanjo *Data class.

    Args:
      data_class (class, optional): Chanjo *Data class
        (default: :class:`chanjo.store.Interval`)

    Returns:
      query: non-executed SQLAlchemy query
    """
    # build base queries for the total number of annotated elements
    return self.query(data_class.sample_id,
                      data_class.group_id,
                      (sqa.func.count(data_class.id)
                       .label(data_class.__tablename__ + ' count'))
                     ).group_by(data_class.sample_id)\
                      .order_by(data_class.sample_id)

  def sex_chromosome_coverage(self):
    """Build query for average coverage on X/Y chromosomes.

    Useful when predicting the gender of a sample based on the alignment.
    """
    # build the query by inner joining Interval and IntervalData
    query = self.query(IntervalData.sample_id,
                       Interval.contig.label('chromosome'),
                       (sqa.func.avg(IntervalData.coverage)
                        .label('avg. coverage'))
                      ).join(IntervalData.parent)

    # filter by sex chromosomes
    sex_chromosomes = ('X', 'Y')
    query = query.filter(Interval.contig.in_(sex_chromosomes))

    # aggregate the result on sample id and contig
    return query.group_by(IntervalData.sample_id, Interval.contig)

  def sex_checker(self, group_id=None, sample_ids=None,
                  include_coverage=False):
    """Predict gender based on coverage on X/Y chromosomes."""
    # limit query on request
    query = limit_query(self.sex_chromosome_coverage(), group=group_id,
                        samples=sample_ids)

    # group tuples (rows) based on first item (sample ID)
    samples = itertools.groupby(query, getitem(0))

    for sample in samples:
      # extract X and Y coverage from the sample group
      sample_id, data_group = sample
      sex_coverage = [coverage for _, _, coverage in data_group]

      # run the predictor
      gender = predict_gender(*sex_coverage)

      if include_coverage:
        # return also raw coverage numbers
        yield sample_id, gender, sex_coverage[0], sex_coverage[1]

      else:
        yield sample_id, gender

  def gc_content(self, query=None, gc_amount='high', gene_ids=None):
    """Generate query to estimate coverage performace.

    Works by default on a small subset of genes with high/low GC
    content levels (BioMart).
    """
    # use the average metrics query unless otherwise requested
    query = query or self.average_metrics()

    if gc_amount == 'high':
      # highest GC content supersets
      identifiers = gene_ids or ['UTF1', 'BHLHA9', 'C20orf201', 'LRRC26',
                                 'HES4', 'BHLHE23', 'C9orf172', 'NKX6-2',
                                 'CITED4']

    elif gc_amount == 'low':
      # lowest GC content supersets
      identifiers = gene_ids or ['DEFB114', 'NTS', 'ANGPTL3', 'CYLC2',
                                 'GPR22', 'SI', 'CSN3', 'KLRC4', 'CSN1S1']

    else:
      raise ValueError("'gc_amount' must be either 'high' or 'low'")

    # build and return the query
    return query.filter(SuperblockData.parent_id.in_(identifiers))

  def covered_bases(self):
    """Count the number of covered bases across exome (full completeness).

    Returns:
      query: non-executed SQLAlchemy query
    """
    # number of bases per interval
    bp_per_interval = (Interval.end - (Interval.start + 1)
                       + (Sample.extension * 2))
    # number of bases fully covered per interval
    covered_bp_per_interval = bp_per_interval * IntervalData.completeness

    # compose SQL query for all samples in database
    return self.query(IntervalData.sample_id,
                      IntervalData.group_id,
                      (sqa.func.sum(covered_bp_per_interval)
                       / sqa.func.sum(bp_per_interval)).label('covered bases')
                     ).group_by(IntervalData.sample_id)\
                      .order_by(IntervalData.sample_id)

  def pass_filter(self, sample_id, data_class=BlockData,
                  metric='completeness', cutoff=1):
    """Filter out elements that pass a certain filter cutoff.

    You need to filter down to a single sample since this is the only
    thing that makes sense for the end result.
    """
    # extract column to filter on
    metric_column = getattr(data_class, metric)

    # set up base query
    return self.query(data_class)\
               .filter(metric_column >= cutoff)\
               .filter_by(sample_id=sample_id)\

  def pass_filter_count(self, data_class=BlockData,
                        metric='completeness', cutoff=1):
    """Count all elements that pass a cutoff for a given metric.

    You can choose to count the elements by calling ".count()" on the
    returned query instead of iterating over it.
    """
    # extract column to filter on
    metric_column = getattr(data_class, metric)

    # set up base query
    return self.total_count(data_class=data_class)\
               .filter(metric_column >= cutoff)

  def diagnostic_yield(self, metric='completeness', cutoff=1,
                       superblock_ids=None, group_id=None, sample_ids=None):
    """Calculate diagnostic yield."""
    # extract column to filter on
    metric_column = getattr(BlockData, metric)

    # set up the base query for all blocks
    total_query = self.total_count(BlockData)

    if superblock_ids:
      # apply the superblock filter on the Block class level
      total_query = total_query.join(BlockData.parent)\
                               .filter(Block.superblock_id.in_(superblock_ids))

    # extend base query to include only passed blocks
    pass_query = total_query.filter(metric_column >= cutoff)

    # optionally limit query
    queries = [limit_query(query, group=group_id, samples=sample_ids)
               for query in (total_query, pass_query)]

    # group multiple queries by sample ID (first column)
    metrics = groupby(get(0), concat(queries))

    # iterate over all values, concat different query results, and keep
    # only the unique values (excluding second sample_id)
    combined = (unique(concat(values)) for values in itervalues(metrics))

    # calculate diagnostic yield by simple division
    for sample_id, group_id, total, covered in combined:
      yield sample_id, group_id, (covered / total)

  def contig_coverage(self, contigs=None, samples=None, group=None):
    """Calculates coverage on contig(s)

    Args:
      contigs (str, optional): Contig(s) to calculate average for
      samples (str, optional): Id of sample(s)
      group (str, optional): Id of group 

    Returns:
      list: Result grouped with sample Id
    """
    # Three columns are needed for the prediction
    average = sqa.func.avg(IntervalData.coverage)
    columns = (IntervalData.sample_id, Interval.contig_id, average)
    # Build the query by inner joining Interval and IntervalData
    query = self.query(*columns)\
                .join(Interval, IntervalData.parent_id == Interval.id)
  
    if contigs:
      # Filter by contig
      query = query.filter(Interval.contig_id.in_(contigs))

    if samples:
      # Filter either by a list of samples...
      query = query.filter(IntervalData.sample_id.in_(samples))

    elif group:
      # ... or by a defined group of samples (e.g. group Id)
      query = query.join(Sample, IntervalData.sample_id == Sample.id)\
                   .filter(Sample.group_id == group)

    # Aggregate the result on sample Id and contig
    return query.group_by(IntervalData.sample_id, Interval.contig_id)
