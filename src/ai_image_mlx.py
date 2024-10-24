import random
import config
from PIL import Image

from diffusionkit.mlx import FluxPipeline, DiffusionPipeline

def generate_image(prompt, negative_prompt, n_images, output, seed):
    original_output = output

    for i in range(n_images):
        output = original_output.replace(".png", f"_{i}_{seed}.png")

        if "FLUX" in config.DIFF_MODEL_VERSION:
            pipeline = FluxPipeline(
                model_version=config.DIFF_MODEL_VERSION,
                low_memory_mode=config.DIFF_LOW_MEMORY_MODE,
                shift=config.DIFF_SHIFT,
                use_t5=config.DIFF_USE_T5,
                a16=config.DIFF_A16,
                w16=config.DIFF_W16
            )
        else:
            pipeline = DiffusionPipeline(
                model_version=config.DIFF_MODEL_VERSION,
                low_memory_mode=config.DIFF_LOW_MEMORY_MODE,
                shift=config.DIFF_SHIFT,
                use_t5=config.DIFF_USE_T5,
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
        seed = random.randint(0, 2**32 - 1)

        if n_images > 1 and i < n_images - 1:
            image.show()

        del pipeline
    
    return output
