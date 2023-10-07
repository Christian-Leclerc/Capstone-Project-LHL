import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.manifold import TSNE
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

def TSNE_kMeans_figure(quantitatives):
    # Initialize the scaler
    scaler = StandardScaler()

    # Fit the scaler and transform the data
    scaled_data = scaler.fit_transform(quantitatives)

    # Create a t-SNE object
    tsne = TSNE(n_components=2, random_state=0)

    # Fit and transform your data
    tsne_results = tsne.fit_transform(scaled_data)

    # Clusters
    n_clusters = 5 # 5 to start
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(tsne_results)

    # Map the cluster label back to your original DataFrame
    quantitatives['cluster_label'] = clusters

    # Compute centroids for each cluster in the t-SNE dimensions
    centroids = np.array([tsne_results[clusters == i].mean(axis=0) for i in range(n_clusters)])

    # Define cluster names/features
    cluster_features = [
        ['Triplex'],
        ['Duplex'],
        ['Duplex'],
        ['Triplex'],
        ['Triplex++']
    ]

    # Visualize
    plt.figure(figsize=(10,8))
    scatter = plt.scatter(tsne_results[:, 0], tsne_results[:, 1], c=clusters, cmap='viridis', alpha=0.6)

    # Add a colorbar and legend
    cbar = plt.colorbar(scatter)
    cbar.set_label('Cluster Label')
    legend1 = plt.legend(*scatter.legend_elements(), title="Clusters")

    # Add cluster features to centroids
    for i, c in enumerate(centroids):
        # Calculate vertical position offset for each feature in the list
        for j, feature in enumerate(cluster_features[i]):
            offset = j * 3.5
            plt.text(c[0], c[1]-offset, feature, fontsize=10, ha='center', va='center', bbox=dict(facecolor='white', alpha=1.0, edgecolor='black'))

    # Add horizontal line
    plt.axhline(-7, color='red', linestyle='--')  # Red dashed line at t-SNE = 0

    # Add labels
    plt.text(-50, 45, 'Average:Less parking and yard, Older', color='black', ha='left')  # Adjust the x and y values as needed
    plt.text(-50, -45, 'Avergae: More parking and yard, Younger', color='black', ha='left')  # Adjust the x and y values as needed


    plt.title('t-SNE with KMeans Clusters')
    plt.xlabel('t-SNE feature 1')
    plt.ylabel('t-SNE feature 2')
    plt.show()

    