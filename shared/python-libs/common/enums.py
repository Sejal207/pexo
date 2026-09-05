from enum import Enum

class UserRole(str, Enum):
    ADMIN = "ADMIN"
    HR_MANAGER = "HR_MANAGER"
    PAYROLL_OFFICER = "PAYROLL_OFFICER"
    EMPLOYEE = "EMPLOYEE"

class EmploymentStatus(str, Enum):
    ACTIVE = "ACTIVE"
    ON_LEAVE = "ON_LEAVE"
    TERMINATED = "TERMINATED"
    PROBATION = "PROBATION"

class ContractType(str, Enum):
    FULL_TIME = "FULL_TIME"
    PART_TIME = "PART_TIME"
    CONTRACT = "CONTRACT"
    INTERN = "INTERN"

class AttendanceStatus(str, Enum):
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    HALF_DAY = "HALF_DAY"
    LATE = "LATE"

class TimeOffStatus(str, Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"

class PayrunStatus(str, Enum):
    DRAFT = "DRAFT"
    COMPUTED = "COMPUTED"
    CONFIRMED = "CONFIRMED"
    PAID = "PAID"
    CANCELLED = "CANCELLED"

class RuleCategory(str, Enum):
    BASIC = "BASIC"
    ALLOWANCE = "ALLOWANCE"
    GROSS = "GROSS"
    DEDUCTION = "DEDUCTION"
    NET = "NET"
    COMPANY_CONTRIBUTION = "COMPANY_CONTRIBUTION"

class RuleCalculationType(str, Enum):
    FIXED = "FIXED"
    PERCENTAGE = "PERCENTAGE"
    FORMULA = "FORMULA"
