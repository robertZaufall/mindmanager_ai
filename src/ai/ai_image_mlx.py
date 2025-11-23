import random

from mlx import core as mx
from PIL import Image

import config_image as cfg

def generate_image(model, prompt, negative_prompt, n_images, outputs, seed, data={}):
    config = cfg.get_image_config(model)

    if "mflux-" not in config.IMAGE_MODEL_ID:
        raise ValueError("Only FLUX model is supported")

    from mflux.generate import Config, Flux1

    model_name = (
        config.IMAGE_MODEL_ID.replace("mflux-", "")
        .replace("-4bit", "")
        .replace("-8bit", "")
        .replace("-6bit", "")
    )

    if getattr(config, "IMAGE_MODEL_VERSION", "") == "qwen":
        from huggingface_hub import snapshot_download
        from mflux.config.model_config import ModelConfig
        from mflux.models.qwen.variants.txt2img.qwen_image import QwenImage

        model_config = ModelConfig.from_name(model_name=model_name)
        local_path = snapshot_download(
            repo_id=model_config.model_name,
            allow_patterns=[
                "text_encoder/*",
                "transformer/*",
                "vae/*",
                "tokenizer/*",
            ],
            resume_download=True,
        )
        generator = QwenImage(
            model_config=model_config,
            quantize=config.IMAGE_MODEL_QUANTIZATION,
            local_path=local_path,
        )
    else:
        generator = Flux1.from_name(
            model_name=model_name,
            quantize=config.IMAGE_MODEL_QUANTIZATION,
        )

    base_outputs = outputs[:]
    current_seed = seed
    default_guidance = 3.5 if getattr(config, "IMAGE_MODEL_VERSION", "") == "dev" else 4.0
    guidance = getattr(config, "IMAGE_GUIDANCE", default_guidance)
    config_kwargs = dict(
        num_inference_steps=config.IMAGE_NUM_STEPS,
        height=config.IMAGE_HEIGHT,
        width=config.IMAGE_WIDTH,
        guidance=guidance,
    )
    precision_dtype = None
    if getattr(config, "IMAGE_MODEL_QUANTIZATION", None) is not None:
        if int(config.IMAGE_MODEL_QUANTIZATION) <= 4:
            precision_dtype = mx.float16
    for index in range(n_images):
        generation_config = Config(**config_kwargs)
        if precision_dtype is not None:
            generation_config.precision = precision_dtype
        image = generator.generate_image(
            seed=current_seed,
            prompt=prompt,
            config=generation_config,
            negative_prompt=negative_prompt or None,
        )

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
