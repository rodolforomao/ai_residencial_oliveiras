from controllers.main_controller import MainController
from test.unit.google_calendar import UnitTestGoogleCalendar
import unittest

if __name__ == "__main__":
    # Running the unit test
    unittest.main()
    
    # Optionally run the MainController as well
    controller = MainController()
    controller.iniciar()
