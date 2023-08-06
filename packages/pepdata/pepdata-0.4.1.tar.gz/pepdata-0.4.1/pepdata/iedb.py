# Copyright (c) 2014. Mount Sinai School of Medicine
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from os.path import join

import numpy as np
import pandas as pd


from reduced_alphabet import make_alphabet_transformer
from features import (
    make_ngram_dataset, make_ngram_dataset_from_args,
    make_unlabeled_ngram_dataset, make_unlabeled_ngram_dataset_from_args
)
from common import (
    split_classes, bad_amino_acids, fetch_file, delete_old_file
)


def _load_dataframe(
        filename,
        human = True,
        mhc_class = None, # 1, 2, or None for both
        hla = None, # regex pattern i.e. '(HLA-A2)|(HLA-A\*02)'
        exclude_hla = None, # regex pattern i.e. '(HLA-A2)|(HLA-A\*02)'
        peptide_length = None,
        assay_method=None,
        assay_group=None,
        nrows = None,
        reduced_alphabet = None,
        verbose= False):
    """
    Load an IEDB csv into a pandas dataframe and filter using the
    criteria given as function arguments
    """
    df = pd.read_csv(
            filename,
            skipinitialspace=True,
            nrows = nrows,
            low_memory=False)

    # Sometimes the IEDB seems to put in an extra comma in the
    # header line, which creates an unnamed column of NaNs.
    # To deal with this, drop any columns which are all NaN
    df = df.dropna(axis=1, how='all')

    n = len(df)

    epitopes = df['Epitope Linear Sequence'].str.upper()
    df['Epitope Linear Sequence'] = epitopes

    null_epitope_seq = epitopes.isnull()

    # if have rare or unknown amino acids, drop the sequence
    bad_epitope_seq = \
        epitopes.str.contains(bad_amino_acids, na=False).astype('bool')

    if verbose:
        print "Dropping %d null sequences" % null_epitope_seq.sum()
        print "Dropping %d bad sequences" % bad_epitope_seq.sum()

    mask = ~(bad_epitope_seq | null_epitope_seq)

    if human:
        organism = df['Host Organism Name']
        mask &= organism.str.startswith('Homo sapiens', na=False).astype('bool')

    # Match known alleles such as 'HLA-A*02:01',
    # broader groupings such as 'HLA-A2'
    # and unknown alleles of the MHC-1 listed either as
    #  'HLA-Class I,allele undetermined'
    #  or
    #  'Class I,allele undetermined'

    mhc = df['MHC Allele Name']

    if mhc_class == 1:
        mhc1_pattern = 'Class I,|HLA-[A-C](?:[0-9]|\*)'
        mask &= mhc.str.contains(mhc1_pattern, na=False).astype('bool')
    elif mhc_class == 2:
        mhc2_pattern = "Class II,|HLA-D(?:P|M|O|Q|R)"
        mask &= mhc.str.contains(mhc2_pattern, na=False).astype('bool')

    if hla:
        mask &= df['MHC Allele Name'].str.contains(hla, na=False)

    if exclude_hla:
        mask &= ~df['MHC Allele Name'].str.contains(exclude_hla, na=False)

    if assay_group:
        mask &= df['Assay Group'].str.contains(assay_group)

    if assay_method:
        mask &= df['Method/Technique'].str.contains(assay_method)

    if peptide_length:
        assert peptide_length > 0
        mask &=  df['Epitope Linear Sequence'].str.len() == peptide_length

    df = df[mask]

    if verbose:
        print "Returning %d / %d entries after filtering" % (len(df), n)

    if reduced_alphabet:
        epitopes = df['Epitope Linear Sequence']
        df['Epitope Linear Sequence']  = \
            epitopes.map(make_alphabet_transformer(reduced_alphabet))

    return df

def _group_epitopes(
        df,
        unique_sequences = True,
        min_count = 0,
        group_by_allele = False,
        verbose = False):
    """
    Given a dataframe of epitopes and qualitative measures,
    group the epitope strings (optionally also grouping by allele),
    and associate each group with its percentage of Positive
    Qualitative Measure results.
    """
    epitopes = df['Epitope Linear Sequence']
    measure = df['Qualitative Measure']
    mhc = df['MHC Allele Name']
    pos_mask = measure.str.startswith('Positive').astype('bool')

    if group_by_allele:
        groups = pos_mask.groupby([epitopes, mhc])
    else:
        groups = pos_mask.groupby(epitopes)

    values = groups.mean()
    counts = groups.count()
    pos_counts = groups.sum()
    neg_counts = counts - pos_counts

    if min_count:
        mask = counts >= min_count
        values = values[mask]
        counts = counts[mask]
        pos_counts = pos_counts[mask]
        neg_counts = neg_counts[mask]

    result = pd.DataFrame(
        data = {
            'value' : values,
            'count': counts,
            'pos' : pos_counts,
            'neg' : neg_counts,
        },
        index = values.index)
    return result

def _tcell_local_path():
    return fetch_file(
        filename = "tcell_compact.csv",
        download_url = "http://www.iedb.org/doc/tcell_compact.zip",
        decompress = True)

def clear_tcell_cache():
    delete_old_file(_tcell_local_path())

def load_tcell(
        mhc_class = None, # 1, 2, or None for neither
        hla = None,
        exclude_hla = None,
        human = True,
        peptide_length = None,
        assay_method=None,
        assay_group=None,
        reduced_alphabet = None, # 20 letter AA strings -> simpler alphabet
        nrows = None,
        verbose= False):
    """
    Load IEDB T-cell data without aggregating multiple entries for same epitope

    Parameters
    ----------
    mhc_class: {None, 1, 2}
        Restrict to MHC Class I or Class II (or None for neither)

    hla: regex pattern, optional
        Restrict results to specific HLA type used in assay

    exclude_hla: regex pattern, optional
        Exclude certain HLA types

    human: bool
        Restrict to human samples (default True)

    peptide_length: int, optional
        Restrict epitopes to amino acid strings of given length

    assay_method string, optional
        Only collect results with assay methods containing the given string

    assay_group: string, optional
        Only collect results with assay groups containing the given string

    nrows: int, optional
        Don't load the full IEDB dataset but instead read only the first nrows

    reduced_alphabet: dictionary, optional
        Remap amino acid letters to some other alphabet

    verbose: bool
        Print debug output
    """

    data_path = _tcell_local_path()

    return _load_dataframe(
            data_path,
            human=human,
            mhc_class=mhc_class,
            hla=hla,
            exclude_hla=exclude_hla,
            assay_method=assay_method,
            assay_group=assay_group,
            peptide_length=peptide_length,
            reduced_alphabet=reduced_alphabet,
            nrows=nrows,
            verbose=verbose)


def load_tcell_values(
        mhc_class = None, # 1, 2, or None for neither
        hla = None,
        exclude_hla = None,
        human = True,
        peptide_length = None,
        assay_method=None,
        assay_group=None,
        reduced_alphabet = None, # 20 letter AA strings -> simpler alphabet
        nrows = None,
        min_count = 0,
        group_by_allele = False,
        verbose= False):
    """
    Load the T-cell response data from IEDB, collect into a dataframe mapping
    epitopes to percentage positive results.

    Parameters
    ----------
    mhc_class: {None, 1, 2}
        Restrict to MHC Class I or Class II (or None for neither)

    hla: regex pattern, optional
        Restrict results to specific HLA type used in assay

    exclude_hla: regex pattern, optional
        Exclude certain HLA types

    human: bool
        Restrict to human samples (default True)

    peptide_length: int, optional
        Restrict epitopes to amino acid strings of given length

    assay_method string, optional
        Only collect results with assay methods containing the given string

    assay_group: string, optional
        Only collect results with assay groups containing the given string

    reduced_alphabet: dictionary, optional
        Remap amino acid letters to some other alphabet

    nrows: int, optional
        Don't load the full IEDB dataset but instead read only the first nrows

    group_by_allele:
        Don't combine epitopes across multiple HLA types

    min_count: int, optional
        Exclude epitopes which appear fewer times than min_count

    verbose: bool
        Print debug output
    """

    df = load_tcell(
        mhc_class=mhc_class,
        hla=hla,
        human=human,
        exclude_hla=exclude_hla,
        peptide_length=peptide_length,
        assay_method=assay_method,
        assay_group=assay_group,
        reduced_alphabet=reduced_alphabet,
        nrows=nrows,
        verbose=verbose)

    return _group_epitopes(
            df,
            group_by_allele = group_by_allele,
            min_count = min_count,
            verbose = verbose)

def load_tcell_classes(*args, **kwargs):
    """
    Split the T-cell assay results into positive and negative sets.

    Parameters
    ----------
    noisy_labels : {'majority', 'negative', 'positive'}
        Which class do we assign an epitope with contradictory labels?

    *args, **kwargs : same as 'load_tcell'
    """
    noisy_labels = kwargs.pop('noisy_labels', 'majority')
    verbose = kwargs.get('verbose')
    tcell_values = load_tcell_values(*args, **kwargs)
    return split_classes(
        tcell_values.value,
        noisy_labels = noisy_labels,
        verbose = verbose)

def load_tcell_ngrams(*args, **kwargs):
    """
    Construct n-gram input features X and output labels Y for T-cell responses

    Parameters:
    ----------
    max_ngram : int
        Order of n-grams to consider when constructing X.
        For example, when max_ngram = 1, the vector space is the individual
        frequencies of letters in the amino acid strings.

    normalize_row : bool, optional
        If True (default), then return frequencies, else raw counts.

    subsample_bigger_class: bool, optional
        When the number of samples in both classes are unbalanced,
        randomly drop some samples from the larger class (default = False).

    return_transformer: bool
        Return `X, Y, f` instead of just `X, Y`,
        where f can be used to transform new amino acid strings into
        the same space as the training data.


    *args, **kwargs : same as `load_tcell_classes`
    """
    kwargs['training_already_reduced'] = True
    return make_ngram_dataset_from_args(load_tcell_classes, *args, **kwargs)

def _mhc_local_path():
    return fetch_file(
        filename = "elution_compact.csv",
        download_url = "http://www.iedb.org/doc/mhc_ligand_compact.zip",
        decompress = True)

def clear_mhc_cache():
    delete_old_file(_mhc_local_path())

def load_mhc(
        mhc_class = None, # 1, 2, or None for neither
        hla = None,
        exclude_hla = None,
        human = True,
        peptide_length = None,
        assay_method=None,
        assay_group=None,
        reduced_alphabet = None, # 20 letter AA strings -> simpler alphabet
        nrows = None,
        verbose = False,
        cache_download=True):
    """
    Load IEDB MHC data without aggregating multiple entries for the same epitope


    Parameters
    ----------
    mhc_class : {None, 1, 2}
        Restrict to MHC Class I or Class II (or None for neither)

    hla : regex pattern, optional
        Restrict results to specific HLA type used in assay

    exclude_hla : regex pattern, optional
        Exclude certain HLA types

    human : bool
        Restrict to human samples (default True)

    peptide_length: int, optional
        Restrict epitopes to amino acid strings of given length

    assay_method : string, optional
        Limit to assay methods which contain the given string

    assay_group : string, optional
        Limit to assay groups which contain the given string

    reduced_alphabet : dictionary, optional
        Remap amino acid letters to some other alphabet

    nrows : int, optional
        Don't load the full IEDB dataset but instead read only the first nrows

    verbose : bool
        Print debug output
    """
    data_path = _mhc_local_path()

    return _load_dataframe(
                data_path,
                mhc_class=mhc_class,
                hla=hla,
                exclude_hla=exclude_hla,
                human=human,
                peptide_length=peptide_length,
                assay_method=assay_method,
                assay_group=assay_group,
                reduced_alphabet=reduced_alphabet,
                nrows=nrows,
                verbose=verbose)


def load_mhc_values(
        mhc_class=None, # 1, 2, or None for neither
        hla=None,
        exclude_hla=None,
        human=True,
        peptide_length=None,
        assay_method=None,
        assay_group=None,
        reduced_alphabet=None, # 20 letter AA strings -> simpler alphabet
        nrows=None,
        group_by_allele=False,
        min_count=0,
        verbose=False):
    """
    Load the MHC binding results from IEDB, collect into a dataframe mapping
    epitopes to percentage positive results.

    Parameters
    ----------
    mhc_class: {None, 1, 2}
        Restrict to MHC Class I or Class II (or None for neither)

    hla: regex pattern, optional
        Restrict results to specific HLA type used in assay

    exclude_hla: regex pattern, optional
        Exclude certain HLA types

    human: bool
        Restrict to human samples (default True)

    peptide_length: int, optional
        Restrict epitopes to amino acid strings of given length

    assay_method string, optional
        Only collect results with assay methods containing the given string

    assay_group: string, optional
        Only collect results with assay groups containing the given string

    reduced_alphabet: dictionary, optional
        Remap amino acid letters to some other alphabet

    nrows: int, optional
        Don't load the full IEDB dataset but instead read only the first nrows

    group_by_allele:
        Don't combine epitopes across multiple HLA types

    min_count: int, optional
        Exclude epitopes which appear fewer times than min_count

    verbose: bool
        Print debug output
    """
    df = load_mhc(
        mhc_class=mhc_class,
        hla=hla,
        exclude_hla=exclude_hla,
        human=human,
        peptide_length=peptide_length,
        assay_method=assay_method,
        assay_group=assay_group,
        reduced_alphabet=reduced_alphabet,
        nrows=nrows,
        verbose=verbose)

    return _group_epitopes(
            df,
            group_by_allele=group_by_allele,
            min_count=min_count,
            verbose=verbose)

def load_mhc_classes(*args, **kwargs):
    """
    Split the MHC binding assay results into positive and negative sets.

    Parameters
    ----------
    noisy_labels : 'majority' | 'negative' | 'positive'
        Which class do we assign an epitope with contradictory labels?

    *args, **kwargs : same as 'load_tcell'
    """
    noisy_labels = kwargs.pop('noisy_labels', 'majority')
    verbose = kwargs.get('verbose')
    mhc_values = load_mhc_values(*args, **kwargs)
    return split_classes(
        mhc_values.value,
        noisy_labels=noisy_labels,
        verbose=verbose)

def load_mhc_ngrams(*args, **kwargs):
    """
    Construct n-gram input features X and output labels Y for MHC binding

    Parameters:
    ----------
    max_ngram : int
        Order of n-grams to consider when constructing X.
        For example, when ngram = 1, the vector space is the individual
        frequencies of letters in the amino acid strings.

    normalize_row : bool, optional
        If True (default), then return frequencies, else raw counts.

    subsample_bigger_class: bool, optional
        When the number of samples in both classes are unbalanced,
        randomly drop some samples from the larger class (default = False).

    return_transformer: bool
        Return `X, Y, f` instead of just `X, Y`,
        where f can be used to transform new amino acid strings into
        the same space as the training data.


    *args, **kwargs : same as `load_tcell_classes`
    """
    kwargs['training_already_reduced'] = True
    return make_ngram_dataset_from_args(load_mhc_classes, *args, **kwargs)

def load_tcell_vs_mhc(
        mhc_class=None, # 1, 2, or None for neither
        hla=None,
        exclude_hla=None,
        peptide_length=None,
        min_count=0,
        mhc_assay_method=None,
        mhc_assay_group=None,
        tcell_assay_method=None,
        tcell_assay_group=None,
        nrows=None,
        group_by_allele=False,
        verbose=False):
    """
    Percentage positive results for both T-cell response assays
    and MHC binding assays (keyed by epitopes for which we have data
    for both)
    """
    mhc = load_mhc_values(
            mhc_class=mhc_class,
            hla=hla,
            exclude_hla=exclude_hla,
            peptide_length=peptide_length,
            assay_method=mhc_assay_method,
            assay_group=mhc_assay_group,
            nrows=nrows,
            min_count = min_count,
            group_by_allele = group_by_allele,
            verbose = verbose)
    tcell = load_tcell_values(
                mhc_class = mhc_class,
                hla = hla,
                exclude_hla = exclude_hla,
                assay_method=tcell_assay_method,
                assay_group=tcell_assay_group,
                peptide_length = peptide_length,
                nrows = nrows,
                min_count = min_count,
                group_by_allele = group_by_allele,
                verbose = verbose)
    df_combined = pd.DataFrame({'mhc':mhc.value, 'tcell':tcell.value})
    both = ~(df_combined.mhc.isnull() | df_combined.tcell.isnull())
    return df_combined[both]

