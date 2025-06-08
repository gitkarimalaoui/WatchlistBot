"""Simple Tkinter popup to confirm trade execution."""

import tkinter as tk


def show_trade_popup(ticker: str, price: float, qty: int, stop_loss: float) -> None:
    """Display confirmation dialog with trade details.

    Parameters
    ----------
    ticker : str
        Stock ticker to trade.
    price : float
        Order price.
    qty : int
        Quantity to buy.
    stop_loss : float
        Stop loss level displayed for information.
    """

    # Lazy import to avoid heavy dependencies when unused
    from utils.order_executor import executer_ordre_reel_direct

    def on_execute() -> None:
        root.destroy()
        executer_ordre_reel_direct(ticker, price, qty, stop_loss)

    root = tk.Tk()
    root.title("WatchlistBot - Trade Alert")
    root.attributes("-topmost", True)

    message = (
        f"Ticker : {ticker}\n"
        f"Prix : {price}\n"
        f"Quantité : {qty}\n"
        f"Stop Loss : {stop_loss:.2f}"
    )
    tk.Label(root, text=message, justify="left", padx=20, pady=10).pack()

    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=10)
    tk.Button(btn_frame, text="Exécuter", command=on_execute).pack(side="left", padx=5)
    tk.Button(btn_frame, text="Annuler", command=root.destroy).pack(side="left", padx=5)

    root.mainloop()

