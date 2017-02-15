"""
@author: The KnowEnG dev team
"""
import os
from enum import Enum
import pandas as pd
import numpy as np
from scipy import stats
import knpackage.toolbox as kn


class ColumnType(Enum):
    """Two categories of phenotype traits.
    """
    CONTINUOUS = "continuous"
    CATEGORICAL = "categorical"


def combine_phenotype_data_and_clustering(run_parameters):
    """This is to insert the sample clusters column into the phenotype dataframe.

    Returns:
        phenotype_df: phenotype dataframe with the first column as sample clusters.
    """
    phenotype_df = kn.get_spreadsheet_df(run_parameters['phenotype_data_full_path'])
    phenotype_df.insert(0, 'Cluster_ID', np.nan)
    cluster_labels_df = pd.read_csv(
        run_parameters['cluster_mapping_full_path'], index_col=0, header=None, sep='\t')
    cluster_labels_df.columns = ['Cluster_ID']
    common_samples = kn.find_common_node_names(phenotype_df.index, cluster_labels_df.index)
    phenotype_df.loc[common_samples, 'Cluster_ID'] = cluster_labels_df.loc[common_samples, 'Cluster_ID']
    return phenotype_df


def run_post_processing_phenotype_clustering_data(cluster_phenotype_df, run_parameters):
    """This is the clean up function of phenotype data with nans removed.

    Parameters:
        phenotype_df: phenotype dataframe with the first column as sample clusters.
    Returns:
        output_dict: dictionary with keys to be categories of phenotype data and values
        to be a list of related dataframes.
    """
    from collections import defaultdict

    output_dict = defaultdict(list)

    for column in cluster_phenotype_df:
        if (column == 'Cluster_ID'):
            continue
        cur_df = cluster_phenotype_df[['Cluster_ID', column]].dropna(axis=0)
        cur_df_lowercase = cur_df.apply(lambda x: x.astype(str).str.lower())
        num_uniq_value = len(cur_df_lowercase[column].unique())
        if cur_df_lowercase[column].dtype == object and num_uniq_value > run_parameters["threshold"]:
            continue
        if num_uniq_value > run_parameters["threshold"]:
            classification = ColumnType.CONTINUOUS
        else:
            classification = ColumnType.CATEGORICAL
        output_dict[classification].append(cur_df_lowercase)
    return output_dict


def f_oneway(phenotype_df):
    """ Perform a f_oneway test and report the results.

    Parameters:
        phenotype_df: dataframe with two columns with clusters and phenotype trait values.
        ret: result of the phenotype dataframe.
    """
    if phenotype_df.empty:
        return ['f_oneway', 0, 0, np.nan, np.nan]

    uniq_trait = np.unique(phenotype_df.values[:, 1].reshape(-1))
    uniq_cluster = np.unique(phenotype_df.values[:, 0])
    if (len(uniq_cluster) == 1):
        return ['f_oneway', len(uniq_trait), phenotype_df.shape[0], np.nan, np.nan]
    groups = []
    uniq_cm_vals = sorted(set(phenotype_df.values[:, 0]))

    phenotype_name = phenotype_df.columns.values[1]
    for i in uniq_cm_vals:
        groups.append(
            phenotype_df.loc[phenotype_df['Cluster_ID'] == i, phenotype_name].values.tolist())

    fval, pval = stats.f_oneway(*groups)
    ret = ['f_oneway', len(uniq_trait), phenotype_df.shape[0], fval, pval]
    return ret


def chisquare(phenotype_df):
    """ Perform a chi-square test and report the results.

    Parameters:
        phenotype_df: dataframe with two columns with clusters and phenotype trait values.
        ret: result of the phenotype dataframe.
    """
    if phenotype_df.empty:
        return ['chisquare', 0, 0, np.nan, np.nan]

    uniq_category = np.unique(phenotype_df.values[:, 1])
    uniq_cluster = np.unique(phenotype_df.values[:, 0])
    num_clusters = len(uniq_cluster)
    num_phenotype = len(uniq_category)
    phenotype_name = phenotype_df.columns.values[1]
    phenotype_val_dict = dict(zip(uniq_category, range(num_phenotype)))
    cluster_dict = dict(zip(uniq_cluster, range(num_clusters)))

    cont_table = np.zeros((num_clusters, num_phenotype))

    for sample in phenotype_df.index:
        clus = cluster_dict[phenotype_df.loc[sample, 'Cluster_ID']]
        trt = phenotype_val_dict[phenotype_df.loc[sample, phenotype_name]]  # pylint: disable=no-member
        cont_table[clus, trt] += 1

    chi, pval, dof, expected = stats.chi2_contingency(cont_table)
    ret = ['chisquare', num_phenotype, phenotype_df.shape[0], chi, pval]
    return ret


def clustering_evaluation(run_parameters):
    """ Run clustering evaluation on the whole dataframe of phenotype data.
    Save the results to tsv file.
    """
    cluster_phenotype_df = combine_phenotype_data_and_clustering(run_parameters)
    output_dict = run_post_processing_phenotype_clustering_data(cluster_phenotype_df, run_parameters)

    result_df = pd.DataFrame(
        index=['Measure', 'Trait_length_after_dropna', 'Sample_number_after_dropna', 'chi/fval', 'pval'])

    for key, df_list in output_dict.items():
        if (key == ColumnType.CATEGORICAL):
            for item in df_list:
                phenotype_name = item.columns.values[1]
                result_df[phenotype_name] = chisquare(item)
        else:
            for item in df_list:
                phenotype_name = item.columns.values[1]
                result_df[phenotype_name] = f_oneway(item)

    file_name = kn.create_timestamped_filename("clustering_evaluation_result", "tsv")
    file_path = os.path.join(run_parameters["results_directory"], file_name)
    result_df.T.to_csv(file_path, header=True, index=True, sep='\t', na_rep='NA')
    
