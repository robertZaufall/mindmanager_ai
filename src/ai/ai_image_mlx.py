import gc
import random

from mlx import core as mx
from PIL import Image

import config_image as cfg
from huggingface_hub import snapshot_download

from mflux.models.common.config import ModelConfig
from mflux.models.flux.variants.txt2img.flux import Flux1
from mflux.models.qwen.variants.txt2img.qwen_image import QwenImage
from mflux.models.fibo.variants.txt2img.fibo import FIBO
from mflux.models.fibo_vlm.model.fibo_vlm import FiboVLM
from mflux.models.z_image.variants.turbo.z_image_turbo import ZImageTurbo


def generate_image(model, prompt, negative_prompt, n_images, outputs, seed, data={}):
    config = cfg.get_image_config(model)

    if "mflux-" not in config.IMAGE_MODEL_ID:
        raise ValueError("Model not supported")

    quantize = data.get("model_quantization")
    model_name = (
        config.IMAGE_MODEL_ID.replace("mflux-", "")
        .replace("-4bit", "")
        .replace("-8bit", "")
        .replace("-6bit", "")
    )

    base_outputs = outputs[:]
    current_seed = seed
    guidance = float(data.get("guidance", "3.5"))
    height = int(data.get("image_height"))
    width = int(data.get("image_width"))
    num_inference_steps = int(data.get("num_steps"))
    negative_prompt = data.get("negative_prompt", "")

    # Qwen
    if model_name == "qwen":
        generator = QwenImage(
            quantize=quantize
        )
    
    # Fibo
    elif model_name == "fibo":
        generator = FIBO(
            quantize=quantize
        )
        vlm = FiboVLM(quantize=quantize)
        prompt = vlm.generate(prompt=prompt, seed=seed)
        del vlm
        gc.collect()
        mx.clear_cache()
    
    # Z-Image Turbo
    elif model_name == "z-image-turbo":
        generator = ZImageTurbo(
            quantize=quantize
        )
    
    # Flux
    else:
        generator = Flux1(
            model_config=ModelConfig.from_name(model_name=model_name, base_model=model_name),
            quantize=quantize
        )
    
    for index in range(n_images):
        generate_kwargs = {
            "seed": current_seed,
            "prompt": prompt,
            "width": width,
            "height": height,
            "num_inference_steps": num_inference_steps,
        }

        if model_name == "z-image-turbo":
            image = generator.generate_image(**generate_kwargs)
        else:
            generate_kwargs.update(
                guidance=guidance,
                negative_prompt=negative_prompt or None,
            )
            if model_name == "fibo":
                generate_kwargs["scheduler"] = "flow_match_euler_discrete"

            image = generator.generate_image(**generate_kwargs)

        used_seed = current_seed
        for output_index, base_path in enumerate(base_outputs):
            new_path = base_path.replace(".png", f"_{index}_{used_seed}.png")
            outputs[output_index] = new_path
            image.save(new_path)

        if n_images > 1 and index < n_images - 1:
            with Image.open(outputs[0]) as preview_image:
                preview_image.show()

        current_seed = random.randint(0, 2**32 - 1)

    return outputs
