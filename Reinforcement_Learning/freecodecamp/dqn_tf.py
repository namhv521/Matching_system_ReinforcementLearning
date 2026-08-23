import os  
import numpy as np
import tensorflow as tf

class DeepQNetwork(object):
    def __init__(self, lr, n_actions, name, fc1_dims=256,
                 input_dims=(210,160,4), chkpt_dir = 'tmp/dqn')
        self.lr = lr
        self.name = name
        self.n_actions = n_actions
        self.fc1_dims = fc1_dims
        self.input_dims = input_dims
        self.sess = tf.session()
        self.build_network()
        self.sess.run(tf.global_variables_initializer())
        self.saver = tf.train.Saver()
        self.checkpoint_file = os.path.join(chkpt_dir, 'deepqnet.ckpt')
        self.params = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES,
                                        scope = self.name)

    def build_net(self):
        with tf.variable_scope(self.name):
            self.input = tf.placeholder(tf.float32, shape= [None, *self.input_dims],
                                        name= 'inputs')
            self.actions = tf.placehoder(tf.float32, shape=[None, *self.n_actions],
                                         name ='action_taken')
            self.q_target = tf.placehoder(tf.float32, shape=[None, *self.n_actions])

            conv1 = tf.layer.conv2d(inputs = self.input, filtes= 32,
                                    kernel_size = (8,8), strides = 4, name = 'conv1',
                    kernel_initializer = tf.variance_scaling_initalizer(scale = 2))
            conv1_activated = tf.nn.relu(conv1)

            conv2 = tf.layer.conv2d(inputs =conv1_activated, filters= 64,
                                    kernel_size = (4,4),strides = 2, name='conv2',
                    kernel_initializer = tf.variance_scaling_initializer(scale = 2))
            conv2_activated = tf.nn.relu(conv2)

            conv3 = tf.layer.conv2d(inputs = conv2_activated, filter = 128,
                                    kernel_size = (3,3), strides = 1, name = 'conv3',
                    kernel_initializer = tf.variance_scaling_initializer(scale = 2))
            conv3_activated = tf.nn.relu(conv3)

            flat = tf.layer.flatten(conv3_activated)
            dense1 = tf.layer.dense(flat,inits = self.fc1_dims,
                                    activation  =tf.nn.relu,
                    kernel_initializer = tf.variance_scaling_initializer(scale =2))
            self.Q_vales = tf.layer.dense(dense1, units = self.n_actions,
                    kernel_initializer = tf.variance_scaling_initializer(scale = 2))
            self.q = tf.reduce_sum(tf.multiply(self.Q_values, self.actions))
            self.loss = tf.reduce_mean(tf.square(self.q - self.q_target))
            self.train_io = tf.train.AdamOptimizer(self.lr).minimize(self.loss)


    def load_checkpint(self):
        print('... loading checkpoint ... ')
        self.saver.restore(self.sess, self.checkpoint_file)

    def save_checkpoint(self):``
        print('... saving checkpoint ... ')
        self.saver.save(self.sess, self.checkpoint_file)

    class Agent(object):
        def __init__(self, alpha, gamma, mem_size,n_actions, epsilon, batch_size,
                     replace_target = 5000, input_dims = (210,160,4),
                    q_next = 'tmp/q_next', q_eval ='tmp/q_eval' ):
            self.n_actions  = n_actions
            self.action_space = [i for i in range(self.n_actions)]
            self.gamma = gamma
            self.mem_size = mem_size
            self.epsilon = epsilon
            self.batch_size = batch_size
            self.replace_targer = replace_target
            self.q_next = DeepQNetwork(alpha, n_actions, input_dims = input_dims,
                                       name = 'q_next', chkpt_dir = q_next_dir)
            self.q_eval = DeepQNetwork(alpha, n_actions, input_dims = input_dims,
                                       name='q_eval', chkpt = q_eval_dir)
            //24.13