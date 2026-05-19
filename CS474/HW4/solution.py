from sklearn.svm import SVC


def svm_with_diff_c(train_label, train_data, test_label, test_data):
    '''
    Use different value of cost c to train a svm model. Then apply the trained model
    on testing label and data.
    
    The value of cost c you need to try is listing as follow:
    c = [0.01, 0.1, 1, 2, 3, 5]
    Please set kernel to 'linear' and keep other parameter options as default.
    No return value is needed
    '''

    ### YOUR CODE HERE

    c_values = [0.01, 0.1, 1, 2, 3, 5]

    print("Results for different C values with linear kernel:")
    for c in c_values:
        model = SVC(C=c, kernel='linear')
        model.fit(train_data, train_label)

        accuracy = model.score(test_data, test_label)
        total_support_vectors = sum(model.n_support_)

        print(f"C = {c}")
        print(f"Accuracy = {accuracy:.4f}")
        print(f"Total support vectors = {total_support_vectors}")
        print()

    ### END YOUR CODE
    

def svm_with_diff_kernel(train_label, train_data, test_label, test_data):
    '''
    Use different kernel to train a svm model. Then apply the trained model
    on testing label and data.
    
    The kernel you need to try is listing as follow:
    'linear': linear kernel
    'poly': polynomial kernel
    'rbf': radial basis function kernel
    Please keep other parameter options as default.
    No return value is needed
    '''

    ### YOUR CODE HERE

    kernels = ['linear', 'poly', 'rbf']

    print("Results for different kernels:")
    for kernel_name in kernels:
        model = SVC(kernel=kernel_name)
        model.fit(train_data, train_label)

        accuracy = model.score(test_data, test_label)
        total_support_vectors = sum(model.n_support_)

        print(f"Kernel = {kernel_name}")
        print(f"Accuracy = {accuracy:.4f}")
        print(f"Total support vectors = {total_support_vectors}")
        print()

    ### END YOUR CODE
