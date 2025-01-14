from functools import partial
from typing import List, Callable

# import albumentations as A
import numpy as np
import torch
from sklearn.externals._pilutil import bytescale
from torchvision.ops import nms
import torchvision.transforms as T
from utils import select_interpolation_method

def addHM(inp: np.ndarray):
    inp_out =  np.append(inp,[[123 for i in range(inp.shape[0])]], axis = 0)
    return inp_out


def normalize_01(inp: np.ndarray):
    """Acotar la imagen de entrada al rango de valores [0, 1] (sin recorte)"""
    inp_out = (inp - np.min(inp)) / np.ptp(inp)
    return inp_out


def normalize(inp: np.ndarray, mean: float, std: float):
    """Normalizar basado en una media y una desviación estándar."""
    inp_out = (inp - mean) / std
    return inp_out


def re_normalize(inp: np.ndarray, low: int = 0, high: int = 255):
    """Normalizar la información a cierto rango. Por Defecto: [0-255]"""
    inp_out = bytescale(inp, low=low, high=high)
    return inp_out


def clip_bbs(inp: np.ndarray, bbs: np.ndarray):
    """
    Si las cajas dilimitadoras exceden la imagen en alguna dimensión, son recortadas a el
    máximo posible dentro de esa dimensión.
    Se esperan las cajas delimitadoras con el formato xyxy.
    Ejemplo: x_value=224 but x_shape=200 -> x1=199
    """

    def clip(value: int, max: int):

        if value >= max - 1:
            value = max - 1
        elif value <= 0:
            value = 0

        return value

    output = []
    for bb in bbs:
        x1, y1, x2, y2 = tuple(bb)
        x_shape = inp.shape[1]
        y_shape = inp.shape[0]

        x1 = clip(x1, x_shape)
        y1 = clip(y1, y_shape)
        x2 = clip(x2, x_shape)
        y2 = clip(y2, y_shape)

        output.append([x1, y1, x2, y2])

    return np.array(output)


def map_class_to_int(labels: List[str], mapping: dict):
    """Mapea una cadena (string) a un entero (int)."""
    labels = np.array(labels)
    dummy = np.empty_like(labels)
    for key, value in mapping.items():
        dummy[labels == key] = value

    return dummy.astype(np.uint8)


def apply_nms(target: dict, iou_threshold):
    """Supresión de No-Máximos (Non-maximum Suppression NMS)"""
    boxes = torch.tensor(target["boxes"])
    labels = torch.tensor(target["labels"])
    scores = torch.tensor(target["scores"])

    if boxes.size()[0] > 0:
        mask = nms(boxes, scores, iou_threshold=iou_threshold)
        mask = (np.array(mask),)

        target["boxes"] = np.asarray(boxes)[mask]
        target["labels"] = np.asarray(labels)[mask]
        target["scores"] = np.asarray(scores)[mask]

    return target


def apply_score_threshold(target: dict, score_threshold):
    """Remueve las prediciones de las cajas delimitadoras con bajos puntajes."""
    boxes = target["boxes"]
    labels = target["labels"]
    scores = target["scores"]

    mask = np.where(scores > score_threshold)
    target["boxes"] = boxes[mask]
    target["labels"] = labels[mask]
    target["scores"] = scores[mask]

    return target


class Repr:
    """Representación de cadena evaluable de un objeto"""

    def __repr__(self):
        return f"{self.__class__.__name__}: {self.__dict__}"


class FunctionWrapperSingle(Repr):
    """Una función wrapper que regresa un parcial para una sola entrada."""

    def __init__(self, function: Callable, *args, **kwargs):
        self.function = partial(function, *args, **kwargs)

    def __call__(self, inp: np.ndarray):
        return self.function(inp)


class FunctionWrapperDouble(Repr):
    """Una función wrapper que regresa un parcial para un par entrada-objetivo."""

    def __init__(
        self,
        function: Callable,
        input: bool = True,
        target: bool = False,
        *args,
        **kwargs,
    ):
        self.function = partial(function, *args, **kwargs)
        self.input = input
        self.target = target

    def __call__(self, inp: np.ndarray, tar: dict):
        if self.input:
            inp = self.function(inp)
        if self.target:
            tar = self.function(tar)
        return inp, tar


class Compose:
    """Clase Base - compone multiples transformaciones juntas."""

    def __init__(self, transforms: List[Callable]):
        self.transforms = transforms

    def __repr__(self):
        return str([transform for transform in self.transforms])


class ComposeDouble(Compose):
    """Compone transformaciones para pares entrada-objetico."""

    def __call__(self, inp: np.ndarray, target: dict):
        for t in self.transforms:
            try:
                inp, target = t(inp, target)
            except:
                inp = np.squeeze(t(torch.from_numpy(np.expand_dims(inp, axis = 0))).numpy())
        return inp, target


class ComposeSingle(Compose):
    """Compone transformaciones para una única entrada."""

    def __call__(self, inp: np.ndarray):
        for t in self.transforms:
            inp = t(inp)
        return inp


class AlbumentationWrapper(Repr):
    """
    Un wrapper para el paquete albumentation.
    Es esperado que las cajas delimitadoras estén en el formato xyxy (pascal_voc)
    Las cajas delimitadoras no pueden ser mas grandes que la dimensión espacial de la imagen
    Se usa Clip() si alguna caja delimitadora sale del espacio de la imagen, antes de usar la función.
    """

    def __init__(self, albumentation: Callable, format: str = "pascal_voc"):
        self.albumentation = albumentation
        self.format = format

    def __call__(self, inp: np.ndarray, tar: dict):
        # input, target
        transform = A.Compose(
            [self.albumentation],
            bbox_params=A.BboxParams(format=self.format, label_fields=["class_labels"]),
        )

        out_dict = transform(image=inp, bboxes=tar["boxes"], class_labels=tar["labels"])

        input_out = np.array(out_dict["image"])
        boxes = np.array(out_dict["bboxes"])
        labels = np.array(out_dict["class_labels"])

        tar["boxes"] = boxes
        tar["labels"] = labels

        return input_out, tar


class Clip(Repr):
    """
    Si las cajas delimitadoras exceden una dimensión, son cortadas al máximo valor de la dimenisón
    Las cajas delimitadoras son esperadas en formato xyxy.
    Ejemplo: x_value=224 but x_shape=200 -> x1=199
    """

    def __call__(self, inp: np.ndarray, tar: dict):
        new_boxes = clip_bbs(inp=inp, bbs=tar["boxes"])
        tar["boxes"] = new_boxes

        return inp, tar

class RescaleWithBB:

    def __init__(self, size, interp_m = 'bilinear', to_PIL = False):
        self.size = size
        self.interp_m = interp_m
        self.to_PIL = to_PIL

    # hace el objeto llamable,
    # se comporta como una una función
    def __call__(self, img, box):
        # obtenemos las dimensiones originales
        try:
            img_h, img_w = img.shape
        except:
            img_h, img_w,_ = img.shape

        if len(self.size) == 1:
            if len(img.shape) < 3:
                if self.interp_m in ['box','hamming','lanczos'] or self.to_PIL: # Pasamos a PIL para poder aplicar estas interpolaciones de rescalado de imagen
                    img = np.squeeze(T.ToTensor()(T.Resize([self.size[0],self.size[0]],interpolation = select_interpolation_method(self.interp_m))(T.ToPILImage()(torch.from_numpy(np.expand_dims(img, axis = 0))))).numpy())
                else:
                    img = np.squeeze(T.Resize([self.size[0],self.size[0]],interpolation = select_interpolation_method(self.interp_m))(torch.from_numpy(np.expand_dims(img, axis = 0))).numpy())
            else:
                if self.interp_m in ['box','hamming','lanczos'] or self.to_PIL: # Pasamos a PIL para poder aplicar estas interpolaciones de rescalado de imagen
                    img = np.moveaxis(T.ToTensor()(T.Resize([self.size[0],self.size[0]],interpolation = select_interpolation_method(self.interp_m))(T.ToPILImage()(torch.from_numpy(np.moveaxis(img, -1, 0))))).numpy(), 0, -1)
                else:
                    img = np.moveaxis(T.Resize([self.size[0],self.size[0]],interpolation = select_interpolation_method(self.interp_m))(torch.from_numpy(np.moveaxis(img, -1, 0))).numpy(), 0, -1)

            # calculamos escalas
            scale_x = img_w / self.size[0]
            scale_y = img_h / self.size[0]

        elif len(self.size) == 2:
            if len(img.shape) < 3:
                if self.interp_m in ['box','hamming','lanczos'] or self.to_PIL: # Pasamos a PIL para poder aplicar estas interpolaciones de rescalado de imagen
                    img = np.squeeze(T.ToTensor()(T.Resize([self.size[0],self.size[1]],interpolation = select_interpolation_method(self.interp_m))(T.ToPILImage()(torch.from_numpy(np.expand_dims(img, axis = 0))))).numpy())
                else:
                    img = np.squeeze(T.Resize([self.size[0],self.size[1]],interpolation = select_interpolation_method(self.interp_m))(torch.from_numpy(np.expand_dims(img, axis = 0))).numpy())
            else:
                if self.interp_m in ['box','hamming','lanczos'] or self.to_PIL: # Pasamos a PIL para poder aplicar estas interpolaciones de rescalado de imagen
                    img = np.moveaxis(T.ToTensor()(T.Resize([self.size[0],self.size[1]],interpolation = select_interpolation_method(self.interp_m))(T.ToPILImage()(torch.from_numpy(np.moveaxis(img, -1, 0))))).numpy(), 0, -1)
                else:
                    img = np.moveaxis(T.Resize([self.size[0],self.size[1]],interpolation = select_interpolation_method(self.interp_m))(torch.from_numpy(np.moveaxis(img, -1, 0))).numpy(), 0, -1)
            # calculamos escalas
            scale_x = img_w / self.size[0]
            scale_y = img_h / self.size[1]

        totalboxes = []
        for bx in box['boxes']:
            # escalamos el cuadro delimitador
            x1, y1, x2, y2 = bx
            y1 = int(y1 / scale_y)
            y2 = int(y2 / scale_y)
            x1 = int(x1 / scale_x)
            x2 = int(x2 / scale_x)

            # calculamos ancho y alto
            w = x2 #- x1
            h = y2 #- y1
            # armamos cuadro delimitador
            totalboxes.append([x1, y1, w, h])
        box['boxes'] = np.array(totalboxes, dtype=np.float32)

        return img, box
