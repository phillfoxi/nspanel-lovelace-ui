import logging

LOGGER = logging.getLogger(__name__)

class Updater:
    def __init__(self, controller, mode, desired_display_firmware_version, desired_display_firmware_url, desired_tasmota_driver_version, desired_tasmota_driver_url):
        self.desired_display_firmware_version = desired_display_firmware_version
        self.desired_display_firmware_url     = desired_display_firmware_url
        self.desired_tasmota_driver_version   = desired_tasmota_driver_version
        self.desired_tasmota_driver_url       = desired_tasmota_driver_url
        
        self.mode = mode
        self.controller = controller
        self.current_tasmota_driver_version   = None
        self.current_display_firmware_version = None

    def set_tasmota_driver_version(self, driver_version):
        self.current_tasmota_driver_version = driver_version
    def set_current_display_firmware_version(self, panel_version):
        self.current_display_firmware_version = panel_version

    def check_pre_req(self):
        # we need to know both versions to continue
        if self.current_tasmota_driver_version is not None and self.current_display_firmware_version is not None:
            # tasmota driver has to be at least version 2 for Update command 
            # and panel has to be at version 11 for notify commands
            # version 16 for new button cmd format
            if self.current_tasmota_driver_version >= 2 and self.current_display_firmware_version >= 16:
                return True
            return False

    def check_updates(self):
        # return's true if a notification was send to the panel
        # run pre req check
        if self.check_pre_req():
            LOGGER.info("Update Pre-Check sucessful Tasmota Driver Version: %s Panel Version: %s", self.current_tasmota_driver_version, self.current_display_firmware_version)
            # check if tasmota driver needs update
            if self.current_tasmota_driver_version < self.desired_tasmota_driver_version:
                LOGGER.info("Update of Tasmota Driver needed")
                # in auto mode just do the update
                if self.mode == "auto":
                    self.update_berry_driver()
                    return False
                # send notification about the update
                if self.mode == "auto-notify":
                    update_msg = "There's an update avalible for the tasmota      berry driver, do you want to start the update  now?                                                                      If you encounter issues after the update or      this message appears frequently, please checkthe manual and repeat the installation steps   for the tasmota berry driver. "
                    self.controller._pages_gen.send_message_page("updateBerryNoYes", "Driver Update available!", update_msg, "Dismiss", "Yes")
                    return True
                return False
            # check if display firmware needs an update
            if self.current_display_firmware_version < self.desired_display_firmware_version:
                LOGGER.info("Update of Display Firmware needed")
                # in auto mode just do the update
                if self.mode == "auto":
                    self.update_panel_driver()
                    return False
                # send notification about the update
                if self.mode == "auto-notify":
                    update_msg = "There's a firmware update avalible for the       nextion sceen inside of nspanel, do you want  to start the update now?                                     If the update fails check the installation         manual and flash again over the tasmota console. Be pationed the update will take a while."
                    self.controller._pages_gen.send_message_page("updateDisplayNoYes", "Display Update available!", update_msg, "Dismiss", "Yes")
                    return True
                return False
        else:
            LOGGER.info("Update Pre-Check failed Tasmota Driver Version: %s Panel Version: %s", self.current_tasmota_driver_version, self.current_display_firmware_version)
            return False

    def update_berry_driver(self):
        topic = self.controller._config["panelSendTopic"].replace("CustomSend", "UpdateDriverVersion")
        self.controller._send_mqtt_msg(topic, self.desired_tasmota_driver_url)
    def update_panel_driver(self):
        topic = self.controller._config["panelSendTopic"].replace("CustomSend", "FlashNextion")
        self.controller._send_mqtt_msg(topic, self.desired_display_firmware_url)
