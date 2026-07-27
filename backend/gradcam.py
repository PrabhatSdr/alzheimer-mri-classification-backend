import os
import cv2
import numpy as np
import tensorflow as tf


def find_last_conv_layer(model):
    """
    Finds the last convolutional layer in the model.
    """

    # Iterate through the layers in reverse order
    # to locate the final convolutional layer.
    for layer in reversed(model.layers):
        try:
            # Convolutional layers typically produce
            # 4-dimensional feature maps.
            if len(layer.output.shape) == 4:
                return layer.name
        except Exception:
            # Skip layers that do not expose an output shape.
            continue

    raise ValueError("No convolutional layer found in the model.")


def generate_gradcam(model, image_array, original_image_path, class_index, output_path):
    """
    Generates Grad-CAM heatmap and saves overlay image.
    """

    # Find the last convolutional layer used for Grad-CAM.
    last_conv_layer_name = find_last_conv_layer(model)

    # Create a model that outputs both the feature maps
    # and the final prediction scores.
    grad_model = tf.keras.models.Model(
        inputs=model.inputs,
        outputs=[
            model.get_layer(last_conv_layer_name).output,
            model.output
        ]
    )

    # Convert the input image into a TensorFlow tensor.
    image_tensor = tf.convert_to_tensor(image_array, dtype=tf.float32)

    # Record operations for automatic gradient computation.
    with tf.GradientTape() as tape:
        conv_outputs, predictions = grad_model(image_tensor)

        # Select the prediction corresponding to the target class.
        loss = predictions[:, class_index]

    # Compute gradients of the selected class
    # with respect to the convolutional feature maps.
    grads = tape.gradient(loss, conv_outputs)

    # Average the gradients across the spatial dimensions.
    pooled_grads = tf.reduce_mean(
        grads,
        axis=(0, 1, 2)
    )

    # Remove the batch dimension from the feature maps.
    conv_outputs = conv_outputs[0]

    # Compute the weighted combination of feature maps.
    heatmap = tf.reduce_sum(
        conv_outputs * pooled_grads,
        axis=-1
    )

    # Keep only positive activations for visualization.
    heatmap = tf.maximum(heatmap, 0)

    # Normalize the heatmap values to the range [0, 1].
    max_val = tf.reduce_max(heatmap)

    if max_val != 0:
        heatmap = heatmap / max_val

    heatmap = heatmap.numpy()

    # Load the original image for visualization.
    original_img = cv2.imread(original_image_path)

    if original_img is None:
        raise ValueError("Could not read original image for Grad-CAM.")

    # Resize the original image to match the model input size.
    original_img = cv2.resize(original_img, (224, 224))

    # Resize the heatmap to match the original image.
    heatmap = cv2.resize(heatmap, (224, 224))
    heatmap = np.uint8(255 * heatmap)

    # Apply a color map to improve visual interpretation.
    heatmap_color = cv2.applyColorMap(
        heatmap,
        cv2.COLORMAP_JET
    )

    # Blend the heatmap with the original image.
    overlay = cv2.addWeighted(
        original_img,
        0.6,
        heatmap_color,
        0.4,
        0
    )

    # Create the output directory if it does not already exist.
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Save the final Grad-CAM visualization.
    cv2.imwrite(output_path, overlay)

    # Return the saved image path.
    return output_path