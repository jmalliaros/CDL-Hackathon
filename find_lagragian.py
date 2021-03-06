import tensorflow as tf

x = tf.get_variable("x", shape = [1], initializer = tf.constant_initializer(0.0))
y = tf.get_variable("y", shape = [1], initializer = tf.constant_initializer(0.0))
lamb = tf.get_variable("lambda", shape = [1], initializer = tf.constant_initializer(-3.0))


# The problem is f(x) = x1 + x2,
# c(x) = x1^2 + x2^2 - 1, where c(x) = 0

f_x = x + y
c_x = tf.square(x)+tf.square(y)-1

# Lagrange function / Lagrangian. There's only one constraint c(x).
Lagrange = f_x - lamb*(c_x)

learning_rate = 0.01

lamb_gradient = tf.gradients(ys = Lagrange, xs=lamb, grad_ys= learning_rate)

train2 = tf.assign(lamb, tf.reshape(lamb + lamb_gradient, [-1]))

train1 = tf.train.GradientDescentOptimizer(learning_rate).minimize(loss = Lagrange, var_list = [x, y])
sess = tf.Session()
sess.run(tf.global_variables_initializer())

f_x_tract = []
c_x_tract = []
lamb_tract = []

while True:
    prev = sess.run(Lagrange)
    while True:
        for i in range(10):
            sess.run(train1)
        curr = sess.run(Lagrange)
        if abs(curr - prev )<0.01: # Until Convergence
            break
        prev = curr
    sess.run(train2)
    f_x_tract.append(sess.run(f_x))
    c_x_tract.append(sess.run(c_x))
    lamb_tract.append(sess.run(lamb))
    if abs(sess.run(c_x))<0.001: # Until Convergence
        break

print(lamb_tract[-1])
