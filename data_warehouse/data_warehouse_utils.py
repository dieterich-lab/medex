import collections
import pandas as pd
import sklearn.cluster
import sklearn.metrics.pairwise
import sklearn.mixture
import sklearn.preprocessing
import modules.load_data_postgre as ps

import data_warehouse.redis_rwh as rwh

ALLOWED_MISSING = {
    "drop",
    "mean",
    "median",
    "most_frequent"
}


def _retrieve_numeric_fieds_df(entities, r, standardize=True, missing='drop', min_max_filter=None):
    """ Retrieve patient records from the db and preprocess as specified.

    Paramters
    ---------
    entities: list of strings
        The names of the numeric entities

    r : redis.StrictRedis
        The redis database connection

    standardize : bool
        Whether to standardize the values before clustering

    missing : string
        How to handle missing data. The available values are:
            * "drop" : do not consider rows with missing data
            * "mean", "median", "most_frequent": these values are passed to an
                sklearn.preprocessing.Imputer. Please see its documentation for
                more details.

    Returns
    -------
    patient_df: pd.DataFrame
        The data frame containing entity values for each patient

    scaler: sklearn.preprocessing.StandardScaler, or None
        The scaler to standardize the data, or None if the data is not
        standardized. The idea is that standardized values can be transformed
        back, and raw values can be transformed, using this.

    """
    if missing not in ALLOWED_MISSING:
        msg = "Invalid \"missing\" argument: {}".format(missing)
        raise ValueError(msg)

    df = ps.get_values(entities, r)


    if missing == "drop":
        df = df.dropna()
        X = df[entities].values
    else:
        X = df[entities].values
        imp = sklearn.preprocessing.Imputer(strategy=missing)
        X = imp.fit_transform(X)

    scaler = None
    if standardize:
        scaler = sklearn.preprocessing.StandardScaler()
        X = scaler.fit_transform(X)

    df[entities] = X
    return df, scaler, None


# use in clustering
def cluster_numeric_fields(entities, r, standardize=True, missing='drop', min_max_filter=None):
    """ Cluster the given numeric entities using a DP-GMM.

    Paramters
    ---------
    entities: list of strings
        The names of the numeric entities

    r : redis.StrictRedis
        The redis database connection

    standardize : bool
        Whether to standardize the values before clustering

    missing : string
        How to handle missing data. The available values are:
            * "drop" : do not consider rows with missing data
            * "mean", "median", "most_frequent": these values are passed to an
                sklearn.preprocessing.Imputer. Please see its documentation for
                more details.

    Returns
    -------
    m : sklearn.mixture.BayesianGaussianMixture
        The fit mixture model

    label_uses : dict
        A dictionary mapping from each label to the number of items with that
        label.

    patient_df: pd.DataFrame
        The data frame containing entity values for each patient
    """
    import misc.math_utils as math_utils

    df, scaler, error = _retrieve_numeric_fieds_df(
        entities,
        r,
        standardize=standardize,
        missing=missing,
        min_max_filter=min_max_filter
    )
    if error:
        # cluster_data, cluster_labels, df
        return None, None, None, error
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

    if standardize:
        for i, means in enumerate(cluster_data.means_):
            cluster_data.means_[i] = scaler.inverse_transform(means)

    return cluster_data, cluster_labels, df, None





