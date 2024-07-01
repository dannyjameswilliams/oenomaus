# PIL for image processing
from PIL import Image, ImageSequence

# Numpy for matrix manipulation
import numpy as np

# Scipy for matrix rotation
from scipy.ndimage import rotate

# time for timing functions
import time

# HTML requests for image download
import requests
from io import BytesIO

# log the gif making process (only time taken)
log = True

# parameter to adjust number of frames in gif. by default takes every frame, but larger values will skip frames according to the value
# e.g. every_n_frames = 2 will take every second frame etc.
every_n_frames = 2

def create_upper_fragments(bigimagenp, small_upper, topleftpos, shatter_size):
    """
    Create fragments of the upper part of the small image to be whipped (shattering).
    """
    
    small_upper_size = small_upper.shape

    horizontal_segment = small_upper[-shatter_size:]

    fragments = []
    cumulative_fragment_size = 0
    while cumulative_fragment_size < small_upper_size[1]:

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

    return fragments

def create_lower_fragments(bigimagenp, small_upper, small_lower, topleftpos, shatter_size):
    """
    Create fragments of the lower part of the small image to be whipped (shattering).
    """

    small_lower_size = small_lower.shape


    horizontal_segment = small_lower[:shatter_size]

    fragments = []
    cumulative_fragment_size = 0
    while cumulative_fragment_size < small_lower_size[1]:

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

    return fragments


def format_and_split_images_with_shatter(bigimagenp, smallimagenp, topleftpos = (0, 0), shatter_size = 15):
    """
    Split the small image (anime to be whipped) into two parts and fragments.
    Same size as big image padded with nans to fill the gaps
    """

    # split small image in two  
    small_upper = smallimagenp[:(smallimagenp.shape[0] // 2), :, :]
    small_lower = smallimagenp[(smallimagenp.shape[0] // 2):, :, :]

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
    """
    Effects for the upper fragments.
    I.e. move upwards, left or right, spin.

    direction: array size len(fragments); for every unit upwards, how many units left (negative) or right (positive) it will move       
    spin_direction: array size len(fragments); for every unit upwards, how many degrees it will spin
    speed: array size len(fragments); for every unit upwards, how many units it will move
    """
    
    fragments_out = []

    # each fragment has a speed/direction/spin associated to it individually
    for j, fragment in enumerate(upper_fragments):

        # move fragment upwards speed[j]
        fragment = np.vstack((
            fragment,
            np.nan*np.zeros((speed[j], fragment.shape[1], 3))
        ))
        fragment = fragment[speed[j]:] 

        # move fragment left direction[j]
        if direction[j] < 0:

            fragment = np.hstack((
                fragment,
                np.nan*np.zeros((fragment.shape[0], -direction[j], 3))
            ))

            fragment = fragment[:, (-direction[j]):]

        # or right direction[j]
        elif direction[j] > 0:

            fragment = np.hstack((
                np.nan*np.zeros((fragment.shape[0], direction[j], 3)),
                fragment
            ))

            fragment = fragment[:, :(-direction[j])]    
        
        # randomly spin fragment
        fragment = rotate(fragment, spin_direction[j], reshape=False, order=1, cval = np.nan)

        fragments_out.append(fragment)

    return fragments_out

def lower_fragment_effects(lower_fragments, direction, spin_direction, speed):
    """
    Same as above but speed moves downwards.
    """
    fragments_out = []
    for j, fragment in enumerate(lower_fragments):

        # move fragment downwards
        fragment = np.vstack((
            np.nan*np.zeros((speed[j], fragment.shape[1], 3)),
            fragment
        ))
        fragment = fragment[:(-speed[j])] 

        if direction[j] < 0:

            fragment = np.hstack((
                fragment,
                np.nan*np.zeros((fragment.shape[0], -direction[j], 3))
            ))

            fragment = fragment[:, (-direction[j]):]

        elif direction[j] > 0:

            fragment = np.hstack((
                np.nan*np.zeros((fragment.shape[0], direction[j], 3)),
                fragment
            ))

            fragment = fragment[:, :(-direction[j])]    
        
        fragment = rotate(fragment, spin_direction[j], reshape=False, order=1, cval = np.nan)

        fragments_out.append(fragment)

    return fragments_out

def upper_effects(small_upper, i):
    """
    Effects on the upper part of the small image (not fragments).
    I.e. moves upwards and rotates away to left.
    """

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
    """
    Effects on the lower part of the small image (not fragments).
    I.e. moves downwards and rotates away to right.
    """

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

    n_frames = min(50, bigimagenp.shape[0])

    # initialise animation array
    anim = np.empty((n_frames, bigimagenp.shape[1], bigimagenp.shape[2], bigimagenp.shape[3]))

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

    # initialise counting variable at non-zero
    i = 1

    # loop over frames and rotation/scale index i
    for frame in range(n_frames):
        
        if frame > int(n_frames/2):
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

        anim[frame, :, :, :] = bigimagenp[frame]


    # cut animation to the last frame rendered
    anim = anim[:frame]

    # Save gif to resources/current_whip.gif
    numpy_array_to_gif(anim, 'resources/current_whip.gif')

def numpy_array_to_gif(array, filepath, fps=20):
    """
    Save a numpy array of frames as a GIF file.
    """

    # Convert each frame in the numpy array to an image
    frames = [Image.fromarray(np.array(frame*255, dtype=np.uint8)) for frame in array]

    # Calculate the duration for each frame

    # duration mod asymptotically approaches 2 as every_n_frames increases
    duration_mod = lambda x: 2 - 1/(x+1)
    duration = (1000 // fps) *duration_mod(every_n_frames) # duration in milliseconds

    # Save all frames as a GIF
    frames[0].save(filepath, save_all=True, append_images=frames[1:], loop=0, duration=duration)

def gif_to_numpy_array(bigimage, every_n_frames=every_n_frames):
    """
    Load a GIF file and return a numpy array of its frames.
    """

    frames = []
    for frame in ImageSequence.Iterator(bigimage):
        frame_array = np.array(frame.convert('RGB'))
        frames.append(frame_array)
    frames_array = np.array(frames)/255
    return frames_array[np.arange(0, len(frames_array), every_n_frames)]


def adaptive_resize(height, width, target_dim = 200):
    """
    Get the size of the image as close to target_dim, target_dim as possible while keeping aspect ratio.
    Returns height and width.
    """
    
    if height > width:
        new_height = target_dim
        new_width = int(width * (new_height / height))
    else:
        new_width = target_dim
        new_height = int(height * (new_width / width))

    return new_height, new_width

def resize_image(img, height, width):
    return img.resize((width, height), Image.Resampling.NEAREST)

def resize_gif(gif, height, width, do_resize=True):
    """
    Resize a gif to a new height and width.
    """

    # resize each frame
    
    frames = []
    for frame in ImageSequence.Iterator(gif):
        if do_resize:
            frame = frame.resize((width, height), Image.Resampling.NEAREST)
        frames.append(frame)
    
    # combine frames into gif using pil
    output_image = frames[0]
    output_image.save(
        "resources/resized.gif",
        save_all=True,
        append_images=frames[1:],
        disposal=gif.disposal_method,
        **gif.info,
    )    
    
def get_images(bigpath, smallpath):

    bigimage = Image.open(bigpath)
    bigimagenp = gif_to_numpy_array(bigimage)

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

def do_gif(main_gif_path = "resources/whip.gif", image="https://ichef.bbci.co.uk/news/976/cpsprodpb/F382/production/_123883326_852a3a31-69d7-4849-81c7-8087bf630251.jpg"):
    """
    Do everything in order.
    """

    t0 = time.perf_counter()

    # Retrieve images 
    bigimagenp, smallimage = get_images(main_gif_path, image)

    # Resize the small image
    height, width = adaptive_resize(smallimage.height, smallimage.width)

    # Format the images
    smallimagenp = format_image(smallimage, height, width)

    # Split the images and create fragments
    small_upper, small_lower, upper_fragments, lower_fragments = format_and_split_images_with_shatter(bigimagenp, smallimagenp, topleftpos=(100, 100))

    # Construct the animation
    construct_animation(bigimagenp, small_upper, small_lower, upper_fragments, lower_fragments)

    if log:
        print(f"Time taken for GIF creation: {time.perf_counter() - t0}")


