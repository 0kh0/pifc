from os import listdir
from os.path import isfile, join

import io
from PIL import Image
from PIL import ImageCms
import PIL

import matplotlib.pyplot as plt
import matplotlib.image as mpimg

import traceback
import sys

"""
img = cv.imread("debug/243.295.png")
if img is None:
    sys.exit("Could not read the image.")
cv.imshow("Display window", img)
k = cv.waitKey(0)
if k != None:
    sys.exit()
"""


BLACK_TRANSPARENCY = (0, 0, 0, 0)
WHITE_TRANSPARENCY = (255, 255, 255, 0)
PINK = (255, 0, 255, 255)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

MEGA_COLOR_LIMIT = 10000
COLOR_LIMIT = 1000
WEIRD_LIMIT = 1000

path_custom = "CustomBattlers"
path_debug = "debug"
bad_fusions = []


main_path = path_custom


TEST_SIZE = False
TEST_PALETTE = False
TEST_HIGH_DIVERSITY = False
TEST_MASSIVE_DIVERSITY = False

TEST_TRANSPARENCY = True

VERBOSE_MODE = False






def is_valid_size(image):
    return image.size == (288,288)


def show_sprite(element):
    
    image = mpimg.imread(join(main_path, element))

    print("show_sprite", type(image))

    fig, ax = plt.subplots(figsize=(4, 4))
    imgplot = plt.imshow(image)
    plt.show()


def apply_borders(pixels):
    for i in range(0, 288): 
            pixels[i, 0] = PINK
            pixels[i, 287] = PINK
            pixels[0, i] = PINK
            pixels[287, i] = PINK


def have_normal_transparency(pixels, i, j):
    if isinstance(pixels[i, j], tuple) and len(pixels[i, j]) == 4:
        return pixels[i, j][3] == 0
    else:
        return True


def have_weird_transparency(pixels, i, j):
    if isinstance(pixels[i, j], tuple) and len(pixels[i, j]) == 4:
        return pixels[i, j][3] != 0 and pixels[i, j][3] != 255
    else:
        return False


def is_not_transparent(pixels, i, j):
    return pixels[i, j][3] != 0


def detect_weird_transparency(image, pixels):
    weird_amount = 0

    if isinstance(pixels[0, 0], tuple) and len(pixels[0, 0]) == 4:
        for i in range(0, 288):
            for j in range(0, 288):

                # Weird pixels : PINK
                if have_weird_transparency(pixels, i, j):
                    # print(i, j, pixels[i, j])
                    pixels[i, j] = PINK
                    weird_amount += 1

                # Background : WHITE
                elif have_normal_transparency(pixels, i, j):
                    pixels[i, j] = WHITE

                # Actual sprite : BLACK
                else:
                    pixels[i, j] = BLACK

    return weird_amount


def find_one_pixel(pixels):
    one_pixel = None
    should_break = False
    size = 50

    for i in range(0, size):
        for j in range(0, size):
            if is_not_transparent(pixels, i, j):
                print(i, j, pixels[i, j])
                pixels[i, j] = PINK
                one_pixel = i, j
                should_break = True
                break
        if should_break:
            break
    return one_pixel


def is_using_palette(pixels):
    return isinstance(pixels[0,0], int)


def is_missing_colors(image):
    return image.getcolors(MEGA_COLOR_LIMIT) is None


def get_non_transparent_colors(image):
    old_colors = image.getcolors(MEGA_COLOR_LIMIT)
    new_colors = []

    # TODO : be careful of RGBA with 3 channels
    if old_colors is not None and isinstance(old_colors[0][1], tuple) and len(old_colors[0][1]) == 4:
        for old_color in old_colors:
            if old_color[1][3]==255:
                new_colors.append(old_color)

    return new_colors


def is_overusing_colors(image):
    colors = get_non_transparent_colors(image)
    if colors is not None:
        color_amount = len(colors)
        return color_amount > COLOR_LIMIT
    return False


def test_colors(image):
    return_value = 0
    if TEST_MASSIVE_DIVERSITY:
        try:
            if is_missing_colors(image):
                print("[MASSIVE COLOR DIVERSITY]")
                return_value = 1
        except Exception as e:
            print("test_colors", e)
            return_value = 100
    return return_value


def test_palette(pixels):
    return_value = 0
    if TEST_PALETTE:
        try:
            if is_using_palette(pixels):
                print("[COLOR PALETTE USAGE]")
                return_value = 1
        except Exception as e:
            print("test_palette", e)
            return_value = 100
    return return_value


def test_size(image):
    return_value = 0
    if TEST_SIZE:
        try:
            if not is_valid_size(image):
                print("[SIZE ERROR]", image.size)
                return_value = 1
        except Exception as e:
            print("test_size", e)
            return_value = 100
    return return_value


def test_diversity(image):
    return_value = 0
    if TEST_HIGH_DIVERSITY:
        try:
            if is_overusing_colors(image):
                color_amount = len(get_non_transparent_colors(image))
                print("[HIGH COLOR DIVERSITY]", color_amount)
                return_value = 1
        except Exception as e:
            print("test_diversity", e)
            print(traceback.format_exc())
            return_value = 100
    return return_value


# This test destroys the picture
def test_transparency(image, pixels):
    return_value = 0
    if TEST_TRANSPARENCY:
        try:
            weird_amount = detect_weird_transparency(image, pixels)
            if weird_amount > WEIRD_LIMIT:
                image.show()
                print("[TRANSPARENCY ERROR]", weird_amount)
                return_value = 1
        except Exception as e:
            if e == IndexError:
                print("test_transparency", e)
                print(traceback.format_exc())
                return_value = 100
                
    return return_value


def analyze_sprite(element):
    fusion_name = element[:-4]
    try:
        image = Image.open(join(main_path, element))
        pixels = image.load()
        
        
        # apply_borders(pixels)
        # one_pixel = find_one_pixel(pixels)
        

        # print("analyze_sprite", type(pixels))
        # image.show()
        # show_sprite(element)
        
    except Exception as e:
        # print(fusion_name, "[UNKNOWN FILE ERROR]", e, "\n")
        pass
    
    else:
        error_amount = 0

        error_amount += test_size(image)
        error_amount += test_palette(pixels)
        error_amount += test_colors(image)
        error_amount += test_diversity(image)

        # Destructive test
        error_amount += test_transparency(image, pixels)
    
        if error_amount > 0:
                print(">>",fusion_name, "\n")

        image.close()
        

def explore_sprites():
    print("[ START ]\n")
    for element in listdir(main_path):
        if isfile(join(main_path, element)) and element.endswith(".png"):
            analyze_sprite(element)
    print("[ END ]")


explore_sprites()

# analyze_sprite("243.299.png")





