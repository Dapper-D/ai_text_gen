import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from tkinter import ttk
import os
import google.generativeai as genai
from dotenv import load_dotenv
from ttkthemes import ThemedStyle
from googlesearch import search
import requests
from bs4 import BeautifulSoup

# Load environment variables
load_dotenv()

class AIEditor:
    def __init__(self):
        # Default API key for Gemini AI (free tier)
        default_api_key = "AIzaSyDAn8Nk89nmhRi3qNmo7wH7-ov3Che0UeM"  # Gemini API key
        
        # Try to get API key from environment, fall back to default if not found
        api_key = os.getenv('GEMINI_API_KEY', default_api_key)
        
        # Configure Google AI with Gemini API
        genai.configure(api_key=api_key)
        
        # List available models
        try:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    print(f"Available model: {m.name}")
            # Use Gemini model
            self.model = genai.GenerativeModel('gemini-2.0-flash')
        except Exception as e:
            print(f"Error listing models: {str(e)}")
            # Fallback to Gemini model
            self.model = genai.GenerativeModel('gemini-2.0-flash')
        
    def generate_text(self, prompt, max_tokens=2000):
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating text: {str(e)}"

class TextEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Text Generator")
        self.root.geometry("1200x800")
        
        # Initialize AI editor
        self.ai_editor = AIEditor()
        
        # Create main menu
        self.menu_bar = tk.Menu(root)
        self.root.config(menu=self.menu_bar)
        
        # File menu
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="New", command=self.new_file)
        self.file_menu.add_command(label="Open", command=self.open_file)
        self.file_menu.add_command(label="Save", command=self.save_file)
        self.file_menu.add_command(label="Save As", command=self.save_as)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=root.quit)
        
        # Create main container
        self.main_container = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
        self.main_container.pack(expand=True, fill='both', padx=5, pady=5)
        
        # Left panel for text editing
        self.left_panel = ttk.Frame(self.main_container)
        self.main_container.add(self.left_panel, weight=3)
        
        # Create text area with line numbers
        self.text_frame = ttk.Frame(self.left_panel)
        self.text_frame.pack(expand=True, fill='both')
        
        self.line_numbers = tk.Text(self.text_frame, width=4, padx=3, takefocus=0,
                                  border=0, state='disabled',
                                  bg='#424242', fg='#ffffff')
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        
        self.text_area = scrolledtext.ScrolledText(self.text_frame, wrap=tk.WORD, undo=True)
        self.text_area.pack(side=tk.LEFT, expand=True, fill='both')
        
        # Right panel for AI controls
        self.right_panel = ttk.Frame(self.main_container)
        self.main_container.add(self.right_panel, weight=1)
        
        # Create canvas and scrollbar for right panel
        self.right_canvas = tk.Canvas(self.right_panel)
        self.right_scrollbar = ttk.Scrollbar(self.right_panel, orient="vertical", command=self.right_canvas.yview)
        self.scrollable_frame = ttk.Frame(self.right_canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.right_canvas.configure(scrollregion=self.right_canvas.bbox("all"))
        )
        
        self.right_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.right_canvas.configure(yscrollcommand=self.right_scrollbar.set)
        
        # Pack the canvas and scrollbar
        self.right_scrollbar.pack(side="right", fill="y")
        self.right_canvas.pack(side="left", fill="both", expand=True)
        
        # AI Controls
        self.create_ai_controls()
        
        # Current file path
        self.current_file = None
        
        # Bind events
        self.text_area.bind('<<Modified>>', self.update_line_numbers)
        self.text_area.bind('<Key>', self.update_line_numbers)
        
        # Set focus to text area
        self.text_area.focus_set()
        
        # Apply a dark theme using ttkthemes
        self.style = ThemedStyle(self.root)
        self.style.set_theme("black")
    
    def create_ai_controls(self):
        # AI Generation Controls
        ttk.Label(self.scrollable_frame, text="AI Generation").pack(pady=5)
        
        self.prompt_text = scrolledtext.ScrolledText(self.scrollable_frame, height=5)
        self.prompt_text.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(self.scrollable_frame, text="Generate", command=self.generate_text).pack(pady=5)
        
        # Add separator
        ttk.Separator(self.scrollable_frame, orient='horizontal').pack(fill='x', padx=5, pady=10)
        
        # Web Search Controls
        ttk.Label(self.scrollable_frame, text="Web Search").pack(pady=5)
        
        # Search query
        ttk.Label(self.scrollable_frame, text="Search Query:").pack(anchor='w', padx=5)
        self.search_query = scrolledtext.ScrolledText(self.scrollable_frame, height=3)
        self.search_query.pack(fill=tk.X, padx=5, pady=5)
        
        # Search results
        ttk.Label(self.scrollable_frame, text="Search Results:").pack(anchor='w', padx=5)
        self.search_results = scrolledtext.ScrolledText(self.scrollable_frame, height=5)
        self.search_results.pack(fill=tk.X, padx=5, pady=5)
        
        # Search buttons
        search_buttons_frame = ttk.Frame(self.scrollable_frame)
        search_buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(search_buttons_frame, text="Search", command=self.perform_web_search).pack(side=tk.LEFT, padx=2)
        ttk.Button(search_buttons_frame, text="Add to Document", command=self.add_search_result).pack(side=tk.LEFT, padx=2)
        ttk.Button(search_buttons_frame, text="Clear", command=self.clear_search_section).pack(side=tk.LEFT, padx=2)
        
        # Add separator
        ttk.Separator(self.scrollable_frame, orient='horizontal').pack(fill='x', padx=5, pady=10)
        
        # Text Transformation Controls
        ttk.Label(self.scrollable_frame, text="Text Transformation").pack(pady=5)
        
        # Text to transform
        ttk.Label(self.scrollable_frame, text="Text to Transform:").pack(anchor='w', padx=5)
        self.transform_text = scrolledtext.ScrolledText(self.scrollable_frame, height=5)
        self.transform_text.pack(fill=tk.X, padx=5, pady=5)
        
        # Transformation instructions
        ttk.Label(self.scrollable_frame, text="Transformation Instructions:").pack(anchor='w', padx=5)
        self.transform_instructions = scrolledtext.ScrolledText(self.scrollable_frame, height=3)
        self.transform_instructions.pack(fill=tk.X, padx=5, pady=5)
        
        # Buttons for text transformation
        transform_buttons_frame = ttk.Frame(self.scrollable_frame)
        transform_buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(transform_buttons_frame, text="Copy Selected", command=self.copy_selected_text).pack(side=tk.LEFT, padx=2)
        ttk.Button(transform_buttons_frame, text="Apply Changes", command=self.apply_text_transformation).pack(side=tk.LEFT, padx=2)
        ttk.Button(transform_buttons_frame, text="Clear", command=self.clear_transform_section).pack(side=tk.LEFT, padx=2)
    
    def update_line_numbers(self, event=None):
        self.line_numbers.config(state='normal')
        self.line_numbers.delete(1.0, tk.END)
        text_content = self.text_area.get(1.0, tk.END)
        line_count = text_content.count('\n') + 1
        for i in range(1, line_count + 1):
            self.line_numbers.insert(tk.END, f"{i}\n")
        self.line_numbers.config(state='disabled')
    
    def generate_text(self):
        prompt = self.prompt_text.get(1.0, tk.END).strip()
        if not prompt:
            messagebox.showwarning("Warning", "Please enter a prompt for text generation")
            return
        
        try:
            generated_text = self.ai_editor.generate_text(prompt)
            self.text_area.insert(tk.INSERT, generated_text)
        except Exception as e:
            messagebox.showerror("Error", f"Error generating text: {str(e)}")
    
    def new_file(self):
        if self.text_area.edit_modified():
            if messagebox.askyesno("Save Changes?", "Do you want to save changes before creating a new file?"):
                self.save_file()
        self.text_area.delete(1.0, tk.END)
        self.current_file = None
        self.root.title("AI Text Generator - New File")
        self.text_area.edit_modified(False)
        
    def open_file(self):
        if self.text_area.edit_modified():
            if messagebox.askyesno("Save Changes?", "Do you want to save changes before opening a new file?"):
                self.save_file()
                
        file_path = filedialog.askopenfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    self.text_area.delete(1.0, tk.END)
                    self.text_area.insert(1.0, file.read())
                self.current_file = file_path
                self.root.title(f"AI Text Generator - {os.path.basename(file_path)}")
                self.text_area.edit_modified(False)
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {str(e)}")
                
    def save_file(self):
        if self.current_file:
            try:
                content = self.text_area.get(1.0, tk.END)
                with open(self.current_file, 'w', encoding='utf-8') as file:
                    file.write(content)
                self.text_area.edit_modified(False)
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {str(e)}")
        else:
            self.save_as()
            
    def save_as(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                content = self.text_area.get(1.0, tk.END)
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(content)
                self.current_file = file_path
                self.root.title(f"AI Text Generator - {os.path.basename(file_path)}")
                self.text_area.edit_modified(False)
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {str(e)}")

    def copy_selected_text(self):
        try:
            selected_text = self.text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.transform_text.delete(1.0, tk.END)
            self.transform_text.insert(1.0, selected_text)
        except tk.TclError:
            messagebox.showwarning("Warning", "No text selected in the main editor")

    def apply_text_transformation(self):
        original_text = self.transform_text.get(1.0, tk.END).strip()
        instructions = self.transform_instructions.get(1.0, tk.END).strip()
        
        if not original_text:
            messagebox.showwarning("Warning", "No text to transform")
            return
            
        if not instructions:
            messagebox.showwarning("Warning", "Please provide transformation instructions")
            return
            
        try:
            # Create a prompt for the AI to transform the text
            prompt = f"Transform this text according to these instructions:\n\nText: {original_text}\n\nInstructions: {instructions}\n\nProvide only the transformed text without any explanations or line breaks at the end."
            
            transformed_text = self.ai_editor.generate_text(prompt).strip()
            
            # Replace the selected text in the main editor
            try:
                self.text_area.delete(tk.SEL_FIRST, tk.SEL_LAST)
                self.text_area.insert(tk.INSERT, transformed_text)
            except tk.TclError:
                # If no text is selected, just insert at the current cursor position
                self.text_area.insert(tk.INSERT, transformed_text)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error transforming text: {str(e)}")

    def clear_transform_section(self):
        self.transform_text.delete(1.0, tk.END)
        self.transform_instructions.delete(1.0, tk.END)

    def perform_web_search(self):
        query = self.search_query.get(1.0, tk.END).strip()
        if not query:
            messagebox.showwarning("Warning", "Please enter a search query")
            return
            
        try:
            self.search_results.delete(1.0, tk.END)
            self.search_results.insert(tk.END, "Searching...\n")
            self.root.update()
            
            # Perform the search
            search_results = []
            for url in search(query, num_results=5):
                try:
                    response = requests.get(url, timeout=5)
                    soup = BeautifulSoup(response.text, 'html.parser')
                    title = soup.title.string if soup.title else url
                    # Get first paragraph or meta description
                    content = soup.find('meta', {'name': 'description'})
                    if content:
                        content = content.get('content', '')
                    else:
                        content = soup.find('p')
                        content = content.text if content else ''
                    
                    search_results.append(f"Title: {title}\nURL: {url}\nContent: {content[:200]}...\n\n")
                except Exception as e:
                    continue
            
            self.search_results.delete(1.0, tk.END)
            if search_results:
                self.search_results.insert(tk.END, "".join(search_results))
            else:
                self.search_results.insert(tk.END, "No results found.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error performing web search: {str(e)}")
    
    def add_search_result(self):
        try:
            selected_text = self.search_results.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.text_area.insert(tk.INSERT, selected_text + "\n\n")
        except tk.TclError:
            messagebox.showwarning("Warning", "No text selected in search results")
    
    def clear_search_section(self):
        self.search_query.delete(1.0, tk.END)
        self.search_results.delete(1.0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = TextEditor(root)
    root.mainloop() 