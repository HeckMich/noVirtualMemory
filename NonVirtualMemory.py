# No Virtual Memory

from tkinter import Tk, Label, Frame
from PIL import Image, ImageTk
import os
import io

MEMORY_SIZE = 2048000
physical_memory = bytearray(MEMORY_SIZE)

lable_A = None

def load_bmp_to_array(bmp_file_path):
    with open(bmp_file_path, 'rb') as file:
              bmp_data = file.read()
    return bmp_data

def get_bmp_dimensions(bmp_data):
    width = int.from_bytes(bmp_data[18:22], 'little')
    height = int.from_bytes(bmp_data[22:26], 'little')
    return width, height

def create_white_bmp(width, height):
    image = Image.new("RGB", (width, height), "white")
    with io.BytesIO() as byte_io:
        image.save(byte_io, format='BMP')
        return byte_io.getvalue()

def calculate_row_padding(width):
    bytes_per_pixel = 3
    bytes_per_row = width * bytes_per_pixel
    padding = (4 - (bytes_per_row % 4)) % 4
    return bytes_per_row + padding

def store_white_image_to_memory(width, height, offset):
    white_bmp_data = create_white_bmp(width, height)
    if offset + len(white_bmp_data) > len(physical_memory):
        raise ValueError("Not enough memory allocated.")
    physical_memory[offset:offset + len(white_bmp_data)] = white_bmp_data
    return len(white_bmp_data)

def incremental_load_to_memory(data, offset, start_position, chunk_size=5000):
    pixel_data_offset = 54
    start = pixel_data_offset + start_position
    end_position = min(start + chunk_size, len(data))
    physical_memory[offset + start:offset + end_position] = data[start:end_position]
    return end_position - pixel_data_offset

def incremental_load_to_memory_A(data, offset, start_position, offset2, start_position2, chunk_size=5000):
    pixel_data_offset = 54
    start = pixel_data_offset + start_position
    end_position = min(start + chunk_size, len(data))

    start2 = pixel_data_offset + start_position2
    end_position2 = min(start2 + chunk_size, len(data))

    physical_memory[offset + start:offset + end_position] = data[start2:end_position]
    return end_position - pixel_data_offset

def update_image_data_from_memory(offset, length, label):
    image_data = physical_memory[offset:offset + length]
    image = Image.open(io.BytesIO(image_data))
    photo = ImageTk.PhotoImage(image)
    label.config(image=photo)
    label.image = photo

def store_image_data_to_memory(image_data, offset):
    if offset + len(image_data) > len(physical_memory):
        raise ValueError("Not enough memory allocated.")
    physical_memory[offset:offset + len(image_data)] = image_data

def run_program_A(title, master, offset, image_data, width, height):
    global label_A
    frame = Frame(master, borderwidth=2, relief='groove')
    frame.pack(side='left', expand=True, fill='both', padx=10, pady=10)
    frame_title = Label(frame, text=title)
    frame_title.pack(side='top')

    store_white_image_to_memory(width, height, offset)
    label_A = Label(frame, borderwidth=2, relief='solid')
    label_A.pack()

    def update_image():
        end_position = [0]
        total_length = width * height * 3 + 54
        
        def perform_update():
            if end_position[0] < total_length - 54:
                end_position[0] = incremental_load_to_memory(image_data, offset, end_position[0])
                update_image_from_memory(offset, total_length, label_A)
                label_A.after(100, perform_update)
            else:
                print("Finished loading image data.")

        perform_update()

    label_A.after(1000, update_image)

def run_program_B(title, master, offset, image_data, width, height):
    frame = Frame(master, borderwidth=2, relief='groove')
    frame.pack(side='left', expand=True, fill='both', padx=10, pady=10)
    frame_title = Label(frame, text=title)
    frame_title.pack(side='top')

    store_white_image_to_memory(width, height, offset)
    label_B = Label(frame, borderwidth=2, relief='solid')
    label_B.pack()

    def update_image():
        end_position = [0]
        end_position_A = [0]
        total_length = width * height * 3 + 54

        def perform_update():
            if end_position[0] < total_length - 54:
                end_position[0] = incremental_load_to_memory(image_data, offset, end_position[0])
                if end_position[0] >= total_length / 2 and end_position[0] < total_length - 10000:
                    end_position_A[0] = incremental_load_to_memory_A(image_data, 0, end_position_A[0], offset, end_position[0])

                update_image_from_memory(offset, total_length, label_B)
                update_image_from_memory(0, total_length, label_A)
                label_B.after(100, perform_update)
            else:
                print("Finished loading image data.")

        perform_update()

    label_B.after(1000, update_image)

def main():
    root = Tk()
    root.title("My Computer")
    process_A_data = load_bmp_to_array('mona_lisa.bmp')
    process_B_data = load_bmp_to_array('coffee.bmp')

    width, height = get_bmp_dimensions(process_A_data)

    run_program_A("Program A", root, 0, process_A_data, width, height)
    input("Press Enter to execute Program B...")
    run_program_B("Program B", root, MEMORY_SIZE//2, process_B_data, width, height)

    root.mainloop()

if __name__ == "__main__":
    main()
                
    











    
