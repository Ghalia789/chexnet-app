from pytorch_grad_cam import GradCAM
from pytorch_grad_cam.utils.image import show_cam_on_image
import numpy as np
import cv2

def setup_gradcam(model):
    target_layers = [model.densenet.features.denseblock4.denselayer16.conv2]
    return GradCAM(model=model, target_layers=target_layers)

def generate_heatmap(model, cam, img_tensor, img_array):
    grayscale_cam = cam(input_tensor=img_tensor, targets=None)
    grayscale_cam = grayscale_cam[0, :]
    
    heatmap = show_cam_on_image(
        img_array, 
        grayscale_cam,
        use_rgb=True,
        colormap=cv2.COLORMAP_JET,
        image_weight=0.6
    )
    return heatmap