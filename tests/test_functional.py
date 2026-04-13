import pytest
from src.manager import Manager
from src.models import Parameters

def czy_suma_sie_zgadza_z_mieszkania():
    manager = Manager(Parameters())
    apartment_key = 'apart-polanka'
    year = 2025
    month = 1
    apartment_settlement = manager.get_settlement(apartment_key, year, month)
    assert apartment_settlement is not None, "Rozliczenie dla mieszkania powinno zostać wygenerowane."

    tenant_settlements = manager.create_tenants_settlements(apartment_settlement)
    assert tenant_settlements is not None, "Rozliczenia dla lokatorów powinny zostać wygenerowane."
    assert len(tenant_settlements) > 0, "W mieszkaniu powinni być przypisani jacyś lokatorzy."
    total_tenants_due = sum(ts.total_due_pln for ts in tenant_settlements)

    assert total_tenants_due == pytest.approx(apartment_settlement.total_due_pln), \
        f"Suma obciążeń lokatorów ({total_tenants_due}) nie zgadza się z kosztem mieszkania ({apartment_settlement.total_due_pln})"