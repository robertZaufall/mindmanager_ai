import mlx.core as mx
import mlx.nn as nn
import numpy as np
from PIL import Image
from tqdm import tqdm

from stable_diffusion import StableDiffusion, StableDiffusionXL

def generate_image(model, prompt, negative_prompt, n_images, steps, cfg, n_rows, decoding_batch_size, float16, quantize, preload_models, output, seed):

    # Load the models
    if model == "sdxl":
        sd = StableDiffusionXL("stabilityai/sdxl-turbo", float16=float16)
        if quantize:
            nn.quantize(
                sd.text_encoder_1, class_predicate=lambda _, m: isinstance(m, nn.Linear)
            )
            nn.quantize(
                sd.text_encoder_2, class_predicate=lambda _, m: isinstance(m, nn.Linear)
            )
            nn.quantize(sd.unet, group_size=32, bits=8)
        cfg = cfg or 0.0
        steps = steps or 2
    else:
        sd = StableDiffusion(
            "stabilityai/stable-diffusion-2-1-base", float16=float16
        )
        if quantize:
            nn.quantize(
                sd.text_encoder, class_predicate=lambda _, m: isinstance(m, nn.Linear)
            )
            nn.quantize(sd.unet, group_size=32, bits=8)
        cfg = cfg or 7.5
        steps = steps or 50

    # Ensure that models are read in memory if needed
    if preload_models:
        sd.ensure_models_are_loaded()

    # Generate the latent vectors using diffusion
    latents = sd.generate_latents(
        prompt,
        n_images=n_images,
        cfg_weight=cfg,
        num_steps=steps,
        seed=seed,
        negative_text=negative_prompt,
    )
    for x_t in tqdm(latents, total=steps):
        mx.eval(x_t)

    # The following is not necessary but it may help in memory
    # constrained systems by reusing the memory kept by the unet and the text
    # encoders.
    if model == "sdxl":
        del sd.text_encoder_1
        del sd.text_encoder_2
    else:
        del sd.text_encoder
    del sd.unet
    del sd.sampler
    peak_mem_unet = mx.metal.get_peak_memory() / 1024**3

    # Decode them into images
    decoded = []
    for i in tqdm(range(0, n_images, decoding_batch_size)):
        decoded.append(sd.decode(x_t[i : i + decoding_batch_size]))
        mx.eval(decoded[-1])
    peak_mem_overall = mx.metal.get_peak_memory() / 1024**3
    
    '''
    # Arrange them on a grid
    x = mx.concatenate(decoded, axis=0)
    x = mx.pad(x, [(0, 0), (8, 8), (8, 8), (0, 0)])
    B, H, W, C = x.shape
    x = x.reshape(n_rows, B // n_rows, H, W, C).transpose(0, 2, 1, 3, 4)
    x = x.reshape(n_rows * H, B // n_rows * W, C)
    x = (x * 255).astype(mx.uint8)

    # Save them to disc
    im = Image.fromarray(np.array(x))
    im.save(output)
    '''

    file_path = output
    for idx, img_batch in enumerate(decoded):
        for j, img in enumerate(img_batch):
            # Convert to uint8 and scale to 0-255
            img_array = (img * 255).astype(mx.uint8)
            
            # Convert to numpy array
            img_np = np.array(img_array)
            
            # Create PIL Image
            pil_img = Image.fromarray(img_np)
            
            # Save the image
            file_path = output.replace(".png", f"_{idx * decoding_batch_size + j}.png")
            pil_img.save(file_path)

    return file_path


