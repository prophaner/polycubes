from itertools import product
import numpy as np
import struct
from model import Database
MAX_3D = 20
MASK = [(-1, 0, 0), (0, -1, 0), (0, 0, -1), (0, 0, 1), (0, 1, 0), (1, 0, 0)]


def encoder(array):
    array_flat = array.astype(np.bool_).flatten()
    extra_zeros = (8 - (array_flat.size % 8)) % 8
    array_padded = np.concatenate([array_flat, np.zeros(extra_zeros, dtype=np.uint8)])
    array_packed = np.packbits(array_padded)
    sizes_encoded = (array.shape[0] - 1) * (MAX_3D**2) + (array.shape[1] - 1) * MAX_3D + (array.shape[2] - 1)
    sizes_and_extra_zeros_encoded = (sizes_encoded * 8) + extra_zeros
    sizes_and_extra_zeros_bytes = struct.pack('H', sizes_and_extra_zeros_encoded)
    return sizes_and_extra_zeros_bytes + array_packed.tobytes()


def decoder(encoded):
    sizes_and_extra_zeros_bytes, array_packed_bytes = encoded[:2], encoded[2:]
    sizes_and_extra_zeros_encoded = struct.unpack('H', sizes_and_extra_zeros_bytes)[0]
    sizes_encoded, extra_zeros = sizes_and_extra_zeros_encoded // 8, sizes_and_extra_zeros_encoded % 8
    sizes = ((sizes_encoded // (MAX_3D**2)) + 1, ((sizes_encoded % (MAX_3D**2)) // MAX_3D) + 1, (sizes_encoded % MAX_3D) + 1)
    array_packed = np.frombuffer(array_packed_bytes, dtype=np.uint8)
    array_padded = np.unpackbits(array_packed)
    array_flat = array_padded[:-extra_zeros] if extra_zeros > 0 else array_padded
    return array_flat.reshape(sizes)


def trim(array):
    min_indices = np.min(np.nonzero(array), axis=1)
    max_indices = np.max(np.nonzero(array), axis=1) + 1
    return array[min_indices[0]:max_indices[0], min_indices[1]:max_indices[1], min_indices[2]:max_indices[2]]


def get_neighbors(i, j, k, array):
    return np.any([array[i+dx, j+dy, k+dz] for dx, dy, dz in MASK if 0 <= i+dx < array.shape[0] and 0 <= j+dy < array.shape[1] and 0 <= k+dz < array.shape[2]])


def get_identities(array):
    larger_array = np.pad(array, pad_width=1)
    new_cubes = set()
    for loc in np.ndindex(*larger_array.shape):
        if larger_array[loc] == 0 and get_neighbors(*loc, larger_array):
            new_cube = larger_array.copy()
            new_cube[loc] = 1
            new_cubes.add(encoder(get_identity(trim(new_cube))))
    return new_cubes


def get_identity(array):
    min_rotation = min_key = None
    for z, y, x in product(range(4), range(4), range(2)):
        rotated = np.rot90(np.rot90(np.rot90(array, k=z, axes=(0, 1)), k=y, axes=(0, 2)), k=x, axes=(1, 2))
        if list(rotated.shape) == sorted(rotated.shape):
            key = int(''.join(map(str, rotated.flatten())), 2)
            if min_key is None or key < min_key:
                min_rotation, min_key = rotated, key
    return min_rotation


def compute(shapes):
    return list(set(identity for shape in shapes for identity in get_identities(decoder(shape))))


def main(size, start=0):
    print(f"Index={start}")
    db = Database()
    db.postprocess(compute(db.process(size, start)), size)
