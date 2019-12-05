import misc.mpl_utils as mpl_utils
import data_warehouse.data_warehouse_utils as dwu
import misc.utils as utils

from flask import Flask, session, g, redirect, url_for, render_template, flash
from flask_login import LoginManager
from flask_redis import FlaskRedis

# I don't like the idea of handling all the urls in the same file
# I'll put all the new urls in the 'url_handlers' directory (one file for each new url)
# then can import it here and register (below) as a Blueprint: http://flask.pocoo.org/docs/1.0/blueprints/
from url_handlers.data_management import data_management_page
from url_handlers.basic_stats import basic_stats_page
from url_handlers.plots import plots_page
from url_handlers.clustering import clustering_page
from url_handlers.login import login_page
from url_handlers.histogram import histogram_page
from url_handlers.boxplot import boxplot_page
from url_handlers.coplots import coplots_page

from url_handlers.login import User

import os

###
#   Images
###
from flask import make_response, request
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

import matplotlib.pyplot as plt

import flask
import io
import matplotlib.backends.backend_agg

import seaborn as sns

sns.set(style='whitegrid')

# from: https://arusahni.net/blog/2014/03/flask-nocache.html
from functools import wraps, update_wrapper
from datetime import datetime

from modules.import_scheduler import Scheduler
import atexit

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
        SECRET_KEY='development key',
        USERNAME='admin',
        PASSWORD='default'
        ))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

# register blueprints here:
app.register_blueprint(data_management_page)
app.register_blueprint(basic_stats_page)
app.register_blueprint(plots_page)
app.register_blueprint(clustering_page)
app.register_blueprint(login_page)
app.register_blueprint(histogram_page)
app.register_blueprint(boxplot_page)
app.register_blueprint(coplots_page)

# login manager
login_manager = LoginManager()
login_manager.init_app(app)


# don't understand why we need this
@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)


# @app.context_processor
# def inject_enumerate():
#     return dict(enumerate=enumerate)

###
#   Database stuff
###

def connect_db():
    """ connects to our redis database """
    app.config["REDIS_URL"] = os.environ["REDIS_URL"]  # || "redis://docker.for.mac.localhost:6379/0"
    redis_store = FlaskRedis()
    redis_store.init_app(app)
    return redis_store


def get_db():
    """ opens a new database connection if there is none yet for the
        current application context
    """
    if not hasattr(g, 'redis_db'):
        g.redis_db = connect_db()
    return g.redis_db


@app.teardown_appcontext
def close_db(error):
    """ close the database, or whatever, on exit """
    pass


def init_db():
    db = get_db()
    return

    # we can use app.open_resource to grab something from the main
    # folder (flaskr, here)
    with app.open_resource('schema.sql', mode='r') as f:
        pass


@app.cli.command('initdb')
def initdb_command():
    """ this function is associated with the "initdb" command of the
        "flask" script
    """
    init_db()


@app.route('/', methods=['GET'])
def root_route():
    return redirect('/basic_stats')


###
#   Security
###
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = "Invalid username"
        elif request.form['password'] != app.config['PASSWORD']:
            error = "Invalid password"
        else:
            session['logged_in'] = True
            flash("You were logged in")
            return redirect(url_for('show_entities'))
    return render_template('login_page.html', error=error)


# @app.route('/login', methods=['POST'])
# def login():
#     error = None
#     if request.method == 'POST':
#         if request.form['email'] != app.config['USERNAME']:
#             error = "Login error: Invalid username"
#         elif request.form['password'] != app.config['PASSWORD']:
#             error = "Login error: Invalid password"
#         else:
#             session['logged_in'] = True
#             flash("You were logged in")
#     # todo: error message
#     return redirect(request.referrer)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash("You were logged out")


#     return redirect(request.referrer)

# @app.route('/a', methods=['GET','POST'])
# def show_cluster_numeric_entities():
#     r = get_db()
#     all_numeric_entities = rwh.get_numeric_entities(r)
#     all_categorical_entities = rwh.get_categorical_entities(r)
#
#     all_categorical_only_entities = set(all_categorical_entities) - set(all_numeric_entities)
#     all_categorical_only_entities = sorted(all_categorical_only_entities)
#
#     # numeric clustering
#     numeric_m = None
#     numeric_label_uses = None
#     numeric_entities = None
#     numeric_cluster_image = None
#     numeric_standardize=None
#     numeric_missing=None
#
#     # categorical clustering
#     cluster_category_values = None
#     categorical_label_uses = None
#     categorical_entities = None
#     category_values = None
#     categorical_cluster_image = None
#
#     # counting
#     counts = None
#     all_present = None
#     any_present = None
#
#     if 'cluster_numeric' in request.form:
#         numeric_entities = request.form.getlist('numeric_entities')
#         numeric_standardize = request.form['standardize'] == "yes"
#         numeric_missing = request.form['missing']
#         if any([entitiy for entitiy in numeric_entities]):
#             np.random.seed(8675309)
#             cluster_info = dwu.cluster_numeric_fields(
#                 numeric_entities,
#                 r,
#                 standardize=numeric_standardize,
#                 missing=numeric_missing
#             )
#
#             numeric_m, numeric_label_uses, df = cluster_info
#             any_present = df.shape[0]
#             all_present = df.dropna().shape[0]
#             numeric_cluster_image = True
#
#     elif 'count_numeric' in request.form:
#         numeric_entities = request.form.getlist('numeric_entities')
#         if any([numeric_entitiy for numeric_entitiy in numeric_entities]):
#             numeric_df = rwh.get_joined_numeric_values(numeric_entities, r)
#             numeric_df = numeric_df[numeric_entities]
#             counts = numeric_df.count()
#             any_present = numeric_df.shape[0]
#             all_present = numeric_df.dropna().shape[0]
#
#     elif 'count_categorical' in request.form:
#         categorical_entities = request.form.getlist('categorical_entities')
#
#         if any([entitiy for entitiy in categorical_entities]):
#             categorical_df = rwh.get_joined_categorical_values(categorical_entities, r)
#             #
#             categorical_df = categorical_df[categorical_entities]
#
#             counts = categorical_df.count()
#             any_present = categorical_df.shape[0]
#             all_present = categorical_df.dropna().shape[0]
#
#     elif 'cluster_categorical' in request.form:
#         categorical_entities = request.form.getlist('categorical_entities')
#         if any([entitiy for entitiy in categorical_entities]):
#             eps = 0.15
#             min_samples = 10
#
#             np.random.seed(8675309)
#
#             cluster_info = dwu.cluster_categorical_entities(
#                 categorical_entities,
#                 r,
#                 eps=eps,
#                 min_samples=min_samples
#             )
#
#             ccv, cat_rep_np, category_values, categorical_label_uses, cat_df = cluster_info
#             cluster_category_values = ccv
#             any_present = cat_df.shape[0]
#             all_present = cat_df.dropna().shape[0]
#
#             categorical_cluster_image = True
#
#     return render_template('statistics.html',
#         all_numeric_entities=all_numeric_entities,
#         all_categorical_entities=all_categorical_only_entities,
#         numeric_m=numeric_m,
#         numeric_label_uses=numeric_label_uses,
#         numeric_entities=numeric_entities,
#         numeric_cluster_image=numeric_cluster_image,
#         numeric_standardize=numeric_standardize,
#         numeric_missing=numeric_missing,
#         cluster_category_values=cluster_category_values,
#         categorical_label_uses=categorical_label_uses,
#         categorical_entities=categorical_entities,
#         category_values=category_values,
#         categorical_cluster_image=categorical_cluster_image,
#         counts=counts,
#         any_present=any_present,
#         all_present=all_present
#     )


def send_image(fig):
    fig.tight_layout()
    canvas = matplotlib.backends.backend_agg.FigureCanvas(fig)
    img = io.BytesIO()
    fig.savefig(img)
    img.seek(0)
    return flask.send_file(img, mimetype='image/png')


def nocache(view):
    @wraps(view)
    def no_cache(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers['Last-Modified'] = datetime.now()
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response

    return update_wrapper(no_cache, view)


@app.route('/categorical_cluster_image/<entities>')
@nocache
def categorical_cluster_image(entities):
    import numpy as np
    import pandas as pd
    import sklearn.preprocessing

    r = get_db()

    np.random.seed(8675309)

    categorical_entities = entities.split(",")

    cluster_info = dwu.cluster_categorical_entities(
            categorical_entities,
            r
            )

    ccv, cat_rep_np, category_values, categorical_label_uses, cat_df = cluster_info
    ccv_df = pd.DataFrame(ccv)

    # this should all be pulled into a function
    patient_count_field = "Scaled patient count"

    ccv_np = ccv_df.values
    scaled_ccv_np = sklearn.preprocessing.normalize(ccv_np, norm="l1")
    scaled_ccv_pivot_np = scaled_ccv_np.transpose()

    ccv_pivot_df = pd.DataFrame(scaled_ccv_pivot_np)
    ccv_pivot_df.columns = ccv_df.index
    ccv_pivot_df.index = ccv_df.columns

    cols_to_visualize = list(ccv_pivot_df.columns) + [patient_count_field]

    label_uses_df = utils.dict_to_dataframe(categorical_label_uses, key_name="cluster", value_name="count")

    label_counts = label_uses_df['count']
    label_counts = label_counts.values.reshape(1, -1)
    label_uses_df[patient_count_field] = sklearn.preprocessing.normalize(label_counts, norm="l1")[0]

    ccv_pivot_merge_df = ccv_pivot_df.merge(label_uses_df, left_index=True, right_on='cluster')
    ccv_pivot_merge_df.index = ccv_pivot_merge_df['cluster']

    df = ccv_pivot_merge_df[cols_to_visualize]

    new_df = pd.DataFrame(df.values.transpose())
    new_df.columns = df.index
    new_df.index = df.columns
    m_zero = new_df == 0

    # create the image

    fig, ax = plt.subplots(figsize=(25, 10))
    fontsize = 30

    vmax = 1
    sns.heatmap(
            new_df,
            cmap="Blues",
            ax=ax,
            vmin=0,
            vmax=vmax,
            mask=m_zero
            )

    mpl_utils.set_ticklabel_rotation(ax, 0, axis='y')
    mpl_utils.set_ticklabels_fontsize(ax, fontsize)
    mpl_utils.set_title_fontsize(ax, fontsize)
    mpl_utils.set_label_fontsize(ax, fontsize)

    ax.xaxis.tick_top()
    ax.xaxis.set_label_position('top')

    # get the colorbar, as well
    cax = plt.gcf().axes[-1]
    mpl_utils.set_ticklabels_fontsize(cax, fontsize)

    return send_image(fig)


@app.route('/patient_categorical_cluster_image/<entities>')
@nocache
def patient_categorical_cluster_image(entities):
    import numpy as np
    import sklearn.manifold

    r = get_db()

    eps = 0.15
    min_samples = 10

    np.random.seed(8675309)

    categorical_entities = entities.split(",")

    cluster_info = dwu.cluster_categorical_entities(
            categorical_entities,
            r,
            eps=eps,
            min_samples=min_samples
            )

    ccv, cat_rep_np, category_values, categorical_label_uses, cat_df = cluster_info

    np.random.seed(8675309)
    tsne = sklearn.manifold.TSNE(n_components=2)
    np.set_printoptions(suppress=True)
    projection = tsne.fit_transform(cat_rep_np)

    fig, ax = plt.subplots()  # figsize=(15,15))

    # Black removed and is used for noise instead.
    unique_labels = sorted(cat_df['cluster'].unique())
    colors = plt.cm.Spectral(np.linspace(0, 1, len(unique_labels)))
    for k, col in zip(unique_labels, colors):
        if k == -1:
            # Black used for noise.
            col = 'k'

        m_cluster = np.array(cat_df['cluster'] == k)

        xy = projection[m_cluster]
        ax.plot(
                xy[:, 0],
                xy[:, 1],
                'o',
                markerfacecolor=col,
                markeredgecolor='k',
                markersize=8,
                markeredgewidth=1,
                label=str(k)
                )

    ax.legend(loc='best')

    return send_image(fig)


@app.route('/numeric_cluster_image/<entities>', methods=['GET'])
@nocache
def numeric_cluster_image(entities):
    import numpy as np
    import pandas as pd
    import sklearn.preprocessing

    r = get_db()

    numeric_entities = entities.split(",")
    standardize = request.args.get('standardize')
    missing = request.args.get('missing')

    np.random.seed(8675309)
    cluster_info = dwu.cluster_numeric_fields(
            numeric_entities,
            r,
            standardize=standardize,
            missing=missing
            )

    numeric_m, numeric_label_uses, patient_df = cluster_info

    # this should be a function
    X = patient_df[numeric_entities].values
    X = sklearn.preprocessing.scale(X)

    scaled_df = pd.DataFrame(X)
    scaled_df.columns = numeric_entities
    scaled_df.index = patient_df.index
    scaled_df['cluster'] = patient_df['cluster']

    tidy_scaled_df = pd.melt(scaled_df, id_vars=['cluster'], value_name="Scaled value")
    tidy_scaled_df['variable'] = dwu.clean_entity_names(tidy_scaled_df['variable'])

    # m_outlier = tidy_scaled_df['cluster'] == 2
    # tidy_scaled_no_outlier = tidy_scaled_df[~m_outlier]

    # create the plot
    viz_df = tidy_scaled_df
    fontsize = 20

    num_clusters = len(viz_df['cluster'].unique())

    g = sns.factorplot(
            x="variable",
            y="Scaled value",
            col="cluster",
            col_wrap=3,
            # row="variable",
            data=viz_df,
            kind='violin',
            sharey=False,
            # size=5,
            aspect=num_clusters / 5
            )

    g.set(ylim=(-10, 10))

    for ax in g.axes.flat:
        mpl_utils.set_title_fontsize(ax, fontsize)
        mpl_utils.set_ticklabels_fontsize(ax, fontsize)

    # g.set_xticklabels(fontsize=fontsize)
    # g.set_yticklabels(fontsize=fontsize)
    g.set_xlabels(fontsize=fontsize)
    g.set_ylabels(fontsize=fontsize)

    g.fig.tight_layout()

    return send_image(g.fig)


@app.route('/patient_numeric_cluster_image/<entities>', methods=['GET'])
@nocache
def patient_numeric_cluster_image(entities):
    import numpy as np
    import sklearn.manifold

    r = get_db()

    numeric_entities = entities.split(",")
    standardize = request.args.get('standardize')
    missing = request.args.get('missing')

    np.random.seed(8675309)
    cluster_info = dwu.cluster_numeric_fields(
            numeric_entities,
            r,
            standardize=standardize,
            missing=missing
            )

    numeric_m, numeric_label_uses, patient_df = cluster_info

    np.random.seed(8675309)
    tsne = sklearn.manifold.TSNE(n_components=2)
    np.set_printoptions(suppress=True)
    projection = tsne.fit_transform(patient_df[numeric_entities])

    fig, ax = plt.subplots()  # figsize=(15,15))

    # Black removed and is used for noise instead.
    unique_labels = sorted(patient_df['cluster'].unique())
    colors = plt.cm.Spectral(np.linspace(0, 1, len(unique_labels)))
    for k, col in zip(unique_labels, colors):
        if k == -1:
            # Black used for noise.
            col = 'k'

        m_cluster = np.array(patient_df['cluster'] == k)
        xy = projection[m_cluster]
        ax.plot(
                xy[:, 0],
                xy[:, 1],
                'o',
                markerfacecolor=col,
                markeredgecolor='k',
                markersize=8,
                markeredgewidth=1,
                label=str(k)
                )

    ax.legend(loc='best')

    return send_image(fig)


def check_for_env(key: str, default=None, cast=None):
    if key in os.environ:
        if cast:
            return cast(os.environ.get(key))
        return os.environ.get(key)
    return default


day_of_week = check_for_env('IMPORT_DAY_OF_WEEK', default='mon-sun')
hour = check_for_env('IMPORT_HOUR', default=5)
minute = check_for_env('IMPORT_MINUTE', default=5)

if os.environ.get('IMPORT_DISABLED') is None:
    scheduler = Scheduler(day_of_week=day_of_week, hour=hour, minute=minute)
    scheduler.start()


@atexit.register
def exit():
    scheduler.stop()


def main():
    return app
