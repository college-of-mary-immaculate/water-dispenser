import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from PIL import Image, ImageTk 

def triangular_membership(x, a, b, c):
    if x <= a or x >= c:
        return 0
    elif a < x <= b:
        return (x - a) / (b - a)
    elif b < x < c:
        return (c - x) / (c - b)
    return 0

class WaterDispenser:
    def __init__(self):
        self.current_cold_temp = 15  
        self.current_hot_temp = 40   
        self.water_level = 100       
        self.ambient_temp = 25       
        self.heating_element = 0     
        self.cooling_element = 0     
        self.min_cold_temp = 5       
        self.max_hot_temp = 100      

    def adjust_temperature(self, target_cold_temp, target_hot_temp):
        
        cold_too_cold = triangular_membership(self.current_cold_temp, 0, 5, target_cold_temp)
        cold_ideal = triangular_membership(self.current_cold_temp, target_cold_temp - 2, target_cold_temp, target_cold_temp + 2)
        cold_too_hot = triangular_membership(self.current_cold_temp, target_cold_temp, target_cold_temp + 5, 100)

        hot_too_cold = triangular_membership(self.current_hot_temp, 0, 40, target_hot_temp - 5)
        hot_ideal = triangular_membership(self.current_hot_temp, target_hot_temp - 5, target_hot_temp, target_hot_temp + 5)
        hot_too_hot = triangular_membership(self.current_hot_temp, target_hot_temp, target_hot_temp + 10, 100)

        if cold_too_hot > 0.5:
            self.cooling_element = 80
            self.heating_element = 0
        elif hot_too_cold > 0.5:
            self.heating_element = 80
            self.cooling_element = 0
        else:
            self.cooling_element = 0
            self.heating_element = 0

        self.current_cold_temp = max(self.min_cold_temp, self.current_cold_temp - self.cooling_element / 100.0)
        self.current_hot_temp = min(self.max_hot_temp, self.current_hot_temp + self.heating_element / 100.0)

    def check_water_level(self):
        if self.water_level > 50:
            return "Water level: Sufficient"
        elif 20 < self.water_level <= 50:
            return "Water level: Moderate"
        elif self.water_level <= 20:
            return "Water level: Low! Please refill soon."
        return "No water left! Please refill the bottle."

    def dispense_water(self, target_temp):
        if self.water_level == 0:
            return "No water left! Please refill the bottle."
        
        if self.current_cold_temp < target_temp < self.current_hot_temp:
            total_range = self.current_hot_temp - self.current_cold_temp
            hot_percentage = (target_temp - self.current_cold_temp) / total_range
            cold_percentage = 1 - hot_percentage
            
            # Calculate mixed temperature
            mixed_temp = (self.current_cold_temp * cold_percentage) + (self.current_hot_temp * hot_percentage)

            self.current_cold_temp += cold_percentage * 1.0  
            self.current_hot_temp -= hot_percentage * 1.0    

            self.reduce_water_level()  
            return f"Dispensing mixed water at {mixed_temp:.2f}°C"
        else:
            return f"Cannot dispense water at {target_temp:.2f}°C. Out of range."

    def reduce_water_level(self):
        self.water_level -= 1
        if self.water_level < 0:
            self.water_level = 0

    def refill_water(self):
        self.water_level = 100

class WaterDispenserApp:
    def __init__(self, root, dispenser):
        self.root = root
        self.dispenser = dispenser
        self.target_cold_temp = 8
        self.target_hot_temp = 85
        
        self.root.title("Water Dispenser Simulation")
        self.root.geometry("1080x507")  

        self.background_image = Image.open("wt.jpg")  
        self.background_image = self.background_image.resize((1080, 507))  
        self.background_photo = ImageTk.PhotoImage(self.background_image)  

        self.canvas = tk.Canvas(root, width=1080, height=507)
        self.canvas.pack()

        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.background_photo)

        center_x = 720  
        start_y = 100   

        
        self.cold_temp_label = tk.Label(root, text=f"Cold Water Temp: {self.dispenser.current_cold_temp:.2f}°C", bg='lightblue')
        self.cold_temp_label.place(x=center_x - 700, y=start_y)  
        
        self.hot_temp_label = tk.Label(root, text=f"Hot Water Temp: {self.dispenser.current_hot_temp:.2f}°C", bg='lightblue')
        self.hot_temp_label.place(x=center_x + 150, y=start_y)  

        self.water_level_label = tk.Label(root, text=f"Water Level: {self.dispenser.water_level}%", bg='lightblue')
        self.water_level_label.place(x=center_x - 250, y=start_y - 80)  

        self.cold_temp_scale = tk.Scale(root, from_=1, to=10, orient='vertical', length=200, fg='blue')
        self.cold_temp_scale.place(x=center_x - 600, y=start_y + 20)
        
        self.hot_temp_scale = tk.Scale(root, from_=1, to=10, orient='vertical', length=200, fg='red')
        self.hot_temp_scale.place(x=center_x + 250, y=start_y + 20)

        self.water_level_progress = ttk.Progressbar(root, orient='horizontal', length=200, mode='determinate')
        self.water_level_progress.place(x=center_x - 280, y=start_y - 60)

        self.target_temp_entry = tk.Entry(root, width=10)
        self.target_temp_entry.place(x=center_x - 250, y=start_y + 20)

        self.target_temp_button = tk.Button(root, text="Dispense Water", command=self.dispense_target_temp, width=20, bg="orange")
        self.target_temp_button.place(x=center_x - 250, y=start_y + 160)  

        self.refill_button = tk.Button(root, text="Refill Water", command=self.refill_water, width=20, bg="skyblue")
        self.refill_button.place(x=center_x - 250, y=start_y + 200)  

        
        self.update_loop()

    def update_loop(self):
        
        self.dispenser.adjust_temperature(self.target_cold_temp, self.target_hot_temp)
        
        
        self.cold_temp_label.config(text=f"Cold Water Temp: {self.dispenser.current_cold_temp:.2f}°C")
        self.hot_temp_label.config(text=f"Hot Water Temp: {self.dispenser.current_hot_temp:.2f}°C")
        self.water_level_label.config(text=f"Water Level: {self.dispenser.water_level}%")
        
        self.update_scale_bars()

        self.root.after(1000, self.update_loop)

    def update_scale_bars(self):
        cold_scale_value = max(1, (self.dispenser.current_cold_temp - self.dispenser.min_cold_temp) / (self.dispenser.ambient_temp - self.dispenser.min_cold_temp) * 9 + 1)
        hot_scale_value = max(1, (self.dispenser.current_hot_temp - self.dispenser.min_cold_temp) / (self.dispenser.max_hot_temp - self.dispenser.min_cold_temp) * 9 + 1)
        
        self.cold_temp_scale.set(cold_scale_value)

        self.hot_temp_scale.set(hot_scale_value)

        self.water_level_progress['value'] = self.dispenser.water_level

    def dispense_target_temp(self):
        try:
            target_temp = float(self.target_temp_entry.get())
            if target_temp < self.dispenser.min_cold_temp or target_temp > self.dispenser.current_hot_temp:
                raise ValueError("Temperature out of bounds")
            message = self.dispenser.dispense_water(target_temp)
        except ValueError:
            message = "Please enter a valid temperature."

        self.show_message(message)

    def refill_water(self):
        self.dispenser.refill_water()
        self.show_message("Water bottle refilled!")

    def show_message(self, message):
        messagebox.showinfo("Water Dispenser", message)

def main():
    dispenser = WaterDispenser()
    root = tk.Tk()
    app = WaterDispenserApp(root, dispenser)
    root.mainloop()

if __name__ == "__main__":
    main()
