from src.models import Apartment, Bill, Parameters, Tenant, TenantSettlement, Transfer, ApartmentSettlement
from typing import List, Tuple

class Manager:
    def __init__(self, parameters: Parameters):
        self.parameters = parameters 

        self.apartments = {}
        self.tenants = {}
        self.transfers = []
        self.bills = []
       
        self.load_data()

    def load_data(self):
        self.apartments = Apartment.from_json_file(self.parameters.apartments_json_path)
        self.tenants = Tenant.from_json_file(self.parameters.tenants_json_path)
        self.transfers = Transfer.from_json_file(self.parameters.transfers_json_path)
        self.bills = Bill.from_json_file(self.parameters.bills_json_path)

    def check_tenants_apartment_keys(self) -> bool:
        for tenant in self.tenants.values():
            if tenant.apartment not in self.apartments:
                return False
        return True

    def get_apartment_costs(self, apartment_key: str, year: int = None, month: int = None) -> float | None:
        if month is not None and (month < 1 or month > 12):
            raise ValueError("Month must be between 1 and 12")
        if apartment_key not in self.apartments:
            return None
        total_cost = 0.0
        for bill in self.bills:
            if bill.apartment == apartment_key and (year is None or bill.settlement_year == year) and (month is None or bill.settlement_month == month):
                total_cost += bill.amount_pln
        return total_cost

    def get_settlement(self, apartment_key: str, year: int, month: int) -> ApartmentSettlement | None:
        if month < 1 or month > 12:
            raise ValueError("Month must be between 1 and 12")
        if apartment_key not in self.apartments:
            return None
        total_cost = self.get_apartment_costs(apartment_key, year, month)
        if total_cost is None:
            return None
        
        return ApartmentSettlement(
            key=f"{apartment_key}-{year}-{month}",
            apartment=apartment_key,
            year=year,
            month=month,
            total_due_pln=total_cost
        )
    
    def create_tenants_settlements(self, apartment_settlement: ApartmentSettlement) -> List[TenantSettlement] | None:
        if apartment_settlement.month < 1 or apartment_settlement.month > 12:
            raise ValueError("Month must be between 1 and 12")
        if apartment_settlement.apartment not in self.apartments:
            return None
        tenants_in_apartment = [tenant for tenant in self.tenants.values() if tenant.apartment == apartment_settlement.apartment]
        if not tenants_in_apartment:
            return []
        
        return [
            TenantSettlement(
                tenant=tenant.name,
                apartment_settlement=apartment_settlement.key,
                month=apartment_settlement.month,
                year=apartment_settlement.year,
                total_due_pln=apartment_settlement.total_due_pln / len(tenants_in_apartment)
            )
        for tenant in tenants_in_apartment ] 
    

    def dluznicy(self, year: int, month: int) -> list:
        debtors = []
        for apartment_key in self.apartments:
            apartment_settlement = self.get_settlement(apartment_key, year, month)
            if not apartment_settlement:
                continue

            tenant_settlements = self.create_tenants_settlements(apartment_settlement)
            if not tenant_settlements:
                continue
            for ts in tenant_settlements:
                tenant_key = None
                tenant_obj = None
                for key, tenant in self.tenants.items():
                    if tenant.name == ts.tenant:
                        tenant_key = key
                        tenant_obj = tenant
                        break

                if not tenant_obj:
                    continue

                total_expected = tenant_obj.rent_pln + ts.total_due_pln
                total_paid = sum(
                    transfer.amount_pln
                    for transfer in self.transfers
                    if transfer.tenant == tenant_key 
                    and transfer.settlement_year == year 
                    and transfer.settlement_month == month
                )

                if total_paid < total_expected - 0.01:
                    debtors.append({
                        'name': tenant_obj.name,
                        'expected_pln': total_expected,
                        'paid_pln': total_paid,
                        'debt_pln': total_expected - total_paid
                    })
    
        return debtors
    
    def get_annual_summary(self, year: int) -> dict:
        total_costs = sum(
            bill.amount_pln 
            for bill in self.bills 
            if bill.settlement_year == year
        )
        
        total_incomes = sum(
            transfer.amount_pln 
            for transfer in self.transfers 
            if transfer.settlement_year == year
        )

        return {
            "total_costs_pln": total_costs,
            "total_incomes_pln": total_incomes
        }
    def get_tax(self, year: int, month: int, tax_rate: float) -> int:
        total_incomes = sum(
            transfer.amount_pln 
            for transfer in self.transfers 
            if transfer.settlement_year == year and transfer.settlement_month == month
        )
        return round(total_incomes * tax_rate)

    def get_annual_report(self, year: int) -> dict:
        total_costs = sum(
            bill.amount_pln 
            for bill in self.bills 
            if bill.settlement_year == year
        )
        total_incomes = sum(
            transfer.amount_pln 
            for transfer in self.transfers 
            if transfer.settlement_year == year
        )
        return {
            "total_costs_pln": total_costs,
            "total_incomes_pln": total_incomes
        }