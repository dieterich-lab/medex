import collections
import pandas as pd
import sklearn.cluster
import sklearn.metrics.pairwise
import sklearn.mixture
import sklearn.preprocessing


def cluster_numeric_fields(entities, df):
    """ Cluster the given numeric entities using a DP-GMM.

    Paramters
    ---------
    entities: list of strings
        The names of the numeric entities

    standardize : bool
        Whether to standardize the values before clustering


    Returns
    -------
    df : sklearn.mixture.BayesianGaussianMixture
        The fit mixture model

    cluster_data : dict
        A dictionary mapping from each label to the number of items with that
        label.

    cluster_labels: pd.DataFrame
        The data frame containing entity values for each patient
    """
    import misc.math_utils as math_utils

    df = df.dropna()
    X = df[entities].values
    scaler = sklearn.preprocessing.StandardScaler()
    X = scaler.fit_transform(X)
    df[entities] = X
    X = df[entities].values

    # make sure we do not use too many components
    # otherwise, sklearn will complain
    n_components = min(100, X.shape[0] - 1)

    cluster_data = math_utils.fit_bayesian_gaussian_mixture(
        X,
        n_components=n_components,
        max_iter=10000,
        reg_covar=0,
        mean_precision_prior=0.8,
        weight_concentration_prior_type="dirichlet_process",
        init_params='kmeans',
        seed=8675309
    )

    clusters = cluster_data.predict(X)

    df['cluster'] = clusters

    cluster_labels = collections.defaultdict(int)
    for l in clusters:
        cluster_labels[l] += 1

    for i, means in enumerate(cluster_data.means_):
        cluster_data.means_[i] = scaler.inverse_transform(means)

    return cluster_data, cluster_labels, df, None