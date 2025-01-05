import random
import config as cfg
from PIL import Image

def generate_image(model, prompt, negative_prompt, n_images, outputs, seed):
    from mflux import Flux1, Config

    config = cfg.get_image_config(model)

    if "-flux1" in config.IMAGE_MODEL_ID:
        flux = Flux1.from_alias(
            alias = config.IMAGE_MODEL_VERSION,
            quantize = config.IMAGE_MODEL_QUANTIZATION,
        )
        for i in range(n_images):
            image = flux.generate_image(
                seed=seed,
                prompt=prompt,
                config=Config(
                    num_inference_steps=config.IMAGE_NUM_STEPS,  # "schnell" works well with 2-4 steps, "dev" works well with 20-25 steps
                    height=config.IMAGE_HEIGHT,
                    width=config.IMAGE_WIDTH)
            )
            seed = random.randint(0, 2**32 - 1)
            for i in range(len(outputs)):
                outputs[i] = outputs[i].replace(".png", f"_{i}_{seed}.png")
                image.save(outputs[i])

            if n_images > 1 and i < n_images - 1:
                pimage = Image.open(outputs[0])  
                pimage.show()
        return outputs
    else:
        raise ValueError("Only FLUX model is supported")
