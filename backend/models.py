# Kairos Accounting - Comprehensive ERP Models
# ERPNext-inspired with AI-first approach

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone

# ==================== CRM Module ====================
class Lead(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    lead_name: str
    company_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    source: str = "AI Conversation"
    status: str = "Open"  # Open, Qualified, Lost, Converted
    industry: Optional[str] = None
    requirement: Optional[str] = None
    ai_score: Optional[float] = None
    conversation_log: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class Opportunity(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    opportunity_from: str  # Lead or Customer
    party_name: str
    expected_closing: Optional[str] = None
    probability: float = 50.0
    opportunity_amount: float = 0.0
    status: str = "Open"  # Open, Quotation, Converted, Lost
    items: List[Dict[str, Any]] = []
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class Customer(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customer_name: str
    customer_type: str = "Company"  # Company, Individual
    customer_group: str = "Commercial"
    territory: str = "India"
    gstin: Optional[str] = None
    pan: Optional[str] = None
    billing_address: Optional[str] = None
    shipping_address: Optional[str] = None
    credit_limit: float = 0.0
    payment_terms: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

# ==================== Sales Module ====================
class Quotation(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customer_name: str
    quotation_to: str = "Customer"
    order_type: str = "Sales"
    transaction_date: str
    valid_till: Optional[str] = None
    items: List[Dict[str, Any]] = []
    total_qty: float = 0.0
    total: float = 0.0
    taxes: List[Dict[str, Any]] = []
    grand_total: float = 0.0
    terms: Optional[str] = None
    status: str = "Draft"  # Draft, Submitted, Ordered, Lost
    created_from_prompt: bool = True
    prompt_text: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class SalesOrder(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customer: str
    order_type: str = "Sales"
    transaction_date: str
    delivery_date: Optional[str] = None
    po_no: Optional[str] = None
    items: List[Dict[str, Any]] = []
    total_qty: float = 0.0
    total: float = 0.0
    taxes: List[Dict[str, Any]] = []
    grand_total: float = 0.0
    advance_paid: float = 0.0
    status: str = "Draft"  # Draft, To Deliver, To Bill, Completed, Cancelled
    per_delivered: float = 0.0
    per_billed: float = 0.0
    quotation_ref: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class DeliveryNote(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customer: str
    posting_date: str
    posting_time: str
    sales_order_ref: Optional[str] = None
    items: List[Dict[str, Any]] = []
    total_qty: float = 0.0
    lr_no: Optional[str] = None  # Lorry Receipt
    transporter: Optional[str] = None
    vehicle_no: Optional[str] = None
    status: str = "Draft"  # Draft, To Bill, Completed
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

# ==================== Purchase Module ====================
class MaterialRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    material_request_type: str = "Purchase"
    transaction_date: str
    required_by: str
    items: List[Dict[str, Any]] = []
    status: str = "Draft"  # Draft, Submitted, Ordered, Received
    ai_suggested: bool = False
    reorder_reason: Optional[str] = None
    created_at: str = Field(default_factory=lambda: str(uuid.uuid4()))

class RequestForQuotation(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    transaction_date: str
    suppliers: List[str] = []
    items: List[Dict[str, Any]] = []
    message_for_supplier: Optional[str] = None
    status: str = "Draft"
    material_request_ref: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class SupplierQuotation(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    supplier: str
    transaction_date: str
    valid_till: Optional[str] = None
    items: List[Dict[str, Any]] = []
    total: float = 0.0
    taxes: List[Dict[str, Any]] = []
    grand_total: float = 0.0
    status: str = "Draft"
    rfq_ref: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class PurchaseOrder(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    supplier: str
    transaction_date: str
    schedule_date: Optional[str] = None
    items: List[Dict[str, Any]] = []
    total_qty: float = 0.0
    total: float = 0.0
    taxes: List[Dict[str, Any]] = []
    grand_total: float = 0.0
    status: str = "Draft"  # Draft, To Receive, To Bill, Completed
    per_received: float = 0.0
    per_billed: float = 0.0
    supplier_quotation_ref: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class PurchaseReceipt(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    supplier: str
    posting_date: str
    posting_time: str
    purchase_order_ref: Optional[str] = None
    items: List[Dict[str, Any]] = []
    total_qty: float = 0.0
    supplier_delivery_note: Optional[str] = None
    lr_no: Optional[str] = None
    status: str = "Draft"
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

# ==================== Stock/Inventory Module ====================
class Item(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    item_code: str
    item_name: str
    item_group: str
    stock_uom: str = "Nos"
    is_stock_item: bool = True
    is_sales_item: bool = True
    is_purchase_item: bool = True
    has_serial_no: bool = False
    has_batch_no: bool = False
    opening_stock: float = 0.0
    valuation_rate: float = 0.0
    standard_rate: float = 0.0
    hsn_code: Optional[str] = None
    gst_rate: float = 18.0
    reorder_level: float = 0.0
    reorder_qty: float = 0.0
    warehouse: str = "Main Warehouse"
    description: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class StockEntry(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    stock_entry_type: str  # Material Receipt, Material Issue, Material Transfer, Repack
    posting_date: str
    posting_time: str
    from_warehouse: Optional[str] = None
    to_warehouse: Optional[str] = None
    items: List[Dict[str, Any]] = []
    total_amount: float = 0.0
    status: str = "Draft"
    created_from_image: bool = False
    image_url: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class StockReconciliation(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    posting_date: str
    posting_time: str
    purpose: str = "Stock Reconciliation"
    items: List[Dict[str, Any]] = []
    expense_account: str = "Stock Adjustment - KA"
    difference_amount: float = 0.0
    ai_reconciled: bool = False
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

# ==================== HR Module ====================
class Employee(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    employee_name: str
    employee_number: Optional[str] = None
    gender: Optional[str] = None
    date_of_birth: Optional[str] = None
    date_of_joining: str
    department: Optional[str] = None
    designation: Optional[str] = None
    employment_type: str = "Full-time"
    status: str = "Active"
    attendance_device_id: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class Attendance(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    employee: str
    attendance_date: str
    status: str  # Present, Absent, Half Day, On Leave
    shift: Optional[str] = None
    in_time: Optional[str] = None
    out_time: Optional[str] = None
    working_hours: float = 0.0
    late_entry: bool = False
    early_exit: bool = False
    marked_by_ai: bool = False
    image_ref: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class LeaveApplication(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    employee: str
    leave_type: str
    from_date: str
    to_date: str
    total_leave_days: float = 0.0
    leave_balance: float = 0.0
    reason: Optional[str] = None
    status: str = "Draft"  # Draft, Approved, Rejected, Cancelled
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class SalarySlip(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    employee: str
    salary_month: str
    earnings: List[Dict[str, Any]] = []
    deductions: List[Dict[str, Any]] = []
    gross_pay: float = 0.0
    total_deduction: float = 0.0
    net_pay: float = 0.0
    tds: float = 0.0
    payment_days: float = 0.0
    status: str = "Draft"
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

# ==================== Projects Module ====================
class Project(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_name: str
    status: str = "Open"  # Open, Completed, Cancelled
    project_type: Optional[str] = None
    priority: str = "Medium"
    expected_start_date: Optional[str] = None
    expected_end_date: Optional[str] = None
    estimated_costing: float = 0.0
    actual_costing: float = 0.0
    percent_complete: float = 0.0
    customer: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class Task(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    subject: str
    project: Optional[str] = None
    status: str = "Open"  # Open, Working, Pending Review, Completed, Cancelled
    priority: str = "Medium"
    task_weight: float = 0.0
    expected_time: float = 0.0
    actual_time: float = 0.0
    exp_start_date: Optional[str] = None
    exp_end_date: Optional[str] = None
    assigned_to: Optional[str] = None
    description: Optional[str] = None
    created_from_conversation: bool = False
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class Timesheet(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    employee: str
    time_logs: List[Dict[str, Any]] = []
    total_hours: float = 0.0
    total_billable_hours: float = 0.0
    total_billed_hours: float = 0.0
    status: str = "Draft"
    ai_generated: bool = False
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

# ==================== Manufacturing Module ====================
class BOM(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    item: str
    quantity: float = 1.0
    items: List[Dict[str, Any]] = []
    total_cost: float = 0.0
    with_operations: bool = False
    operations: List[Dict[str, Any]] = []
    is_active: bool = True
    is_default: bool = False
    ai_suggested: bool = False
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class WorkOrder(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    production_item: str
    bom_no: str
    qty: float = 0.0
    produced_qty: float = 0.0
    planned_start_date: str
    expected_delivery_date: Optional[str] = None
    source_warehouse: Optional[str] = None
    wip_warehouse: str
    fg_warehouse: str
    status: str = "Draft"  # Draft, Not Started, In Process, Completed
    required_items: List[Dict[str, Any]] = []
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

# ==================== Quality Module ====================
class QualityInspection(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    inspection_type: str  # Incoming, Outgoing, In Process
    reference_type: str  # Purchase Receipt, Delivery Note, Stock Entry
    reference_name: str
    item_code: str
    sample_size: float = 0.0
    inspected_by: str
    inspection_date: str
    readings: List[Dict[str, Any]] = []
    status: str = "Accepted"  # Accepted, Rejected
    image_url: Optional[str] = None
    ai_quality_score: Optional[float] = None
    remarks: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())