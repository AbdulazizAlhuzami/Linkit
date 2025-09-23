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

# Set the appearance mode and color theme
ctk.set_appearance_mode("System")  # "System", "Dark", "Light"
ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"

class LinkManagerApp(ctk.CTk):
    """
    A cross-platform desktop application for managing links.
    This version includes an improved UI, QR code generation, and a more
    robust and visually appealing PDF export feature.
    """
    
    LINKS_FILE = "links.json"  # Path to the JSON file where links will be saved

    def __init__(self):
        super().__init__()

        # Window setup
        self.title("Link Manager")
        self.geometry("1000x700")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # Dictionary to hold checkbox variables for link selection
        self.checkbox_vars = {}
        self.editing_index = None

        # --- UI Components ---

        # Main frame
        self.top_frame = ctk.CTkFrame(self, corner_radius=10)
        self.top_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="nsew")
        self.top_frame.grid_columnconfigure(0, weight=1)
        self.top_frame.grid_columnconfigure(1, weight=1)

        # Frame for adding/editing links
        self.add_frame = ctk.CTkFrame(self.top_frame, corner_radius=10)
        self.add_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.add_frame.grid_columnconfigure(0, weight=1)
        
        self.link_label = ctk.CTkLabel(self.add_frame, text="Link Name:", font=ctk.CTkFont(size=14, weight="bold"))
        self.link_label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        
        self.link_entry = ctk.CTkEntry(self.add_frame, placeholder_text="Enter a descriptive name for your link")
        self.link_entry.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        self.url_label = ctk.CTkLabel(self.add_frame, text="URL:", font=ctk.CTkFont(size=14, weight="bold"))
        self.url_label.grid(row=2, column=0, padx=10, pady=(10, 5), sticky="w")
        
        self.url_entry = ctk.CTkEntry(self.add_frame, placeholder_text="Enter the full URL (e.g., https://www.google.com)")
        self.url_entry.grid(row=3, column=0, padx=10, pady=5, sticky="ew")

        self.add_button = ctk.CTkButton(self.add_frame, text="Add Link", command=self.add_or_update_link)
        self.add_button.grid(row=4, column=0, padx=10, pady=(10, 10))

        # Action buttons frame
        self.action_frame = ctk.CTkFrame(self.top_frame, corner_radius=10)
        self.action_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.action_frame.grid_columnconfigure(0, weight=1)

        self.select_all_button = ctk.CTkButton(self.action_frame, text="Select All", command=self.select_all_links)
        self.select_all_button.grid(row=0, column=0, padx=20, pady=5, sticky="ew")

        self.deselect_all_button = ctk.CTkButton(self.action_frame, text="Deselect All", command=self.deselect_all_links)
        self.deselect_all_button.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        
        self.delete_selected_button = ctk.CTkButton(self.action_frame, text="Delete Selected", command=self.delete_selected_links, fg_color="#F44336", hover_color="#D32F2F")
        self.delete_selected_button.grid(row=2, column=0, padx=20, pady=5, sticky="ew")

        self.export_button = ctk.CTkButton(self.action_frame, text="Export to PDF", command=self.export_to_pdf)
        self.export_button.grid(row=3, column=0, padx=20, pady=5, sticky="ew")

        # Search bar
        self.search_entry = ctk.CTkEntry(self, placeholder_text="Search links...")
        self.search_entry.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")
        self.search_entry.bind("<KeyRelease>", self.filter_links)

        # Scrollable frame
        self.link_list_frame = ctk.CTkScrollableFrame(self, corner_radius=10)
        self.link_list_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.link_list_frame.grid_columnconfigure(1, weight=1)

        # --- Data Handling ---
        self.links = self.load_links()
        self.display_links()

    # --- Methods (unchanged from your version) ---
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
            qr_window = ctk.CTkToplevel(self)
            qr_window.title(f"QR Code for: {name}")
            qr_window.geometry("340x380")
            img_tk = ctk.CTkImage(light_image=img, dark_image=img, size=(300, 300))
            qr_label = ctk.CTkLabel(qr_window, image=img_tk, text="")
            qr_label.pack(pady=(20, 10))
            name_label = ctk.CTkLabel(qr_window, text=name, font=ctk.CTkFont(size=14, weight="bold"))
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
        margin, qr_size, h_spacing, v_spacing = 50, 120, 20, 50
        max_cols = int((letter[0] - 2 * margin) / (qr_size + h_spacing))
        x_pos, y_pos, col_count = margin, letter[1] - margin, 0
        img_buffer = io.BytesIO()
        c.setFont("Helvetica-Bold", 18)
        c.drawString(margin, y_pos, "QR Codes")
        y_pos -= v_spacing
        for link in selected_links:
            if y_pos < margin + qr_size + v_spacing:
                c.showPage()
                x_pos, y_pos, col_count = margin, letter[1] - margin, 0
                c.setFont("Helvetica-Bold", 18)
                c.drawString(margin, y_pos, "QR Codes (cont.)")
                y_pos -= v_spacing
            if col_count >= max_cols:
                col_count, x_pos = 0, margin
                y_pos -= qr_size + v_spacing
            try:
                qr = qrcode.QRCode(version=1, box_size=5, border=4)
                qr.add_data(link['url'])
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")
                img_buffer.seek(0)
                img_buffer.truncate(0)
                img.save(img_buffer, "PNG")
                c.drawImage(ImageReader(img_buffer), x_pos, y_pos - qr_size, width=qr_size, height=qr_size)
                text_x, text_y = x_pos + qr_size / 2, y_pos - qr_size - 15
                c.setFont("Helvetica-Bold", 12)
                c.drawCentredString(text_x, text_y, link['name'])
                c.setFont("Helvetica", 10)
                c.drawCentredString(text_x, text_y - 30, link['url'])
                x_pos += qr_size + h_spacing
                col_count += 1
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
            ctk.CTkLabel(self.link_list_frame, text="No links found.").grid(row=0, column=0, pady=20)
        for i, (idx, link) in enumerate(filtered_links):
            card = ctk.CTkFrame(self.link_list_frame, corner_radius=8)
            card.grid(row=i, column=0, padx=10, pady=5, sticky="ew")
            card.grid_columnconfigure(1, weight=1)
            self.checkbox_vars[idx] = ctk.IntVar(value=0)
            ctk.CTkCheckBox(card, text="", variable=self.checkbox_vars[idx]).grid(row=0, column=0, rowspan=2, padx=(10, 0), pady=10, sticky="w")
            ctk.CTkLabel(card, text=link["name"], font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=1, padx=(5, 5), pady=5, sticky="w")
            ctk.CTkLabel(card, text=link["url"], font=ctk.CTkFont(size=12), text_color="#A9A9A9").grid(row=1, column=1, padx=(5, 5), pady=5, sticky="w")
            act = ctk.CTkFrame(card, corner_radius=0, fg_color="transparent")
            act.grid(row=0, column=2, rowspan=2, padx=(5, 10), pady=5, sticky="e")
            act.grid_columnconfigure((0, 1, 2), weight=1)
            ctk.CTkButton(act, text="View QR", command=lambda l=link: self.show_qr_code(l["url"], l["name"]), width=80).grid(row=0, column=0, padx=5, pady=5)
            ctk.CTkButton(act, text="Edit", command=lambda i=idx: self.set_edit_mode(i), width=80).grid(row=0, column=1, padx=5, pady=5)
            ctk.CTkButton(act, text="Delete", command=lambda i=idx: self.delete_link(i), width=80, fg_color="#F44336", hover_color="#D32F2F").grid(row=0, column=2, padx=5, pady=5)

if __name__ == "__main__":
    app = LinkManagerApp()
    app.mainloop()
