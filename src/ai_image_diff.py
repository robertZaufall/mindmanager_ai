import config
from PIL import Image

from diffusionkit.mlx import FluxPipeline

def generate_image(prompt, negative_prompt, n_images, output, seed):
    pipeline = FluxPipeline(
        model=config.DIFF_MODEL,
        shift=config.DIFF_SHIFT,
        model_version=config.DIFF_MODEL_VERSION,
        low_memory_mode=config.DIFF_LOW_MEMORY_MODE,
        a16=config.DIFF_A16,
        w16=config.DIFF_W16
    )

    image, _ = pipeline.generate_image(
        prompt,
        cfg_weight=config.IMAGE_CFG_WEIGHT,
        num_steps=config.IMAGE_NUM_STEPS,
        latent_size=(config.IMAGE_HEIGHT // 8, config.IMAGE_WIDTH // 8),
        seed = seed,
        negative_text=negative_prompt,
    )

    image.save(output)

    return output
