import tensorflow as tf
from tensorflow.keras import layers, models


class CustomConvLayer(layers.Layer):
    def __init__(self, kernel_size, name="custom_conv_layer", **kwargs):
        super(CustomConvLayer, self).__init__(**kwargs)
        self.scaling = layers.Lambda(
            lambda x: x / (tf.reduce_sum(x, axis=[1, 2], keepdims=True) + 1e-6))
        # First convolutional layer with ReLU activation
        self.conv1 = layers.Conv2D(
            8, (3, 3), padding='same', activation='relu')
        # Second convolutional layer with 2 filters, no bias, and no activation
        self.conv2 = layers.Conv2D(
            1, (4, 4), padding='same', activation='sigmoid')

    def call(self, inputs):
        x = self.scaling(inputs)
        x = self.conv1(x)
        x_weight = self.conv2(x)
        # x_bias = self.conv1(inputs)
        # Apply second convolutional layer without activation (since we use the outputs directly)
        # conv_output = self.conv2(x)
        # weight_output = conv_output[..., 0:1]  # 0th filter output as weight
        # bias_output = conv_output[..., 1]    # 1st filter output as bias

        weight_estimated = x_weight*0.4 + 0.8

        # Apply weights and biases to the input
        # output = weight_output * inputs + bias_output
        output = weight_estimated * inputs

        # Reduce sum across height, width, and channels
        reduced_output = tf.reduce_sum(output, axis=[1, 2, 3])
        return reduced_output, weight_estimated


def buildCNNModel(input_shape=(4, 4, 1), kernel_size=(4, 4)):
    inputs = tf.keras.Input(shape=input_shape)
    x, weight_estimated = CustomConvLayer(kernel_size)(inputs)
    model = models.Model(inputs, x)
    return model


def loadCNNModel(model_path):
    best_model = models.load_model(model_path, custom_objects={
        'CustomConvLayer': CustomConvLayer})
    intermediate_layer_model = models.Model(
        inputs=best_model.input, outputs=best_model.get_layer('custom_conv_layer').output)
    return intermediate_layer_model
