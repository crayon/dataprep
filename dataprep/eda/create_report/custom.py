"""This module provides classes to be use when customising the context used by create_report()"""

from typing import Any, Dict, List, Optional, Tuple, Union
from plotly.graph_objects import Figure as goFigure
import PIL.Image
from io import BytesIO
import numpy as np
import base64
#from urllib.parse import quote

class CustomObject:
    """ Base Class for custom objects """
    pass

class CustomPlotly(CustomObject):
    """ Plotly-specific version of custom object """
    def __init__(
        self,
        name: str,
        obj: goFigure,
        *args,
        **kwargs,
    ) -> None:
        """ `*args` and `**kwargs` are passed to 
            plotly.graph_objects.Figure.to_html() """
        self.name = name
        self.object_type = "plotly"
        self.figure = obj # TODO: Decide if this is actually necessary
        self.html = obj.to_html(*args, **kwargs)
        # TODO: Only return the <div> child of <body> if the <style> elements 
        # from <head> can be captured elsewhere in the template

class CustomHTML(CustomObject):
    """ A wrapper around any HTML string """
    def __init__(
        self,
        name: str,
        obj: str,
    ) -> None:
        self.name = name
        self.object_type = "html"
        self.html = obj

class CustomImage(CustomObject):
    """ TO DO
        Converts `PIL.Image.Image` objects and `np.ndarray`s to PNG first.
        To insert `matplotlip.figure.Figure`s first convert them to 
        `numpy.ndarray`s using 
    """
    def __init__(
        self,
        name: str,
        obj: Union[str, PIL.Image.Image, np.ndarray]
    ) -> None:
        self.name = name
        self.object_type = "image"

        if isinstance(obj, str):
            image_url = get_image_url(obj)
            self.html = '<img class="custom-image">'+image_url+'</img>'
        elif isinstance(obj, PIL.Image.Image):
            with BytesIO() as buffer:
                obj.save(buffer, format = "PNG")
                byte_data = buffer.getvalue()
            # might have to change this to urlib.parse.quote instead of .decode()
            # if .decode() doesn't work
            image_str = base64.b64encode(byte_data).decode()
            image_url = f"data:image/png;base64,{image_str}"
            self.html = f'<img class="custom-image" src="{image_url}" />'
        elif isinstance(obj, np.ndarray):
            im = PIL.Image.fromarray(obj)
            with BytesIO() as buffer:
                im.save(buffer, format = "PNG")
                byte_data = buffer.getvalue()
            # might have to change this to urlib.parse.quote instead of .decode()
            # if .decode() doesn't work
            image_str = base64.b64encode(byte_data).decode()
            image_url = f"data:image/png;base64,{image_str}"
            self.html = f'<img class="custom-image" src="{image_url}" />'
        else:
            raise TypeError(f"obj must be a string, PIL.Image.Image or an numpy.ndarray. Got {type(obj)}")

class CustomSection:
    """ For use in add_section() and create_report.
        `CustomObject`s can be passed on initialisation or through
        the add_object() method
    """
    def __init__(
        self,
        title: str,
        customobjects: Optional[Union[CustomObject, List[CustomObject]]] = None,
    ) -> None:
        self.title = title
        self.customobjects = []
        if isinstance(customobjects, CustomObject):
            self.customobjects += [customobjects]
        elif isinstance(customobjects, list):
            self.customobjects += customobjects
        else:
            None

    def add_object(self, customobject: Union[CustomHTML, CustomPlotly, CustomImage]):
        self.customobjects.append(customobject)
        return self

def get_image_url(path: str):
    """ Generates a base64 url from an image file path
        path
            path to file that can be loaded by open().
    """
    mime_types = {
        "png": "image/png", 
        "svg": "image/svg+xml", #not yet tested
        "apng": "image/apng", #not yet tested
        "avif": "image/avif", #not yet tested
        "gif": "image/gif", #not yet tested
        "jpg": "image/jpeg", #not yet tested
        "jpeg": "image/jpeg", #not yet tested
        "webp": "image/webp", #not yet tested
    }

    file_type = path.split(".")[-1]
    print(file_type)
    with open(path, mode = "rb") as im:
        image_str = base64.b64encode(im.read()).decode()

    image_url = f"data:{mime_types[file_type]}:base64,{image_str}"
    return image_url

def convert_mplfigure_to_array(fig, **kwargs):
    """ Takes a matplotlib.figure.figure and returns a numpy array.
        kwargs
            arguments passed on to fig.savefig(). `dpi` defaults to set to `fig.dpi`
    """
    if "dpi" not in kwargs.keys():
        kwargs["dpi"] = fig.dpi

    with BytesIO() as buffer:
        fig.savefig(buffer, format = "raw", **kwargs)
        #print(buffer.getvalue()[:1000])
        array = np.frombuffer(buffer.getvalue(), dtype=np.uint8)
    
    return np.reshape(
                array,
                newshape=(int(fig.bbox.size[1]), int(fig.bbox.size[0]), -1))

def add_section(context: Dict, section: CustomSection) -> Dict:
    """ Adds a custom section to a context dictionary """

    context["components"]["has_customsections"] = True
    try:
        context["components"]["customsections"].append(section)
    except KeyError:
        context["components"]["customsections"] = [section]
    return context


