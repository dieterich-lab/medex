
import plotly.graph_objects as go
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import pandas as pd
#UMAP
import umap

def plot_2d(component1, component2,y):
    fig = go.Figure(data=go.Scatter(
        x=component1,
        y=component2,
        mode='markers',
        marker=dict(
            size=20,
            color=y,  # set color equal to a variable
            colorscale='Rainbow',  # one of plotly colorscales
            showscale=True,
            line_width=1
        )
    ))
    fig.update_layout(margin=dict(l=100, r=100, b=100, t=100), width=2000, height=1200)

    fig.show()

def plot_3d(component1, component2, component3,y):
    fig = go.Figure(data=[go.Scatter3d(
        x=component1,
        y=component2,
        z=component3,
        mode='markers',
        marker=dict(
            size=10,
            color=y,  # set color to an array/list of desired values
            colorscale='Rainbow',  # choose a colorscale
            opacity=1,
            line_width=1
        )
    )])
    fig.show()

def calculate(x,y):

    ## Standardizing the data
    x = StandardScaler().fit_transform(x)

    """
    pca = PCA(n_components=3)
    principalComponents = pca.fit_transform(x)
    principal = pd.DataFrame(data=principalComponents
                             , columns=['principal component 1', 'principal component 2', 'principal component 3'])

    plot_2d(principalComponents[:, 0], principalComponents[:, 1],y)

    plot_3d(principalComponents[:, 0], principalComponents[:, 1], principalComponents[:, 2],y)
    """
    reducer = umap.UMAP(random_state=42,n_components=2)
    embedding = reducer.fit_transform(x)

    #plot_2d(reducer.embedding_[:, 0],reducer.embedding_[:, 1],y)
    #plot_3d(reducer.embedding_[:, 0], reducer.embedding_[:, 1], reducer.embedding_[:, 2],y)
    return reducer,embedding

def calculate_c(x,y):

    ## Standardizing the data
    #x = StandardScaler().fit_transform(x)

    """
    pca = PCA(n_components=3)
    principalComponents = pca.fit_transform(x)
    principal = pd.DataFrame(data=principalComponents
                             , columns=['principal component 1', 'principal component 2', 'principal component 3'])

    plot_2d(principalComponents[:, 0], principalComponents[:, 1],y)

    plot_3d(principalComponents[:, 0], principalComponents[:, 1], principalComponents[:, 2],y)
    """
    reducer = umap.UMAP(n_neighbors=5,min_dist=0.1,metric='precomputed')
    embedding = reducer.fit_transform(x)

    #plot_2d(reducer.embedding_[:, 0],reducer.embedding_[:, 1],y)
    #plot_3d(reducer.embedding_[:, 0], reducer.embedding_[:, 1], reducer.embedding_[:, 2],y)
    return reducer,embedding
