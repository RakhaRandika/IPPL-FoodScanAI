"""
FoodScanAI - Model Training Script (Transfer Learning with MobileNetV2)
Dataset: Fruits 360 (https://www.kaggle.com/datasets/moltean/fruits)
Output: ../backend/model/foodscan_model.h5
"""

import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping
import os

# =============================== 
# 🔧 Konfigurasi dasar
# ===============================
train_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "dataset", "train"))
val_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "dataset", "val"))
model_output_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "backend", "model", "foodscan_model.h5"))

# Buat folder model kalau belum ada
os.makedirs(os.path.dirname(model_output_path), exist_ok=True)

# ===============================
# 📦 Preprocessing Dataset
# ===============================
IMAGE_SIZE = (224, 224)
BATCH_SIZE = 32

train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=20,
    zoom_range=0.2,
    width_shift_range=0.2,
    height_shift_range=0.2,
    horizontal_flip=True
)

val_datagen = ImageDataGenerator(rescale=1./255)

train_gen = train_datagen.flow_from_directory(
    train_dir,
    target_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical'
)

val_gen = val_datagen.flow_from_directory(
    val_dir,
    target_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical'
)

# ===============================
# 🧠 Transfer Learning - MobileNetV2
# ===============================
base_model = MobileNetV2(weights='imagenet', include_top=False, input_shape=(224, 224, 3))

# Freeze semua layer dasar
for layer in base_model.layers:
    layer.trainable = False

# Tambahkan lapisan baru untuk klasifikasi bahan makanan
x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dropout(0.3)(x)
x = Dense(128, activation='relu')(x)
predictions = Dense(train_gen.num_classes, activation='softmax')(x)

model = Model(inputs=base_model.input, outputs=predictions)

# ===============================
# ⚙️ Compile Model
# ===============================
model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),
              loss='categorical_crossentropy',
              metrics=['accuracy'])

# ===============================
# 🧩 Callback: EarlyStopping + Save Model
# ===============================
checkpoint = ModelCheckpoint(model_output_path, monitor='val_accuracy',
                             save_best_only=True, mode='max', verbose=1)
earlystop = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)

# ===============================
# 🚀 Training
# ===============================
EPOCHS = 15

history = model.fit(
    train_gen,
    validation_data=val_gen,
    epochs=EPOCHS,
    callbacks=[checkpoint, earlystop]
)

# ===============================
# 💾 Simpan model akhir
# ===============================
model.save(model_output_path)
print(f"\n✅ Model berhasil disimpan ke: {model_output_path}")
    
# Simpan labels agar inference bisa memuat label yang sesuai urutan indeks
if hasattr(train_gen, 'class_indices') and train_gen.class_indices:
    # invert mapping to list indexed by class index
    labels = [None] * len(train_gen.class_indices)
    for lbl, idx in train_gen.class_indices.items():
        labels[idx] = lbl
    labels_path = os.path.join(os.path.dirname(model_output_path), 'labels.txt')
    with open(labels_path, 'w', encoding='utf-8') as f:
        for l in labels:
            f.write(l + '\n')
    print(f"\n✅ Labels berhasil disimpan ke: {labels_path}")
