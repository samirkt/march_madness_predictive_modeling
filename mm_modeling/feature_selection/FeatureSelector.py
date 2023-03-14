'''
Kevin Anderson
March 13, 2023
'''

import numpy as np
import pandas as pd

class FeatureSelector:
    
    def __init__(self,X):
        self.X = X
        self.n, self.d = X.shape

    def pca(self,num_components):
        # Center the data
        X_centered = self.X - np.mean(self.X, axis=0)
        
        # Get covariance matrix
        cov = np.cov(X_centered, rowvar=False)
        
        # Sort the eigenvalues and eigenvectors
        eigenvalues, eigenvectors = np.linalg.eigh(cov)
        sorted_inds = np.argsort(eigenvalues)[::-1]
        sorted_eigenvalues = eigenvalues[sorted_inds]
        sorted_eigenvectors = eigenvectors[:,sorted_inds]

        # Get n principal components and project the data onto them
        principal_components = sorted_eigenvectors[:,0:num_components]
        X_reduced = np.dot(X_centered,principal_components)

        return X_reduced







if __name__ == '__main__':
    from sklearn.datasets import load_diabetes

    diabetes = load_diabetes()

    X = pd.DataFrame(data=diabetes.data, columns=diabetes.feature_names)

    obj = FeatureSelector(X) 

    X_reduced = obj.pca(num_components=0)
