import tensorflow as tf
import numpy as np
import pandas as pd
from sklearn import preprocessing
from scipy.stats import spearmanr
import time

FILENAME = "halide_blur_3x3_gpu.csv"

# ------------------Data-----------------------#
data = np.array(pd.read_csv(FILENAME))

# currently input data length is hardcoded:
train_data = data[:500]
test_data = data[500:]

X_train = np.array(train_data[:, [1, 2, 3, 4]])
y_train = np.array(train_data[:, [0]])
X_test = np.array(test_data[:, [1, 2, 3, 4]])

print(test_data.shape)

x = tf.placeholder(tf.float32, [None, 4])
y = tf.placeholder(tf.float32, [None, 1])  

X_train = preprocessing.scale(X_train)  
X_test = preprocessing.scale(X_test)  

print(X_test.shape)

# ------------------Model----------------------#
# hidden layer
L1 = tf.layers.dense(x, 5, tf.nn.relu)
L2 = tf.layers.dense(x, 5, tf.nn.relu)
# output layer
prediction = tf.layers.dense(L2,1)
# loss function: MSE
loss = tf.reduce_mean(tf.square(y - prediction))
# train step
train_step = tf.train.AdamOptimizer(0.01).minimize(loss)
# print out total parameters of the model: our model needs to be lightweight
total_parameters = 0
for variable in tf.trainable_variables():
    shape = variable.get_shape()
    print(shape)
    print(len(shape))
    variable_parameters = 1
    for dim in shape:
        print(dim)
        variable_parameters *= dim.value
    print(variable_parameters)
    total_parameters += variable_parameters
print("total parameters: ", total_parameters)

saver = tf.train.Saver()

with tf.Session() as sess:

    sess.run(tf.global_variables_initializer())
    print(sess.run(loss, feed_dict={x: X_train, y: y_train}))
    # training
    for i in range(10000):
        sess.run(train_step, feed_dict={x: X_train, y: y_train})
        if i % 200 == 0:
            print(i)
            print(sess.run(loss, feed_dict={x: X_train, y: y_train}))

    # inference
    inference_start = time.clock()
    prd = sess.run(prediction, feed_dict={x: X_test})
    inference_end = time.clock()
    
    # print out inference time: our model needs to make quick decisions during runtime
    print('Inference time:', (inference_end - inference_start) / test_data.shape[0])
    
    # write results to a file for further inspection
    f = open('re.txt', 'w')
    for i in range(test_data.shape[0]):
        f.writelines(str(prd[i][0]) + "\n")
    f.close()

    # ------------------Results--------------------#
    # calculate MAE, MSE, and MAPE
    sum_MAE = 0.0
    sum_MSE = 0.0
    sum_MAPE_1 = 0.0
    sum_MAPE_5 = 0.0

    pred_list = []
    test_list = []

    testdata_length = test_data.shape[0]
    MAPE_1_length = 0
    MAPE_5_length = 0

    for i in range(test_data.shape[0]):

        pred_value = prd[i][0]
        truth_value = test_data[:, [0]][i][0]
        abs_value = abs(prd[i][0] - test_data[:, [0]][i][0])
        # we focus on prediction accuracy for data instances with a relatively large execution time
        # if the execution time > 0.1s
        if truth_value > 0.1:
            sum_MAPE_1 += (abs_value/truth_value)
            MAPE_1_length+=1
        # if the execution time > 0.5s
        if truth_value > 0.5:
            sum_MAPE_5 += (abs_value / truth_value)
            MAPE_5_length+=1

        sum_MAE += abs_value
        sum_MSE += pow(prd[i][0] - test_data[:, [0]][i][0], 2)

        pred_list.append(pred_value)
        test_list.append(truth_value)
    # summary
    print("MAE: ", sum_MAE / test_data.shape[0])
    print("MSE: ", sum_MSE / test_data.shape[0])
    print("MAPE(>0.1s): ", sum_MAPE_1 / MAPE_1_length)
    print("MAPE(>0.5s): ", sum_MAPE_5 / MAPE_5_length)
    # Spearman's rank correlation coefficient
    rho, pval = spearmanr(pred_list,test_list)
    print('rho:', rho)

    # --------------------------------------------#
    # save model 
    saver.save(sess, "model/my-model")
