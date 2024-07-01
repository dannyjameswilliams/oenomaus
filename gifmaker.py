

from PIL import Image, ImageSequence
import numpy as np
from moviepy.editor import ImageSequenceClip
from scipy.ndimage import zoom, rotate
from scipy import ndimage

import requests
from io import BytesIO



def numpy_array_to_gif(array, filepath, fps=20):
    # Convert each frame in the numpy array to an image
    frames = [Image.fromarray(np.array(frame*255,dtype=np.uint8)) for frame in array]
    # Calculate the duration for each frame
    duration = 1000 // fps  # duration in milliseconds
    # Save all frames as a GIF
    frames[0].save(filepath, save_all=True, append_images=frames[1:], loop=0, duration=duration)

def gif_to_numpy_array(filepath):
    img = Image.open(filepath)
    frames = []
    for frame in ImageSequence.Iterator(img):
        frame_array = np.array(frame.convert('RGB'))
        frames.append(frame_array)
    frames_array = np.array(frames)/255
    return frames_array


# def dispImage(im):
#     display(Image.fromarray(np.array(im*255, dtype=np.uint8)))

def format_and_split_images(bigimagenp, smallimagenp, topleftpos = (0, 0)):

    # split small image in two
    small_upper = smallimagenp[:(smallimagenp.shape[0] // 2), :, :]
    small_lower = smallimagenp[(smallimagenp.shape[0] // 2):, :, :]

    # change zero values (true black) to a slightly higher value (optional)
    # small_upper[small_upper == 0] = 1
    # small_lower[small_lower == 0] = 1

    # save size of small_upper
    small_upper_size = small_upper.shape

    # pad zeros on top and below
    small_upper = np.vstack((
        np.nan*np.zeros((topleftpos[0], small_upper.shape[1], 3)),
        small_upper,
        np.nan*np.zeros((bigimagenp.shape[1] - small_upper.shape[0] - topleftpos[0], small_upper.shape[1], 3))
    ))

    # pad zeros left and right
    small_upper = np.hstack((
        np.nan*np.zeros((small_upper.shape[0], topleftpos[1], 3)),
        small_upper,
        np.nan*np.zeros((small_upper.shape[0], bigimagenp.shape[2] - small_upper.shape[1] - topleftpos[1], 3))
    ))

    # same for lower, but it needs to start below small_upper
    small_lower = np.vstack((
        np.nan*np.zeros((topleftpos[0] + small_upper_size[0], small_lower.shape[1], 3)),
        small_lower,
        np.nan*np.zeros((bigimagenp.shape[1] - small_lower.shape[0] - topleftpos[0] - small_upper_size[0], small_lower.shape[1], 3))
    ))

    # horizontal is the same
    small_lower = np.hstack((
        np.nan*np.zeros((small_lower.shape[0], topleftpos[1], 3)),
        small_lower,
        np.nan*np.zeros((small_lower.shape[0], bigimagenp.shape[2] - small_lower.shape[1] - topleftpos[1], 3))
    ))

    return small_upper, small_lower

def create_upper_fragments(bigimagenp, small_upper, topleftpos, shatter_size):

    # print(f"creating upper fragments...")
    small_upper_size = small_upper.shape


    horizontal_segment = small_upper[-shatter_size:]

    fragments = []
    cumulative_fragment_size = 0
    while cumulative_fragment_size < small_upper_size[1]:

        # print(f"fragment {len(fragments)}: cumulative_fragment_size = {cumulative_fragment_size}/{small_upper_size[1]}")

        # create random size fragments
        fragment_size = min(np.random.randint(7, 15), small_upper_size[1] - cumulative_fragment_size) # min-max size of fragment

        fragment = horizontal_segment[:, cumulative_fragment_size:(cumulative_fragment_size+fragment_size)]

        # create fragment
        fragment = np.vstack((
            np.nan*np.zeros((topleftpos[0] + (small_upper.shape[0] - shatter_size), fragment.shape[1], 3)),
            fragment,
            np.nan*np.zeros((bigimagenp.shape[1] - topleftpos[0] - small_upper.shape[0], fragment.shape[1], 3))
        ))

        fragment = np.hstack((
            np.nan*np.zeros((fragment.shape[0], topleftpos[1] + cumulative_fragment_size, 3)),
            fragment,
            np.nan*np.zeros((fragment.shape[0], bigimagenp.shape[2] - topleftpos[1] - cumulative_fragment_size - fragment_size, 3))
        ))

        cumulative_fragment_size += fragment_size

        fragments.append(fragment)
    # print("done.\n")
    return fragments

def create_lower_fragments(bigimagenp, small_upper, small_lower, topleftpos, shatter_size):

    # print(f"creating upper fragments...")
    small_lower_size = small_lower.shape


    horizontal_segment = small_lower[:shatter_size]

    fragments = []
    cumulative_fragment_size = 0
    while cumulative_fragment_size < small_lower_size[1]:

        # print(f"fragment {len(fragments)}: cumulative_fragment_size = {cumulative_fragment_size}/{small_upper_size[1]}")

        # create random size fragments
        fragment_size = min(np.random.randint(7, 15), small_lower_size[1] - cumulative_fragment_size) # min-max size of fragment

        fragment = horizontal_segment[:, cumulative_fragment_size:(cumulative_fragment_size+fragment_size)]

        # create fragment
        fragment = np.vstack((
            np.nan*np.zeros((topleftpos[0] + small_upper.shape[0], fragment.shape[1], 3)),
            fragment,
            np.nan*np.zeros((bigimagenp.shape[1] - topleftpos[0] - small_upper.shape[0] - shatter_size, fragment.shape[1], 3))
        ))

        fragment = np.hstack((
            np.nan*np.zeros((fragment.shape[0], topleftpos[1] + cumulative_fragment_size, 3)),
            fragment,
            np.nan*np.zeros((fragment.shape[0], bigimagenp.shape[2] - topleftpos[1] - cumulative_fragment_size - fragment_size, 3))
        ))

        cumulative_fragment_size += fragment_size

        fragments.append(fragment)
    # print("done.\n")
    return fragments


def format_and_split_images_with_shatter(bigimagenp, smallimagenp, topleftpos = (0, 0), shatter_size = 15):

    # split small image in two
    small_upper = smallimagenp[:(smallimagenp.shape[0] // 2), :, :]
    small_lower = smallimagenp[(smallimagenp.shape[0] // 2):, :, :]

    # change zero values (true black) to a slightly higher value (optional)
    # small_upper[small_upper == 0] = 1
    # small_lower[small_lower == 0] = 1

    upper_fragments = create_upper_fragments(bigimagenp, small_upper, topleftpos, shatter_size)
    lower_fragments = create_lower_fragments(bigimagenp, small_upper, small_lower, topleftpos, shatter_size)

    # save size of small_upper
    small_upper_size = small_upper.shape

    small_upper = small_upper[:-shatter_size]


    # pad zeros on top and below
    small_upper = np.vstack((
        np.nan*np.zeros((topleftpos[0], small_upper.shape[1], 3)),
        small_upper,
        np.nan*np.zeros((bigimagenp.shape[1] - small_upper.shape[0] - topleftpos[0], small_upper.shape[1], 3))
    ))

    # pad zeros left and right
    small_upper = np.hstack((
        np.nan*np.zeros((small_upper.shape[0], topleftpos[1], 3)),
        small_upper,
        np.nan*np.zeros((small_upper.shape[0], bigimagenp.shape[2] - small_upper.shape[1] - topleftpos[1], 3))
    ))

    # same for lower, but it needs to start below small_upper
    small_lower = np.vstack((
        np.nan*np.zeros((topleftpos[0] + small_upper_size[0], small_lower.shape[1], 3)),
        small_lower,
        np.nan*np.zeros((bigimagenp.shape[1] - small_lower.shape[0] - topleftpos[0] - small_upper_size[0], small_lower.shape[1], 3))
    ))

    # horizontal is the same
    small_lower = np.hstack((
        np.nan*np.zeros((small_lower.shape[0], topleftpos[1], 3)),
        small_lower,
        np.nan*np.zeros((small_lower.shape[0], bigimagenp.shape[2] - small_lower.shape[1] - topleftpos[1], 3))
    ))

    return small_upper, small_lower, upper_fragments, lower_fragments

def upper_fragment_effects(upper_fragments, direction, spin_direction, speed):

    # print(f"creating upper fragment effects...")
    # shuffle fragments so they overlap randomly
    
    fragments_out = []
    for j, fragment in enumerate(upper_fragments):

        # direction = this will be for every unit upwards, how many units left (negative) or right (positive) it will move       

        # print(f"fragment {i}")

        # move fragment upwards
        fragment = np.vstack((
            fragment,
            np.nan*np.zeros((speed[j], fragment.shape[1], 3))
        ))
        fragment = fragment[speed[j]:] 

        # move fragment left
        if direction[j] < 0:

            fragment = np.hstack((
                fragment,
                np.nan*np.zeros((fragment.shape[0], -direction[j], 3))
            ))

            fragment = fragment[:, (-direction[j]):]

        # # or right
        elif direction[j] > 0:

            fragment = np.hstack((
                np.nan*np.zeros((fragment.shape[0], direction[j], 3)),
                fragment
            ))

            fragment = fragment[:, :(-direction[j])]    
        
        # randomly spin fragment
        fragment = rotate(fragment, spin_direction[j], reshape=False, order=1, cval = np.nan)

        fragments_out.append(fragment)

    # print(f"done.\n")
    return fragments_out

def lower_fragment_effects(lower_fragments, direction, spin_direction, speed):

    # print(f"creating upper fragment effects...")
    # shuffle fragments so they overlap randomly
    fragments_out = []
    for j, fragment in enumerate(lower_fragments):

        # direction = this will be for every unit upwards, how many units left (negative) or right (positive) it will move       

        # print(f"fragment {i}")

        # move fragment downwards
        fragment = np.vstack((
            np.nan*np.zeros((speed[j], fragment.shape[1], 3)),
            fragment
        ))
        fragment = fragment[:(-speed[j])] 

        # move fragment left
        if direction[j] < 0:

            fragment = np.hstack((
                fragment,
                np.nan*np.zeros((fragment.shape[0], -direction[j], 3))
            ))

            fragment = fragment[:, (-direction[j]):]

        # or right
        elif direction[j] > 0:

            fragment = np.hstack((
                np.nan*np.zeros((fragment.shape[0], direction[j], 3)),
                fragment
            ))

            fragment = fragment[:, :(-direction[j])]    
        
        # randomly spin fragment
        fragment = rotate(fragment, spin_direction[j], reshape=False, order=1, cval = np.nan)

        fragments_out.append(fragment)

    # print(f"done.\n")
    return fragments_out

def upper_effects(small_upper, i):

    # pad rotated lower image so it moves up by i pixels
    small_upper = np.vstack((
        small_upper,
        np.nan*np.zeros((int(i*0.75), small_upper.shape[1], 3))
    ))
    small_upper = small_upper[int(i*0.75):] 

    # Create a mask of the NaNs
    nan_mask = np.isnan(small_upper)

    # Rotate the image and the mask
    small_upper = rotate(small_upper, 1 + (i*0.05), reshape=False, order=1, cval = np.nan)
    rotated_nan_mask = rotate(nan_mask, 1 + (i*0.05), reshape=False, order=1, cval = np.nan)

    # Apply the rotated mask to the rotated image
    small_upper[rotated_nan_mask] = np.nan

    return small_upper

def lower_effects(small_lower, i):

    # pad rotated lower image so it moves down by i pixels
    small_lower = np.vstack((
        np.nan*np.zeros((int(i*0.75), small_lower.shape[1], 3)),
        small_lower
    ))
    small_lower = small_lower[:-int(i*0.75)] 

    # Create a mask of the NaNs
    nan_mask = np.isnan(small_lower)

    # Rotate the image and the mask
    small_lower = rotate(small_lower, 1 + (i*0.05), reshape=False, order=1, cval = np.nan)
    rotated_nan_mask = rotate(nan_mask, 1 + (i*0.05), reshape=False, order=1, cval = np.nan)

    # Apply the rotated mask to the rotated image
    small_lower[rotated_nan_mask] = np.nan

    return small_lower
    
def construct_animation(bigimagenp, small_upper, small_lower, upper_fragments, lower_fragments):

    # save copy of bigimage with small_upper in it to replace in each frame of animation
    # base_bigimage = bigimagenp.copy()
    
    n_frames = min(50, bigimagenp.shape[0])

    # initialise animation array
    anim = np.empty((n_frames, bigimagenp.shape[1], bigimagenp.shape[2], bigimagenp.shape[3]))

    i = 1

    # shuffle order of fragments
    np.random.shuffle(upper_fragments)
    np.random.shuffle(lower_fragments)

    # initialise directions for fragments
    upper_directions = np.random.randint(-25, 25, len(upper_fragments))
    lower_directions = np.random.randint(-25, 25, len(lower_fragments))

    upper_rotations = np.random.randint(-5, 5, len(upper_fragments))
    lower_rotations = np.random.randint(-5, 5, len(lower_fragments))

    upper_speeds = np.random.randint(10, 20, len(upper_fragments))
    lower_speeds = np.random.randint(10, 20, len(lower_fragments))

    # loop over frames and rotation/scale index i
    for frame in range(n_frames):
        # print(f"frame {frame}")
        # copy base big image
        # bigimagenp[frame] = base_bigimage[frame].copy()

        if frame > 25:
            small_lower = lower_effects(small_lower, i)
            small_upper = upper_effects(small_upper, i)
            
            upper_fragments = upper_fragment_effects(upper_fragments, upper_directions, upper_rotations, upper_speeds)
            lower_fragments = lower_fragment_effects(lower_fragments, lower_directions, lower_rotations, lower_speeds)
            
            i += 1

        
        # get mask of rotated lower image
        small_lower_mask = ~np.isnan(small_lower)
        small_upper_mask = ~np.isnan(small_upper)

        # put small images in big image
        bigimagenp[frame][small_upper_mask] = small_upper[small_upper_mask]
        bigimagenp[frame][small_lower_mask] = small_lower[small_lower_mask]

        for i, fragment in enumerate(upper_fragments):
            upper_fragment_mask = ~np.isnan(fragment)
            bigimagenp[frame][upper_fragment_mask] = fragment[upper_fragment_mask]
        
        for i, fragment in enumerate(lower_fragments):
            lower_fragment_mask = ~np.isnan(fragment)
            bigimagenp[frame][lower_fragment_mask] = fragment[lower_fragment_mask]

        # print("done.\n")
        anim[frame, :, :, :] = bigimagenp[frame]


    # cut animation to the last frame rendered
    anim = anim[:frame]

    # save gif with moviepy
    # clip = ImageSequenceClip(list(anim), fps=20)
    # clip.write_gif('test.gif', fps=20)

    # Usage
    numpy_array_to_gif(anim, 'current_whip.gif')

def adaptive_resize(height, width):
    
    # get the size of the image as close to 200, 200 as possible while keeping aspect ratio
    if height > width:
        new_height = 200
        new_width = int(width * (new_height / height))
    else:
        new_width = 200
        new_height = int(height * (new_width / width))

    return new_height, new_width

def resize_image(img, height, width):
    return img.resize((width, height), Image.Resampling.LANCZOS)

def get_images(bigpath, smallpath):

    bigimagenp = gif_to_numpy_array(bigpath)
    # smallimage = Image.open(smallpath)

    response   = requests.get(smallpath)
    smallimage = Image.open(BytesIO(response.content))
    
    # If the image is a GIF, take the first frame
    if "is_animated" in dir(smallimage):
        smallimage.seek(0)
    

    return bigimagenp, smallimage

def format_image(smallimage, height, width):
    smallimage = smallimage.convert('RGB')
    smallimage = resize_image(smallimage, height, width)
    smallimagenp = np.array(smallimage)/255
    return smallimagenp

def do_gif(main_gif_path = "whip.gif", image="testanime.png"):

    bigimagenp, smallimage = get_images(main_gif_path, image)
    height, width = adaptive_resize(smallimage.height, smallimage.width)
    smallimagenp = format_image(smallimage, height, width)
    small_upper, small_lower, upper_fragments, lower_fragments = format_and_split_images_with_shatter(bigimagenp, smallimagenp, topleftpos=(100, 100))
    construct_animation(bigimagenp, small_upper, small_lower, upper_fragments, lower_fragments)



if __name__ == "__main__":


    do_gif()


