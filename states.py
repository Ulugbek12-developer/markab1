from aiogram.fsm.state import State, StatesGroup

class SellPhone(StatesGroup):
    model = State()
    photos = State()
    memory = State()
    battery = State()
    condition = State()
    region = State()
    box = State()
    price = State()
    contact = State()
    confirm = State()

class BuyPhone(StatesGroup):
    model = State()
    branch = State()
    select_id = State()
    payment_type = State()
    location = State()
    installment_plan = State()
    confirm = State()

class PricePhone(StatesGroup):
    model = State()
    photos = State()
    battery_range = State()
    manual_battery = State()
    memory = State()
    condition = State()
    region = State()
    box = State()

class AdminAuth(StatesGroup):
    waiting_for_password = State()

class AdminState(StatesGroup):
    setting_price = State()
    setting_branch = State()
    counter_price = State()

class AdminAddProduct(StatesGroup):
    model = State()
    branch = State()
    storage = State()
    battery = State()
    condition = State()
    price = State()
    photos = State()

class AdminBranchMgmt(StatesGroup):
    waiting_for_name = State()
    waiting_for_delete = State()

class AdminDeleteProduct(StatesGroup):
    waiting_for_model = State()
    waiting_for_selection = State()
