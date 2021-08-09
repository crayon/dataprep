"""This module provides classes to be use when customising the context used by create_report()"""

from typing import Dict, List, Optional, Union
from plotly.graph_objects import Figure as goFigure
from matplotlib.figure import Figure as mplFigure
import PIL.Image
from io import BytesIO
import numpy as np
import base64
from pandas import DataFrame
from numpy import ndarray
import dataprep.eda.container
# from urllib.parse import quote
import warnings
try:
    from markdown import Markdown
    md = Markdown(output_format="html5")
except ModuleNotFoundError:
    msg = (
        "'markdown' module not found. Install markdown using `pip install markdown` "
        "to create CustomMarkdown objects."
    )
    warnings.warn(msg, ImportWarning)


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
        self.figure=obj  # TODO: Decide if this is actually necessary
        self.html=obj.to_html(*args, **kwargs)
        # TODO: Only return the <div> child of <body> if the <style> elements
        # from <head> can be captured elsewhere in the


class CustomHTML(CustomObject):
    """ A wrapper around any HTML string """
    def __init__(
        self,
        name: str,
        obj: str,
    ) -> None:
        self.name = name
        self.object_type = "html"
        self.html=obj


class CustomMarkdown(CustomObject):
    def __init__(
        self,
        name: str,
        text: str,
    ) -> None:
        self.name = name
        self.object_type = "markdown"
        self.html=md.reset().convert(text)


class CustomVideo(CustomObject):
    # TODO Igor's idea. Medium priority.
    def __init__(self):
        pass


class CustomPandasProfiling(CustomObject):
    # TODO low priority
    pass


class CustomDataPrep(CustomObject):
    """ A wrapper around `dataprep.eda.container.Container`
    """
    def __init__(
        self,
        name: str,
        obj: dataprep.eda.container.Container,
    ) -> None:
        self.name = name
        self.object_type = "dataprep"
        self.html = obj._repr_html_()
        # from bs4 import BeautifulSoup
        # soup = BeautifulSoup(self.html, "html.parser")
        # self.scripts = soup.findall("script")
        # self.body = None
        # self.styles = None
        # TODO extract out body, styles and scripts from html if overhead gets too large


class CustomMatplotlib(CustomObject):
    """ A wrapper around `matplotlib.figure.Figure`.
        *args and **kwargs are passed to `matplotlib.figure.Figure.savefig()`
    """
    def __init__(
        self,
        name: str,
        obj: mplFigure,
        *args,
        **kwargs,
    ) -> None:
        self.name = name
        self.object_type = "matplotlib"
        with BytesIO() as buffer:
            obj.savefig(buffer, *args, **kwargs)
            byte_data=buffer.getvalue()
        image_str=base64.b64encode(byte_data).decode(encoding="utf-8")
        self.image_str=image_str
        image_url=f"data:image/png;base64,{image_str}"
        self.image_url=image_url
        self.html=f'<img class="custom-image" src="{image_url}" />'


# Alias for CustomMatplotlib
CustomMPL = CustomMatplotlib


class CustomImage(CustomObject):
    """ TO DO
        Converts `PIL.Image.Image` objects and `np.ndarray`s to PNG first.
        To insert `matplotlip.figure.Figure`s first convert them to
        `numpy.ndarray`s using `convert_mplfigure_to_array`.
    """
    def __init__(
        self,
        name: str,
        obj: Union[str, PIL.Image.Image, np.ndarray]
    ) -> None:
        self.name = name
        self.object_type = "image"

        if isinstance(obj, str):
            image_url, image_str=get_image_url(obj)
            self.image_str=image_str
            self.image_url=image_url
            self.html='<img class="custom-image">'+image_url+'</img>'
        elif isinstance(obj, PIL.Image.Image):
            with BytesIO() as buffer:
                obj.save(buffer, format="PNG")
                byte_data=buffer.getvalue()
            # might have to change this to urlib.parse.quote instead of .decode()
            # if .decode() doesn't work
            image_str=base64.b64encode(byte_data).decode(encoding="utf-8")
            self.image_str=image_str
            image_url=f"data:image/png;base64,{image_str}"
            self.image_url=image_url
            self.html=f'<img class="custom-image" src="{image_url}" />'
        elif isinstance(obj, np.ndarray):
            im=PIL.Image.fromarray(obj)
            with BytesIO() as buffer:
                im.save(buffer, format="PNG")
                byte_data=buffer.getvalue()
            # might have to change this to urlib.parse.quote instead of .decode()
            # if .decode() doesn't work
            image_str=base64.b64encode(byte_data).decode(encoding="utf-8")
            self.image_str=image_str
            image_url=f"data:image/png;base64,{image_str}"
            self.image_url=image_url
            self.html=f'<img class="custom-image" src="{image_url}" />'
        else:
            raise TypeError(f"obj must be a string, PIL.Image.Image or an numpy.ndarray. Got {type(obj)}")


class CustomTable(CustomObject):
    """ a pandas.DataFrame specific version of CustomObject.
    name: str
        Name of the Table
    obj:
        Either a pandas.DataFrame or a numpy.ndarray with 2 dimensions or fewer.
    kwargs:
        passed to pandas.DataFrame().to_html() and must NOT include `buf`.
        If `buf` is passed, it will be ignored.
    """
    def __init__(
        self,
        name: str,
        obj: Union[DataFrame, ndarray],
        **kwargs
    ) -> None:
        self.name = name
        self.object_type = "table"
        kwargs.pop("buf", None)
        if isinstance(obj, DataFrame):
            self.html=obj.to_html(buf=None, **kwargs)
        elif isinstance(obj, ndarray):
            if obj.ndim > 2:
                raise ValueError(f"numpy.ndarray must not have more than 2 dimensions. Got {obj.ndim}")
            self.html=DataFrame(obj).to_html(buf=None, **kwargs)
        else:
            raise TypeError(f"`obj` must be a pandas.DataFrame or a numpy.ndarray. Got {type(obj)}")


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
        self.title=title
        if isinstance(customobjects, list):
            self.customobjects = customobjects
        else:
            self.customobjects = [customobjects]

    def add_object(
        self,
        customobject: Union[CustomHTML, CustomPlotly, CustomImage]
    ):
        if isinstance(customobject, list):
            self.customobjects += customobject
        else:
            self.customobjects.append(customobject)
        return self


def get_image_url(path: str):
    """ Generates a base64 url from an image file path
        path
            path to file that can be loaded by open().
        Returns
        -------
        image_url, image_str
    """
    mime_types={
        "png": "image/png",
        "svg": "image/svg+xml",  # not yet tested
        "apng": "image/apng",  # not yet tested
        "avif": "image/avif",  # not yet tested
        "gif": "image/gif",  # not yet tested
        "jpg": "image/jpeg",  # not yet tested
        "jpeg": "image/jpeg",  # not yet tested
        "webp": "image/webp",  # not yet tested
    }

    file_type=path.split(".")[-1]
    print(file_type)
    with open(path, mode="rb") as im:
        image_str=base64.b64encode(im.read()).decode(encoding="utf-8")

    image_url=f"data:{mime_types[file_type]}:base64,{image_str}"
    return image_url, image_str


def convert_mplfigure_to_array(fig, **kwargs):
    """ Takes a matplotlib.figure.figure and returns a numpy array.
        kwargs
            arguments passed on to fig.savefig(). `dpi` defaults to set to `fig.dpi`
    """
    if "dpi" not in kwargs.keys():
        kwargs["dpi"]=fig.dpi

    with BytesIO() as buffer:
        fig.savefig(buffer, format="raw", **kwargs)
        # print(buffer.getvalue()[:1000])
        array=np.frombuffer(buffer.getvalue(), dtype=np.uint8)
   
    return np.reshape(
        array,
        newshape=(int(fig.bbox.size[1]), int(fig.bbox.size[0]), -1))
