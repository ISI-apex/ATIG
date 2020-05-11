import tensorflow as tf
import numpy as np
import pandas as pd
from sklearn import preprocessing

FILENAME = "out.csv"

data = np.array(pd.read_csv(FILENAME))

train_data = data[:70]
test_data = data[70:]


train_feature = np.array(train_data[:, [1, 2, 3]])


train_label = np.array(train_data[:, [0]])


test_x = np.array(test_data[:, [1, 2, 3]])


print(test_data.shape)

x = tf.placeholder(tf.float32, [None, 3])
y = tf.placeholder(tf.float32, [None, 1])  
train_feature = preprocessing.scale(train_feature)  
test_xs = preprocessing.scale(test_x)  

print(test_xs.shape)


L1 = tf.layers.dense(x, 5, tf.nn.relu)
L2 = tf.layers.dense(x, 5, tf.nn.relu)


prediction = tf.layers.dense(L2,1)



# mean
loss = tf.reduce_mean(tf.square(y - prediction))

#mean, loss = tf.nn.moments(tf.square(y - prediction), 0) #?

saver = tf.train.Saver()


train_step = tf.train.AdamOptimizer(0.01).minimize(loss)


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

with tf.Session() as sess:

    sess.run(tf.global_variables_initializer())



    print(sess.run(loss, feed_dict={x: train_feature, y: train_label}))

    for i in range(10000):
        sess.run(train_step, feed_dict={x: train_feature, y: train_label})
        if i % 200 == 0:
            print(i)
            print(sess.run(loss, feed_dict={x: train_feature, y: train_label}))


    prd = sess.run(prediction, feed_dict={x: test_xs})

    f = open('re.txt', 'w')
    for i in range(test_data.shape[0]):
        f.writelines(str(prd[i][0]) + "\n")
    f.close()


    sum = 0.0
    for i in range(test_data.shape[0]):
        sum += abs(prd[i][0] - test_data[:, [0]][i][0])
    print("MAE: ", sum / test_data.shape[0])


    saver.save(sess, "model/my-model")
