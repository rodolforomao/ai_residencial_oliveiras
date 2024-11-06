from controllers.main_controller import MainController
from controllers.principal_controller import PrincipalController
from test.unit.google_calendar import UnitTestGoogleCalendar
import unittest

whatsapp_mode = True
terminal_mode = True

if __name__ == "__main__":
    
    # Running the unit test
    #unittest.main()
    
    if whatsapp_mode:
        controller = PrincipalController()
        controller.executar()
    elif terminal_mode:
        # debug mode - use the terminal to put messages
        controller = MainController()
        controller.iniciar()
