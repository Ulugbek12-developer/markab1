from aiogram.fsm.state import State, StatesGroup

class SellPhone(StatesGroup):
    choice = State()
    model = State()
    esim = State()
    color = State()
    memory = State()
    photos = State()
    battery = State()
    cycles = State()
    replaced_parts = State()
    defects = State()
    screen_condition = State()
    body_condition = State()
    description = State()
    region = State()
    box = State()
    price = State()
    contact = State()
    confirm = State()

class BuyPhone(StatesGroup):
    choice = State()
    model = State()
    memory = State()
    color = State()
    select_id = State()
    payment_type = State()
    location = State()
    installment_plan = State()
    confirm = State()

class PricePhone(StatesGroup):
    choice = State()
    model = State()
    esim = State()
    color = State()
    memory = State()
    photos = State()
    battery = State()
    cycles = State()
    replaced_parts = State()
    defects = State()
    screen_condition = State()
    body_condition = State()
    region = State()
    manual_region = State()
    box = State()
    is_opened = State()
    confirm = State()

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
