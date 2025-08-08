from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, date
from typing import Optional, List
from decimal import Decimal
from enum import Enum


# Enums for various statuses and types
class UserRole(str, Enum):
    ADMINISTRATOR = "administrator"
    INVENTORY_MANAGER = "inventory_manager"
    FINANCIAL_STAFF = "financial_staff"
    PRODUCTION_MANAGER = "production_manager"


class InventoryMovementType(str, Enum):
    IN = "in"  # Stock in (purchase, return)
    OUT = "out"  # Stock out (usage, sale, loss)
    ADJUSTMENT = "adjustment"  # Stock adjustment from opname


class OrderStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    DELIVERED = "delivered"


class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"


class StockOpnameStatus(str, Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


# User Management Models
class User(SQLModel, table=True):
    __tablename__ = "users"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, max_length=50)
    email: str = Field(unique=True, max_length=255)
    password_hash: str = Field(max_length=255)
    full_name: str = Field(max_length=100)
    role: UserRole = Field(default=UserRole.INVENTORY_MANAGER)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    # Relationships
    inventory_movements: List["InventoryMovement"] = Relationship(back_populates="user")
    stock_opnames: List["StockOpname"] = Relationship(back_populates="user")
    financial_transactions: List["FinancialTransaction"] = Relationship(back_populates="user")


# Raw Material Inventory Management Models
class RawMaterial(SQLModel, table=True):
    __tablename__ = "raw_materials"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(unique=True, max_length=50)
    name: str = Field(max_length=200)
    description: str = Field(default="", max_length=1000)
    unit: str = Field(max_length=20)  # e.g., "meter", "piece", "kg"
    unit_price: Decimal = Field(decimal_places=2, max_digits=12, default=Decimal("0"))
    current_stock: Decimal = Field(decimal_places=2, max_digits=12, default=Decimal("0"))
    minimum_stock: Decimal = Field(decimal_places=2, max_digits=12, default=Decimal("0"))
    maximum_stock: Optional[Decimal] = Field(decimal_places=2, max_digits=12, default=None)
    supplier_name: str = Field(default="", max_length=200)
    supplier_contact: str = Field(default="", max_length=200)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    # Relationships
    inventory_movements: List["InventoryMovement"] = Relationship(back_populates="raw_material")
    stock_opname_items: List["StockOpnameItem"] = Relationship(back_populates="raw_material")
    order_items: List["OrderItem"] = Relationship(back_populates="raw_material")


class InventoryMovement(SQLModel, table=True):
    __tablename__ = "inventory_movements"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    raw_material_id: int = Field(foreign_key="raw_materials.id")
    user_id: int = Field(foreign_key="users.id")
    movement_type: InventoryMovementType
    quantity: Decimal = Field(decimal_places=2, max_digits=12)
    unit_price: Decimal = Field(decimal_places=2, max_digits=12, default=Decimal("0"))
    total_value: Decimal = Field(decimal_places=2, max_digits=12, default=Decimal("0"))
    reference_number: str = Field(default="", max_length=100)  # PO number, production order, etc.
    notes: str = Field(default="", max_length=500)
    movement_date: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    raw_material: RawMaterial = Relationship(back_populates="inventory_movements")
    user: User = Relationship(back_populates="inventory_movements")


# Stock Opname Management Models
class StockOpname(SQLModel, table=True):
    __tablename__ = "stock_opnames"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    opname_number: str = Field(unique=True, max_length=50)
    title: str = Field(max_length=200)
    description: str = Field(default="", max_length=1000)
    user_id: int = Field(foreign_key="users.id")
    status: StockOpnameStatus = Field(default=StockOpnameStatus.PLANNED)
    planned_date: date
    started_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    # Relationships
    user: User = Relationship(back_populates="stock_opnames")
    items: List["StockOpnameItem"] = Relationship(back_populates="stock_opname")


class StockOpnameItem(SQLModel, table=True):
    __tablename__ = "stock_opname_items"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    stock_opname_id: int = Field(foreign_key="stock_opnames.id")
    raw_material_id: int = Field(foreign_key="raw_materials.id")
    system_stock: Decimal = Field(decimal_places=2, max_digits=12)
    physical_stock: Optional[Decimal] = Field(decimal_places=2, max_digits=12, default=None)
    difference: Optional[Decimal] = Field(decimal_places=2, max_digits=12, default=None)
    notes: str = Field(default="", max_length=500)
    counted_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    stock_opname: StockOpname = Relationship(back_populates="items")
    raw_material: RawMaterial = Relationship(back_populates="stock_opname_items")


# Order Tracking Models
class Customer(SQLModel, table=True):
    __tablename__ = "customers"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=200)
    company: str = Field(default="", max_length=200)
    email: str = Field(default="", max_length=255)
    phone: str = Field(default="", max_length=50)
    address: str = Field(default="", max_length=1000)
    city: str = Field(default="", max_length=100)
    postal_code: str = Field(default="", max_length=20)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    # Relationships
    orders: List["Order"] = Relationship(back_populates="customer")


class Order(SQLModel, table=True):
    __tablename__ = "orders"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    order_number: str = Field(unique=True, max_length=50)
    customer_id: int = Field(foreign_key="customers.id")
    status: OrderStatus = Field(default=OrderStatus.PENDING)
    order_date: date = Field(default_factory=date.today)
    due_date: date
    completion_date: Optional[date] = Field(default=None)
    delivery_date: Optional[date] = Field(default=None)
    total_amount: Decimal = Field(decimal_places=2, max_digits=15, default=Decimal("0"))
    notes: str = Field(default="", max_length=1000)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    # Relationships
    customer: Customer = Relationship(back_populates="orders")
    items: List["OrderItem"] = Relationship(back_populates="order")


class Product(SQLModel, table=True):
    __tablename__ = "products"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(unique=True, max_length=50)
    name: str = Field(max_length=200)
    description: str = Field(default="", max_length=1000)
    category: str = Field(default="", max_length=100)
    unit_price: Decimal = Field(decimal_places=2, max_digits=12, default=Decimal("0"))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    # Relationships
    order_items: List["OrderItem"] = Relationship(back_populates="product")


class OrderItem(SQLModel, table=True):
    __tablename__ = "order_items"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="orders.id")
    product_id: Optional[int] = Field(foreign_key="products.id", default=None)
    raw_material_id: Optional[int] = Field(foreign_key="raw_materials.id", default=None)
    item_name: str = Field(max_length=200)  # Product or raw material name
    quantity: Decimal = Field(decimal_places=2, max_digits=12)
    unit_price: Decimal = Field(decimal_places=2, max_digits=12)
    total_price: Decimal = Field(decimal_places=2, max_digits=12)
    notes: str = Field(default="", max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    order: Order = Relationship(back_populates="items")
    product: Optional[Product] = Relationship(back_populates="order_items")
    raw_material: Optional[RawMaterial] = Relationship(back_populates="order_items")


# Financial Management Models
class FinancialCategory(SQLModel, table=True):
    __tablename__ = "financial_categories"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=200)
    transaction_type: TransactionType
    description: str = Field(default="", max_length=500)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    transactions: List["FinancialTransaction"] = Relationship(back_populates="category")


class FinancialTransaction(SQLModel, table=True):
    __tablename__ = "financial_transactions"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    transaction_number: str = Field(unique=True, max_length=50)
    user_id: int = Field(foreign_key="users.id")
    category_id: int = Field(foreign_key="financial_categories.id")
    transaction_type: TransactionType
    amount: Decimal = Field(decimal_places=2, max_digits=15)
    description: str = Field(max_length=1000)
    reference_number: str = Field(default="", max_length=100)
    transaction_date: date = Field(default_factory=date.today)
    payment_method: str = Field(default="", max_length=100)  # Cash, Bank Transfer, etc.
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    # Relationships
    user: User = Relationship(back_populates="financial_transactions")
    category: FinancialCategory = Relationship(back_populates="transactions")


# Employee Management Models
class Department(SQLModel, table=True):
    __tablename__ = "departments"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, max_length=200)
    description: str = Field(default="", max_length=500)
    manager_name: str = Field(default="", max_length=200)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    employees: List["Employee"] = Relationship(back_populates="department")


class Employee(SQLModel, table=True):
    __tablename__ = "employees"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    employee_number: str = Field(unique=True, max_length=50)
    full_name: str = Field(max_length=200)
    email: str = Field(default="", max_length=255)
    phone: str = Field(default="", max_length=50)
    address: str = Field(default="", max_length=1000)
    city: str = Field(default="", max_length=100)
    postal_code: str = Field(default="", max_length=20)
    birth_date: Optional[date] = Field(default=None)
    hire_date: date = Field(default_factory=date.today)
    termination_date: Optional[date] = Field(default=None)
    department_id: int = Field(foreign_key="departments.id")
    position: str = Field(max_length=200)
    salary: Optional[Decimal] = Field(decimal_places=2, max_digits=12, default=None)
    is_active: bool = Field(default=True)
    emergency_contact_name: str = Field(default="", max_length=200)
    emergency_contact_phone: str = Field(default="", max_length=50)
    notes: str = Field(default="", max_length=1000)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    # Relationships
    department: Department = Relationship(back_populates="employees")


# Non-persistent schemas for validation and API
class UserCreate(SQLModel, table=False):
    username: str = Field(max_length=50)
    email: str = Field(max_length=255)
    password: str = Field(min_length=8)
    full_name: str = Field(max_length=100)
    role: UserRole = Field(default=UserRole.INVENTORY_MANAGER)


class UserUpdate(SQLModel, table=False):
    username: Optional[str] = Field(default=None, max_length=50)
    email: Optional[str] = Field(default=None, max_length=255)
    full_name: Optional[str] = Field(default=None, max_length=100)
    role: Optional[UserRole] = Field(default=None)
    is_active: Optional[bool] = Field(default=None)


class RawMaterialCreate(SQLModel, table=False):
    code: str = Field(max_length=50)
    name: str = Field(max_length=200)
    description: str = Field(default="", max_length=1000)
    unit: str = Field(max_length=20)
    unit_price: Decimal = Field(decimal_places=2, max_digits=12, default=Decimal("0"))
    minimum_stock: Decimal = Field(decimal_places=2, max_digits=12, default=Decimal("0"))
    maximum_stock: Optional[Decimal] = Field(decimal_places=2, max_digits=12, default=None)
    supplier_name: str = Field(default="", max_length=200)
    supplier_contact: str = Field(default="", max_length=200)


class RawMaterialUpdate(SQLModel, table=False):
    name: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    unit: Optional[str] = Field(default=None, max_length=20)
    unit_price: Optional[Decimal] = Field(default=None, decimal_places=2, max_digits=12)
    minimum_stock: Optional[Decimal] = Field(default=None, decimal_places=2, max_digits=12)
    maximum_stock: Optional[Decimal] = Field(default=None, decimal_places=2, max_digits=12)
    supplier_name: Optional[str] = Field(default=None, max_length=200)
    supplier_contact: Optional[str] = Field(default=None, max_length=200)


class InventoryMovementCreate(SQLModel, table=False):
    raw_material_id: int
    movement_type: InventoryMovementType
    quantity: Decimal = Field(decimal_places=2, max_digits=12)
    unit_price: Decimal = Field(decimal_places=2, max_digits=12, default=Decimal("0"))
    reference_number: str = Field(default="", max_length=100)
    notes: str = Field(default="", max_length=500)


class CustomerCreate(SQLModel, table=False):
    name: str = Field(max_length=200)
    company: str = Field(default="", max_length=200)
    email: str = Field(default="", max_length=255)
    phone: str = Field(default="", max_length=50)
    address: str = Field(default="", max_length=1000)
    city: str = Field(default="", max_length=100)
    postal_code: str = Field(default="", max_length=20)


class OrderCreate(SQLModel, table=False):
    order_number: str = Field(max_length=50)
    customer_id: int
    due_date: date
    notes: str = Field(default="", max_length=1000)


class OrderUpdate(SQLModel, table=False):
    status: Optional[OrderStatus] = Field(default=None)
    due_date: Optional[date] = Field(default=None)
    completion_date: Optional[date] = Field(default=None)
    delivery_date: Optional[date] = Field(default=None)
    notes: Optional[str] = Field(default=None, max_length=1000)


class EmployeeCreate(SQLModel, table=False):
    employee_number: str = Field(max_length=50)
    full_name: str = Field(max_length=200)
    email: str = Field(default="", max_length=255)
    phone: str = Field(default="", max_length=50)
    address: str = Field(default="", max_length=1000)
    birth_date: Optional[date] = Field(default=None)
    hire_date: date = Field(default_factory=date.today)
    department_id: int
    position: str = Field(max_length=200)
    salary: Optional[Decimal] = Field(default=None, decimal_places=2, max_digits=12)
    emergency_contact_name: str = Field(default="", max_length=200)
    emergency_contact_phone: str = Field(default="", max_length=50)


class FinancialTransactionCreate(SQLModel, table=False):
    transaction_number: str = Field(max_length=50)
    category_id: int
    transaction_type: TransactionType
    amount: Decimal = Field(decimal_places=2, max_digits=15)
    description: str = Field(max_length=1000)
    reference_number: str = Field(default="", max_length=100)
    transaction_date: date = Field(default_factory=date.today)
    payment_method: str = Field(default="", max_length=100)
