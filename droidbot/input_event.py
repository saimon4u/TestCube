import json
import os
import random
import time
from abc import abstractmethod

from . import utils
from .intent import Intent

POSSIBLE_KEYS = [
    "BACK",
    "MENU",
    "HOME"
]

# Unused currently, but should be useful.
POSSIBLE_BROADCASTS = [
    "android.intent.action.AIRPLANE_MODE_CHANGED",
    "android.intent.action.BATTERY_CHANGED",
    "android.intent.action.BATTERY_LOW",
    "android.intent.action.BATTERY_OKAY",
    "android.intent.action.BOOT_COMPLETED",
    "android.intent.action.DATE_CHANGED",
    "android.intent.action.DEVICE_STORAGE_LOW",
    "android.intent.action.DEVICE_STORAGE_OK",
    "android.intent.action.INPUT_METHOD_CHANGED",
    "android.intent.action.INSTALL_PACKAGE",
    "android.intent.action.LOCALE_CHANGED",
    "android.intent.action.MEDIA_EJECT",
    "android.intent.action.MEDIA_MOUNTED",
    "android.intent.action.MEDIA_REMOVED",
    "android.intent.action.MEDIA_SHARED",
    "android.intent.action.MEDIA_UNMOUNTED",
    "android.intent.action.NEW_OUTGOING_CALL",
    "android.intent.action.OPEN_DOCUMENT",
    "android.intent.action.OPEN_DOCUMENT_TREE",
    "android.intent.action.PACKAGE_ADDED",
    "android.intent.action.PACKAGE_CHANGED",
    "android.intent.action.PACKAGE_DATA_CLEARED",
    "android.intent.action.PACKAGE_FIRST_LAUNCH",
    "android.intent.action.PACKAGE_FULLY_REMOVED",
    "android.intent.action.PACKAGE_INSTALL",
    "android.intent.action.PACKAGE_REMOVED",
    "android.intent.action.PACKAGE_REPLACED",
    "android.intent.action.PACKAGE_RESTARTED",
    "android.intent.action.PACKAGE_VERIFIED",
    "android.intent.action.PASTE",
    "android.intent.action.POWER_CONNECTED",
    "android.intent.action.POWER_DISCONNECTED",
    "android.intent.action.POWER_USAGE_SUMMARY",
    "android.intent.action.PROVIDER_CHANGED",
    "android.intent.action.QUICK_CLOCK",
    "android.intent.action.REBOOT",
    "android.intent.action.SCREEN_OFF",
    "android.intent.action.SCREEN_ON",
    "android.intent.action.SET_WALLPAPER",
    "android.intent.action.SHUTDOWN",
    "android.intent.action.TIMEZONE_CHANGED",
    "android.intent.action.TIME_CHANGED",
    "android.intent.action.TIME_TICK",
    "android.intent.action.UID_REMOVED",
    "android.intent.action.UNINSTALL_PACKAGE",
    "android.intent.action.USER_BACKGROUND",
    "android.intent.action.USER_FOREGROUND",
    "android.intent.action.USER_INITIALIZE",
    "android.intent.action.USER_PRESENT",
    "android.intent.action.VOICE_COMMAND",
    "android.intent.action.WALLPAPER_CHANGED",
    "android.intent.action.WEB_SEARCH"
]

KEY_KeyEvent = "key"
KEY_ManualEvent = "manual"
KEY_ExitEvent = "exit"
KEY_TouchEvent = "touch"
KEY_LongTouchEvent = "long_touch"
KEY_SelectEvent = "select"
KEY_UnselectEvent = "unselect"
KEY_SwipeEvent = "swipe"
KEY_ScrollEvent = "scroll"
KEY_SetTextEvent = "set_text"
KEY_IntentEvent = "intent"
KEY_SpawnEvent = "spawn"
KEY_KillAppEvent = "kill_app"


class InvalidEventException(Exception):
    pass


class InputEvent(object):
    """
    The base class of all events
    """
    def __init__(self):
        self.event_type = None
        self.log_lines = None

    def to_dict(self):
        return self.__dict__

    def to_json(self):
        return json.dumps(self.to_dict())

    def __str__(self):
        return self.to_dict().__str__()

    @abstractmethod
    def send(self, device):
        """
        send this event to device
        :param device: Device
        :return:
        """
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def get_random_instance(device, app):
        """
        get a random instance of event
        :param device: Device
        :param app: App
        """
        raise NotImplementedError

    @staticmethod
    def from_dict(event_dict):
        if not isinstance(event_dict, dict):
            return None
        if 'event_type' not in event_dict:
            return None
        event_type = event_dict['event_type']
        if event_type == KEY_KeyEvent:
            return KeyEvent(event_dict=event_dict)
        elif event_type == KEY_TouchEvent:
            return TouchEvent(event_dict=event_dict)
        elif event_type == KEY_LongTouchEvent:
            return LongTouchEvent(event_dict=event_dict)
        elif event_type == KEY_SelectEvent or event_type == KEY_UnselectEvent:
            return SelectEvent(event_dict=event_dict)
        elif event_type == KEY_SwipeEvent:
            return SwipeEvent(event_dict=event_dict)
        elif event_type == KEY_ScrollEvent:
            return ScrollEvent(event_dict=event_dict)
        elif event_type == KEY_SetTextEvent:
            return SetTextEvent(event_dict=event_dict)
        elif event_type == KEY_IntentEvent:
            return IntentEvent(event_dict=event_dict)
        elif event_type == KEY_ExitEvent:
            return ExitEvent(event_dict=event_dict)
        elif event_type == KEY_SpawnEvent:
            return SpawnEvent(event_dict=event_dict)

    @abstractmethod
    def get_event_str(self, state):
        pass

    def get_views(self):
        return []


class EventLog(object):
    """
    save an event to local file system
    """

    def __init__(self, device, app, event, profiling_method=None, tag=None):
        self.device = device
        self.app = app
        self.event = event
        if tag is None:
            from datetime import datetime
            tag = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        self.tag = tag

        self.from_state = None
        self.to_state = None
        self.event_str = None

        self.profiling_method = profiling_method
        self.trace_remote_file = "/data/local/tmp/event.trace"
        self.is_profiling = False
        self.profiling_pid = -1
        self.sampling = None
        self.events = []
        # sampling feature was added in Android 5.0 (API level 21)
        if profiling_method is not None and \
           str(profiling_method) != "full" and \
           self.device.get_sdk_version() >= 21:
            self.sampling = int(profiling_method)

    def to_dict(self):
        return {
            "tag": self.tag,
            "event": self.event.to_dict(),
            "start_state": self.from_state.state_str,
            "stop_state": self.to_state.state_str,
            "event_str": self.event_str
        }

    def save2dir(self, output_dir=None):
        # Save event
        if output_dir is None:
            if self.device.output_dir is None:
                return
            else:
                output_dir = os.path.join(self.device.output_dir, "events")
        try:
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            event_json_file_path = "%s/event_%s.json" % (output_dir, self.tag)
            event_json_file = open(event_json_file_path, "w")
            json.dump(self.to_dict(), event_json_file, indent=2)
            event_json_file.close()
        except Exception as e:
            self.device.logger.warning("Saving event to dir failed.")
            self.device.logger.warning(e)

    def save_views(self, output_dir=None):
        # Save views
        views = self.event.get_views()
        if views:
            for view_dict in views:
                self.from_state.save_view_img(view_dict=view_dict, output_dir=output_dir)

    def is_start_event(self):
        if isinstance(self.event, IntentEvent):
            intent_cmd = self.event.intent
            if "start" in intent_cmd and self.app.get_package_name() in intent_cmd:
                return True
        return False

    def start(self):
        """
        start sending event
        """
        if self.event in self.events:
            return
        else:
            self.events.append(self.event)
        self.from_state = self.device.get_current_state()
        self.start_profiling()
        self.event_str = self.event.get_event_str(self.from_state)
        print("Action: %s" % self.event_str)
        
        self.device.send_event(self.event)

    def start_profiling(self):
        """
        start profiling the current event
        @return:
        """
        if self.profiling_method is None:
            return
        if self.is_profiling:
            return
        pid = self.device.get_app_pid(self.app)
        if pid is None:
            if self.is_start_event():
                start_intent = self.app.get_start_with_profiling_intent(self.trace_remote_file, self.sampling)
                self.event.intent = start_intent.get_cmd()
                self.is_profiling = True
            return
        if self.sampling is not None:
            self.device.adb.shell(
                ["am", "profile", "start", "--sampling", str(self.sampling), str(pid), self.trace_remote_file])
        else:
            self.device.adb.shell(["am", "profile", "start", str(pid), self.trace_remote_file])
        self.is_profiling = True
        self.profiling_pid = pid

    def stop(self):
        """
        finish sending event
        """
        self.stop_profiling()
        self.to_state = self.device.get_current_state()
        self.save2dir()
        self.save_views()

    def stop_profiling(self, output_dir=None):
        if self.profiling_method is None:
            return
        if not self.is_profiling:
            return
        try:
            if self.profiling_pid == -1:
                pid = self.device.get_app_pid(self.app)
                if pid is None:
                    return
                self.profiling_pid = pid

            self.device.adb.shell(["am", "profile", "stop", str(self.profiling_pid)])
            if self.sampling is None:
                time.sleep(3)  # guess this time can vary between machines

            if output_dir is None:
                if self.device.output_dir is None:
                    return
                else:
                    output_dir = os.path.join(self.device.output_dir, "events")
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            event_trace_local_path = "%s/event_trace_%s.trace" % (output_dir, self.tag)
            self.device.pull_file(self.trace_remote_file, event_trace_local_path)

        except Exception as e:
            self.device.logger.warning("profiling event failed")
            self.device.logger.warning(e)


class ManualEvent(InputEvent):
    """
    a manual event
    """

    def __init__(self, event_dict=None):
        super().__init__()
        self.event_type = KEY_ManualEvent
        self.time = time.time()
        if event_dict is not None:
            self.__dict__.update(event_dict)

    @staticmethod
    def get_random_instance(device, app):
        return None

    def send(self, device):
        # do nothing
        pass

    def get_event_str(self, state):
        return "%s(time=%s)" % (self.__class__.__name__, self.time)


class ExitEvent(InputEvent):
    """
    an event to stop testing
    """

    def __init__(self, event_dict=None):
        super().__init__()
        self.event_type = KEY_ExitEvent
        if event_dict is not None:
            self.__dict__.update(event_dict)

    @staticmethod
    def get_random_instance(device, app):
        return None

    def send(self, device):
        # device.disconnect()
        raise KeyboardInterrupt()

    def get_event_str(self, state):
        return "%s()" % self.__class__.__name__


class KillAppEvent(InputEvent):
    """
    an event to stop testing
    """

    def __init__(self, app=None, event_dict=None):
        super().__init__()
        self.event_type = KEY_KillAppEvent
        self.stop_intent = None
        if app:
            self.stop_intent = app.get_stop_intent().get_cmd()
        elif event_dict is not None:
            self.__dict__.update(event_dict)

    @staticmethod
    def get_random_instance(device, app):
        return None

    def send(self, device):
        if self.stop_intent:
            device.send_intent(self.stop_intent)
        device.key_press('HOME')

    def get_event_str(self, state):
        return "%s()" % self.__class__.__name__


class KeyEvent(InputEvent):
    """
    a key pressing event
    """

    def __init__(self, name=None, event_dict=None):
        super().__init__()
        self.event_type = KEY_KeyEvent
        self.name = name
        if event_dict is not None:
            self.__dict__.update(event_dict)

    @staticmethod
    def get_random_instance(device, app):
        key_name = random.choice(POSSIBLE_KEYS)
        return KeyEvent(key_name)

    def send(self, device):
        device.key_press(self.name)
        return True

    def get_event_str(self, state):
        return "%s(state=%s, name=%s)" % (self.__class__.__name__, state.state_str, self.name)


class UIEvent(InputEvent):
    """
    This class describes a UI event of app, such as touch, click, etc
    """
    def __init__(self):
        super().__init__()

    def send(self, device):
        raise NotImplementedError

    @staticmethod
    def get_random_instance(device, app):
        if not device.is_foreground(app):
            # if current app is in background, bring it to foreground
            component = app.get_package_name()
            if app.get_main_activity():
                component += "/%s" % app.get_main_activity()
            return IntentEvent(Intent(suffix=component))

        else:
            choices = {
                TouchEvent: 6,
                LongTouchEvent: 2,
                SwipeEvent: 2
            }
            event_type = utils.weighted_choice(choices)
            return event_type.get_random_instance(device, app)

    @staticmethod
    def get_xy(x, y, view):
        if x and y:
            return x, y
        if view:
            from .device_state import DeviceState
            return DeviceState.get_view_center(view_dict=view)
        return x, y

    @staticmethod
    def view_str(state, view):
        view_class = view['class'].split('.')[-1]
        view_text = view['text'].replace('\n', '\\n') if 'text' in view and view['text'] else ''
        view_text = view_text[:10] if len(view_text) > 10 else view_text
        view_short_sig = f'{state.activity_short_name}/{view_class}-{view_text}'
        return f"state={state.state_str}, view={view['view_str']}({view_short_sig})"


class TouchEvent(UIEvent):
    """
    a touch on screen
    """

    def __init__(self, x=None, y=None, view=None, event_dict=None):
        super().__init__()
        self.event_type = KEY_TouchEvent
        self.x = x
        self.y = y
        self.view = view
        if event_dict is not None:
            self.__dict__.update(event_dict)

    @staticmethod
    def get_random_instance(device, app):
        x = random.uniform(0, device.get_width())
        y = random.uniform(0, device.get_height())
        return TouchEvent(x, y)
    

    async def send_test_case(self, test_case):
        from .SocketClient import SocketClient
        await SocketClient.connect()
        SocketClient.send_message("test_case", test_case)

    


    # Saimon Bhuiyan (SPL2)
    def send(self, device):
        if self.view and self.view['class'] and ("Button" not in self.view['class'] and "EditText" not in self.view['class']):
            return True
        if self.view and "Button" in self.view['class'] and self.view['clickable']:
            before = device.take_screenshot()
            print(f'Before Image: {before}')
            x, y = UIEvent.get_xy(x=self.x, y=self.y, view=self.view)
            device.view_long_touch(x=x, y=y, duration=200)
            import time
            time.sleep(1.5)
            after = device.take_screenshot()
            print(f'After Image: {after}')
            result = ImageComparer.compareImage(before, after)

            import json
            import re

            match = re.search(r'\{.*\}', result, re.DOTALL)

            if match:
                json_str = match.group(0) 
                parsed_data = json.loads(json_str)
                

                import asyncio
                asyncio.run(self.send_test_case(parsed_data))


                print('\n\n\n')
                print(f'Verdict = {parsed_data["verdict"]}')
                print(f'Response = {parsed_data["response"]}')
                print('\n\n\n')
                # if "Navigation" in parsed_data["response"] or parsed_data['verdict'] == 'fail':
                #     import os, time
                #     device.set_last_known_state()
                #     time.sleep(2)
                #     os.system("adb shell input keyevent KEYCODE_BACK")
                    
            else:
                print("No JSON found in the text.")

        else:
            x, y = UIEvent.get_xy(x=self.x, y=self.y, view=self.view)
            device.view_long_touch(x=x, y=y, duration=200)
        return True

    def get_event_str(self, state):
        if self.view is not None:
            return f"{self.__class__.__name__}({UIEvent.view_str(state, self.view)})"
        elif self.x is not None and self.y is not None:
            return "%s(state=%s, x=%s, y=%s)" % (self.__class__.__name__, state.state_str, self.x, self.y)
        else:
            msg = "Invalid %s!" % self.__class__.__name__
            raise InvalidEventException(msg)

    def get_views(self):
        return [self.view] if self.view else []


class SelectEvent(UIEvent):
    """
    select a checkbox
    """

    def __init__(self, event_type=KEY_SelectEvent, x=None, y=None, view=None, event_dict=None):
        super().__init__()
        self.event_type = event_type
        self.x = x
        self.y = y
        self.view = view
        if event_dict is not None:
            self.__dict__.update(event_dict)

    def send(self, device):
        x, y = UIEvent.get_xy(x=self.x, y=self.y, view=self.view)
        if 'special_attr' in self.view:
            if self.event_type == KEY_UnselectEvent and 'selected' in self.view['special_attr']:
                device.view_long_touch(x=x, y=y, duration=200)
            elif self.event_type == KEY_SelectEvent and 'selected' not in self.view['special_attr']:
                device.view_long_touch(x=x, y=y, duration=200)
        else:
            device.view_long_touch(x=x, y=y, duration=200)
        return True

    def get_event_str(self, state):
        if self.view is not None:
            return f"{self.__class__.__name__}(type={self.event_type}, {UIEvent.view_str(state, self.view)})"
        elif self.x is not None and self.y is not None:
            return "%s(type=%s, state=%s, x=%s, y=%s)" % (self.event_type, self.__class__.__name__, state.state_str, self.x, self.y)
        else:
            msg = "Invalid %s!" % self.__class__.__name__
            raise InvalidEventException(msg)

    def get_views(self):
        return [self.view] if self.view else []


class LongTouchEvent(UIEvent):
    """
    a long touch on screen
    """

    def __init__(self, x=None, y=None, view=None, duration=2000, event_dict=None):
        super().__init__()
        self.event_type = KEY_LongTouchEvent
        self.x = x
        self.y = y
        self.view = view
        self.duration = duration
        if event_dict is not None:
            self.__dict__.update(event_dict)

    @staticmethod
    def get_random_instance(device, app):
        x = random.uniform(0, device.get_width())
        y = random.uniform(0, device.get_height())
        return LongTouchEvent(x, y)

    def send(self, device):
        x, y = UIEvent.get_xy(x=self.x, y=self.y, view=self.view)
        device.view_long_touch(x=x, y=y, duration=self.duration)
        return True

    def get_event_str(self, state):
        if self.view is not None:
            return f"{self.__class__.__name__}({UIEvent.view_str(state, self.view)})"
        elif self.x is not None and self.y is not None:
            return "%s(state=%s, x=%s, y=%s)" %\
                   (self.__class__.__name__, state.state_str, self.x, self.y)
        else:
            msg = "Invalid %s!" % self.__class__.__name__
            raise InvalidEventException(msg)

    def get_views(self):
        return [self.view] if self.view else []


class SwipeEvent(UIEvent):
    """
    a drag gesture on screen
    """

    def __init__(self, start_x=None, start_y=None, start_view=None, end_x=None, end_y=None, end_view=None,
                 duration=1000, event_dict=None):
        super().__init__()
        self.event_type = KEY_SwipeEvent

        self.start_x = start_x
        self.start_y = start_y
        self.start_view = start_view

        self.end_x = end_x
        self.end_y = end_y
        self.end_view = end_view

        self.duration = duration

        if event_dict is not None:
            self.__dict__.update(event_dict)

    @staticmethod
    def get_random_instance(device, app):
        start_x = random.uniform(0, device.get_width())
        start_y = random.uniform(0, device.get_height())
        end_x = random.uniform(0, device.get_width())
        end_y = random.uniform(0, device.get_height())
        return SwipeEvent(start_x=start_x, start_y=start_y,
                          end_x=end_x, end_y=end_y)

    def send(self, device):
        start_x, start_y = UIEvent.get_xy(x=self.start_x, y=self.start_y, view=self.start_view)
        end_x, end_y = UIEvent.get_xy(x=self.end_x, y=self.end_y, view=self.end_view)
        device.view_drag((start_x, start_y), (end_x, end_y), self.duration)
        return True

    def get_event_str(self, state):
        if self.start_view is not None:
            start_view_str = UIEvent.view_str(state, self.start_view)
        elif self.start_x is not None and self.start_y is not None:
            start_view_str = "state=%s, start_x=%s, start_y=%s" % (state.state_str, self.start_x, self.start_y)
        else:
            msg = "Invalid %s!" % self.__class__.__name__
            raise InvalidEventException(msg)

        if self.end_view is not None:
            end_view_str = "end_view=%s" % self.end_view['view_str']
        elif self.end_x is not None and self.end_y is not None:
            end_view_str = "end_x=%s, end_y=%s" % (self.end_x, self.end_y)
        else:
            msg = "Invalid %s!" % self.__class__.__name__
            raise InvalidEventException(msg)

        return "%s(%s, %s, duration=%s)" % (self.__class__.__name__, start_view_str, end_view_str, self.duration)

    def get_views(self):
        views = []
        if self.start_view:
            views.append(self.start_view)
        if self.end_view:
            views.append(self.end_view)
        return views


class ScrollEvent(UIEvent):
    """
    swipe gesture
    """

    def __init__(self, x=None, y=None, view=None, direction="down", event_dict=None):
        super().__init__()
        self.event_type = KEY_ScrollEvent
        self.x = x
        self.y = y
        self.view = view
        self.direction = direction

        if event_dict is not None:
            self.__dict__.update(event_dict)

    @staticmethod
    def get_random_instance(device, app):
        x = random.uniform(0, device.get_width())
        y = random.uniform(0, device.get_height())
        direction = random.choice(["up", "down", "left", "right"])
        return ScrollEvent(x, y, direction)

    def send(self, device):
        if self.view is not None:
            from .device_state import DeviceState
            width = DeviceState.get_view_width(view_dict=self.view)
            height = DeviceState.get_view_height(view_dict=self.view)
        else:
            width = device.get_width()
            height = device.get_height()

        x, y = UIEvent.get_xy(x=self.x, y=self.y, view=self.view)
        if not x or not y:
            # If no view and no coordinate specified, use the screen center coordinate
            x = width / 2
            y = height / 2

        start_x, start_y = x, y
        end_x, end_y = x, y
        duration = 500

        if self.direction == "UP":
            start_y -= height * 2 / 5
            end_y += height * 2 / 5
        elif self.direction == "DOWN":
            start_y += height * 2 / 5
            end_y -= height * 2 / 5
        elif self.direction == "LEFT":
            start_x -= width * 2 / 5
            end_x += width * 2 / 5
        elif self.direction == "RIGHT":
            start_x += width * 2 / 5
            end_x -= width * 2 / 5

        device.view_drag((start_x, start_y), (end_x, end_y), duration)
        return True

    def get_event_str(self, state):
        if self.view is not None:
            return \
                f"{self.__class__.__name__}({UIEvent.view_str(state, self.view)}, direction={self.direction})"
        elif self.x is not None and self.y is not None:
            return "%s(state=%s, x=%s, y=%s, direction=%s)" %\
                   (self.__class__.__name__, state.state_str, self.x, self.y, self.direction)
        else:
            return "%s(state=%s, direction=%s)" % \
                   (self.__class__.__name__, state.state_str, self.direction)

    def get_views(self):
        return [self.view] if self.view else []


class SetTextEvent(UIEvent):
    """
    input text to target UI
    """

    @staticmethod
    def get_random_instance(device, app):
        pass

    def __init__(self, x=None, y=None, view=None, text=None, event_dict=None):
        super().__init__()
        self.event_type = KEY_SetTextEvent
        self.x = x
        self.y = y
        self.view = view
        self.text = text
        if event_dict is not None:
            self.__dict__.update(event_dict)
        
    async def send_input(self, data):
        from .SocketClient import SocketClient
        await SocketClient.connect()
        SocketClient.send_message("input", data)

    def send(self, device):
        # import os
        # os.system("adb shell input keyevent KEYCODE_BACK")
        # return True
        x, y = UIEvent.get_xy(x=self.x, y=self.y, view=self.view)
        touch_event = TouchEvent(x=x, y=y)
        touch_event.send(device)


        # Saimon Bhuiyan (SPL2)
        from .GeminiAI import GeminiAi

        input_list = GeminiAi.generate_random_input()
        if input_list is not None:
            input_string = "".join(map(str, input_list.values()))
            if self.view["text"] in input_string or "Enter" not in self.view["text"]:
                device.view_set_text(self.view["text"])
                return True
        # print(input_list)
        chat = GeminiAi.get_chat()
        response = chat.send_message(f'prompt: {self.view["text"]}, {self.get_event_str(device.get_current_state()) if ("Login" or "Sign") in self.get_event_str(device.get_current_state()) else ""}')
        text = input_list[response.text.strip()]
        if not text:
            text = ""
        device.view_set_text(text)

        if text:
            import asyncio
            asyncio.run(self.send_input({"field": response.text.strip(), "text": text}))
        
        
        return True

    def get_event_str(self, state):
        if self.view is not None:
            return f"{self.__class__.__name__}({UIEvent.view_str(state, self.view)}, text={self.text})"
        elif self.x is not None and self.y is not None:
            return "%s(state=%s, x=%s, y=%s, text=%s)" %\
                   (self.__class__.__name__, state.state_str, self.x, self.y, self.text)
        else:
            msg = "Invalid %s!" % self.__class__.__name__
            raise InvalidEventException(msg)

    def get_views(self):
        return [self.view] if self.view else []


class IntentEvent(InputEvent):
    """
    An event describing an intent
    """

    def __init__(self, intent=None, event_dict=None):
        super().__init__()
        self.event_type = KEY_IntentEvent
        if event_dict is not None:
            intent = event_dict['intent']
        if isinstance(intent, Intent):
            self.intent = intent.get_cmd()
        elif isinstance(intent, str):
            self.intent = intent
        else:
            msg = "intent must be either an instance of Intent or a string."
            raise InvalidEventException(msg)
        if event_dict is not None:
            self.__dict__.update(event_dict)

    @staticmethod
    def get_random_instance(device, app):
        pass

    def send(self, device):
        device.send_intent(intent=self.intent)
        return True

    def get_event_str(self, state):
        return "%s(intent='%s')" % (self.__class__.__name__, self.intent)


class SpawnEvent(InputEvent):
    """
    An event to spawn then stop testing
    """

    def __init__(self, event_dict=None):
        super().__init__()
        self.event_type = KEY_SpawnEvent
        if event_dict is not None:
            self.__dict__.update(event_dict)

    @staticmethod
    def get_random_instance(device, app):
        return None

    def send(self, device):
        master = self.__dict__["master"]
        # force touch the view
        init_script = {
            "views": {
                "droid_master_view": {
                    "resource_id": self.__dict__["view"]["resource_id"],
                    "class": self.__dict__["view"]["class"],
                }
            },
            "states": {
                "droid_master_state": {
                    "views": ["droid_master_view"]
                }
            },
            "operations": {
                "droid_master_operation": [
                    {
                        "event_type": "touch",
                        "target_view": "droid_master_view"
                    }
                ]
            },
            "main": {
                "droid_master_state": ["droid_master_operation"]
            }
        }
        init_script_json = json.dumps(init_script, indent=2)
        import xmlrpc.client
        proxy = xmlrpc.client.ServerProxy(master)
        proxy.spawn(device.serial, init_script_json)

    def get_event_str(self, state):
        return "%s()" % self.__class__.__name__


EVENT_TYPES = {
    KEY_KeyEvent: KeyEvent,
    KEY_TouchEvent: TouchEvent,
    KEY_LongTouchEvent: LongTouchEvent,
    KEY_SwipeEvent: SwipeEvent,
    KEY_ScrollEvent: ScrollEvent,
    KEY_IntentEvent: IntentEvent,
    KEY_SpawnEvent: SpawnEvent
}



# Saimon Bhuiyan (SPL2)
class ImageComparer:
    @staticmethod
    def compareImage(before_image_path, after_image_path):
        import google.generativeai as genai
        import PIL.Image
        import os
        genai.configure(api_key="AIzaSyDy_VQnRxk5LqrOvEtpdZzxXdM8tIt_0xg")

        try:
            image1 = PIL.Image.open(before_image_path)
            image2 = PIL.Image.open(after_image_path)

            model = genai.GenerativeModel('gemini-2.0-flash')
            response = model.generate_content([
                "Describe the key visual differences between these two images. Focus on changes in objects, colors, and overall composition. I am mainly searching if this two page is identical or not. So if you find any type of dissimilarity ans yes otherwise no. By anytype i mean at the app screen not the system bar of the phone. Ans me in only yes or no. Give me response as a json. The json should contain 2 things. For example the dissimilarity is a toast message that contains Password must be 8 character long. But if both pages are completely different page in that case consider as a pass. Because the navigation took place. So You should create a json like {verditc: fail, response: Password must be 8 character long} here verdict will be the tone of the response like it's negative or positive. Positive means pass and negative means fail. Also if the 2nd image contain a new page image then it should consider as a pass and response should be 'Navigation occured'.",
                image1,
                image2
            ])
            return response.text

        except FileNotFoundError:
            print("Error: Image files not found.")
        except Exception as e:
            print(f"An error occurred: {e}")
