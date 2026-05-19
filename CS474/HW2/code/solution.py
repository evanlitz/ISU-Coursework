import numpy as np
import sys
from helper import *


def show_images(data):
    """Show the input images and save them.

    Args:
        data: A stack of two images from train data with shape (2, 16, 16).
              Each of the image has the shape (16, 16)

    Returns:
        Do not return any arguments. Save the plots to 'image_1.*' and 'image_2.*' and
        include them in your report
    """
    ### YOUR CODE HERE

    # Loop over 2 images. i = 0 or 1 and img is the 16x16 numpy array that constructs the image
    for i, img in enumerate(data):
        fig, ax = plt.subplots()    # Create figure and axes for each image
        ax.imshow(img, cmap='gray')     # Draw the 16 by 16 array as a greyed out image
        ax.axis('off')         
        plt.savefig(f'image_{i+1}.png')     # Save to image_#.png 
        plt.show()          # Show the image
        plt.close()         # Close the image

    ### END YOUR CODEj


def show_features(X, y, save=True):
    """Plot a 2-D scatter plot in the feature space and save it. 

    Args:
        X: An array of shape [n_samples, n_features].
        y: An array of shape [n_samples,]. Only contains 1 or -1.
        save: Boolean. The function will save the figure only if save is True.

    Returns:
        Do not return any arguments. Save the plot to 'train_features.*' and include it
        in your report.
    """
    ### YOUR CODE HERE

    ones = (y == 1)     # True for every sample labeled as digit 1
    fives = (y==-1)     # True for every sample labeled as digit 5

    # Plot the classes dseperately, each scatter call adds one group of points to the plot. Different colors and markers.
    plt.scatter(X[ones, 0], X[ones, 1], marker='*', color='red', label='1')
    plt.scatter(X[fives, 0], X[fives, 1], marker='*', color='blue', label='5')

    # Plot the symmetry, average intensity, and feature space.
    plt.xlabel('Symmetry')
    plt.ylabel('Average Intensity')
    plt.title('Feature Space')
    plt.legend()

    # Save and display the plot
    if save:
        plt.savefig('train_features.png')
        plt.show()
        plt.close()

    ### END YOUR CODE


class Perceptron(object):
    
    def __init__(self, max_iter):
        self.max_iter = max_iter

    def fit(self, X, y):
        """Train perceptron model on data (X,y).

        Args:
            X: An array of shape [n_samples, n_features].
            y: An array of shape [n_samples,]. Only contains 1 or -1.

        Returns:
            self: Returns an instance of self.
        """
        ### YOUR CODE HERE
        
        n_samples, n_features = X.shape
        w = np.zeros(n_features)

        for _ in range(self.max_iter):
            for i in range(n_samples):
                pred = np.sign(np.dot(w, X[i]))
                if pred != y[i]:
                    w = w + y[i] * X[i]

        self.W = w








        # After implementation, assign your weights w to self as below:
        # self.W = w
        
        ### END YOUR CODE
        
        return self

    def get_params(self):
        """Get parameters for this perceptron model.

        Returns:
            W: An array of shape [n_features,].
        """
        if self.W is None:
            print("Run fit first!")
            sys.exit(-1)
        return self.W

    def predict(self, X):
        """Predict class labels for samples in X.

        Args:
            X: An array of shape [n_samples, n_features].

        Returns:
            preds: An array of shape [n_samples,]. Only contains 1 or -1.
        """
        ### YOUR CODE HERE

        return np.sign(X @ self.W)

        ### END YOUR CODE

    def score(self, X, y):
        """Returns the mean accuracy on the given test data and labels.

        Args:
            X: An array of shape [n_samples, n_features].
            y: An array of shape [n_samples,]. Only contains 1 or -1.

        Returns:
            score: An float. Mean accuracy of self.predict(X) wrt. y.
        """
        ### YOUR CODE HERE

        preds = self.predict(X)
        return np.mean(preds == y)

        ### END YOUR CODE




def show_result(X, y, W):
    """Plot the linear model after training. 
       You can call show_features with 'save' being False for convenience.

    Args:
        X: An array of shape [n_samples, 2].
        y: An array of shape [n_samples,]. Only contains 1 or -1.
        W: An array of shape [n_features,].
    
    Returns:
        Do not return any arguments. Save the plot to 'result.*' and include it
        in your report.
    """
    ### YOUR CODE HERE
    show_features(X, y, save=False)

    x1_min = X[:, 0].min()
    x1_max = X[:, 0].max()
    x1 = np.linspace(x1_min, x1_max, 100)
    x2 = -(W[0] + W[1] * x1) / W[2]

    plt.plot(x1, x2, 'k-', label='Decision Boundary')
    plt.legend()
    plt.savefig('result.png')
    plt.show()
    plt.close()


    ### END YOUR CODE



def test_perceptron(max_iter, X_train, y_train, X_test, y_test):

    # train perceptron
    model = Perceptron(max_iter)
    model.fit(X_train, y_train)
    train_acc = model.score(X_train, y_train)
    W = model.get_params()

    # test perceptron model
    test_acc = model.score(X_test, y_test)

    return W, train_acc, test_acc