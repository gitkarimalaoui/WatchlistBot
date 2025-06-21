from typing import Dict, List
from datetime import datetime, timedelta, date
import json
import os

from core.db import get_session
from core import models

from utils.utils_signaux import is_buy_signal


class DecisionEngine:
    """Simple engine computing trade decisions and viability."""

    def __init__(self, thresholds_path: str = os.path.join("config", "thresholds.json")) -> None:
        self.thresholds = self._load_thresholds(thresholds_path)

    def _load_thresholds(self, path: str) -> Dict:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _count_open_positions(self) -> int:
        try:
            session = get_session()
            count = (
                session.query(models.TradeSimule)
                .filter(models.TradeSimule.exit_price.is_(None))
                .count()
            )
            session.close()
            return count
        except Exception:
            return 0

    def _daily_loss(self) -> float:
        try:
            session = get_session()
            today = date.today()
            trades = (
                session.query(models.TradeSimule)
                .filter(models.TradeSimule.date >= today)
                .all()
            )
            loss = 0.0
            for t in trades:
                if t.exit_price is None:
                    continue
                pnl = (t.exit_price - t.prix_achat) * t.quantite - (t.frais or 0)
                if pnl < 0:
                    loss += -pnl
            session.close()
            return loss
        except Exception:
            return 0.0

    def _risk_limits_reached(self) -> str:
        max_pos = self.thresholds.get("max_concurrent_biotech_positions")
        if max_pos is not None and self._count_open_positions() >= max_pos:
            return "Maximum biotech positions reached"
        limit = self.thresholds.get("daily_loss_limit")
        if limit is not None and self._daily_loss() >= limit:
            return "Daily loss limit reached"
        return ""

    def analyze_trade_decision(self, ticker_data: Dict) -> Dict:
        """Return reasons to buy or avoid a trade and confidence level."""
        reasons_buy: List[str] = []
        reasons_avoid: List[str] = []

        if is_buy_signal(ticker_data):
            reasons_buy.append("Conditions techniques réunies")
        else:
            reasons_avoid.append("Conditions techniques insuffisantes")

        if ticker_data.get("has_fda"):
            reasons_buy.append("Catalyseur FDA")

        if ticker_data.get("volume_ratio", 1.0) <= 1.5:
            reasons_avoid.append("Volume trop faible")

        cat_date = ticker_data.get("catalyst_date")
        if cat_date:
            try:
                dt = datetime.fromisoformat(cat_date)
                if dt - datetime.utcnow() > timedelta(days=1):
                    reasons_avoid.append("Catalyseur trop lointain")
                else:
                    reasons_buy.append("Catalyseur imminent")
            except Exception:
                pass

        confidence = min(float(ticker_data.get("score_ia", 0)) / 100.0, 1.0)
        return {"buy": reasons_buy, "avoid": reasons_avoid, "confidence": confidence}

    def calculate_trade_viability(
        self,
        price_entry: float,
        price_target: float,
        quantity: int,
        broker_fees: Dict[str, float],
    ) -> Dict:
        """Estimate net profit after fees and viability."""
        commission = max(
            broker_fees.get("commission_per_share", 0.0049) * quantity,
            broker_fees.get("commission_min", 0.99),
        )
        platform = max(
            broker_fees.get("platform_fee_per_share", 0.005) * quantity,
            broker_fees.get("platform_fee_min", 1.0),
        )
        max_ratio = broker_fees.get("platform_max_ratio", 0.01)
        platform = min(platform, price_entry * quantity * max_ratio)

        total_fees = round(commission + platform, 2)
        gross = (price_target - price_entry) * quantity
        net = round(gross - total_fees, 2)
        roi_after_fees = net / (price_entry * quantity) if price_entry and quantity else 0.0

        return {
            "net_profit": net,
            "total_fees": total_fees,
            "viable": net > 0,
            "roi_after_fees": roi_after_fees,
        }

    def generate_order_suggestions(self, ticker_data: Dict) -> Dict:
        """Suggest order parameters based on ticker data."""
        reason = self._risk_limits_reached()
        if reason:
            return {"blocked": reason}

        price = float(ticker_data.get("price", 0) or 0)
        atr = ticker_data.get("atr")
        capital = float(ticker_data.get("capital", 0) or 0)
        quantity = 1
        if price > 0 and capital > 0:
            quantity = max(1, int((capital * 0.02) // price))
        sl_pct = 0.08
        if atr and price:
            sl_pct = min(0.08, (2 * atr) / price)
        stop_loss = round(price * (1 - sl_pct), 2) if price else 0.0
        take_profit = round(price * 1.05, 2) if price else 0.0
        return {
            "price": price,
            "quantity": quantity,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "order_type": "limit",
        }
