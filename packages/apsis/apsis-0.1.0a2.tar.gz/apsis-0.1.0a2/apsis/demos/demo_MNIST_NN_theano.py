__author__ = 'Frederik Diehl'

# Code adapted from http://nbviewer.ipython.org/github/craffel/theano-tutorial/blob/master/Theano%20Tutorial.ipynb

import numpy as np
import matplotlib.pyplot as plt
import theano
import theano.tensor as T
from sklearn.datasets import fetch_mldata
import os
from sklearn.cross_validation import train_test_split
from sklearn.utils import shuffle

class Layer(object):
    def __init__(self, W_init, b_init, activation):
        n_output, n_input = W_init.shape
        assert b_init.shape == (n_output,)
        self.W = theano.shared(value=W_init.astype(theano.config.floatX),
                               name='W',
                               borrow=True)
        self.b = theano.shared(value=b_init.reshape(-1, 1).astype(theano.config.floatX),
                               name='b',
                               borrow=True,
                               broadcastable=(False, True))
        self.activation = activation
        self.params = [self.W, self.b]

    def output(self, x):
        lin_output = T.dot(self.W, x) + self.b
        return (lin_output if self.activation is None else self.activation(lin_output))

class MLP(object):
    def __init__(self, W_init, b_init, activations):
        assert len(W_init) == len(b_init) == len(activations)
        self.layers = []
        for W, b, activation in zip(W_init, b_init, activations):
            self.layers.append(Layer(W, b, activation))
        self.params = []
        for layer in self.layers:
            self.params += layer.params

    def output(self, x):
        for layer in self.layers:
            x = layer.output(x)
        return x

    def squared_error(self, x, y):
        return T.sum((self.output(x) - y)**2)

def gradient_updates_momentum(cost, params, learning_rate, momentum):
    assert momentum < 1 and momentum >= 0
    updates = []
    for param in params:
        param_update = theano.shared(param.get_value()*0., broadcastable=param.broadcastable)
        updates.append((param, param - learning_rate*param_update))
        updates.append((param_update, momentum*param_update + (1. - momentum)*T.grad(cost, param)))
    return updates



def load_mnist(percentage=1):
    mnist = fetch_mldata('MNIST original',
                         data_home=os.environ.get('MNIST_DATA_CACHE', '~/.mnist-cache'))

    mnist.data, mnist.target = shuffle(mnist.data, mnist.target, random_state=0)

    mnist.data = mnist.data[:int(percentage*mnist.data.shape[0])]
    mnist.target = mnist.target[:int(percentage*mnist.target.shape[0])]
    mnist_target_matrix = np.zeros((mnist.target.shape[0], 10))
    for i in range(mnist.target.shape[0]):
        mnist_target_matrix[i, mnist.target[i]] = 1
    #train test split
    X, VX, Z, VZ = \
        train_test_split(mnist.data, mnist_target_matrix, test_size=0.1, random_state=42)
    #for a in [X, Z, VX, VZ]:
    #    a.transpose()
    return X.transpose(), Z.transpose(), VX.transpose(), VZ.transpose()

def init_mlp(layer_sizes):
    W_init = []
    b_init = []
    activations = []
    for n_input, n_output in zip(layer_sizes[:-1], layer_sizes[1:]):
        W_init.append(np.random.uniform(low=-n_input**0.5, high=n_input**0.5, size=(n_output, n_input)))
        b_init.append(np.ones(n_output))
        activations.append(T.nnet.sigmoid)
    return MLP(W_init, b_init, activations)

if __name__ == '__main__':
    percentage = 0.01
    X, Z, VX, VZ = load_mnist(percentage)
    for a in [X, Z, VX, VZ]:
        print(a.shape)
    hidden_size = X.shape[0]
    layer_sizes = [X.shape[0], hidden_size, hidden_size, hidden_size, 10]
    mlp = init_mlp(layer_sizes)
    mlp_input = T.matrix('mlp_input')
    mlp_target = T.matrix('mlp_target')
    learning_rate = 0.01
    momentum = 0.99
    cost = mlp.squared_error(mlp_input, mlp_target)
    train = theano.function([mlp_input, mlp_target], cost,
                            updates=gradient_updates_momentum(cost, mlp.params, learning_rate, momentum), allow_input_downcast=True)
    mlp_output = theano.function([mlp_input], mlp.output(mlp_input), allow_input_downcast=True)

    ZL = np.argmax(Z, 0)
    VZL = np.argmax(VZ, 0)
    accs = []
    val_accs = []
    for i in range(0, 100):
        current_cost = train(X, Z)
        current_output = mlp_output(X)
        # We can compute the accuracy by thresholding the output
        # and computing the proportion of points whose class match the ground truth class.
        prediction = np.argmax(current_output, 0)

        accuracy = np.mean(prediction == ZL)
        accs.append(accuracy)
        output_val = mlp_output(VX)
        prediction_val= np.argmax(output_val, 0)
        accuracy_val = np.mean(prediction_val == VZL)
        val_accs.append(accuracy_val)
        print("%i:\t%f\t%f" %(i, accuracy, accuracy_val))
        # Plot network output after this iteration
        #plt.figure(figsize=(8, 8))
        #plt.scatter(X[0, :], X[1, :], c=current_output,
        #            lw=.3, s=3, cmap=plt.cm.cool, vmin=0, vmax=1)
        #plt.axis([-6, 6, -6, 6])
        #plt.title('Cost: {:.3f}, Accuracy: {:.3f}'.format(float(current_cost), accuracy))
        #plt.show()
    plt.plot(val_accs, label="Validation accuracy")
    plt.plot(accs, label="training accuracy")
    plt.legend("lower left")
    plt.show()