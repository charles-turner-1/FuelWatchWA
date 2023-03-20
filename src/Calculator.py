from fuelwatch import Journey, FuelPrice, CarInfo

from PyQt6.QtWidgets import  QApplication, QWidget, QLabel, QComboBox, QPushButton, QCheckBox, QFrame, QLineEdit
import sys

class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(440, 600)
        self.setWindowTitle("Fuel Watcher")
        interval = 60
 
        self.fuel = FuelPrice()
        self.journey = Journey()
        self.car = CarInfo()

        self.start_location = QLineEdit(self,placeholderText="Start Address")
        self.start_location.move(100,100+ 0* interval)
        self.start_location.resize(250,40)


        self.end_location = QLineEdit(self,placeholderText="End Address")
        self.end_location.move(100,100+ 1* interval)
        self.end_location.resize(250,40)

        self.product = QComboBox(self)
        self.product.addItem("Any")
        for product in self.fuel.get_products():
             self.product.addItem(product)
        self.product.move(100,100+ 2* interval)
        self.product.resize(250,40)

 
        self.max_detour = QLineEdit(self,placeholderText="Max Acceptable Detour")
        self.max_detour.move(100,100+ 3* interval)
        self.max_detour.resize(250,40)

        self.num_litres = QLineEdit(self,placeholderText="How many litres do you want?")
        self.num_litres.move(100,100+ 4* interval)
        self.num_litres.resize(250,40)

        self.car_efficiency = QLineEdit(self,placeholderText="Car Fuel Efficiency (L/100km)")
        self.car_efficiency.move(100,100+ 5* interval)
        self.car_efficiency.resize(250,40)

        button = QPushButton("Submit", self)
        button.clicked.connect(self.submit)

        button.move(100,100 + 6 * interval)
        button.resize(250,40)
 
    def submit(self):
        # Need to set defaults properly
        start_loc = self.start_location
        end_loc = self.end_location
        product_val = (self.product.currentText() 
                     if self.product.currentText() != "Any" 
                     else None)
        n_litres = self.num_litres  


        self.fuel.set_product(product=product_val)
        self.journey.set_start_address(start_loc)
        self.journey.set_end_address(end_loc)
        self.journey.set_max_detour(self.max_detour)
        self.car.set_fuel_type(self.product)
        self.car.set_mileage(self.car_efficiency)

        self.journey.get_car_info(self.car)

        self.journey.get_all_detour_values(n_litres)

        self.fuel.request()
        self.fuel.print_all()
        
    def inc_surround(self):
        print("Selected: ", self.surrounding.isChecked())
        return self.surrounding.isChecked()
 
 
app = QApplication(sys.argv)
window = Window()
window.show()
sys.exit(app.exec())