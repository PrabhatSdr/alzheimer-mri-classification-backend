import os
import cv2
import numpy as np
import tensorflow as tf


def find_last_conv_layer(model):
    """
    Finds the last convolutional layer in the model.
    """

    for layer in reversed(model.layers):
        try:
            if len(layer.output.shape) == 4:
                return layer.name
        except Exception:
            continue

    raise ValueError("No convolutional layer found in the model.")


def generate_gradcam(model, image_array, original_image_path, class_index, output_path):
    """
    Generates Grad-CAM heatmap and saves overlay image.
    """

    last_conv_layer_name = find_last_conv_layer(model)

    grad_model = tf.keras.models.Model(
        inputs=model.inputs,
        outputs=[
            model.get_layer(last_conv_layer_name).output,
            model.output
        ]
    )

    image_tensor = tf.convert_to_tensor(image_array, dtype=tf.float32)

    with tf.GradientTape() as tape:
        conv_outputs, predictions = grad_model(image_tensor)
        loss = predictions[:, class_index]

    grads = tape.gradient(loss, conv_outputs)

    pooled_grads = tf.reduce_mean(
        grads,
        axis=(0, 1, 2)
    )

    conv_outputs = conv_outputs[0]

    heatmap = tf.reduce_sum(
        conv_outputs * pooled_grads,
        axis=-1
    )

    heatmap = tf.maximum(heatmap, 0)

    max_val = tf.reduce_max(heatmap)

    if max_val != 0:
        heatmap = heatmap / max_val

    heatmap = heatmap.numpy()

    original_img = cv2.imread(original_image_path)

    if original_img is None:
        raise ValueError("Could not read original image for Grad-CAM.")

    original_img = cv2.resize(original_img, (224, 224))

    heatmap = cv2.resize(heatmap, (224, 224))
    heatmap = np.uint8(255 * heatmap)

    heatmap_color = cv2.applyColorMap(
        heatmap,
        cv2.COLORMAP_JET
    )

    overlay = cv2.addWeighted(
        original_img,
        0.6,
        heatmap_color,
        0.4,
        0
    )

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    cv2.imwrite(output_path, overlay)

    return output_path