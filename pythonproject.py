import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from openai import OpenAI, OpenAIError
import threading
import queue
import os
import mysql.connector
from mysql.connector import Error

# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY", "<OPEN_API_KEY_HERE>")
client = OpenAI(api_key=api_key)

class InteractiveGeographyMap:
    def __init__(self):
        # Initialize the database
        self.init_db()
        
        self.root = tk.Tk()
        self.root.title("Login & Sign Up")
        self.center_window(self.root, 500, 550)
        self.root.resizable(False, False)
        self.root.attributes("-alpha", 0.0)
        self.root.configure(bg="#06142E")
        self.show_login()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.fade_in(self.root)
        self.root.mainloop()

    def init_db(self):
        """Initialize the MySQL database and create the users table if it doesn't exist."""
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",  # Add your MySQL password here if required
                database="geography_db"
            )
            if conn.is_connected():
                cursor = conn.cursor()
                cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                                (username VARCHAR(50) PRIMARY KEY, password VARCHAR(50))''')
                conn.commit()
                print("MySQL database initialized successfully.")
        except Error as e:
            print(f"Error initializing MySQL database: {e}")
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()

    def connect_db(self):
        """Connect to the MySQL database."""
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",  # Add your MySQL password here if required
                database="geography_db"
            )
            return conn
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to connect: {e}")
            return None

    def center_window(self, win, width, height):
        screen_width = win.winfo_screenwidth()
        screen_height = win.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        win.geometry(f"{width}x{height}+{x}+{y}")

    def fade_in(self, window, alpha=0.0):
        if alpha < 1.0:
            alpha += 0.05
            window.attributes("-alpha", alpha)
            self.root.after(10, lambda: self.fade_in(window, alpha))
        else:
            window.attributes("-alpha", 1.0)

    def animate_card(self, widget, y_pos=600):
        def step():
            nonlocal y_pos
            if y_pos > 50:
                y_pos -= 5
                widget.place_configure(y=y_pos)
                self.root.after(20, step)
            else:
                widget.place_configure(y=50)
        step()

    def clear_frame(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def create_card(self, title, icon, action_btn_text, action_btn_command, switch_text, switch_btn_text, switch_btn_command):
        card = tk.Frame(self.root, bg="#0C2340")
        card.place(x=50, width=400, height=450)
        self.animate_card(card)

        tk.Label(card, text=icon, font=("Arial", 30), bg="#0C2340", fg="white").pack(pady=(30, 5))
        tk.Label(card, text=title, font=("Helvetica", 20, "bold"), bg="#0C2340", fg="white").pack(pady=(0, 20))

        username_entry = tk.Entry(card, font=("Helvetica", 12), width=30, bd=1, relief="solid")
        username_entry.pack(pady=10)
        password_entry = tk.Entry(card, show="*", font=("Helvetica", 12), width=30, bd=1, relief="solid")
        password_entry.pack(pady=10)

        login_btn = tk.Button(card, text=action_btn_text, font=("Helvetica", 12, "bold"), bg="#1E90FF", fg="white",
                              width=25, height=1, command=lambda: action_btn_command(username_entry.get(), password_entry.get()))
        login_btn.pack(pady=20)
        login_btn.bind("<Enter>", lambda e: login_btn.config(bg="#4682B4"))
        login_btn.bind("<Leave>", lambda e: login_btn.config(bg="#1E90FF"))

        tk.Label(card, text=switch_text, bg="#0C2340", fg="white").pack(pady=(20, 5))
        tk.Button(card, text=switch_btn_text, bg="gray25", fg="white", width=15, command=switch_btn_command).pack()

    def show_login(self):
        self.clear_frame()
        self.create_card(
            title="Login", icon="🔐", action_btn_text="LOGIN", action_btn_command=self.login_user,
            switch_text="Don't have an account?", switch_btn_text="SIGN UP", switch_btn_command=self.show_signup
        )

    def show_signup(self):
        self.clear_frame()
        self.create_card(
            title="Sign Up", icon="📝", action_btn_text="SIGN UP", action_btn_command=self.signup_user,
            switch_text="Already have an account?", switch_btn_text="LOGIN", switch_btn_command=self.show_login
        )

    def login_user(self, username, password):
        if not username or not password:
            messagebox.showwarning("Warning", "All fields are required!")
            return
        conn = self.connect_db()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
                result = cursor.fetchone()
                if result:
                    messagebox.showinfo("Success", f"Welcome, {username}!")
                    self.root.destroy()
                    MainMapPage()
                else:
                    messagebox.showerror("Failed", "Invalid username or password.")
            except Error as e:
                messagebox.showerror("Database Error", f"Error querying database: {e}")
            finally:
                if conn.is_connected():
                    cursor.close()
                    conn.close()

    def signup_user(self, username, password):
        """Handle user signup by adding to the MySQL database."""
        if not username or not password:
            messagebox.showerror("Error", "Please enter username and password.")
            return
        
        conn = self.connect_db()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
                conn.commit()
                messagebox.showinfo("Success", "Sign up successful! Please log in.")
                self.show_login()
            except mysql.connector.errors.IntegrityError:
                messagebox.showerror("Error", "Username already exists.")
            except Error as e:
                messagebox.showerror("Error", f"Database error: {e}")
            finally:
                if conn.is_connected():
                    cursor.close()
                    conn.close()

    def on_closing(self):
        self.root.quit()
        self.root.destroy()

class MainMapPage:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Main Menu")
        self.center_window(self.root, 900, 550)
        self.root.configure(bg="#06142E")
        self.root.resizable(False, False)

        world_card = tk.Frame(self.root, bg="#0C2340", width=400, height=450)
        world_card.place(x=50, y=50)
        self.animate_card(world_card)
        try:
            world_img = Image.open("world_map.jpg").resize((300, 200), Image.Resampling.LANCZOS)
            self.world_photo = ImageTk.PhotoImage(world_img)
            tk.Label(world_card, image=self.world_photo, bg="#0C2340").pack(pady=(30, 10))
        except Exception as e:
            tk.Label(world_card, text="Image Not Found", bg="#0C2340", fg="#E74C3C").pack(pady=(30, 10))
        tk.Label(world_card, text="World Map", font=("Helvetica", 20, "bold"), bg="#0C2340", fg="white").pack(pady=5)
        world_btn = tk.Button(world_card, text="Explore Continents", font=("Helvetica", 12, "bold"), bg="#1E90FF", fg="white",
                              width=25, command=self.open_world_map)
        world_btn.pack(pady=20)
        world_btn.bind("<Enter>", lambda e: world_btn.config(bg="#4682B4"))
        world_btn.bind("<Leave>", lambda e: world_btn.config(bg="#1E90FF"))

        india_card = tk.Frame(self.root, bg="#0C2340", width=400, height=450)
        india_card.place(x=535, y=50)
        self.animate_card(india_card)
        try:
            india_img = Image.open("india_map.jpg").resize((300, 200), Image.Resampling.LANCZOS)
            self.india_photo = ImageTk.PhotoImage(india_img)
            tk.Label(india_card, image=self.india_photo, bg="#0C2340").pack(pady=(30, 10))
        except Exception as e:
            tk.Label(india_card, text="Image Not Found", bg="#0C2340", fg="#E74C3C").pack(pady=(30, 10))
        tk.Label(india_card, text="India Map", font=("Helvetica", 20, "bold"), bg="#0C2340", fg="white").pack(pady=5)
        india_btn = tk.Button(india_card, text="Explore India", font=("Helvetica", 12, "bold"), bg="#1E90FF", fg="white",
                              width=25, command=self.open_india_map)
        india_btn.pack(pady=20)
        india_btn.bind("<Enter>", lambda e: india_btn.config(bg="#4682B4"))
        india_btn.bind("<Leave>", lambda e: india_btn.config(bg="#1E90FF"))

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def center_window(self, win, width, height):
        screen_width = win.winfo_screenwidth()
        screen_height = win.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        win.geometry(f"{width}x{height}+{x}+{y}")

    def animate_card(self, widget, y_pos=600):
        def step():
            nonlocal y_pos
            if y_pos > 50:
                y_pos -= 5
                widget.place_configure(y=y_pos)
                self.root.after(20, step)
            else:
                widget.place_configure(y=50)
        step()

    def open_world_map(self):
        self.root.destroy()
        WorldMapPage()

    def open_india_map(self):
        self.root.destroy()
        IndiaMapPage()

    def on_closing(self):
        self.root.quit()
        self.root.destroy()

class WorldMapPage:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("World Map")
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg="white")
        self.chat_window = None

        try:
            self.world_map = Image.open("world_map.jpg")
        except Exception as e:
            messagebox.showerror("Error", f"World Map Image Not Found! {str(e)}")
            self.root.destroy()
            return

        self.coordinates_label = tk.Label(self.root, text="Coordinates: ", font=("Helvetica", 20, "bold"), fg="#2C3E50", bg="white")
        self.coordinates_label.pack(side=tk.TOP, pady=5)

        self.canvas = tk.Canvas(self.root, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.update_map_image()

        self.canvas.bind("<Motion>", self.show_coordinates)
        self.canvas.bind("<Button-1>", self.check_coordinates)

        try:
            chatbot_icon = Image.open("chatbot_icon.png").resize((50, 50), Image.Resampling.LANCZOS)
            self.chatbot_photo = ImageTk.PhotoImage(chatbot_icon)
            tk.Button(self.root, image=self.chatbot_photo, command=self.open_chatbot, bg="white", relief="raised", bd=2).pack(side=tk.RIGHT, pady=10, padx=100)
        except Exception as e:
            messagebox.showerror("Error", f"Chatbot Icon Not Found! {str(e)}")

        tk.Button(self.root, text="Back to Main Menu", bg="#2C3E50", fg="white", font=("Helvetica", 16, "bold"), 
                  command=self.go_back).pack(side=tk.BOTTOM, pady=10)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def update_map_image(self):
        try:
            self.world_map_resized = self.world_map.resize((self.root.winfo_screenwidth(), self.root.winfo_screenheight() - 100), 
                                                           Image.Resampling.LANCZOS)
            self.map_tk = ImageTk.PhotoImage(self.world_map_resized)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.map_tk)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to resize map image: {str(e)}")

    def show_coordinates(self, event):
        self.coordinates_label.config(text=f"Coordinates: X={event.x} Y={event.y}")

    def check_coordinates(self, event):
        x, y = event.x, event.y
        regions = {
            "Asia": [
                ((930, 105, 237, 40), "The Great Wall of China (China)", "Spanning over 13,000 miles, the Great Wall is one of the most iconic structures in the world, symbolizing China's historical efforts to defend against invasions. Why Famous: It is an engineering marvel and a UNESCO World Heritage Site, attracting millions of visitors annually.", "Great_wall_of_China.jpg"),
                ((935, 290, 115, 65), "Taj Mahal (India)", "This white marble mausoleum, built by Mughal Emperor Shah Jahan in memory of his wife Mumtaz Mahal, is considered one of the most beautiful buildings in the world. Why Famous: A UNESCO World Heritage Site, it is one of the New Seven Wonders of the World and a symbol of eternal love.", "Taj Mahal.jpg"),
                ((877, 184, 109, 100), "Mount Everest (Nepal/China Border)", "Standing at 8,848.86 meters (29,031.7 feet), Mount Everest is the highest peak in the world, located in the Himalayas along the Nepal-China border. It attracts mountaineers from around the world, symbolizing adventure and human endurance.", "Mount Everest.jpg"),
                ((870, 167, 132, 45), "Borobudur (Indonesia)", "Borobudur is a 9th-century Mahayana Buddhist temple in Central Java. It is the largest Buddhist temple in the world, adorned with thousands of relief panels and Buddha statues. A UNESCO World Heritage Site, Borobudur is an iconic pilgrimage site and a testament to Indonesia's rich cultural and religious history.", "Borobudur.jpg"),
                ((780, 250 , 80, 56), "Kyoto Temples (Japan)", "Kyoto is home to many ancient temples and shrines, including the Golden Pavilion (Kinkaku-ji), a Zen Buddhist temple known for its stunning gold leaf exterior. Kyoto's temples are a UNESCO World Heritage Site and symbolize Japan’s traditional culture, history, and peaceful aesthetics.", "Kyoto Temples.jpg"),
            ],
            "Europe": [
                ((660, 120, 100, 60 ), "Eiffel Tower (France)", "Located in Paris, the Eiffel Tower is a wrought-iron lattice tower designed by Gustave Eiffel. Standing 330 meters (1,083 feet) tall, it offers panoramic views of the city. As one of the most recognizable landmarks in the world, the Eiffel Tower symbolizes Paris and is a global icon of French culture and elegance.", "eiffel_tower.jpg"),
                ((750, 150, 80, 50), "Colosseum (Italy)", "The Colosseum is an ancient Roman amphitheater in the heart of Rome, built in 70-80 AD. It could hold up to 80,000 spectators and was used for gladiatorial contests and public spectacles. As a UNESCO World Heritage Site, the Colosseum is one of the greatest surviving monuments of ancient Rome and a symbol of Roman engineering and culture.", "collosseum.jpg"),
                ((640, 190, 100, 30), "Acropolis of Athens (Greece)", "The Acropolis is a hill in Athens crowned by ancient monuments, most notably the Parthenon, a temple dedicated to the goddess Athena, built in the 5th century BC. As a UNESCO World Heritage Site, the Acropolis is a symbol of ancient Greek civilization, democracy, and architectural achievement.", "Acropolis of Athens.jpg"),
                ((760, 205, 80, 40), "Stonehenge (United Kingdom)", "Located in Wiltshire, England, Stonehenge is a prehistoric stone circle dating back over 4,000 years. Its purpose remains a mystery, though it may have been used for religious or astronomical purposes. As one of the most famous prehistoric sites in the world, Stonehenge is a UNESCO World Heritage Site and a symbol of ancient British history and mystery.", "Stonehenge.jpg"),
            ],
            "Australia": [
                ((1190, 500, 80, 50), "Sydney Opera House (New South Wales)", "Located on Sydney’s Bennelong Point, the Sydney Opera House is a multi-venue performing arts center with its iconic sail-shaped roof, designed by Danish architect Jørn Utzon. One of the most distinctive and famous buildings in the world, the Sydney Opera House is a UNESCO World Heritage Site and a symbol of modern Australia.", "Sydney Opera House.jpg"),
                ((1300, 458, 85, 100), "Great Barrier Reef (Queensland)", "The Great Barrier Reef, located off the coast of Queensland, is the world's largest coral reef system, spanning over 2,300 kilometers. It is home to diverse marine life, including over 1,500 species of fish. As the world’s largest coral reef, it’s a UNESCO World Heritage Site and one of the seven natural wonders of the world, attracting millions of visitors annually for snorkeling and diving.", "Great Barrier Reef.jpg"),
            ],
            "South America": [
                ((235, 373, 200, 100), "Machu Picchu (Peru)", "Machu Picchu is an ancient Incan city perched high in the Andes Mountains. Built in the 15th century, it was abandoned and later rediscovered in 1911 by Hiram Bingham. As a UNESCO World Heritage Site and one of the New Seven Wonders of the World, Machu Picchu is renowned for its breathtaking location and the mystery surrounding its purpose.", "Machu Picchu.jpg"),
                ((260, 490, 150, 160), "Christ the Redeemer (Brazil)", "Christ the Redeemer is a colossal statue of Jesus Christ located atop Mount Corcovado in Rio de Janeiro. Standing at 30 meters tall (98 feet), it overlooks the city with open arms. This iconic statue is a symbol of Christianity around the world and one of the New Seven Wonders of the World. It's a must-see landmark for visitors to Brazil.", "Christ the Redeemer.jpg"),
            ],
            "North America": [
                ((69, 132, 250, 100), "Statue of Liberty (USA)", "The Statue of Liberty is a colossal neoclassical sculpture located on Liberty Island in New York Harbor. It was a gift from France to the United States in 1886, symbolizing freedom and democracy. This iconic symbol of liberty and immigration is one of the most recognizable landmarks in the world and a UNESCO World Heritage Site, representing freedom and opportunity to millions.", "Statue of Liberty.jpg"),
                ((127, 214, 100,120), "Grand Canyon (USA)", "The Grand Canyon, located in Arizona, is a massive gorge carved by the Colorado River over millions of years. It stretches about 277 miles in length and reaches depths of over a mile. It is one of the Seven Natural Wonders of the World and a UNESCO World Heritage Site, known for its stunning layered rock formations that reveal millions of years of geological history.", "Grand Canyon.jpg"),
                ((268, 94, 100, 50), "Grand Canyon (USA)", "The Grand Canyon, located in Arizona, is a massive gorge carved by the Colorado River over millions of years. It stretches about 277 miles in length and reaches depths of over a mile. It is one of the Seven Natural Wonders of the World and a UNESCO World Heritage Site, known for its stunning layered rock formations that reveal millions of years of geological history.", "Grand Canyon.jpg"),
            ],
            "Africa": [
                ((590, 255, 150, 120), "Serengeti National Park, Tanzania", "Famous for its annual Great Migration, the Serengeti is one of the most iconic safari destinations in the world. Visitors can witness millions of wildebeest, zebras, and gazelles journeying across the savannah, while also spotting Africa’s Big Five – lions, leopards, elephants, buffalo, and rhinos.", "Serengeti National Park.jpg"),
                ((675, 390, 130, 200), "Pyramids of Giza, Egypt", "As one of the Seven Wonders of the Ancient World, the Pyramids of Giza are among the most famous historical monuments. These ancient structures, including the Great Pyramid and the Sphinx, have stood for over 4,000 years and are a must-see for history enthusiasts.", "Pyramids of Giza.jpg"),
                ((746, 270, 50, 200), "Victoria Falls, Zambia/Zimbabwe", "One of the largest and most breathtaking waterfalls in the world, Victoria Falls is located on the border of Zambia and Zimbabwe. Known locally as The Smoke That Thunders, the falls drop from a height of 108 meters, creating a spectacular view and misty spray.", "Victoria Falls.jpg"),
            ]
        }

        for continent, locations in regions.items():
            for (rx, ry, rw, rh), title, description, img_path in locations:
                if rx <= x <= rx + rw and ry <= y <= ry + rh:
                    self.show_information_panel(title, description, img_path)
                    return
        messagebox.showinfo("Info", "No information available for this area.")

    def show_information_panel(self, title, description, image_path):
        self.info_window = tk.Toplevel(self.root)
        self.info_window.title(title)
        self.info_window.geometry("650x800")
        self.info_window.resizable(False, False)
        self.info_window.configure(bg="#0C2340")
        self.info_window.transient(self.root)

        main_frame = tk.Frame(self.info_window, bg="#0C2340", padx=10, pady=10)
        main_frame.pack(fill="both", expand=True)

        try:
            img = Image.open(image_path).resize((450, 250), Image.Resampling.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)
            tk.Label(main_frame, image=img_tk, bg="#0C2340").pack(pady=(5, 10))
            main_frame.image = img_tk
        except Exception as e:
            tk.Label(main_frame, text=f"Image not found: {str(e)}", bg="#0C2340", fg="#E74C3C", font=("Helvetica", 14)).pack(pady=(5, 10))

        tk.Label(main_frame, text=title, font=("Helvetica", 24, "bold"), fg="white", bg="#0C2340").pack(pady=5)
        desc_frame = tk.Frame(main_frame, bg="#1C3A70", padx=5, pady=5, bd=2, relief="solid")
        desc_frame.pack(padx=5, pady=5, fill="both", expand=True)
        tk.Label(desc_frame, text=description, font=("Helvetica", 14), fg="white", bg="#1C3A70", 
                 wraplength=470, justify="left").pack(padx=5, pady=5)

        button_frame = tk.Frame(main_frame, bg="#0C2340")
        button_frame.pack(pady=10)
        tk.Button(button_frame, text="Close", font=("Helvetica", 14, "bold"), bg="#1E90FF", fg="white", 
                  command=self.info_window.destroy).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Chatbot", font=("Helvetica", 14, "bold"), bg="#1E90FF", fg="white", 
                  command=lambda: self.open_chatbot_with_info(title, description)).pack(side=tk.LEFT, padx=5)

        self.info_window.grab_set()

    def open_chatbot_with_info(self, title, description):
        if self.chat_window and self.chat_window.winfo_exists():
            self.chat_window.destroy()
        self.chat_window = tk.Toplevel(self.info_window)
        self.chat_window.attributes("-topmost", True)
        initial_prompt = f"Provide a concise overview of {title} based on this context: {description}."
        ChatUI(self.chat_window, country=None, initial_prompt=initial_prompt, parent=self)

    def open_chatbot(self):
        if self.chat_window and self.chat_window.winfo_exists():
            self.chat_window.destroy()
        self.chat_window = tk.Toplevel(self.root)
        self.chat_window.attributes("-topmost", True)
        ChatUI(self.chat_window, country=None, parent=self)

    def go_back(self):
        self.root.destroy()
        MainMapPage()

    def on_closing(self):
        if self.chat_window and self.chat_window.winfo_exists():
            self.chat_window.destroy()
        self.root.quit()
        self.root.destroy()

class IndiaMapPage:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("India Map")
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg="white")
        self.chat_window = None

        try:
            self.india_map = Image.open("india_map.jpg")
        except Exception as e:
            messagebox.showerror("Error", f"India Map Image Not Found! {str(e)}")
            self.root.destroy()
            return

        self.coordinates_label = tk.Label(self.root, text="Coordinates: ", font=("Helvetica", 20, "bold"), fg="#2C3E50", bg="white")
        self.coordinates_label.pack(side=tk.TOP, pady=5)

        self.canvas = tk.Canvas(self.root, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.update_map_image()

        self.canvas.bind("<Motion>", self.show_coordinates)
        self.canvas.bind("<Button-1>", self.check_state_clicked)

        try:
            chatbot_icon = Image.open("chatbot_icon.png").resize((50, 50), Image.Resampling.LANCZOS)
            self.chatbot_photo = ImageTk.PhotoImage(chatbot_icon)
            tk.Button(self.root, image=self.chatbot_photo, command=self.open_chatbot, bg="white", relief="raised", bd=2).pack(side=tk.RIGHT, pady=10, padx=100)
        except Exception as e:
            messagebox.showerror("Error", f"Chatbot Icon Not Found! {str(e)}")

        tk.Button(self.root, text="Back to Main Menu", bg="#2C3E50", fg="white", font=("Helvetica", 16, "bold"), 
                  command=self.go_back).pack(side=tk.BOTTOM, pady=10)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def update_map_image(self):
        try:
            self.india_map_resized = self.india_map.resize((self.root.winfo_screenwidth(), self.root.winfo_screenheight() - 100), 
                                                           Image.Resampling.LANCZOS)
            self.map_tk = ImageTk.PhotoImage(self.india_map_resized)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.map_tk)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to resize map image: {str(e)}")

    def show_coordinates(self, event):
        self.coordinates_label.config(text=f"Coordinates: X={event.x} Y={event.y}")

    def check_state_clicked(self, event):
        x, y = event.x, event.y
        states = {
            "Maharashtra": ((304, 410, 274, 57), "Maharashtra", "Anand Ashok Bansode (Born on 29th July 1985) from Maharashtra, India lead the 1st Indian team of 10 climbers who climbed the 10 highest peaks of the Australian continent - the Aussie10 Expedition. He played (Guitar) Indian National Anthem on the top of the highest peak in the Australian continent - Mount Kosciuszko. The expedition was completed from 1st November 2014 to 4th November 2014. This expedition was organised by Mission Outdoors.", "maharashtra.jpg"),
            "Uttarakhand": ((594, 156, 74, 36), "Uttarakhand", "Labhanshu Sharma (Born on 27th August 1998) From Uttrakhand, India achieved the record “Heaviest Vehicle pulled with Body”. He pulled a 20-ton truck with his body up to 10 meters in Georgia on 20th December 2017.", "Uttarakhand.jpg"),
            "Madhya Pradesh": ((430, 319, 295, 49), "Madhya Pradesh", "Shivani Solanki (Born on 13th March 2002) from Madhya Pradesh, India achieved the record “Smallest Painting of Lord Vishnu's Dashavatar on Betel Nut”. She composed the 6 avatars of Lord Vishnu on the bottom and 4 on top circularly and created paintings of all 10 Avatars of Lord Vishnu. All paintings were made with watercolour, acrylic colour, and betel nut on 15th April 2024 at Ujjain, Madhya Pradesh, India.", "Madhya Pradesh.jpg"),
            "Punjab": ((426, 142, 85, 26), "Punjab", "Raman Kumar (born on 25th October 1977) from Punjab, India has created the record of “Most Bottles Broken by Hands in 30 Seconds He broke 18 out of 30 soft drink bottles with his bare hands in 30 Seconds, on 24th August 2014 on the occasion of Unique World Records - Annual Award Distribution Function held at Hotel Bahia Fort, Bathinda (Punjab) on 24th August 2014.", "Punjab.jpg"),
            "West Bengal": ((1008, 316, 80, 37), "West Bengal", "Suvodeep Chatterjee (born on 8th July 1993) from West Bengal, India has created “World’s Largest Painting by Mouth” measuring 10.668 m (35 ft.) in width and 7.8 m (25.6 ft.) in height. The painting is entitled “Save the World”, where all the continents and religions raise their hands to save the world and make it green from the dark pollution. The painting work started at Ganguly Para, on 31st October 2013 and finished on 10th November 2013.", "West Bengal.jpg"),
            "Rajasthan": ((282, 206, 175, 78), "Rajasthan", "Anshul vijayvargia (Born on 27th October 1993) and Aman soni (Born on 25th August 1997) from Rajasthan, India has created the record of “Longest Distance Covered with Reverse Skating”. They covered 35 kilometres in 1 hour 35 minutes from Ram Dham to Gangrar Toll Naka Bhilwada, Rajasthan on 3rd July 2014.", "Rajasthan.jpg"),
            "Telangana": ((553, 438, 107, 37), "Telangana", "Rajashekar Konka (Born on 5th April 1992) From Telangana India achieved the record “Most Temples Made by Chalk Pieces”. He created 12 Temples of different places of India with chalk pieces varying length from 1 cm to 24 cm, breadth from 4 cm to 32 cm and height from 6 cm to 19 cm. He started his work in 2010 and Finished in 2014", "Telangana.jpg"),
            "Andhra Pradesh": ((550, 520, 132, 47), "Andhra Pradesh", "Chakradhari Kotcherla (born on 27th April 1976) working as a Pharmacist at Primary Health Centre, Vetlapalem from Andhra Pradesh, India has created the smallest idol of the Eiffel Tower using pencil lead measuring height 11 mm in 3 hours. It was exhibited at H.No: 11-1-8, Opp. Govt. Veterinary Hospital, Mehar Complex, Ismayil Nagar, Samalkot, Andhra Pradesh on 29th January 2013.", "Andhra Pradesh.jpg"),
            "Tamil Nadu": ((499, 608, 146, 64), "Tamil Nadu", "Bhargav Vasu (Born on 19th July 2005) Student of Anima World of Arts Institute from Chennai, Tamil Nadu, India achieved the record Most Live Portrait by Pen in 13 Hours. He Completed 165 Live Portraits in 13 Hours, started at 10:00 am and finished at 11:00 pm at Grand Square, Velachery Main Road, Chennai, Tamil Nadu, India to create Suicide Prevention Awareness for the public. The Record Event was Organized by Sadhanai Sigaram Creations in Associate with Grand Square", "Tamil Nadu.jpg"),
            "Gujarat": ((135, 313, 183, 59), "Gujarat", "Yug Italiya (Born on 19th August 2000) from Gujarat, India created the record of “Youngest to Cover Maximum Distance on Cycle”, travelled from Manali to Leh 515 kilometres in 10 days average of 50 kilometres per day including 4 highest passes on a bicycle. He started travelling at 7 am on 23rd June 2014 and ended at 3 pm Khar Dungla (Leh) on 1st July 2014 along with 13 people.", "Gujarat.jpg"),
            "Bihar": ((880, 260, 146, 35), "Bihar", "Abid Hasan (Born on 5th August 1998) from Bihar, India has created the record by becoming “Youngest Founder of an International Foundation” known as India Mauritius Foundation for increased better mutual understanding and relation between Republic of India and Republic of Mauritius as of 30th April 2014.", "Bihar.jpg"),
            "New Delhi": ((520, 196, 18, 9), "New Delhi", "Constable Shashi Kumara A and Constable Sudhakar, Members of the Motorcycle team (Janbaz) of Border Security Force created a World Record of “Handsfree Side Riding while Sitting on Bike (Group Event)”. They rode Royal Enfield 350 CC bike while Sitting with both legs on the same Side and Covered 105.2 km in 03 Hours 13 Minutes and 27 Seconds without breaks (interval) on 15th October 2018 from 03:08 PM to 06:21:27 PM at 25 Bn BSF, RK Wadhwa Parade Ground Chhawla Camp, New Delhi.", "New_Delhi.jpg"),
            "Jharkhand": ((870, 315, 93, 32), "Jharkhand", "Ayush Srivastava (born on 6th January 1992), Pawan Kumar Ashish (born on 16th December 1992), Rakesh Kumar Upadhyay (born on 8th August 1993) and Navin Kumar (born on 28th October 1992), from Jharkhand, India have created Longest Bridge Model Made by Popsicle Sticks. The bridge was made of 17922 popsicle sticks having a length of 21.5 m, a width of 22 cm and a height of 35 cm from top to bottom. The project was started on 1st March 2013 and finished on 14th March 2013.", "Jharkhand.jpg"),
            "Haryana": ((470, 184, 36, 27), "Haryana", "Himmat Bhardwaj (born on 1st November 1988) from Haryana, India created the record by “Reciting Periodic Table”. He demonstrated his skill on 15th May 2013, memorised the entire Periodic Table and then recollected all the 118 elements in the forward order in 36 seconds only.", "Haryana.jpg"),
            "Kerala": ((453, 596, 30, 130), "Kerala", "Josekutty Panackal (born on 11th August 1977) of Kerala, India has created a record of Most News Images Shot by an Individual. He has a collection of 45,496 news images as on 1st June 2012. All images were shot by him for 11 years. He has filed all these images along with related data like caption, Keyword, date, place etc. into The Malayala Manorama archives, making them retrievable anytime, anywhere from The Malayala Manorama Printing and Publishing company office network.", "Kerela.jpg"),
            "Arunachal Pradesh": ((1253, 195, 173, 39), "Arunachal Pradesh", "Tawang district in Arunachal Pradesh holds the Guinness World Record for the largest helmet sentence,On November 20, 2022, over 2,350 helmets were used to form the word Jai Hind at the Gyalwa Tsangyang Gyatso high-altitude stadium. The event was organized by the Amazing Namaste Foundation and the state government.", "Arunachal Pradesh.jpg"),
            "Assam": ((1170, 244, 171, 18), "Assam", "Rajdeep Kashyap, a Botany undergraduate student from Nalbari College in Assam, has set a new Guinness World Record in the “fastest book writing” category ,writes 84-page book in 9hrs, sets Guinness World.", "Assam.jpg"),
            "Chhattisgarh": ((701, 388, 86, 46), "Chhattisgarh", "Aaditya Pratap Singh (DOB 12.01.1988) of Raipur, Chhattisgarh has designed the largest screwdriver in the world, measuring 20 feet & 11.5 inches in length, shaft is 18 feet & 3 inches long ( 1.5 inches diameter) handle length 2ft 8.5 inches (9 inches Diameter) and weighing 6 kgs, made by SS, fibre and steel plates material, It was displayed at Magneto the mall on 26 August 2015. It takes approx 30 man-hours to make it.", "Chhattisgarh.jpg"),
            "Goa": ((338, 512, 28, 12), "Goa", "Vaibhav Rajamani: In 2023, Rajamani broke the record for cycling 151.3 km in 7 hours and 18 minutes without touching the handlebars. Rajamani is a cycling enthusiast who became passionate about setting records after noting them down online at age 16", "Goa.jpg"),
            "Odisha": ((850, 370, 180, 39), "Odisha", "In February 2017, Sudarsan Pattnaik, a renowned sand artist from Odisha, India, set a world record by creating the tallest sandcastle ever recorded. This monumental structure, built on Puri Beach, reached a height of 14.84 meters (48 feet 8 inches), surpassing the previous record held by American artist Ted Siebert. The record-breaking sculpture was constructed during the International Sand Art Festival, an event supported by the Odisha Tourism Department. Pattnaik's creation carried the message 'World Peace'.", "odisha.jpg"),
            "Manipur": ((1315, 281, 50, 29), "Manipur", "The most one arm knuckle push ups in one minute, alternating arms (male) is 67, and was achieved by Thounaojam Niranjoy Singh (India) in Imphal, Manipur, India, on 3 February 2020.Thounaojam was inspired to attempt this Guinness World Records title when he saw what the current record was and believed he could achieve this. Thounaojam trained in the mornings from 5am-7am and from 6pm-9pm.This became his new daily exercise.", "manipur.jpeg"),
            "Nagaland": ((1357, 246, 44, 22), "Nagaland", "The largest traditional Konyak dance consists of 4,687 participants, and was achieved by The Konyak Union (India) in Mon, Nagaland, India, on 5 April 2019. The purpose of attempting this record was to showcase the tradition of the Konyak people and to take a step towards conserving their cultural heritage through traditional dance and music.", "nagaland.jpg"),
            "Tripura": ((1227, 310, 20, 20), "Tripura", "Indian folk musician Thanga Darlong (b. 20 July 1920) was 98 years 319 days old when he was presented with the Padma Shri civilian award on 4 June 2019. Born at Muruai village, in the north-eastern state of Tripura, Darlong is celebrated as the last tribal musician to play the rosem, a flute-like instrument made from wood, bamboo and a traditional water pot used by Tripura’s Darlong tribe. The prestigious award was conferred at a ceremony in Kailashahar, Tripura, together with a prize of 1.5 lakh rupees (£1,600; $2,113).", "tripura.jpg"),
            "Meghalaya": ((1155, 265, 125, 21), "Meghalaya", "Fluorescence is the absorption of UV light resulting in the emission of light of longer wavelengths (e.g. the various colours of visible light). The most fluorescent carnivorous plant is the Khasi Hills pitcher plant Nepenthes khasiana, which is almost entirely restricted to the Khasi Hills of Meghalaya State in northeastern India.", "meghalaya.jpg"),
            "Karnataka": ((415, 480, 77, 95), "Karnataka", "The record for the most people on one moving motorcycle was set by The ASC Tornadoes Motorcycle Team of the Indian Army Corps of Signals. This impressive feat took place on 19 November 2017 at Yelahanka Air Force Station in Bengaluru, Karnataka, India. In this achievement, a total of 58 individuals successfully balanced themselves on a single moving motorcycle, a Royal Enfield 500cc, covering a distance of 1,200 meters without any of the riders falling off.", "karnataka.jpg"),
            "Ladakh": ((475, 40, 214, 40), "Ladakh", "Overlooking the Khardung La mountains, a very special piano performance took place.Davide Locatelli (Italy), a professional pianist and musician, played several piano pieces to break the record for the highest altitude grand piano performance. This piano performance took place at 5,375 metres (17,634 ft) above sea level on 29 June 2023.", "ladakh.jpg"),
            "Jamu & Kashmir": ((381, 68, 77, 47), "Jamu & Kashmir", "The largest Kashmir Sapphire named “The Spirit of Kashmir” is 150.13 carat (30.026 g) and was achieved by Goldiama LLC (UAE), in Dubai, UAE, on 10 November 2023. A Kashmir Sapphire gemstone is highly prized for its exceptional intense and vivid blue hue described as velvety or cornflower blue. The Spirit of Kashmir is a wholly natural gem and untreated other than having been Cushion cut. It measures 29.19 mm X 25.09 mm X 21.72 mm.", "jammu.jpg"),
            "Himachal Pradesh": ((505, 110, 90, 35), "Himachal Pradesh", "Fastest on foot journey of the Manali-Leh highway (male) is 4 days, 21 hr, 13 min, and was achieved by Mahendra Mahajan (India), in Leh, Himachal Pradesh, India, on 7 July 2022. Mahendra is an ultracyclist, a marathon runner and has summited Mt. Everest. He is fond of the Himalayan mountains, so when he learned of this record title, he 'couldn't resist' attempting it.", "himachal_pradesh.jpg"),
            "Uttar Pradesh": ((610, 220, 207, 90), "Uttar Pradesh", "The highest archery score on roller skates is 32 points and was achieved by Arjun Ajay Singh (India) in Varanasi, Uttar Pradesh, India on 5 August 2020. Arjun has been skating and practicing archery since three years old. Arjun was inspired to attempt for this record title by his father. Arjun has attempted archery Guinness World Records titles in the past and would like to continue attempting record titles in this field.", "uttar_pradesh.jpg")  
        }

        for state, ((rx, ry, rw, rh), title, description, img_path) in states.items():
            if rx <= x <= rx + rw and ry <= y <= ry + rh:
                self.show_state_info(title, description, img_path)
                return
        messagebox.showinfo("Info", "No state information available for this area.")

    def show_state_info(self, state_name, info, image_path):
        self.info_window = tk.Toplevel(self.root)
        self.info_window.title(state_name)
        self.info_window.geometry("650x750")
        self.info_window.resizable(False, False)
        self.info_window.configure(bg="#0C2340")
        self.info_window.transient(self.root)

        main_frame = tk.Frame(self.info_window, bg="#0C2340", padx=10, pady=10)
        main_frame.pack(fill="both", expand=True)

        try:
            img = Image.open(image_path).resize((450, 250), Image.Resampling.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)
            tk.Label(main_frame, image=img_tk, bg="#0C2340").pack(pady=(5, 10))
            main_frame.image = img_tk
        except Exception as e:
            tk.Label(main_frame, text=f"Image not found: {str(e)}", bg="#0C2340", fg="#E74C3C", font=("Helvetica", 14)).pack(pady=(5, 10))

        tk.Label(main_frame, text=state_name, font=("Helvetica", 24, "bold"), fg="white", bg="#0C2340").pack(pady=5)
        desc_frame = tk.Frame(main_frame, bg="#1C3A70", padx=5, pady=5, bd=2, relief="solid")
        desc_frame.pack(padx=5, pady=5, fill="both", expand=True)
        tk.Label(desc_frame, text=info, font=("Helvetica", 14), fg="white", bg="#1C3A70", 
                 wraplength=450, justify="left").pack(padx=5, pady=5)

        button_frame = tk.Frame(main_frame, bg="#0C2340")
        button_frame.pack(pady=10)
        tk.Button(button_frame, text="Close", font=("Helvetica", 14, "bold"), bg="#1E90FF", fg="white", 
                  command=self.info_window.destroy).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Chatbot", font=("Helvetica", 14, "bold"), bg="#1E90FF", fg="white", 
                  command=lambda: self.open_chatbot_with_info(state_name, info)).pack(side=tk.LEFT, padx=5)

        self.info_window.grab_set()

    def open_chatbot_with_info(self, title, description):
        if self.chat_window and self.chat_window.winfo_exists():
            self.chat_window.destroy()
        self.chat_window = tk.Toplevel(self.info_window)
        self.chat_window.attributes("-topmost", True)
        initial_prompt = f"Provide a concise overview of {title} based on this context: {description}."
        ChatUI(self.chat_window, country="India", initial_prompt=initial_prompt, parent=self)

    def open_chatbot(self):
        if self.chat_window and self.chat_window.winfo_exists():
            self.chat_window.destroy()
        self.chat_window = tk.Toplevel(self.root)
        self.chat_window.attributes("-topmost", True)
        ChatUI(self.chat_window, country="India", parent=self)

    def go_back(self):
        self.root.destroy()
        MainMapPage()

    def on_closing(self):
        if self.chat_window and self.chat_window.winfo_exists():
            self.chat_window.destroy()
        self.root.quit()
        self.root.destroy()

class ChatUI:
    def __init__(self, root, country=None, initial_prompt=None, parent=None):
        self.root = root
        self.root.title("Responsive Chatbot")
        self.root.geometry("500x800")
        self.root.configure(bg="#0C2340")
        self.root.resizable(False, False)
        self.country = country
        self.response_queue = queue.Queue()
        self.typing_bubble = None
        self.conversation_history = []
        self.parent = parent
        self.retry_pending = False

        self.create_header()
        self.create_chat_area()
        self.create_input_area()
        self.create_rating_area()
        self.add_welcome_message()

        if initial_prompt:
            self.add_user_message(initial_prompt)
            self.send_btn.config(state="disabled")
            self.show_typing_indicator()
            threading.Thread(target=self.fetch_bot_reply, args=(initial_prompt,), daemon=True).start()

        self.root.after(100, self.entry.focus_set)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.after(10, self.check_response_queue)

    def create_header(self):
        header = tk.Frame(self.root, bg="#06142E", height=50)
        header.pack(fill="x", pady=5)
        tk.Label(header, text="SMART CHATBOT", font=("Helvetica", 16, "bold"), bg="#06142E", fg="white").pack(side="left", padx=10)
        tk.Button(header, text="Clear", font=("Helvetica", 12), bg="#FF6347", fg="white", command=self.clear_conversation).pack(side="right", padx=10)

    def create_chat_area(self):
        self.chat_frame = tk.Frame(self.root, bg="#0C2340")
        self.chat_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.canvas = tk.Canvas(self.chat_frame, bg="#0C2340", highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.chat_frame, orient="vertical", command=self.canvas.yview, bg="#1C3A70")
        self.scrollable_frame = tk.Frame(self.canvas, bg="#0C2340")

        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.root.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        if self.canvas and self.canvas.winfo_exists():
            self.canvas.yview_scroll(-1 * int(event.delta / 120), "units")

    def create_input_area(self):
        input_frame = tk.Frame(self.root, bg="#0C2340")
        input_frame.pack(fill="x", pady=5, padx=5)

        self.entry = tk.Entry(input_frame, font=("Helvetica", 13), bg="#1C3A70", fg="white", relief="flat", insertbackground="white")
        self.entry.pack(side="left", fill="x", expand=True, padx=5, ipady=5)
        self.entry.bind("<Return>", lambda e: self.send_msg())

        self.send_btn = tk.Button(input_frame, text="➤", font=("Helvetica", 14), bg="#1E90FF", fg="white", 
                                  relief="flat", command=self.send_msg)
        self.send_btn.pack(side="left", padx=5)

    def create_rating_area(self):
        rating_frame = tk.Frame(self.root, bg="#0C2340")
        rating_frame.pack(pady=5)
        tk.Label(rating_frame, text="Please rate us", font=("Helvetica", 11), bg="#0C2340", fg="lightgray").pack()
        self.stars = []
        for i in range(5):
            star = tk.Label(rating_frame, text="☆", font=("Helvetica", 20), fg="#FFD700", bg="#0C2340")
            star.pack(side="left", padx=2)
            star.bind("<Button-1>", lambda e, i=i: self.rate(i))
            self.stars.append(star)

    def rate(self, index):
        for i, star in enumerate(self.stars):
            star["text"] = "★" if i <= index else "☆"

    def add_welcome_message(self):
        self.add_bot_message("Hi! I'm your smart chatbot. Ask me about any place or anything else!")

    def send_msg(self):
        msg = self.entry.get().strip()
        if msg:
            self.add_user_message(msg)
            self.entry.delete(0, tk.END)
            self.send_btn.config(state="disabled")
            self.show_typing_indicator()
            threading.Thread(target=self.fetch_bot_reply, args=(msg,), daemon=True).start()

    def show_typing_indicator(self):
        if self.typing_bubble:
            self.typing_bubble.destroy()
        self.typing_bubble = tk.Label(self.scrollable_frame, text="Thinking...", wraplength=380, bg="#1C3A70", fg="white", 
                                      font=("Helvetica", 11), padx=5, pady=5, justify="left", anchor="w")
        self.typing_bubble.pack(anchor="w", pady=5, padx=5)
        self.canvas.yview_moveto(1.0)

    def fetch_bot_reply(self, user_input):
        try:
            messages = [{"role": "user", "content": msg} for msg, _ in self.conversation_history if msg] + \
                      [{"role": "assistant", "content": resp} for _, resp in self.conversation_history if resp] + \
                      [{"role": "user", "content": user_input}]
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                timeout=5
            )
            bot_response = completion.choices[0].message.content
            words = bot_response.split()
            if len(words) > 150:
                bot_response = " ".join(words[:150]) + " For more details, ask me again!"
            self.response_queue.put(bot_response)
        except OpenAIError as e:
            if "timeout" in str(e).lower():
                self.response_queue.put("Error: Request timed out. Click 'Try Again' below to retry.")
                self.show_retry_button()
            else:
                self.response_queue.put(f"Error: Could not get response due to {str(e)}. Try again.")
        except Exception as e:
            self.response_queue.put(f"Error: Unexpected issue - {str(e)}. Try again.")

    def show_retry_button(self):
        if not self.retry_pending:
            self.retry_pending = True
            retry_btn = tk.Button(self.scrollable_frame, text="Try Again", font=("Helvetica", 12, "bold"), bg="#1E90FF", fg="white",
                                 command=self.retry_last_request)
            retry_btn.pack(anchor="w", pady=5, padx=5)
            self.canvas.yview_moveto(1.0)

    def retry_last_request(self):
        if self.retry_pending and self.conversation_history:
            last_user_msg = self.conversation_history[-1][0]
            if last_user_msg:
                self.add_user_message(last_user_msg)
                self.send_btn.config(state="disabled")
                self.show_typing_indicator()
                threading.Thread(target=self.fetch_bot_reply, args=(last_user_msg,), daemon=True).start()
                self.retry_pending = False
                for widget in self.scrollable_frame.winfo_children():
                    if widget["text"] == "Try Again":
                        widget.destroy()

    def check_response_queue(self):
        try:
            if not self.response_queue.empty():
                response = self.response_queue.get_nowait()
                if self.typing_bubble:
                    self.typing_bubble.destroy()
                    self.typing_bubble = None
                self.add_bot_message(response)
                self.send_btn.config(state="normal")
        except queue.Empty:
            pass
        self.root.after(10, self.check_response_queue)

    def add_bot_message(self, msg):
        bubble = tk.Label(self.scrollable_frame, text=msg, wraplength=380, bg="#1C3A70", fg="white", 
                          font=("Helvetica", 11), padx=5, pady=5, justify="left", anchor="w")
        bubble.pack(anchor="w", pady=5, padx=5)
        self.conversation_history.append(("", msg))
        self.canvas.yview_moveto(1.0)

    def add_user_message(self, msg):
        bubble = tk.Label(self.scrollable_frame, text=msg, wraplength=380, bg="#4682B4", fg="white", 
                          font=("Helvetica", 11), padx=5, pady=5, justify="right", anchor="e")
        bubble.pack(anchor="e", pady=5, padx=5)
        self.conversation_history.append((msg, ""))
        self.canvas.yview_moveto(1.0)

    def clear_conversation(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.conversation_history = []
        self.retry_pending = False
        self.add_welcome_message()

    def on_closing(self):
        self.root.unbind_all("<MouseWheel>")
        if self.parent and self.parent.chat_window == self.root:
            self.parent.chat_window = None
        self.root.destroy()

if __name__ == "__main__":
    app = InteractiveGeographyMap()
