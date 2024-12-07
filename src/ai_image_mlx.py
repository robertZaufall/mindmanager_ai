import random
import config
from PIL import Image

def generate_image(prompt, negative_prompt, n_images, output, seed):

    from mflux import Flux1, Config

    original_output = output

    if "-flux1" in config.IMAGE_MODEL_ID:

        flux = Flux1.from_alias(
            alias = config.IMAGE_MODEL_VERSION,
            quantize = config.IMAGE_MODEL_QUANTIZATION,
        )

        for i in range(n_images):
            output = original_output.replace(".png", f"_{i}_{seed}.png")

            image = flux.generate_image(
                seed=seed,
                prompt=prompt,
                config=Config(
                    num_inference_steps=config.IMAGE_NUM_STEPS,  # "schnell" works well with 2-4 steps, "dev" works well with 20-25 steps
                    height=config.IMAGE_HEIGHT,
                    width=config.IMAGE_WIDTH,
                )
            )

            image.save(output)
            seed = random.randint(0, 2**32 - 1)

            if n_images > 1 and i < n_images - 1:
                pimage = Image.open(output)  
                pimage.show()

        return output
    else:
        raise ValueError("Only FLUX model is supported")
