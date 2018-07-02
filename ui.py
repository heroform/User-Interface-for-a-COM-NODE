import urwid
import re
import zmq
import sys
import os
import stat
from jsonrpcclient.zeromq_client import ZeroMQClient
from configparser import ConfigParser
from datetime import datetime
import logging



class Ui(urwid.WidgetPlaceholder):
    """
    A class responsible for setting up and running user interface
    """

    def __init__(self):
        super(Ui, self).__init__(urwid.SolidFill(u'/'))
        self.started       = True                  # First state for 'start/stop' button
        self.triggerButton = self.button("Start")  # Set first label for start/stop button
        self.isConfiguring = False                 # Flag to check if the screen show config window

        # Content of footer
        self.status = urwid.Text("Statusbar -- Press Alt + <key> for menu entries")

        # Check which window is showed
        self.state = None

        # Request for RRH 2 (experiment)
        self.rrh2Request = None


    # Edit file config
    def edit_file_config(self):
        """
        Open configuration file and change parameter

        Input  : None
        Output : None
        """

        # User-defined parameters on configuration window
        para = self.parserParameter

        self.status.set_text("Statusbar -- Press Alt + <key> for menu entries")

        try:
            # Create new object of Configparser
            config = ConfigParser()

            # Content in config file
            config.read('config.ini.example')

            # Set text for 'CORE NETWOK' part in config file
            config.set('CORE NETWORK', 'op', para[0])
            config.set('CORE NETWORK', 'ki', para[1])

            # Set text for BBU part in config file
            config.set('BBU', 'BBU_ip_list', "[\"" + para[2].replace(" ", "\",\"") + "\"]")

            # Set text for RRH part in config file
            config.set('RRH', 'number_of_rrh', para[3])
            config.set('RRH', 'number_of_UE_per_rrh', para[4])  # dau bang ban goc khong cach
            config.set('RRH', 'rrh_ip_start', para[5])
            config.set('RRH', 'rrh_netmask', para[6])
            config.set('RRH', 'rrh_gateway', para[7])
            config.set('RRH', 'rrh_interface', para[10])  # Last parameter is rrh_interface according to

            # parse_value function
            config.set('RRH', 'imsi_start', para[8])
            config.set('RRH', 'traffic_target', para[9])

            # Writing to configuration file
            with open('config.ini.example', 'w') as configFile:
                config.write(configFile)
                # config.write(EqualsSpaceRemover(configFile))

            self.status.set_text("Statusbar -- Press Alt + <key> for menu entries")
        except:
            self.status.set_text("Not fill all parameters or No config file!")

    # Create interface
    def button(self, caption):  # TODO: Add callback
        """
        Create a button object

        Input:
         caption    : The button title
        Output:
         newButton  : object of button
        """
        # Create new button widget
        newButton = urwid.Button(caption)
        # Add attribute for button
        newButton = urwid.AttrWrap(newButton, 'button normal', 'button select')
        return newButton

    # RRH buttons
    def rrh_button(self, caption):
        """
        Create a button to switch to RRH state window

        Input:
         caption    :  The button title
        Output:
         return an object of button
        """
        button = urwid.Button(caption)
        urwid.connect_signal(button, 'click', self.trigger())
        return urwid.AttrMap(button, 'button normal', focus_map='reversed')

    def _action(self, button):
        """
        Get button lable when click on

        Input:
         button     : Target button object
        Output:
         label of button
        """
        self.b_pressed = button.get_label()

    def on_animate_button(self, button):
        """Toggle started state and button text."""
        if self.started:
            button.set_label("Start")
            self.started = False
        else:
            button.set_label("Stop")
            self.started = True
        return button

    def trigger(self):
        """ Toggle start/stop button"""
        return self.on_animate_button(self.triggerButton)

    def parse_values(self, text):
        """
        Extract values in single quote from text by REGEX
        Input:
         text          : Text that show content on config window
        Output:
         matches       : all parametter values in string
        """
        # Find parameter from config window
        matches = re.findall(r"selectable flow widget '(.+?)' caption", text)  # Find text between matched pattern
        # Read selectable button of RRH interface in config window
        for option in self.interfaceButton:
            if option.get_state() == True:  # If button is chosen
                matches.append(str(option.get_label()))  # Add the label of button (chosen RRH interface) to the
                # last of parameter list
        # return ",".join(matches)
        return matches

    def unhandled_input(self, key):
        """Screen behaviors with unhandled inputs"""

        started = True  # first state for 'start/stop' button

        # Quit program
        if key in ('meta q', 'meta Q'):
            raise urwid.ExitMainLoop()

        # Switch to config window
        if key in ('meta c', 'meta C'):
            self.loop.widget = self.config_view()

        # Switch to status window
        if key in ('meta i', 'meta I'):
            self.loop.widget = self.status_view()

        # Switch start/stop button
        if key in ('meta s', 'meta S'):
            self.trigger()
            # Save to file config when start button and filling all parameter in config window
            if self.isConfiguring and self.started:
                # Window body content
                txt = str(self.nattributes.contents)
                # Read input parameters from user
                self.parserParameter = self.parse_values(txt)
                self.edit_file_config()

        # For debug UI
        if key == 'f5':
            if self.isConfiguring:
                # Window body content
                txt = str(self.nattributes.contents)
                # Read input parameters from user
                # self.parserParameter = self.parse_values(txt)
                # for debugging
                # section = urwid.Text(self.parserParameter)
                section = urwid.Text(txt)
                fill = urwid.Filler(section, 'top')
                loop = urwid.MainLoop(fill)
                loop.run()
            else:
                raise Exception('Not set configuration yet!')

        # Open RRH full content view
        if key == 'f1':
            self.loop.widget = self.ue_view_rrh1()

        if key == 'f2':
            self.loop.widget = self.ue_view_rrh2()

        if key == 'f3':
            self.loop.widget = self.ue_view_rrh3()

        # Set behavior with Tab
        if key in ('Tab', 'tab'):
            oldWidget, oldPosition = self.body.get_focus()
            self.body.set_focus((oldPosition + 1) % 12)  # with 12 elements in ListBox



    # Window contents

    def menubar(self):
        """
        Menu bar at the top of the screen
        """
        # Content of the top bar
        menu_conf = [('menuf', "C"), ('menu', "onfig   ")]
        menu_info = [('menuf', "I"), ('menu', "nfo   ")]
        menu = []
        menu.append(urwid.AttrWrap(urwid.Text(menu_conf), 'menu'))
        menu.append(urwid.AttrWrap(urwid.Text(menu_info), 'menu'))
        menu.append(self.triggerButton)
        # Make up
        menu.append(urwid.AttrWrap(urwid.Text(" "), 'menu'))
        menu.append(urwid.AttrWrap(urwid.Text(" "), 'menu'))
        menu.append(urwid.AttrWrap(urwid.Text(" "), 'menu'))
        menu.append(urwid.AttrWrap(urwid.Text(" "), 'menu'))
        menu.append(urwid.AttrWrap(urwid.Text(" "), 'menu'))

        menuGrid = urwid.GridFlow(menu, 10, 0, 1, 'left')
        return menuGrid


    def statusbar(self):
        """
        Status bar at the bottom of the screen.
        """

        # self.status_text = self.status
        return urwid.AttrWrap(self.status, 'menu');

    def radio_button(self):
        """Create choiable list for RRH interface"""
        group = []
        self.interfaceButton = []

        # Interfaces of RRH
        interfaces = ["enp0s8", "enp3S0", "enp5S0", "enp6S0", "enp7s0"]

        # Create choicable list
        for interface in interfaces:
            but = urwid.RadioButton(group, interface, False)
            but = urwid.AttrWrap(but, 'button choice', 'button select')
            self.interfaceButton.append(but)
        return urwid.Pile(self.interfaceButton)

    def config_view(self):
        """
        Configuration window content

        Input  : None
        Output :
         frame : urwid Frame object - showing content of configuration window
        """

        # State of screen
        self.state = 'config'

        # Set flag to check if the screen is on config window
        self.isConfiguring = True

        # Set the body content
        self.attributes = [
            # Editable widgets
            urwid.Edit(('menuh', u'Milenage OP\n'),          align='left'),
            urwid.Edit(('menuh', u'Milenage KI\n'),          align='left'),
            urwid.Edit(('menuh', u'BBU IP list\n'),          align='left'),
            urwid.Edit(('menuh', u'Number of RRH\n'),        align='left'),
            urwid.Edit(('menuh', u'Number of UE per RRH\n'), align='left'),
            urwid.Edit(('menuh', u'RRH IP start\n'),         align='left'),
            urwid.Edit(('menuh', u'RRH netmask\n'),          align='left'),
            urwid.Edit(('menuh', u'RRH gateway\n'),          align='left'),

            # Adding choiceable list
            urwid.Text(('menuh', u'RRH interface\n'),        align='left'),
            self.radio_button(),

            # Editable widgets
            urwid.Edit(('menuh', u'IMSI start\n'),           align='left'),
            urwid.Edit(('menuh', u'Traffic target\n'),       align='left'),
        ]

        # Urwid SimpleListWalker to move among widgets by arrow keys
        self.nattributes = urwid.SimpleListWalker(self.attributes)

        # Put all content to a Urwid listbox object
        self.body = urwid.ListBox(self.nattributes)

        # Add atribute for configuration window
        frame = urwid.AttrMap(urwid.Frame(self.body, self.menubar(), self.statusbar()), 'bg')
        return frame

    def is_socket(self, socketPath):
        """
        Check if socket exist
        Input:
         socketPath  : Absolute path to Unix Domain Socket
        :return:
         True: socket exist
         False: socket does not exist
        """
        isSocketExisted = os.path.exists(socketPath)
        return isSocketExisted

    def read_message(self, socketPath, sentRequest):
        """
        Read message in the response from server
        Input:
          socketPath  : the path to socket file
          sentRequest : the request to sent to server
        Output:
          messageContent : The content of response message
        """
        unixDomainSocketPath = 'ipc://' + socketPath
        # Disable request, response logging
        logging.getLogger("jsonrpcclient.client.request").setLevel(logging.WARNING)
        logging.getLogger("jsonrpcclient.client.response").setLevel(logging.WARNING)
        # Send request 'statistics_update' and recieve respond
        messageContent = ZeroMQClient(unixDomainSocketPath).request(sentRequest)
        return messageContent

    def rrh_info_overview(self, messageContent):
        """
        Read the status UI from response message
        Input :
          messageContent : the content of response message
        Output :
          A list of total number of UE having same status.
        """
        # Status overview
        statusList = re.findall(r"status:'(.+?)'", messageContent)
        totalAttached = str(statusList.count('attached'))
        totalDetached = str(statusList.count('detached'))
        totalAttaching = str(statusList.count('attaching'))
        return [totalDetached, totalAttached, totalAttaching]

    def rrh_info_specific(self, messageContent):
        """
          Read the detail from response message
          Input :
            messageContent : the content of response message
          Output :
            A list of content of UE having same status.
        """
        # UE info
        ueidList = re.findall(r"ueid:(.+?),", messageContent)
        imsiList = re.findall(r"imsi:(.+?),", messageContent)
        statusList = re.findall(r"status:'(.+?)'", messageContent)
        return [ueidList, imsiList, statusList]

    def check_ue_state(self):
        """
        Parser log message content.
        Input: None
        Output: None
        """
        # Define the paths of sockets
        rrh1SocketPath = "/home/taitd/var/run/rrh_pool/rrh1.sock"
        rrh2SocketPath = "/home/taitd/var/run/rrh_pool/rrh2.sock"
        rrh3SocketPath = "/home/taitd/var/run/rrh_pool/rrh3.sock"

        # Define request for RRH servers
        sentRequest = "statistics_updates"

        # Check if socket exist
        self.rrh1SocketExist = self.is_socket(rrh1SocketPath)
        self.rrh2SocketExist = self.is_socket(rrh2SocketPath)
        self.rrh3SocketExist = self.is_socket(rrh3SocketPath)

        # Send request and obtain the information
        if (self.rrh1SocketExist):
            rrh1Message = self.read_message(rrh1SocketPath, sentRequest)
            self.rrh1Overview = self.rrh_info_overview(rrh1Message)
            self.rrh1Specific = self.rrh_info_specific(rrh1Message)

        if (self.rrh2Request is None):
            self.rrh2Request = sentRequest
        if (self.is_socket(rrh2SocketPath)):
            # Experiment with another method in server 2
            if (self.rrh2Request != 'statistics_updates_reduce'):
                rrh2Message = self.read_message(rrh2SocketPath, sentRequest)
                self.rrh2Overview = self.rrh_info_overview(rrh2Message)
                self.rrh2Specific = self.rrh_info_specific(rrh2Message)

                # If 6 UE are detached from RRH 2, reconfig for only 3 UEs can attach to RRH2
                if (int(self.rrh2Overview[1]) == 6):
                    self.rrh2Request = 'statistics_updates_reduce'
            else:
                rrh2Message = self.read_message(rrh2SocketPath, self.rrh2Request)
                self.rrh2Overview = self.rrh_info_overview(rrh2Message)
                self.rrh2Specific = self.rrh_info_specific(rrh2Message)

                # If 3 UE are attached to RRH 2, reconfig for 6 UEs can attach to RRH2
                if (int(self.rrh2Overview[0]) == 3):
                    self.rrh2Request = 'statistics_updates'

        if (self.is_socket(rrh3SocketPath)):
            rrh3Message = self.read_message(rrh3SocketPath, sentRequest)
            self.rrh3Overview = self.rrh_info_overview(rrh3Message)
            self.rrh3Specific = self.rrh_info_specific(rrh3Message)


    def ue_view_rrh1(self):
        """
        RRH1 state window content

        Input  : None
        Output :
         frame : urwid Frame object - showing content of RRH1 state window
        """
        # State of screen
        self.state = 'log_rrh1'

        # Title denote server
        rrh1Title = []
        rrh1Title.append(urwid.Divider('-'))
        rrh1Title.append(urwid.AttrWrap(urwid.Text("RRH 1", 'center'), 'rrh1'))
        rrh1Title.append(urwid.Divider('-'))
        rrh1TitleGrid = urwid.GridFlow(rrh1Title, 16, 0, 1, 'left')

        statusTable = [rrh1TitleGrid]

        # Column title
        title = []
        title.append(urwid.AttrWrap(urwid.Text("UEID", 'center'), 'menuf'))
        title.append(urwid.AttrWrap(urwid.Text("IMSI", 'center'), 'menuf'))
        title.append(urwid.AttrWrap(urwid.Text("STATUS", 'center'), 'menuf'))
        titleGrid = urwid.GridFlow(title, 16, 0, 1, 'left')

        # Lines separate rows in table
        border = []
        border.append(urwid.Divider('-'))
        border.append(urwid.Divider('.'))
        border.append(urwid.Divider('-'))
        borderGrid = urwid.GridFlow(border, 16, 0, 1, 'left')

        statusTable.append(titleGrid)

        if (self.rrh1SocketExist):
            # Each element in 'content' list is a row's content.
            content1 = [None] * len(self.rrh1Specific[0])
            gridContent1 = [None] * len(self.rrh1Specific[0])

            # Decorate each row in table
            for index in range(0, len(self.rrh1Specific[0])):
                content1[index] = [urwid.AttrWrap(urwid.Text(self.rrh1Specific[0][index], 'center'), 'bg'),
                                  urwid.AttrWrap(urwid.Text(self.rrh1Specific[1][index], 'center'), 'bg'),
                                  urwid.AttrWrap(urwid.Text(self.rrh1Specific[2][index], 'center'), 'bg')]
                gridContent1[index] = urwid.GridFlow(content1[index], 16, 0, 1, 'left')

                # Add detail to screen table content
                statusTable.append(gridContent1[index])
                statusTable.append(borderGrid)

            # Build a rrh_status_window
            # Create table of content
            # statusTable1 = []

            # for index in range(0, len(self.rrh1Specific[0])):
            #     statusTable.append(gridContent1[index])
            #     statusTable.append(borderGrid)

            statusTable.append(borderGrid)
            # statusTable.append(borderGrid)

        rrhWindow = urwid.SimpleListWalker(statusTable)

        # Frame for RRH status window
        return urwid.AttrMap(urwid.Frame(urwid.ListBox(rrhWindow), self.menubar(), self.statusbar()), 'bg')

    def ue_view_rrh2(self):
        """
        RRH2 state window content

        Input  : None
        Output :
         frame : urwid Frame object - showing content of RRH2 state window
        """
        # State of screen
        self.state = 'log_rrh2'

        # Title denote server
        rrh2Title = []
        rrh2Title.append(urwid.Divider('-'))
        rrh2Title.append(urwid.AttrWrap(urwid.Text("RRH 2", 'center'), 'rrh2'))
        rrh2Title.append(urwid.Divider('-'))
        rrh2TitleGrid = urwid.GridFlow(rrh2Title, 16, 0, 1, 'left')

        statusTable = [rrh2TitleGrid]

        # Column title
        title = []
        title.append(urwid.AttrWrap(urwid.Text("UEID", 'center'), 'menuf'))
        title.append(urwid.AttrWrap(urwid.Text("IMSI", 'center'), 'menuf'))
        title.append(urwid.AttrWrap(urwid.Text("STATUS", 'center'), 'menuf'))
        titleGrid = urwid.GridFlow(title, 16, 0, 1, 'left')

        # Lines separate rows in table
        border = []
        border.append(urwid.Divider('-'))
        border.append(urwid.Divider('.'))
        border.append(urwid.Divider('-'))
        borderGrid = urwid.GridFlow(border, 16, 0, 1, 'left')

        statusTable.append(titleGrid)

        if (self.rrh2SocketExist):
            # Each element in 'content' list is a row's content.
            content2 = [None] * len(self.rrh2Specific[0])
            gridContent2 = [None] * len(self.rrh2Specific[0])

            # Decorate each row in table
            for index in range(0, len(self.rrh2Specific[0])):
                content2[index] = [urwid.AttrWrap(urwid.Text(self.rrh2Specific[0][index], 'center'), 'bg'),
                                   urwid.AttrWrap(urwid.Text(self.rrh2Specific[1][index], 'center'), 'bg'),
                                   urwid.AttrWrap(urwid.Text(self.rrh2Specific[2][index], 'center'), 'bg')]
                gridContent2[index] = urwid.GridFlow(content2[index], 16, 0, 1, 'left')

                # Add detail to screen table content
                statusTable.append(gridContent2[index])
                statusTable.append(borderGrid)

            # Build a rrh_status_window
            # Create table of content
            # statusTable2 = []

            # for index in range(0, len(self.rrh2Specific[0])):
            #     statusTable.append(gridContent2[index])
            #     statusTable.append(borderGrid)

            statusTable.append(borderGrid)
            # statusTable.append(borderGrid)

        rrhWindow = urwid.SimpleListWalker(statusTable)

        # Frame for RRH status window
        return urwid.AttrMap(urwid.Frame(urwid.ListBox(rrhWindow), self.menubar(), self.statusbar()), 'bg')

    def ue_view_rrh3(self):
        """
        RRH3 state window content

        Input  : None
        Output :
         frame : urwid Frame object - showing content of RRH3 state window
        """
        # State of screen
        self.state = 'log_rrh3'

        # Title denote server
        rrh3Title = []
        rrh3Title.append(urwid.Divider('-'))
        rrh3Title.append(urwid.AttrWrap(urwid.Text("RRH 3", 'center'), 'button select'))
        rrh3Title.append(urwid.Divider('-'))
        rrh3TitleGrid = urwid.GridFlow(rrh3Title, 16, 0, 1, 'left')

        statusTable = [rrh3TitleGrid]

        # Column title
        title = []
        title.append(urwid.AttrWrap(urwid.Text("UEID", 'center'), 'menuf'))
        title.append(urwid.AttrWrap(urwid.Text("IMSI", 'center'), 'menuf'))
        title.append(urwid.AttrWrap(urwid.Text("STATUS", 'center'), 'menuf'))
        titleGrid = urwid.GridFlow(title, 16, 0, 1, 'left')

        statusTable.append(titleGrid)

        # Lines separate rows in table
        border = []
        border.append(urwid.Divider('-'))
        border.append(urwid.Divider('.'))
        border.append(urwid.Divider('-'))
        borderGrid = urwid.GridFlow(border, 16, 0, 1, 'left')

        if (self.rrh3SocketExist):
            # Each element in 'content' list is a row's content.
            content3 = [None] * len(self.rrh3Specific[0])
            gridContent3 = [None] * len(self.rrh3Specific[0])

            # Decorate each row in table
            for index in range(0, len(self.rrh3Specific[0])):
                content3[index] = [urwid.AttrWrap(urwid.Text(self.rrh3Specific[0][index], 'center'), 'bg'),
                                   urwid.AttrWrap(urwid.Text(self.rrh3Specific[1][index], 'center'), 'bg'),
                                   urwid.AttrWrap(urwid.Text(self.rrh3Specific[2][index], 'center'), 'bg')]
                gridContent3[index] = urwid.GridFlow(content3[index], 16, 0, 1, 'left')

                # Add detail to screen table content
                statusTable.append(gridContent3[index])
                statusTable.append(borderGrid)

            # Build a rrh_status_window
            # Create table of content
            # for index in range(0, len(self.rrh3Specific[0])):
                # statusTable.append(gridContent3[index])
                # statusTable.append(borderGrid)

            statusTable.append(borderGrid)

        rrhWindow = urwid.SimpleListWalker(statusTable)

        # Frame for RRH status window
        return urwid.AttrMap(urwid.Frame(urwid.ListBox(rrhWindow), self.menubar(), self.statusbar()), 'bg')


    def status_view(self):
        """
        RRH state window content

        Input  : None
        Output :
         frame : urwid Frame object - showing content of RRH state window
        """

        # State of screen
        self.state = 'info'

        self.isConfiguring = False

        # Titles of statistic table
        bodyTitle = []
        bodyTitle.append(urwid.AttrWrap(urwid.Text("RRH"), 'menuf'))
        bodyTitle.append(urwid.AttrWrap(urwid.Text("Attached"), 'menuf'))
        bodyTitle.append(urwid.AttrWrap(urwid.Text("Detached"), 'menuf'))
        bodyTitle.append(urwid.AttrWrap(urwid.Text("Attaching"), 'menuf'))
        titleGrid = urwid.GridFlow(bodyTitle, 10, 0, 1, 'left')

        # Statistic table content
        attributes = [titleGrid]

        # Brief statistic content of RRH 1
        if (self.rrh1SocketExist):
            rrh1 = []
            rrh1Button = self.button("RRH 1")
            rrh1.append(rrh1Button)
            rrh1.append(urwid.AttrWrap(urwid.Text(self.rrh1Overview[0], 'center'), 'menuh'))
            rrh1.append(urwid.AttrWrap(urwid.Text(self.rrh1Overview[1], 'center'), 'menuh'))
            rrh1.append(urwid.AttrWrap(urwid.Text(self.rrh1Overview[2], 'center'), 'menuh'))
            rrh1Grid = urwid.GridFlow(rrh1, 10, 0, 1, 'left')
            attributes.append(rrh1Grid)

        # Brief statistic content of RRH 2
        if (self.rrh2SocketExist):
            rrh2 = []
            rrh2Button = self.button("RRH 2")
            rrh2.append(rrh2Button)
            rrh2.append(urwid.AttrWrap(urwid.Text(self.rrh2Overview[0], 'center'), 'menuh'))
            rrh2.append(urwid.AttrWrap(urwid.Text(self.rrh2Overview[1], 'center'), 'menuh'))
            rrh2.append(urwid.AttrWrap(urwid.Text(self.rrh2Overview[2], 'center'), 'menuh'))
            rrh2Grid = urwid.GridFlow(rrh2, 10, 0, 1, 'left')
            attributes.append(rrh2Grid)

        # Brief statistic content of RRH 3
        if (self.rrh3SocketExist):
            rrh3 = []
            rrh3Button = self.button("RRH 3")
            rrh3.append(rrh3Button)
            rrh3.append(urwid.AttrWrap(urwid.Text(self.rrh3Overview[0], 'center'), 'menuh'))
            rrh3.append(urwid.AttrWrap(urwid.Text(self.rrh3Overview[1], 'center'), 'menuh'))
            rrh3.append(urwid.AttrWrap(urwid.Text(self.rrh3Overview[2], 'center'), 'menuh'))
            rrh3Grid = urwid.GridFlow(rrh3, 10, 0, 1, 'left')
            attributes.append(rrh3Grid)


        # Create frame for Info window
        self.nattributes = urwid.SimpleListWalker(attributes)
        self.body = urwid.ListBox(self.nattributes)
        frame = urwid.AttrMap(urwid.Frame(self.body, self.menubar(), self.statusbar()), 'bg')
        return frame

    palette = [('menu', 'black', 'dark cyan', 'standout'),
               ('menuh', 'yellow', 'dark cyan', ('standout', 'bold')),
               ('menuf', 'black', 'light gray'),
               ('bg', 'light gray', 'dark blue'),
               ('bgf', 'black', 'light gray', 'standout'),
               ('alert', 'light gray', 'dark red', ('standout', 'bold')),
               ('button normal', 'yellow', 'dark cyan', 'standout'),
               ('button select', 'white', 'dark green'),
               ('button choice', 'light gray', 'dark blue', 'standout'),
               ('rrh1', 'white', 'brown'),
               ('rrh2', 'white', 'dark magenta')
               ]

    def refresh(self, dump_, _foo):
        """
        Update screen automatically
        Input : None
          dump_, _foo: 2 dump useless variables
        Output: None
        """
        # Update info window
        if self.state == 'info':
            self.check_ue_state()
            self.loop.widget = self.status_view()

        # Update RRH status window
        elif self.state == 'log_rrh1':
            self.check_ue_state()
            self.loop.widget = self.ue_view_rrh1()
        elif self.state == 'log_rrh2':
            self.check_ue_state()
            self.loop.widget = self.ue_view_rrh2()
        elif self.state == 'log_rrh3':
            self.check_ue_state()
            self.loop.widget = self.ue_view_rrh3()
        else:
            pass

        self.loop.set_alarm_in(1, self.refresh)

    def main(self):
        self.__init__()
        # logFile = open("log.txt", 'r')
        # print ("POS", os.SEEK_CUR, os.SEEK_END)
        self.check_ue_state()
        # logFile.close()
        self.frame = self.status_view()
        self.loop = urwid.MainLoop(self.frame, self.palette, unhandled_input=self.unhandled_input)

        self.loop.set_alarm_in(0, self.refresh)  # TODO: Find a way to close file properly
        # self.loop.set_alarm_in(0, self.update_statistics, )
        self.loop.run()

# screen = Ui()
# screen.main()

if '__main__' == __name__:
    screen = Ui()
    screen.main()

