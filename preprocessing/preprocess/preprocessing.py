"""
Preprocessing
"""
import cv2
from scipy import ndimage


class PreProcess:
    '''
    Preprocess Configuration
    '''
    def process(self, image, preconfigjson):
        """
        Starts the preprocessing of image based on the configuration
        Args:
            image (np.array): image as numpy array
            preconfigjson (dict or json): preprocessing configuration like brightness, rotation etc.
        returns:
            image (np.array): preprocessed image as numpy array
        """
        if preconfigjson["brightness"] is not None:
            image = self.brightness_change(image, preconfigjson["brightness"])
        if (
            preconfigjson["contrast_alpha"] is not None
            and preconfigjson["contrast_beta"]
            and preconfigjson["contrast_sigma_one"] is not None
            and preconfigjson["contrast_sigma_two"] is not None
        ):
            image = self.contrast_change(
                image,
                preconfigjson["contrast_alpha"],
                preconfigjson["contrast_beta"],
                preconfigjson["contrast_sigma_one"],
                preconfigjson["contrast_sigma_two"],
            )
        if preconfigjson["orientation_degree"] is not None:
            image = self.rotate_change(image, preconfigjson["orientation_degree"])
        # if preconfigjson["image_height"] is not None and preconfigjson["image_width"] is not None:
        #     print("===>",preconfigjson["image_height"] )
        #     image=self.resize_image(image,preconfigjson["image_width"],preconfigjson["image_height"])
        # print("=====image=====")
        # print(image)
        return image

    def resize_image(self, image, width=None, height=None, inter=cv2.INTER_AREA):
        """
        performs resize of an image
        Args:
            image (np.array): image as numpy array
            width (int): new width of image
            height(int): new height of image
            inter(cv2.function): interpolation method to shrink image
        Returns:
            resized (np.array): resized imafe
        """
        dim = None
        (h, w) = image.shape[:2]
        # if both the width and height are None, then return the original image
        if width is None and height is None:
            return image
            # check to see if the width is None
        else:
            if width is None:
                # calculate the ratio of the height and construct the dimensions
                r = height / float(h)
                dim = (int(w * r), height)
            # otherwise, the height is None
            else:
                # calculate the ratio of the width and construct the dimensions
                r = width / float(w)
                dim = (width, int(h * r))
            # resize the image
            resized = cv2.resize(image, dim, interpolation=inter)
            # return the resized image
            return resized

    def brightness_change(self, image, bright):
        """
        Preprocessing for brihtness
        Args:
            image (np.array): image from camera
        returns:
            image (np.array): image after preprocessing applied
        """
        image = cv2.convertScaleAbs(image, beta=float(bright))
        return image

    def contrast_change(self, image, alpha, beta, sigma_1, sigma_2):
        """
        Preprocessing for contrast_alpha
        Args:
            image (np.array): image from camera
        returns:
            image (np.array): image after preprocessing applied
        """
        image = cv2.convertScaleAbs(image, alpha=float(alpha), beta=float(beta))
        enhancedimage = cv2.detailEnhance(image, sigma_s=float(sigma_1), sigma_r=float(sigma_2))
        return enhancedimage

    def rotate_change(self, image, value):
        """
        Rotate Image
        Args:
            image (np.array): numpy array of image
        returns:
            value: rotation value
        """
        return ndimage.rotate(image, float(value), reshape=True)

    def mask_image(self, image):
        """
        Preprocessing for masking image
        Args:
            image (np.array): image from camera
        returns:
            image (np.array): image after preprocessing applied
        """

        return image

    def split_rows(self, image):
        """
        Preprocessing for split rows
        Args:
            image (np.array): image from camera
        returns:
            image (np.array): image after preprocessing applied
        """
        return image

    def split_columns(self, image):
        """
        Preprocessing for split columns
        Args:
            image (np.array): image from camera
        returns:
            image (np.array): image after preprocessing applied
        """
        return image

    def split(self, image):
        """
        Preprocessing for split image
        Args:
            image (np.array): image from camera
        returns:
            image (np.array): image after preprocessing applied
        """
        return image

    def threshold(self, image):
        """
        Preprocessing for threshold
        Args:
            image (np.array): image from camera
        returns:
            image (np.array): image after preprocessing applied
        """
        return image
