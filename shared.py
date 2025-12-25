class SharedState:
    def __init__(self):
        self.client = None
        self.clientws_user = None
        self.clientws_market = None
        self.pricer = None
        self.ordermanager = None
        self.orderbook_y = None
        self.orderbook_n = None
        self.position_y = None
        self.position_n = None
        self.y_token = None
        self.n_token = None
        self.market = None
        # New fields for refactored logic
        self.tick_size = 0.01         # Will be fetched from market data
        self.is_unwinding = False     # Flag for unwind mode
        self.inventory_manager = None # Inventory tracking and skew calculations
        self.last_best_bid = None     # Track for requote detection
        self.last_best_ask = None     # Track for requote detection
        self.active_token = None      # The token we're quoting (YES or NO)
        self.active_orderbook = None  # Reference to the active orderbook

shared_state = SharedState()