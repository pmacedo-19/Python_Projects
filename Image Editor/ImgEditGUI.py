from PIL import Image, ImageEnhance, ImageFilter, ImageTk
import os
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

class ImageEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Editor")
        self.param_sliders = {}  # Initialize the param_sliders dictionary
        self.create_widgets()
        self.original_img = None
        self.edited_img = None
        self.photo_image = None
        self.loaded_img_path = None  # Store the path of the loaded image
        self.preview_width = 400  # Initial width of the preview
        
        # Bind the preview_frame's size to the update_preview_image function
        self.preview_frame.bind("<Configure>", self.update_preview_image)
    
    def create_widgets(self):
        # Create a frame for filter selection
        filter_frame = tk.LabelFrame(self.root, text="Select Filters")
        filter_frame.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        # Create a frame for image loading and saving
        action_frame = tk.LabelFrame(self.root, text="Image Actions")
        action_frame.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        
        # Create a frame for the live preview
        self.preview_frame = tk.LabelFrame(self.root, text="Live Preview")
        self.preview_frame.grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky="nsew")
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        
        # Create a list of available filters with their associated parameters (if applicable)
        self.filters = [
            ("SHARPEN", "SHARPEN", None),
            ("BLUR", "BLUR", None),
            ("CONTOUR", "CONTOUR", None),
            ("DETAIL", "DETAIL", None),
            ("EDGE ENHANCE", "EDGE_ENHANCE", None),
            ("EMBOSS", "EMBOSS", None),
            ("BRIGHTNESS", "BRIGHTNESS", (0.0, 2.0, 1.0)),
            ("CONTRAST", "CONTRAST", (0.0, 2.0, 1.0)),
            # Add more filters and parameters here
        ]
        
        # Create checkboxes for selecting filters and their parameter input fields
        self.selected_filters = {}
        row_index = 0
        
        for filter_name, filter_function, param_range in self.filters:
            var = tk.IntVar()
            check_button = tk.Checkbutton(filter_frame, text=filter_name, variable=var, command=self.update_preview)
            check_button.filter_function = filter_function
            check_button.grid(row=row_index, column=0, padx=10, sticky="w")
            self.selected_filters[filter_name] = var
            
            if param_range:
                param_label = tk.Label(filter_frame, text=filter_name + " Value")
                param_label.grid(row=row_index, column=1, padx=10, sticky="w")
                
                param_slider = tk.Scale(filter_frame, from_=param_range[0], to=param_range[1], resolution=0.01, orient="horizontal", command=self.update_preview)
                param_slider.set(param_range[2])  # Default value
                param_slider.grid(row=row_index, column=2, padx=10, sticky="w")
                self.param_sliders[filter_name] = param_slider
            
            row_index += 1
        
        # Create a button to open an image
        self.open_button = tk.Button(action_frame, text="Open Image", command=self.open_image)
        self.open_button.grid(row=0, column=0, padx=10, sticky="w")
        
        # Create a button to edit and save the image
        self.edit_button = tk.Button(action_frame, text="Edit and Save", command=self.edit_and_save)
        self.edit_button.grid(row=1, column=0, padx=10, sticky="w")
        
        # Create a label for live image preview (empty for now)
        self.preview_label = tk.Label(self.preview_frame)
        self.preview_label.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.preview_frame.grid_rowconfigure(0, weight=1)
        self.preview_frame.grid_columnconfigure(0, weight=1)
    
    def open_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.png *.jpeg")])
        if file_path:
            self.loaded_img_path = file_path
            self.original_img = Image.open(file_path)
            self.update_loaded_image_size()  # Resize the loaded image
            self.edited_img = self.original_img.copy()
            self.update_preview()  # Update preview when opening a new image
            messagebox.showinfo("Image Loaded", "Image has been loaded successfully")
    
    def update_loaded_image_size(self):
        if self.original_img:
            preview_width = self.preview_frame.winfo_width()
            preview_height = self.preview_frame.winfo_height()
            aspect_ratio = self.original_img.width / self.original_img.height
            
            if aspect_ratio >= 1:
                new_width = preview_width
                new_height = int(preview_width / aspect_ratio)
            else:
                new_height = preview_height
                new_width = int(preview_height * aspect_ratio)
            
            self.original_img = self.original_img.resize((new_width, new_height), Image.LANCZOS)
    
    def update_preview(self):
        if self.original_img is not None:
            self.edited_img = self.original_img.copy()
            
            for filter_name, var in self.selected_filters.items():
                filter_function = filter_name
                if var.get() == 1 and filter_function:
                    if filter_function in dir(ImageFilter):
                        filter_function = getattr(ImageFilter, filter_function)
                        self.edited_img = self.edited_img.filter(filter_function)
                param_slider = self.param_sliders.get(filter_name)
                if param_slider:
                    param_value = float(param_slider.get())
                    if param_value > 0:
                        if "BRIGHTNESS" in filter_name:
                            enhancer = ImageEnhance.Brightness(self.edited_img)
                            self.edited_img = enhancer.enhance(param_value)
                        elif "CONTRAST" in filter_name:
                            enhancer = ImageEnhance.Contrast(self.edited_img)
                            self.edited_img = enhancer.enhance(param_value)
            
            self.update_preview_image()
    
    def update_preview_image(self, event=None):
        if self.edited_img:
            self.preview_width = self.preview_frame.winfo_width()
            self.preview_height = self.preview_frame.winfo_height()
            aspect_ratio = self.edited_img.width / self.edited_img.height
            
            if aspect_ratio >= 1:
                new_width = self.preview_width
                new_height = int(self.preview_width / aspect_ratio)
            else:
                new_height = self.preview_height
                new_width = int(self.preview_height * aspect_ratio)
            
            self.edited_img = self.edited_img.resize((new_width, new_height), Image.LANCZOS)
            
            self.photo_image = ImageTk.PhotoImage(self.edited_img)
            self.preview_label.configure(image=self.photo_image)
    
    def edit_and_save(self):
        if self.original_img is not None:
            save_path = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("JPEG files", "*.jpg")])
            if save_path:
                self.edited_img.save(save_path)
                messagebox.showinfo("Image Edited and Saved", f"Image has been edited and saved as {save_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageEditorApp(root)
    root.geometry("800x600")  # Set an initial window size
    root.mainloop()
