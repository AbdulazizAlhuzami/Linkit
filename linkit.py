import customtkinter as ctk
import json
import os
import webbrowser
import qrcode
from PIL import Image
import io
import tkinter.messagebox
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib.utils import ImageReader
import uuid
from reportlab.lib.colors import black, white
from reportlab.lib.units import inch

# Set the appearance mode and color theme
ctk.set_appearance_mode("System")  # "System", "Dark", "Light"
ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"

class LinkitApp(ctk.CTk):
    """
    A cross-platform desktop application for managing links and inventory.
    This version includes an improved UI with tabs for different functionalities.
    """
    
    SETTINGS_FILE = "settings.json"
    
    def __init__(self):
        super().__init__()

        # Window setup
        self.title("Link Manager")
        self.geometry("1000x700")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self.load_settings()

        # Toolbar for settings
        self.toolbar = ctk.CTkFrame(self, height=50, fg_color="transparent")
        self.toolbar.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
        self.toolbar.grid_columnconfigure(0, weight=1)

        self.settings_button = ctk.CTkButton(self.toolbar, text="Settings", command=self.open_settings)
        self.settings_button.grid(row=0, column=1, padx=10, sticky="e")

        # Tab view to hold different functionalities
        self.tabview = ctk.CTkTabview(self, width=980)
        self.tabview.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")

        # URL Manager Tab (Original functionality)
        self.url_manager_tab = self.tabview.add("URL Manager")
        self.url_manager_tab.grid_columnconfigure(0, weight=1)
        self.url_manager_tab.grid_rowconfigure(2, weight=1)
        
        # Inventory QRs Tab (New functionality)
        self.inventory_manager_tab = self.tabview.add("Inventory QRs")
        self.inventory_manager_tab.grid_columnconfigure(0, weight=1)
        self.inventory_manager_tab.grid_rowconfigure(1, weight=1)

        # Initialize URL Manager Frame
        self.url_manager_frame = UrlManagerFrame(self.url_manager_tab, self.font_size)
        self.url_manager_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Initialize Inventory Manager Frame
        self.inventory_manager_frame = InventoryManagerFrame(self.inventory_manager_tab, self.font_size)
        self.inventory_manager_frame.pack(fill="both", expand=True, padx=10, pady=10)

    def load_settings(self):
        if os.path.exists(self.SETTINGS_FILE):
            try:
                with open(self.SETTINGS_FILE, "r") as f:
                    settings = json.load(f)
                    ctk.set_appearance_mode(settings.get("theme", "System"))
                    self.font_size = settings.get("font_size", 14)
            except (json.JSONDecodeError, FileNotFoundError):
                self.font_size = 14
        else:
            self.font_size = 14

    def save_settings(self, theme, font_size):
        settings = {"theme": theme, "font_size": font_size}
        with open(self.SETTINGS_FILE, "w") as f:
            json.dump(settings, f, indent=4)
            
    def open_settings(self):
        SettingsFrame(self)

    def change_font_size(self, new_font_size):
        self.font_size = new_font_size
        self.save_settings(ctk.get_appearance_mode(), self.font_size)
        self.update_widgets_font_size()

    def update_widgets_font_size(self):
        self.url_manager_frame.update_font(self.font_size)
        self.inventory_manager_frame.update_font(self.font_size)
        
class SettingsFrame(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.title("Settings")
        self.geometry("300x200")
        self.resizable(False, False)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 1, 2, 3), weight=1)
        
        # Theme Settings
        theme_label = ctk.CTkLabel(self, text="Theme:", font=ctk.CTkFont(size=self.master.font_size, weight="bold"))
        theme_label.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        
        self.theme_options = ctk.CTkOptionMenu(self, values=["System", "Light", "Dark"], command=self.change_theme)
        self.theme_options.set(ctk.get_appearance_mode())
        self.theme_options.grid(row=0, column=1, padx=20, pady=10, sticky="ew")

        # Font Size Settings
        font_label = ctk.CTkLabel(self, text="Font Size:", font=ctk.CTkFont(size=self.master.font_size, weight="bold"))
        font_label.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        
        font_frame = ctk.CTkFrame(self, fg_color="transparent")
        font_frame.grid(row=1, column=1, padx=20, pady=10, sticky="ew")
        font_frame.grid_columnconfigure((0, 1), weight=1)

        decrease_button = ctk.CTkButton(font_frame, text="-", width=40, command=self.decrease_font)
        decrease_button.grid(row=0, column=0, padx=5)

        increase_button = ctk.CTkButton(font_frame, text="+", width=40, command=self.increase_font)
        increase_button.grid(row=0, column=1, padx=5)
        
    def change_theme(self, new_theme):
        ctk.set_appearance_mode(new_theme)
        self.master.save_settings(new_theme, self.master.font_size)
        
    def increase_font(self):
        current_size = self.master.font_size
        new_size = current_size + 2
        if new_size <= 24:
            self.master.change_font_size(new_size)
            self.update_font_size()
            
    def decrease_font(self):
        current_size = self.master.font_size
        new_size = current_size - 2
        if new_size >= 10:
            self.master.change_font_size(new_size)
            self.update_font_size()

    def update_font_size(self):
        self.master.update_widgets_font_size()

class UrlManagerFrame(ctk.CTkFrame):
    """Frame for the original URL management features."""
    
    LINKS_FILE = "links.json"

    def __init__(self, master, font_size):
        super().__init__(master)
        self.font_size = font_size
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        self.checkbox_vars = {}
        self.editing_index = None

        # --- UI Components ---
        self.top_frame = ctk.CTkFrame(self, corner_radius=10)
        self.top_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="nsew")
        self.top_frame.grid_columnconfigure(0, weight=1)
        self.top_frame.grid_columnconfigure(1, weight=1)

        self.add_frame = ctk.CTkFrame(self.top_frame, corner_radius=10)
        self.add_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.add_frame.grid_columnconfigure(0, weight=1)
        
        self.link_label = ctk.CTkLabel(self.add_frame, text="Link Name:", font=ctk.CTkFont(size=self.font_size, weight="bold"))
        self.link_label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        
        self.link_entry = ctk.CTkEntry(self.add_frame, placeholder_text="Enter a descriptive name for your link", font=ctk.CTkFont(size=self.font_size))
        self.link_entry.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        self.url_label = ctk.CTkLabel(self.add_frame, text="URL:", font=ctk.CTkFont(size=self.font_size, weight="bold"))
        self.url_label.grid(row=2, column=0, padx=10, pady=(10, 5), sticky="w")
        
        self.url_entry = ctk.CTkEntry(self.add_frame, placeholder_text="Enter the full URL (e.g., https://www.google.com)", font=ctk.CTkFont(size=self.font_size))
        self.url_entry.grid(row=3, column=0, padx=10, pady=5, sticky="ew")

        self.add_button = ctk.CTkButton(self.add_frame, text="Add Link", command=self.add_or_update_link, font=ctk.CTkFont(size=self.font_size))
        self.add_button.grid(row=4, column=0, padx=10, pady=(10, 10))

        self.action_frame = ctk.CTkFrame(self.top_frame, corner_radius=10)
        self.action_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.action_frame.grid_columnconfigure(0, weight=1)

        self.select_all_button = ctk.CTkButton(self.action_frame, text="Select All", command=self.select_all_links, font=ctk.CTkFont(size=self.font_size))
        self.select_all_button.grid(row=0, column=0, padx=20, pady=5, sticky="ew")

        self.deselect_all_button = ctk.CTkButton(self.action_frame, text="Deselect All", command=self.deselect_all_links, font=ctk.CTkFont(size=self.font_size))
        self.deselect_all_button.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        
        self.delete_selected_button = ctk.CTkButton(self.action_frame, text="Delete Selected", command=self.delete_selected_links, fg_color="#F44336", hover_color="#D32F2F", font=ctk.CTkFont(size=self.font_size))
        self.delete_selected_button.grid(row=2, column=0, padx=20, pady=5, sticky="ew")

        self.export_button = ctk.CTkButton(self.action_frame, text="Export to PDF", command=self.export_to_pdf, font=ctk.CTkFont(size=self.font_size))
        self.export_button.grid(row=3, column=0, padx=20, pady=5, sticky="ew")

        self.search_entry = ctk.CTkEntry(self, placeholder_text="Search links...", font=ctk.CTkFont(size=self.font_size))
        self.search_entry.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")
        self.search_entry.bind("<KeyRelease>", self.filter_links)

        self.link_list_frame = ctk.CTkScrollableFrame(self, corner_radius=10)
        self.link_list_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.link_list_frame.grid_columnconfigure(1, weight=1)

        # --- Data Handling ---
        self.links = self.load_links()
        self.display_links()
        
    def is_valid_url(self, url):
        regex = re.compile(
            r'^(?:http|ftp)s?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return re.match(regex, url) is not None

    def load_links(self):
        if os.path.exists(self.LINKS_FILE):
            try:
                with open(self.LINKS_FILE, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return []
        return []

    def save_links(self):
        try:
            with open(self.LINKS_FILE, "w") as f:
                json.dump(self.links, f, indent=4)
        except Exception as e:
            print(f"Failed to save links: {e}")

    def add_or_update_link(self):
        link_name = self.link_entry.get().strip()
        url = self.url_entry.get().strip()
        if not self.is_valid_url(url):
            tkinter.messagebox.showwarning("Warning", "The URL format is invalid. Please make sure it starts with http:// or https://")
            return
            
        if link_name and url:
            if self.editing_index is not None:
                self.links[self.editing_index]["name"] = link_name
                self.links[self.editing_index]["url"] = url
                self.editing_index = None
                self.add_button.configure(text="Add Link")
            else:
                self.links.append({"name": link_name, "url": url})
            self.save_links()
            self.display_links()
            self.link_entry.delete(0, "end")
            self.url_entry.delete(0, "end")
        else:
            tkinter.messagebox.showwarning("Warning", "Please fill in both the link name and the URL.")

    def update_font(self, new_font_size):
        self.font_size = new_font_size
        self.link_label.configure(font=ctk.CTkFont(size=self.font_size, weight="bold"))
        self.link_entry.configure(font=ctk.CTkFont(size=self.font_size))
        self.url_label.configure(font=ctk.CTkFont(size=self.font_size, weight="bold"))
        self.url_entry.configure(font=ctk.CTkFont(size=self.font_size))
        self.add_button.configure(font=ctk.CTkFont(size=self.font_size))
        self.select_all_button.configure(font=ctk.CTkFont(size=self.font_size))
        self.deselect_all_button.configure(font=ctk.CTkFont(size=self.font_size))
        self.delete_selected_button.configure(font=ctk.CTkFont(size=self.font_size))
        self.export_button.configure(font=ctk.CTkFont(size=self.font_size))
        self.search_entry.configure(font=ctk.CTkFont(size=self.font_size))
        self.display_links(self.search_entry.get().strip().lower())

    def filter_links(self, event=None):
        self.display_links(self.search_entry.get().strip().lower())

    def set_edit_mode(self, index):
        self.editing_index = index
        link = self.links[index]
        self.link_entry.delete(0, "end")
        self.url_entry.delete(0, "end")
        self.link_entry.insert(0, link["name"])
        self.url_entry.insert(0, link["url"])
        self.add_button.configure(text="Update Link")

    def open_link(self, url):
        try:
            webbrowser.open(url)
        except Exception as e:
            tkinter.messagebox.showerror("Error", f"Failed to open URL: {e}")

    def delete_link(self, index):
        if 0 <= index < len(self.links):
            if tkinter.messagebox.askyesno("Confirm Delete", f"Delete '{self.links[index]['name']}'?"):
                del self.links[index]
                self.save_links()
                self.display_links()

    def delete_selected_links(self):
        selected_indices = [i for i in range(len(self.links)) if self.checkbox_vars[i].get() == 1]
        if not selected_indices:
            tkinter.messagebox.showwarning("Warning", "Please select at least one link to delete.")
            return
        if tkinter.messagebox.askyesno("Confirm Bulk Delete", f"Delete {len(selected_indices)} selected link(s)?"):
            for index in sorted(selected_indices, reverse=True):
                del self.links[index]
            self.save_links()
            self.display_links()

    def select_all_links(self):
        for var in self.checkbox_vars.values():
            var.set(1)

    def deselect_all_links(self):
        for var in self.checkbox_vars.values():
            var.set(0)

    def show_qr_code(self, url, name):
        try:
            qr = qrcode.QRCode(version=1, box_size=10, border=4)
            qr.add_data(url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white").resize((300, 300))
            qr_window = ctk.CTkToplevel(self.master.master)
            qr_window.title(f"QR Code for: {name}")
            qr_window.geometry("340x380")
            img_tk = ctk.CTkImage(light_image=img, dark_image=img, size=(300, 300))
            qr_label = ctk.CTkLabel(qr_window, image=img_tk, text="")
            qr_label.pack(pady=(20, 10))
            name_label = ctk.CTkLabel(qr_window, text=name, font=ctk.CTkFont(size=self.font_size+2, weight="bold"))
            name_label.pack()
        except Exception as e:
            tkinter.messagebox.showerror("Error", f"Failed to generate QR code: {e}")

    def export_to_pdf(self):
        selected_links = [self.links[i] for i in range(len(self.links)) if self.checkbox_vars[i].get() == 1]
        if not selected_links:
            tkinter.messagebox.showwarning("Warning", "Please select at least one link to export.")
            return

        filename = "exported_links.pdf"
        c = pdf_canvas.Canvas(filename, pagesize=letter)
        margin = 50
        y_pos = letter[1] - margin
        qr_size = 120
        # Horizontal positions for the 3 columns
        col1_x = margin
        col2_x = margin + qr_size + 20
        col3_x = col2_x + qr_size + 20
        
        c.setFont("Helvetica-Bold", 18)
        c.drawString(margin, y_pos, "QR Codes")
        y_pos -= 30
        
        for i, link in enumerate(selected_links):
            # Determine the column for the current link
            col_index = i % 3
            current_x = margin + col_index * (qr_size + 20)
            
            # Move to a new row if starting a new set of 3
            if col_index == 0 and i > 0:
                y_pos -= (qr_size + 40)
            
            # Check for new page
            if y_pos < margin + (qr_size + 40):
                c.showPage()
                y_pos = letter[1] - margin
                c.setFont("Helvetica-Bold", 18)
                c.drawString(margin, y_pos, "QR Codes (cont.)")
                y_pos -= 30
                current_x = margin

            try:
                # Generate QR code image
                qr = qrcode.QRCode(version=1, box_size=5, border=4)
                qr.add_data(link['url'])
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")
                img_buffer = io.BytesIO()
                img.save(img_buffer, "PNG")

                # Draw QR code
                qr_y = y_pos - qr_size
                c.drawImage(ImageReader(img_buffer), current_x, qr_y, width=qr_size, height=qr_size)

                # Draw link name (truncated if too long)
                c.setFont("Helvetica-Bold", 12)
                name_to_display = link['name']
                max_width = qr_size
                if c.stringWidth(name_to_display) > max_width:
                    while c.stringWidth(name_to_display + "...") > max_width:
                        name_to_display = name_to_display[:-1]
                    name_to_display += "..."
                c.drawString(current_x, qr_y - 15, name_to_display)

                # Draw URL (truncated if too long)
                c.setFont("Helvetica", 8)
                url_to_display = link['url']
                if c.stringWidth(url_to_display) > max_width:
                    while c.stringWidth(url_to_display + "...") > max_width:
                        url_to_display = url_to_display[:-1]
                    url_to_display += "..."
                c.drawString(current_x, qr_y - 25, url_to_display)

            except Exception as e:
                tkinter.messagebox.showerror("Error", f"Failed to generate QR for {link['name']}: {e}")
                
        c.save()
        tkinter.messagebox.showinfo("Export Complete", f"PDF exported successfully:\n{os.path.abspath(filename)}")

    def display_links(self, search_query=""):
        for widget in self.link_list_frame.winfo_children():
            widget.destroy()
        self.checkbox_vars = {}
        filtered_links = [(i, l) for i, l in enumerate(self.links) if search_query in l["name"].lower() or search_query in l["url"].lower()]
        if not filtered_links:
            ctk.CTkLabel(self.link_list_frame, text="No links found.", font=ctk.CTkFont(size=self.font_size)).grid(row=0, column=0, pady=20)
        for i, (idx, link) in enumerate(filtered_links):
            card = ctk.CTkFrame(self.link_list_frame, corner_radius=8)
            card.grid(row=i, column=0, padx=10, pady=5, sticky="ew")
            card.grid_columnconfigure(1, weight=1)
            card.grid_columnconfigure(2, weight=0)
            
            self.checkbox_vars[idx] = ctk.IntVar(value=0)
            ctk.CTkCheckBox(card, text="", variable=self.checkbox_vars[idx]).grid(row=0, column=0, rowspan=2, padx=(10, 0), pady=10, sticky="w")
            
            ctk.CTkLabel(card, text=link["name"], font=ctk.CTkFont(size=self.font_size, weight="bold")).grid(row=0, column=1, padx=(5, 5), pady=5, sticky="w")
            
            url_label = ctk.CTkLabel(card, text=link["url"], font=ctk.CTkFont(size=self.font_size - 2), text_color="#A9A9A9", wraplength=400, justify="left")
            url_label.grid(row=1, column=1, padx=(5, 5), pady=5, sticky="w")
            
            act = ctk.CTkFrame(card, corner_radius=0, fg_color="transparent")
            act.grid(row=0, column=2, rowspan=2, padx=(5, 10), pady=5, sticky="e")
            act.grid_columnconfigure((0, 1, 2), weight=1)
            
            ctk.CTkButton(act, text="View QR", command=lambda l=link: self.show_qr_code(l["url"], l["name"]), width=80, font=ctk.CTkFont(size=self.font_size-2)).grid(row=0, column=0, padx=5, pady=5)
            ctk.CTkButton(act, text="Edit", command=lambda i=idx: self.set_edit_mode(i), width=80, font=ctk.CTkFont(size=self.font_size-2)).grid(row=0, column=1, padx=5, pady=5)
            ctk.CTkButton(act, text="Delete", command=lambda i=idx: self.delete_link(i), width=80, fg_color="#F44336", hover_color="#D32F2F", font=ctk.CTkFont(size=self.font_size-2)).grid(row=0, column=2, padx=5, pady=5)

class InventoryManagerFrame(ctk.CTkFrame):
    """Frame for the new inventory management features."""
    
    INVENTORY_FILE = "inventory.json"
    PDF_DIRECTORY = "exported_inventory_pdfs"

    def __init__(self, master, font_size):
        super().__init__(master)
        self.font_size = font_size
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        if not os.path.exists(self.PDF_DIRECTORY):
            os.makedirs(self.PDF_DIRECTORY)

        self.inventory_items = self.load_inventory()
        self.editing_id = None
        self.checkbox_vars = {}

        # --- UI Components ---
        self.top_frame = ctk.CTkFrame(self, corner_radius=10)
        self.top_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="nsew")
        self.top_frame.grid_columnconfigure(0, weight=1)
        self.top_frame.grid_columnconfigure(1, weight=1)
        
        self.add_frame = ctk.CTkFrame(self.top_frame, corner_radius=10)
        self.add_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.add_frame.grid_columnconfigure(0, weight=1)

        self.item_name_label = ctk.CTkLabel(self.add_frame, text="Item Name:", font=ctk.CTkFont(size=self.font_size, weight="bold"))
        self.item_name_label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        self.item_name_entry = ctk.CTkEntry(self.add_frame, placeholder_text="Name of the item", font=ctk.CTkFont(size=self.font_size))
        self.item_name_entry.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        self.item_desc_label = ctk.CTkLabel(self.add_frame, text="Description:", font=ctk.CTkFont(size=self.font_size, weight="bold"))
        self.item_desc_label.grid(row=2, column=0, padx=10, pady=(10, 5), sticky="w")
        self.item_desc_entry = ctk.CTkEntry(self.add_frame, placeholder_text="Brief description of the item", font=ctk.CTkFont(size=self.font_size))
        self.item_desc_entry.grid(row=3, column=0, padx=10, pady=5, sticky="ew")

        self.add_button = ctk.CTkButton(self.add_frame, text="Generate QR", command=self.add_or_update_item, font=ctk.CTkFont(size=self.font_size))
        self.add_button.grid(row=4, column=0, padx=10, pady=(10, 10))

        self.action_frame = ctk.CTkFrame(self.top_frame, corner_radius=10)
        self.action_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.action_frame.grid_columnconfigure(0, weight=1)

        self.select_all_button = ctk.CTkButton(self.action_frame, text="Select All", command=self.select_all_items, font=ctk.CTkFont(size=self.font_size))
        self.select_all_button.grid(row=0, column=0, padx=20, pady=5, sticky="ew")

        self.deselect_all_button = ctk.CTkButton(self.action_frame, text="Deselect All", command=self.deselect_all_items, font=ctk.CTkFont(size=self.font_size))
        self.deselect_all_button.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        
        self.delete_selected_button = ctk.CTkButton(self.action_frame, text="Delete Selected", command=self.delete_selected_items, fg_color="#F44336", hover_color="#D32F2F", font=ctk.CTkFont(size=self.font_size))
        self.delete_selected_button.grid(row=2, column=0, padx=20, pady=5, sticky="ew")

        self.export_qr_pdf_button = ctk.CTkButton(self.action_frame, text="Export QR to PDF", command=self.export_multi_qr_to_pdf, font=ctk.CTkFont(size=self.font_size))
        self.export_qr_pdf_button.grid(row=3, column=0, padx=20, pady=5, sticky="ew")
        
        self.export_button = ctk.CTkButton(self.action_frame, text="Export to PDF", command=self.export_to_pdf, font=ctk.CTkFont(size=self.font_size))
        self.export_button.grid(row=4, column=0, padx=20, pady=5, sticky="ew")
        
        self.search_entry = ctk.CTkEntry(self, placeholder_text="Search items by ID, name or description...", font=ctk.CTkFont(size=self.font_size))
        self.search_entry.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")
        self.search_entry.bind("<KeyRelease>", self.filter_items)

        self.item_list_frame = ctk.CTkScrollableFrame(self, corner_radius=10)
        self.item_list_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.item_list_frame.grid_columnconfigure(1, weight=1)

        self.display_items()

    def load_inventory(self):
        if os.path.exists(self.INVENTORY_FILE):
            try:
                with open(self.INVENTORY_FILE, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return []
        return []

    def save_inventory(self):
        try:
            with open(self.INVENTORY_FILE, "w") as f:
                json.dump(self.inventory_items, f, indent=4)
        except Exception as e:
            print(f"Failed to save inventory: {e}")

    def add_or_update_item(self):
        item_name = self.item_name_entry.get().strip()
        description = self.item_desc_entry.get().strip()
        if item_name and description:
            if self.editing_id is not None:
                for item in self.inventory_items:
                    if item["id"] == self.editing_id:
                        item["name"] = item_name
                        item["description"] = description
                        break
                self.editing_id = None
                self.add_button.configure(text="Generate QR")
            else:
                new_id = str(uuid.uuid4())
                self.inventory_items.append({"id": new_id, "name": item_name, "description": description})
            
            self.save_inventory()
            self.display_items()
            self.item_name_entry.delete(0, "end")
            self.item_desc_entry.delete(0, "end")
        else:
            tkinter.messagebox.showwarning("Warning", "Please fill in both the item name and description.")

    def update_font(self, new_font_size):
        self.font_size = new_font_size
        self.item_name_label.configure(font=ctk.CTkFont(size=self.font_size, weight="bold"))
        self.item_name_entry.configure(font=ctk.CTkFont(size=self.font_size))
        self.item_desc_label.configure(font=ctk.CTkFont(size=self.font_size, weight="bold"))
        self.item_desc_entry.configure(font=ctk.CTkFont(size=self.font_size))
        self.add_button.configure(font=ctk.CTkFont(size=self.font_size))
        self.select_all_button.configure(font=ctk.CTkFont(size=self.font_size))
        self.deselect_all_button.configure(font=ctk.CTkFont(size=self.font_size))
        self.delete_selected_button.configure(font=ctk.CTkFont(size=self.font_size))
        self.export_qr_pdf_button.configure(font=ctk.CTkFont(size=self.font_size))
        self.export_button.configure(font=ctk.CTkFont(size=self.font_size))
        self.search_entry.configure(font=ctk.CTkFont(size=self.font_size))
        self.display_items(self.search_entry.get().strip().lower())
        
    def filter_items(self, event=None):
        self.display_items(self.search_entry.get().strip().lower())

    def set_edit_mode(self, item_id):
        self.editing_id = item_id
        item = next((item for item in self.inventory_items if item["id"] == item_id), None)
        if item:
            self.item_name_entry.delete(0, "end")
            self.item_desc_entry.delete(0, "end")
            self.item_name_entry.insert(0, item["name"])
            self.item_desc_entry.insert(0, item["description"])
            self.add_button.configure(text="Update Item")

    def show_qr_code(self, item_id, name):
        try:
            qr = qrcode.QRCode(version=1, box_size=10, border=4)
            qr.add_data(item_id)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white").resize((300, 300))
            qr_window = ctk.CTkToplevel(self.master.master)
            qr_window.title(f"QR Code for: {name}")
            qr_window.geometry("340x380")
            img_tk = ctk.CTkImage(light_image=img, dark_image=img, size=(300, 300))
            qr_label = ctk.CTkLabel(qr_window, image=img_tk, text="")
            qr_label.pack(pady=(20, 10))
            name_label = ctk.CTkLabel(qr_window, text=name, font=ctk.CTkFont(size=self.font_size+2, weight="bold"))
            name_label.pack()
        except Exception as e:
            tkinter.messagebox.showerror("Error", f"Failed to generate QR code: {e}")

    def delete_item(self, item_id):
        if tkinter.messagebox.askyesno("Confirm Delete", f"Delete item '{item_id}'?"):
            self.inventory_items = [item for item in self.inventory_items if item["id"] != item_id]
            self.save_inventory()
            self.display_items()

    def delete_selected_items(self):
        selected_ids = [item["id"] for item in self.inventory_items if self.checkbox_vars[item["id"]].get() == 1]
        if not selected_ids:
            tkinter.messagebox.showwarning("Warning", "Please select at least one item to delete.")
            return
        if tkinter.messagebox.askyesno("Confirm Bulk Delete", f"Delete {len(selected_ids)} selected item(s)?"):
            self.inventory_items = [item for item in self.inventory_items if item["id"] not in selected_ids]
            self.save_inventory()
            self.display_items()

    def select_all_items(self):
        for var in self.checkbox_vars.values():
            var.set(1)

    def deselect_all_items(self):
        for var in self.checkbox_vars.values():
            var.set(0)

    def export_to_pdf(self):
        selected_items = [item for item in self.inventory_items if self.checkbox_vars[item["id"]].get() == 1]
        if not selected_items:
            tkinter.messagebox.showwarning("Warning", "Please select at least one item to export.")
            return
        filename = "exported_inventory.pdf"
        c = pdf_canvas.Canvas(filename, pagesize=letter)
        margin = 50
        y_pos = letter[1] - margin
        qr_size = 120
        # Horizontal positions for the 3 columns
        col1_x = margin
        col2_x = margin + qr_size + 20
        col3_x = col2_x + qr_size + 20
        c.setFont("Helvetica-Bold", 18)
        c.drawString(margin, y_pos, "Inventory QR Codes")
        y_pos -= 30

        for i, item in enumerate(selected_items):
            # Determine the column for the current link
            col_index = i % 3
            current_x = margin + col_index * (qr_size + 20)
            
            # Move to a new row if starting a new set of 3
            if col_index == 0 and i > 0:
                y_pos -= (qr_size + 40)
            
            # Check for new page
            if y_pos < margin + (qr_size + 40):
                c.showPage()
                y_pos = letter[1] - margin
                c.setFont("Helvetica-Bold", 18)
                c.drawString(margin, y_pos, "Inventory QR Codes (cont.)")
                y_pos -= 30
                current_x = margin
                
            try:
                qr = qrcode.QRCode(version=1, box_size=5, border=4)
                qr.add_data(item['id'])
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")
                img_buffer = io.BytesIO()
                img.save(img_buffer, "PNG")

                qr_y = y_pos - qr_size
                c.drawImage(ImageReader(img_buffer), current_x, qr_y, width=qr_size, height=qr_size)

                # Draw item name (truncated if too long)
                c.setFont("Helvetica-Bold", 12)
                name_to_display = item['name']
                max_width = qr_size
                if c.stringWidth(name_to_display) > max_width:
                    while c.stringWidth(name_to_display + "...") > max_width:
                        name_to_display = name_to_display[:-1]
                    name_to_display += "..."
                c.drawString(current_x, qr_y - 15, name_to_display)
                
                # Draw description (truncated if too long)
                c.setFont("Helvetica", 8)
                desc_to_display = item['description']
                if c.stringWidth(desc_to_display) > max_width:
                    while c.stringWidth(desc_to_display + "...") > max_width:
                        desc_to_display = desc_to_display[:-1]
                    desc_to_display += "..."
                c.drawString(current_x, qr_y - 25, desc_to_display)

            except Exception as e:
                tkinter.messagebox.showerror("Error", f"Failed to generate QR for {item['name']}: {e}")
        c.save()
        tkinter.messagebox.showinfo("Export Complete", f"PDF exported successfully:\n{os.path.abspath(filename)}")

    def export_multi_qr_to_pdf(self):
        selected_items = [item for item in self.inventory_items if self.checkbox_vars[item["id"]].get() == 1]
        if not selected_items:
            tkinter.messagebox.showwarning("Warning", "Please select at least one item to export.")
            return

        # 1. Create a PDF with all selected items and their details.
        pdf_filename = os.path.join(self.PDF_DIRECTORY, f"inventory_export_{uuid.uuid4().hex[:8]}.pdf")
        c = pdf_canvas.Canvas(pdf_filename, pagesize=letter)
        c.setFont("Helvetica-Bold", 24)
        c.drawString(50, 750, "Inventory Collection Details")
        y_pos = 720
        c.setFont("Helvetica", 12)
        for i, item in enumerate(selected_items):
            if y_pos < 100:
                c.showPage()
                y_pos = 750
                c.setFont("Helvetica-Bold", 24)
                c.drawString(50, y_pos, "Inventory Collection Details (cont.)")
                y_pos -= 30
                c.setFont("Helvetica", 12)

            c.drawString(70, y_pos, f"Item Name: {item['name']}")
            y_pos -= 15
            c.drawString(70, y_pos, f"Description: {item['description']}")
            y_pos -= 15
            c.drawString(70, y_pos, f"Unique ID: {item['id']}")
            y_pos -= 25
            if i < len(selected_items) - 1:
                c.line(50, y_pos, 550, y_pos)
                y_pos -= 15
        
        c.save()

        # 2. Create a single QR code that links to the PDF.
        qr_filename = os.path.join(self.PDF_DIRECTORY, f"qr_code_{uuid.uuid4().hex[:8]}.png")
        qr_data = os.path.abspath(pdf_filename)
        
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(qr_data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(qr_filename)

        # 3. Display the single QR code to the user.
        try:
            qr_window = ctk.CTkToplevel(self)
            qr_window.title("QR Code for Inventory PDF")
            qr_window.geometry("500x550")

            img_tk = ctk.CTkImage(light_image=img, dark_image=img, size=(400, 400))
            qr_label = ctk.CTkLabel(qr_window, image=img_tk, text="")
            qr_label.pack(pady=20)

            name_label = ctk.CTkLabel(qr_window, text="Scan this QR code to view the PDF with all selected item details.", 
                                      font=ctk.CTkFont(size=self.font_size, weight="bold"))
            name_label.pack()

            path_label = ctk.CTkLabel(qr_window, text=f"PDF saved to: {os.path.abspath(pdf_filename)}",
                                      font=ctk.CTkFont(size=self.font_size-2))
            path_label.pack(pady=(10, 0))

        except Exception as e:
            tkinter.messagebox.showerror("Error", f"Failed to generate and display QR code: {e}")

    def display_items(self, search_query=""):
        for widget in self.item_list_frame.winfo_children():
            widget.destroy()
        self.checkbox_vars = {}
        filtered_items = [(i, l) for i, l in enumerate(self.inventory_items) if search_query in l["name"].lower() or search_query in l["description"].lower() or search_query in l["id"].lower()]
        if not filtered_items:
            ctk.CTkLabel(self.item_list_frame, text="No inventory items found.", font=ctk.CTkFont(size=self.font_size)).grid(row=0, column=0, pady=20)
        for i, (idx, item) in enumerate(filtered_items):
            item_card = ctk.CTkFrame(self.item_list_frame, corner_radius=8)
            item_card.grid(row=i, column=0, padx=10, pady=5, sticky="ew")
            item_card.grid_columnconfigure(1, weight=1)
            self.checkbox_vars[item["id"]] = ctk.IntVar(value=0)
            ctk.CTkCheckBox(item_card, text="", variable=self.checkbox_vars[item["id"]]).grid(row=0, column=0, rowspan=2, padx=(10, 0), pady=10, sticky="w")
            ctk.CTkLabel(item_card, text=item["name"], font=ctk.CTkFont(size=self.font_size, weight="bold")).grid(row=0, column=1, padx=(5, 5), pady=5, sticky="w")
            ctk.CTkLabel(item_card, text=f"Description: {item['description']}", font=ctk.CTkFont(size=self.font_size-2), text_color="#A9A9A9").grid(row=1, column=1, padx=(5, 5), pady=5, sticky="w")
            act = ctk.CTkFrame(item_card, corner_radius=0, fg_color="transparent")
            act.grid(row=0, column=2, rowspan=2, padx=(5, 10), pady=5, sticky="e")
            act.grid_columnconfigure((0, 1, 2), weight=1)
            ctk.CTkButton(act, text="View QR", command=lambda i=item['id'], n=item['name']: self.show_qr_code(i, n), width=80, font=ctk.CTkFont(size=self.font_size-2)).grid(row=0, column=0, padx=5, pady=5)
            ctk.CTkButton(act, text="Edit", command=lambda i=item['id']: self.set_edit_mode(i), width=80, font=ctk.CTkFont(size=self.font_size-2)).grid(row=0, column=1, padx=5, pady=5)
            ctk.CTkButton(act, text="Delete", command=lambda i=item['id']: self.delete_item(i), width=80, fg_color="#F44336", hover_color="#D32F2F", font=ctk.CTkFont(size=self.font_size-2)).grid(row=0, column=2, padx=5, pady=5)

if __name__ == "__main__":
    app = LinkitApp()
    app.mainloop()