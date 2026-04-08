import hashlib
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional

DB_NAME = "sfoqs.db"
ACTIVE_STATUSES = ("Queued", "Preparing", "Ready")


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS menu_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT DEFAULT '',
            price REAL NOT NULL,
            is_active INTEGER NOT NULL DEFAULT 1
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer TEXT NOT NULL,
            total_price REAL NOT NULL,
            status TEXT NOT NULL,
            queue_position INTEGER NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            item_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            total_price REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id)
        )
        """
    )

    conn.commit()
    conn.close()
    seed_data()


def seed_data():
    conn = get_connection()
    cur = conn.cursor()

    default_users = [
        ("customer1", hash_password("1234"), "Customer"),
        ("staff1", hash_password("1234"), "Staff"),
        ("admin1", hash_password("1234"), "Administrator"),
    ]

    for username, password_hash, role in default_users:
        cur.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cur.fetchone() is None:
            cur.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                (username, password_hash, role),
            )

    cur.execute("SELECT COUNT(*) AS total FROM menu_items")
    count = cur.fetchone()["total"]
    if count == 0:
        default_items = [
            ("Classic Burger", "Meals", "Grilled beef burger with cheese", 1.500),
            ("Chicken Burger", "Meals", "Crispy chicken burger with sauce", 1.700),
            ("Margherita Pizza", "Meals", "Fresh tomato sauce and cheese", 2.200),
            ("Club Sandwich", "Meals", "Triple layer sandwich", 1.300),
            ("French Fries", "Sides", "Golden crispy fries", 0.700),
            ("Salad Bowl", "Sides", "Fresh mixed vegetables", 0.900),
            ("Orange Juice", "Drinks", "Fresh cold juice", 0.800),
            ("Iced Coffee", "Drinks", "Cold coffee with milk", 0.950),
            ("Chocolate Muffin", "Desserts", "Soft muffin with chocolate", 0.850),
            ("Cheesecake Slice", "Desserts", "Creamy cheesecake", 1.100),
        ]
        cur.executemany(
            "INSERT INTO menu_items (item_name, category, description, price) VALUES (?, ?, ?, ?)",
            default_items,
        )

    conn.commit()
    conn.close()


def validate_user(username: str, password: str, role: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM users WHERE username = ? AND password_hash = ? AND role = ?",
        (username, hash_password(password), role),
    )
    row = cur.fetchone()
    conn.close()
    return row


def get_categories():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT DISTINCT category FROM menu_items WHERE is_active = 1 ORDER BY category"
    )
    rows = cur.fetchall()
    conn.close()
    return [row["category"] for row in rows]


def get_menu_items(search_text: str = "", category: Optional[str] = None):
    conn = get_connection()
    cur = conn.cursor()

    query = "SELECT * FROM menu_items WHERE is_active = 1"
    params = []

    if search_text:
        query += " AND (item_name LIKE ? OR description LIKE ? OR category LIKE ?)"
        keyword = f"%{search_text}%"
        params.extend([keyword, keyword, keyword])

    if category and category != "All":
        query += " AND category = ?"
        params.append(category)

    query += " ORDER BY category, item_name"
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    return rows


def get_menu_item(item_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM menu_items WHERE id = ?", (item_id,))
    row = cur.fetchone()
    conn.close()
    return row


def get_next_queue_position():
    conn = get_connection()
    cur = conn.cursor()
    placeholders = ",".join(["?"] * len(ACTIVE_STATUSES))
    cur.execute(
        f"SELECT MAX(queue_position) AS max_pos FROM orders WHERE status IN ({placeholders})",
        ACTIVE_STATUSES,
    )
    row = cur.fetchone()
    conn.close()
    return 1 if row["max_pos"] is None else int(row["max_pos"]) + 1


def create_order(customer: str, items: List[Dict]):
    if not items:
        raise ValueError("No items provided")

    total_price = sum(float(item["total_price"]) for item in items)
    queue_position = get_next_queue_position()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO orders (customer, total_price, status, queue_position, created_at) VALUES (?, ?, ?, ?, ?)",
        (customer, total_price, "Queued", queue_position, created_at),
    )
    order_id = cur.lastrowid

    for item in items:
        cur.execute(
            "INSERT INTO order_items (order_id, item_name, quantity, unit_price, total_price) VALUES (?, ?, ?, ?, ?)",
            (
                order_id,
                item["item_name"],
                int(item["quantity"]),
                float(item["unit_price"]),
                float(item["total_price"]),
            ),
        )

    conn.commit()
    conn.close()
    return order_id, queue_position


def get_order_items(order_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT item_name, quantity, unit_price, total_price FROM order_items WHERE order_id = ? ORDER BY id",
        (order_id,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def get_latest_order_for_customer(customer: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM orders WHERE customer = ? ORDER BY id DESC LIMIT 1",
        (customer,),
    )
    order = cur.fetchone()
    conn.close()
    return order


def get_all_orders():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT
            o.id,
            o.customer,
            COALESCE(GROUP_CONCAT(oi.item_name || ' x' || oi.quantity, ', '), '') AS items_summary,
            o.total_price,
            o.status,
            o.queue_position,
            o.created_at
        FROM orders o
        LEFT JOIN order_items oi ON oi.order_id = o.id
        GROUP BY o.id, o.customer, o.total_price, o.status, o.queue_position, o.created_at
        ORDER BY o.id DESC
        """
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def update_order_status(order_id: int, new_status: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE orders SET status = ? WHERE id = ?", (new_status, order_id))
    conn.commit()
    conn.close()


def get_report_data():
    conn = get_connection()
    cur = conn.cursor()

    data = {}
    for status in ["Queued", "Preparing", "Ready", "Completed"]:
        cur.execute("SELECT COUNT(*) AS total FROM orders WHERE status = ?", (status,))
        data[status.lower()] = cur.fetchone()["total"]

    cur.execute("SELECT COUNT(*) AS total FROM orders")
    data["total_orders"] = cur.fetchone()["total"]

    placeholders = ",".join(["?"] * len(ACTIVE_STATUSES))
    cur.execute(
        f"SELECT COUNT(*) AS total FROM orders WHERE status IN ({placeholders})",
        ACTIVE_STATUSES,
    )
    data["active_orders"] = cur.fetchone()["total"]

    cur.execute(
        """
        SELECT item_name, COUNT(*) AS total_count
        FROM order_items
        GROUP BY item_name
        ORDER BY total_count DESC, item_name ASC
        LIMIT 1
        """
    )
    top = cur.fetchone()
    data["top_item"] = top["item_name"] if top else "No orders yet"

    conn.close()
    return data


def add_menu_item(item_name: str, category: str, description: str, price: float):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO menu_items (item_name, category, description, price, is_active) VALUES (?, ?, ?, ?, 1)",
        (item_name, category, description, price),
    )
    conn.commit()
    conn.close()


def delete_menu_item(item_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE menu_items SET is_active = 0 WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
