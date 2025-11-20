# from io import BytesIO
# import threading
# from app.config import MODEL_PATH
# import os

# # heavy imports (tensorflow, PIL, numpy) are performed lazily inside functions
# _np = None
# _Image = None


# # Thread-safe lazy model loader
# _model = None
# _model_lock = threading.Lock()

# # TODO: keep this list in sync with your training labels or load from a labels file
# class_labels = ["ayam", "telur", "tomat", "cabai", "bawang"]

# def _load_labels(model_path=MODEL_PATH):
#     """Try to load labels.txt from the model directory. If not found, return default class_labels."""
#     model_dir = os.path.dirname(model_path)
#     labels_file = os.path.join(model_dir, 'labels.txt')
#     if os.path.exists(labels_file):
#         with open(labels_file, 'r', encoding='utf-8') as f:
#             labels = [line.strip() for line in f.readlines() if line.strip()]
#         return labels
#     return class_labels

# def _load_model():
#     global _model
#     if _model is None:
#         with _model_lock:
#             if _model is None:
#                 # import load_model lazily to avoid requiring TF at module import
#                 try:
#                     from tensorflow.keras.models import load_model
#                 except Exception as e:
#                     raise RuntimeError("TensorFlow is required to load the model: " + str(e))
#                 _model = load_model(MODEL_PATH)
#     return _model

# def _prepare_image_from_bytes(img_bytes: bytes, target_size=(224, 224)):
#     # lazy-import PIL and numpy so tests can import module without them
#     global _np, _Image
#     if _Image is None:
#         try:
#             from PIL import Image as _PILImage
#         except Exception:
#             raise RuntimeError("Pillow is required to process images")
#         _Image = _PILImage
#     if _np is None:
#         try:
#             import numpy as _numpy
#         except Exception:
#             raise RuntimeError("numpy is required to process images")
#         _np = _numpy

#     img = _Image.open(BytesIO(img_bytes)).convert("RGB")
#     img = img.resize(target_size)
#     arr = _np.array(img).astype("float32") / 255.0
#     arr = _np.expand_dims(arr, axis=0)
#     return arr

# def predict_ingredients(input_data, from_bytes: bool = False, top_k: int = 5):
#     """Predict ingredients from a file path or raw image bytes.

#     Args:
#         input_data: path (str) when from_bytes=False, or bytes when from_bytes=True
#         from_bytes: whether input_data is raw bytes
#         top_k: number of top predictions to return

#     Returns:
#         dict: {"predictions": [{"label": str, "probability": float}, ...]}
#     """
#     model = _load_model()

#     if from_bytes:
#         img_arr = _prepare_image_from_bytes(input_data)
#     else:
#         # process file path using PIL/numpy lazily
#         img_arr = _prepare_image_from_bytes(open(input_data, 'rb').read())

#     preds = model.predict(img_arr)[0]

#     # load labels mapping (index -> label)
#     labels_map = _load_labels()

#     # get top_k indices
#     top_indices = preds.argsort()[-top_k:][::-1]
#     results = []
#     for idx in top_indices:
#         label = labels_map[idx] if idx < len(labels_map) else (class_labels[idx] if idx < len(class_labels) else str(idx))
#         results.append({
#             "label": label,
#             "probability": float(preds[idx])
#         })

#     return {"predictions": results}
