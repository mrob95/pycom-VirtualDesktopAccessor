from ctypes import *
from ctypes.wintypes import *
from comtypes import (
    IUnknown,
    GUID,
    IID,
    COMMETHOD,
    CoInitialize,
    CoCreateInstance,
    cast,
    CLSCTX_LOCAL_SERVER,
)
from objects import (
    IVirtualDesktop,
    IVirtualDesktopManager,
    IVirtualDesktopManagerInternal,
    IApplicationView,
    IObjectArray,
    IApplicationViewCollection,
    IServiceProvider,
)

CLSID_ImmersiveShell = GUID("{C2F03A33-21F5-47FA-B4BB-156362A2F239}")
CLSID_VirtualDesktopManagerInternal = GUID("{C5E0CDCA-7B6E-41B2-9FC4-D93975CC467B}")
CLSID_IVirtualDesktopManager = GUID("{AA509086-5CA9-4C25-8F95-589D3C07B48A}")


def _register_service():
    CoInitialize()
    pServiceProvider = CoCreateInstance(
        CLSID_ImmersiveShell, IServiceProvider, CLSCTX_LOCAL_SERVER
    )
    pManagerInternal = POINTER(IVirtualDesktopManagerInternal)()
    pServiceProvider.QueryService(
        CLSID_VirtualDesktopManagerInternal, IVirtualDesktopManagerInternal._iid_,
        pManagerInternal
    ),
    # pManagerInternal = cast(
    #     pManagerInternal,
    #     POINTER(IVirtualDesktopManagerInternal),
    # )
    # pManager = cast(
    #     pServiceProvider.QueryService(
    #         CLSID_IVirtualDesktopManager,
    #         IVirtualDesktopManager._iid_,
    #     ),
    #     POINTER(IVirtualDesktopManager),
    # )
    pManager = CoCreateInstance(CLSID_IVirtualDesktopManager, IVirtualDesktopManager)
    return pManager, pManagerInternal


def get_desktop_count():
    pManager, pManagerInternal = _register_service()
    array = POINTER(IObjectArray)()
    pManagerInternal.GetDesktops(array)
    count = array.GetCount()
    return count


# IVirtualDesktop* _GetDesktopByNumber(int number)
def _get_desktop_by_number(number):
    pManager, pManagerInternal = _register_service()
    array = POINTER(IObjectArray)()
    pManagerInternal.GetDesktops(array)
    # found = array.GetAt(number, IVirtualDesktop._iid_)
    found = POINTER(IVirtualDesktop)()
    array.GetAt(number, IVirtualDesktop._iid_, found)
    return found


def _get_current_desktop():
    pManager, pManagerInternal = _register_service()
    found = POINTER(IVirtualDesktop)()
    pManagerInternal.GetCurrentDesktop(found)
    return found


def _get_desktop_number(desktop):
    pManager, pManagerInternal = _register_service()
    target_id = desktop.GetID()
    array = POINTER(IObjectArray)()
    pManagerInternal.GetDesktops(array)
    for i in range(array.GetCount()):
        item = POINTER(IVirtualDesktop)()
        array.GetAt(i, IVirtualDesktop._iid_, item)
        item_id = item.GetID()
        if item_id == target_id:
            return i


def current_desktop_id():
    virtualDesktop = _get_current_desktop()
    number = _get_desktop_number(virtualDesktop)
    return number


def move_window_to(hwnd, number):
    pManager, pManagerInternal = _register_service()
    desktop = _get_desktop_by_number(number)
    # IApplicationView* app = nullptr;
    # 		viewCollection->GetViewForHwnd(window, &app);
    # 		if (app != nullptr) {
    # 			pDesktopManagerInternal->MoveViewToDesktop(app, pDesktop);
    # 			return true;
    # 		}
    pServiceProvider = CoCreateInstance(
        CLSID_ImmersiveShell, IServiceProvider, CLSCTX_LOCAL_SERVER
    )
    pApplicationView = POINTER(IApplicationView)()
    pViewCollection = POINTER(IApplicationViewCollection)()
    pServiceProvider.QueryService(
        IApplicationViewCollection._iid_, IApplicationViewCollection._iid_,
        pViewCollection,
    ),
    pViewCollection.GetViewForHwnd(hwnd, pApplicationView)
    pManagerInternal.MoveViewToDesktop(pApplicationView, desktop)


def go_to_desktop(number):
    # TODO: bounds checking
    pManager, pManagerInternal = _register_service()
    array = POINTER(IObjectArray)()
    pManagerInternal.GetDesktops(array)
    desktop = POINTER(IVirtualDesktop)()
    array.GetAt(number, IVirtualDesktop._iid_, desktop)
    pManagerInternal.SwitchDesktop(desktop)


print(get_desktop_count())
print(current_desktop_id())
go_to_desktop(0)

from dragonfly import Window

current = Window.get_foreground()
print(current)
move_window_to(current.handle, 1)
