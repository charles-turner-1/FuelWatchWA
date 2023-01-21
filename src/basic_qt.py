from fuelwatch import FuelPrice


from PyQt6.QtWidgets import  QApplication, QWidget, QLabel, QComboBox, QPushButton, QCheckBox
import sys
 
class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(600, 500)
        self.setWindowTitle("Fuel Watcher")
        interval = 60
 
        self.fuel = FuelPrice()

        self.brand_selector = QComboBox(self)
        self.brand_selector.addItem("Any")
        for brand in self.fuel.get_brands():
            self.brand_selector.addItem(brand)
        self.brand_selector.move(100,100+ 0* interval)
 
        self.product_selector = QComboBox(self)
        self.product_selector.addItem("Any")
        for product in self.fuel.get_products():
            self.product_selector.addItem(product)
        self.product_selector.move(100,100+ 1* interval)

        self.region_selector = QComboBox(self)
        self.region_selector.addItem("Any")
        for region in self.fuel.get_regions():
            self.region_selector.addItem(region)
        self.region_selector.move(100,100+ 2* interval)

        self.suburb_selector = QComboBox(self)
        self.suburb_selector.addItem("Any")
        for suburb in self.fuel.get_suburbs():
            self.suburb_selector.addItem(suburb)
        self.suburb_selector.move(100,100+ 3* interval)

        self.surrounding = QCheckBox(self)
        self.surrounding.toggled.connect(self.inc_surround)
        self.surrounding.setText("Allow Surrounding Suburbs?")
        self.surrounding.move(100,100+ 4* interval)

        self.brand_selector.width =  self.product_selector.width = self.region_selector.width = self.suburb_selector.width

        button = QPushButton("Submit", self)
        button.clicked.connect(self.submit)

        button.move(100,100 + 5 * interval)
 
    def submit(self):
        # Need to set defaults properly
        region_val = (self.fuel.region[self.region_selector.currentText()] 
                     if self.region_selector.currentText() != "Any" 
                     else None)
        product_val = (self.fuel.product[self.product_selector.currentText()]
                      if self.product_selector.currentText() != "Any"
                      else None)
        suburb_val = (self.suburb_selector.currentText() 
                     if self.suburb_selector.currentText() != "Any" 
                     else None)
        brand_val = (self.fuel.brand[self.brand_selector.currentText()] 
                    if self.brand_selector.currentText() != "Any" 
                    else None)  

        #self.remove_any()

        self.fuel.set_surrounding(surrounding=self.inc_surround()) 
        self.fuel.set_region(region=region_val)
        self.fuel.set_product(product=product_val)
        self.fuel.set_suburb(suburb=suburb_val)
        self.fuel.set_brand(brand=brand_val)    


        self.fuel.request()
        self.fuel.print_all()
        
    def remove_any(self):
        """ Remove any items from self.fuel where self.fuel.key == "Any" """
        new_dict = self.fuel.payload.copy()
        for key, val in new_dict.items():
            if val == "Any":
                self.fuel.payload.pop(key)

    def inc_surround(self):
        print("Selected: ", self.surrounding.isChecked())
        return self.surrounding.isChecked()
 
 
app = QApplication(sys.argv)
window = Window()
window.show()
sys.exit(app.exec())