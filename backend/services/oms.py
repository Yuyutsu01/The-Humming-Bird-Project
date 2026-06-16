#order management system
import uuid
from datetime import datetime

class OrderManagementSystem:
    def __init__(self):
        # In-memory store for mock portfolio
        self.orders = []
        self.positions = {}
        self.cash_balance = 100000.00 # Starting mock cash

    def submit_order(self, symbol: str, quantity: int, side: str, order_type: str = "market", price: float = None):
        """Mock order submission."""
        
        # Basic validation
        if side.lower() not in ["buy", "sell"]:
            raise ValueError("Side must be 'buy' or 'sell'")

        order = {
            "order_id": str(uuid.uuid4()),
            "symbol": symbol.upper(),
            "quantity": quantity,
            "side": side.lower(),
            "order_type": order_type.lower(),
            "price": price,
            "status": "filled", # Automatically filling for MVP
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.orders.append(order)
        self._update_portfolio(order)
        return order

    def _update_portfolio(self, order: dict):
        """Internal logic to update mock positions and cash."""
        sym = order["symbol"]
        qty = order["quantity"] if order["side"] == "buy" else -order["quantity"]
        # In a real system, execution price comes from the exchange. Here we mock it.
        exec_price = order.get("price") or 100.0 # arbitrary mock fill price
        
        if sym not in self.positions:
            self.positions[sym] = 0
            
        self.positions[sym] += qty
        self.cash_balance -= (qty * exec_price)

    def get_portfolio_summary(self):
        return {
            "cash": self.cash_balance,
            "positions": self.positions
        }

# Global singleton for MVP
oms_instance = OrderManagementSystem()
